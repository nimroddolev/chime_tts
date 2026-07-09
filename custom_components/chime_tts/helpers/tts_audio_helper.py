"""Helper class for generating TTS Audio in Chime TTS."""
import asyncio
import io
from datetime import datetime
from homeassistant.core import HomeAssistant
from homeassistant.components import tts
from hass_nabucasa import voice as nabu_voices
import logging
from .filesystem import FilesystemHelper
from .helpers import ChimeTTSHelper
from ..const import (
    TTS_TIMEOUT_KEY,
    TTS_TIMEOUT_DEFAULT,
    QUEUE_TIMEOUT_KEY,
    QUEUE_TIMEOUT_DEFAULT,
    TTS_PLATFORM_KEY,
     FALLBACK_TTS_PLATFORM_KEY,
    AMAZON_POLLY,
    BAIDU,
    ELEVENLABS,
    GOOGLE_CLOUD,
    GOOGLE_TRANSLATE,
    IBM_WATSON_TTS,
    MARYTTS,
    MICROSOFT_EDGE_TTS,
    MICROSOFT_TTS,
    NABU_CASA_CLOUD_TTS,
    NABU_CASA_CLOUD_TTS_OLD,
    OPENAI_TTS,
    PICOTTS,
    PIPER,
    VOICE_RSS,
    YANDEX_TTS,
)

helpers = ChimeTTSHelper()
filesystem_helper = FilesystemHelper()

_LOGGER = logging.getLogger(__name__)


def _clamped_tts_timeout(tts_timeout: int, queue_timeout: int, has_pending_fallback: bool) -> int:
    """Cap the per-platform TTS timeout so a pending fallback fits in the queue window.

    The queue cancels the whole service call after queue_timeout. When a fallback
    platform could still run, reserve room for both attempts so the fallback is
    not cancelled (#232). With no pending fallback, the full timeout is kept.
    """
    if not has_pending_fallback:
        return tts_timeout
    max_timeout = max(1, (queue_timeout - 2) // 2)
    return min(tts_timeout, max_timeout)

class TTSAudioHelper:
    """Helper class for generating TTS Audio in Chime TTS."""

    _data = {}

    async def async_request_tts_audio(self, hass: HomeAssistant, tts_platform: str, message: str, language: str, cache: bool, options: dict, is_fallback: bool = False):
        """Send an API request for TTS audio and return the audio file's local filepath."""
        start_time = datetime.now()

        # Step 1: Input validation and preparation
        tts_platform, tts_options, language = self._prepare_tts_request(hass, tts_platform, message, language, options)
        if not tts_platform:
            return None

        # Step 2: Generate TTS audio
        media_source_id, audio_data = await self._generate_tts_audio(
            hass, tts_platform, message, language, cache, tts_options, is_fallback
        )

        # Step 3: Process the audio data
        audio = await self._process_audio_data(hass, media_source_id, audio_data, start_time)
        if audio:
            return audio

        # Step 4: Retry with fallback platform if needed
        return await self._retry_with_fallback(hass, tts_platform, message, language, cache, options)

    def _prepare_tts_request(self, hass: HomeAssistant, tts_platform, message, language, options):
        if not options:
            options = {}
        tts_options = options.copy()

        if not message:
            _LOGGER.warning("No message text provided for TTS audio")
            return None, None, None

        tts_platform = helpers.get_tts_platform(
            hass=hass,
            tts_platform=tts_platform,
            default_tts_platform=self._data[TTS_PLATFORM_KEY],
            fallback_tts_platform=self._data[FALLBACK_TTS_PLATFORM_KEY],
        )
        if not tts_platform:
            return None, None, None

        language = self._adjust_language_and_voice(tts_platform, language, tts_options)
        return tts_platform, tts_options, language

    def _adjust_language_and_voice(self, tts_platform, language, tts_options):
        original_language = language
        voice = tts_options.get("voice", None)
        # Nabu Casa cloud can arrive as a full entity id (tts.home_assistant_cloud)
        # now that platform matching keeps entity ids; map it to the constant so
        # the language handling below still applies.
        if tts_platform and tts_platform.lower() in ("tts.home_assistant_cloud", "tts.cloud"):
            tts_platform = NABU_CASA_CLOUD_TTS
        language_aware_platforms = [
            AMAZON_POLLY,
            GOOGLE_TRANSLATE,
            GOOGLE_CLOUD,
            NABU_CASA_CLOUD_TTS,
            IBM_WATSON_TTS,
            MICROSOFT_EDGE_TTS,
            MICROSOFT_TTS,
        ]
        if (language or tts_options.get("language")) and tts_platform in language_aware_platforms:
            if not language:
                language = tts_options.get("language")
            if tts_platform == IBM_WATSON_TTS and voice is None:
                tts_options["voice"] = language
                language = None
            elif tts_platform == MICROSOFT_TTS:
                tts_options.pop("language", None)
                if voice:
                    tts_options["type"] = voice
                    tts_options.pop("voice", None)
            elif tts_platform in (NABU_CASA_CLOUD_TTS, GOOGLE_CLOUD):
                # These take the language as a separate argument; leaving it in
                # the options makes the engine reject the call with
                # "Invalid options found: ['language']" (#242, #210).
                tts_options.pop("language", None)

        if tts_platform == NABU_CASA_CLOUD_TTS and isinstance(voice, str) and voice and not language:
            # Styled cloud voices arrive as "name||style"; match on the base name
            # so the style suffix does not break the language lookup (#307).
            base_voice = voice.split("||")[0]
            for key, value in nabu_voices.TTS_VOICES.items():
                if base_voice in value:
                    language = key
                    _LOGGER.debug(
                        " - Setting language to '%s' for Nabu Casa TTS voice: '%s'.",
                        language,
                        voice,
                    )
        return language or original_language
    
    async def _generate_tts_audio(
        self,
        hass: HomeAssistant,
        tts_platform: str,
        message: str,
        language: str | None,
        cache: bool,
        tts_options: dict | None,
        is_fallback: bool = False,
    ) -> tuple[str | None, bytes | None]:
        media_source_id: str | None = None
        audio_data: bytes | None = None
        engine_candidates = self._engine_candidates(hass, tts_platform)

        timeout = int(self._data.get(TTS_TIMEOUT_KEY, TTS_TIMEOUT_DEFAULT))
        try:
            queue_timeout = int(self._data.get(QUEUE_TIMEOUT_KEY, QUEUE_TIMEOUT_DEFAULT))
            # Only reserve room for a fallback when one is configured and this is
            # not already the fallback attempt.
            has_pending_fallback = bool(self._data.get(FALLBACK_TTS_PLATFORM_KEY)) and not is_fallback
            clamped = _clamped_tts_timeout(timeout, queue_timeout, has_pending_fallback)
            if clamped != timeout:
                _LOGGER.debug(
                    "Clamping TTS generation timeout from %ss to %ss so a fallback fits within the %ss queue timeout",
                    timeout,
                    clamped,
                    queue_timeout,
                )
                timeout = clamped
            last_error: Exception | None = None
            last_engine = engine_candidates[0]

            for engine in engine_candidates:
                last_engine = engine
                try:
                    # generate_media_source_id is sync; offload to thread, guard with timeout
                    media_source_id = await asyncio.wait_for(
                        asyncio.to_thread(
                            tts.media_source.generate_media_source_id,
                            hass=hass,
                            message=message,
                            engine=engine,
                            language=language,
                            cache=cache,
                            options=tts_options,
                        ),
                        timeout=timeout,
                    )
                    return media_source_id, audio_data
                except Exception as exc:  # noqa: PERF203
                    last_error = exc
                    if len(engine_candidates) > 1:
                        _LOGGER.debug(
                            "TTS audio generation with %s failed, trying next engine candidate: %s",
                            engine,
                            exc,
                        )

            if last_error is not None:
                self._handle_generation_error(last_error, last_engine, media_source_id)
            return None, None

        except asyncio.TimeoutError:
            _LOGGER.error(
                "TTS audio generation with %s timed out after %ss. "
                "Consider increasing the TTS timeout in the configuration.",
                engine_candidates[0], timeout,
            )
            return None, None

        except asyncio.CancelledError:
            _LOGGER.warning(
                "TTS audio generation with %s cancelled.", engine_candidates[0]
            )
            raise  # preserve cancellation

        except Exception as exc:
            self._handle_generation_error(exc, engine_candidates[0], media_source_id)
            return None, None

    def _engine_candidates(
        self, hass: HomeAssistant, tts_platform: str
    ) -> list[str]:
        """Return likely engine ids for modern entity and legacy provider paths."""
        manager = hass.data.get("tts_manager")
        legacy_providers = set(getattr(manager, "providers", {})) if manager else set()
        candidates: list[str] = []

        def add_candidate(candidate: str) -> None:
            if candidate and candidate not in candidates:
                candidates.append(candidate)

        if tts_platform.startswith("tts."):
            bare_platform = tts_platform[4:]
            add_candidate(tts_platform)
            if bare_platform in legacy_providers:
                add_candidate(bare_platform)
        else:
            if tts_platform in legacy_providers:
                add_candidate(tts_platform)
            add_candidate(f"tts.{tts_platform}")

        return candidates



    async def _process_audio_data(self, hass: HomeAssistant, media_source_id, audio_data, start_time):
        if not media_source_id:
            _LOGGER.error("Error: Unable to generate media_source_id")
            return None

        try:
            audio_data = await tts.async_get_media_source_audio(
                hass=hass, media_source_id=media_source_id
            )
        except Exception as error:
            _LOGGER.error(
                "   - Error calling tts.async_get_media_source_audio with media_source_id = '%s': %s",
                str(media_source_id),
                str(error),
            )

        if audio_data is not None and len(audio_data) == 2:
            return await self._extract_audio(audio_data, start_time)

        return None

    async def _extract_audio(self, audio_data, start_time):
        audio_bytes = audio_data[1]
        file = io.BytesIO(audio_bytes)
        if not file:
            _LOGGER.error("...could not convert TTS bytes to audio")
            return None

        audio = await filesystem_helper.async_load_audio(file)
        if audio and len(audio) > 0:
            end_time = datetime.now()
            completion_time = round((end_time - start_time).total_seconds(), 2)
            completion_time_string = (
                f"{completion_time}s" if completion_time >= 1 else f"{completion_time * 1000}ms"
            )
            _LOGGER.debug("   ...TTS audio generated in %s", completion_time_string)
            return audio

        _LOGGER.error("...could not extract TTS audio from file")
        return None

    async def _retry_with_fallback(self, hass: HomeAssistant, tts_platform, message, language, cache, options):
        fallback_platform = self._data.get(FALLBACK_TTS_PLATFORM_KEY)
        if tts_platform != fallback_platform and fallback_platform:
            _LOGGER.debug(
                "Retrying TTS audio generation with fallback platform '%s'", fallback_platform
            )
            return await self.async_request_tts_audio(
                hass=hass,
                tts_platform=fallback_platform,
                message=message,
                language=language,
                cache=cache,
                options=options,
                is_fallback=True,
            )
        _LOGGER.error("...audio_data generation failed")
        return None

    def _handle_generation_error(self, error, tts_platform, media_source_id):
        if str(error) == "Invalid TTS provider selected":
            missing_tts_platform_error(tts_platform)
        else:
            _LOGGER.error(
                "   - Error calling tts.media_source.generate_media_source_id: %s",
                error,
            )


def missing_tts_platform_error(tts_platform):
    """Write a TTS platform specific debug warning when the TTS platform has not been configured."""
    tts_platform_name = tts_platform
    tts_platform_documentation = "https://www.home-assistant.io/integrations/#text-to-speech"
    if tts_platform is AMAZON_POLLY:
        tts_platform_name = "Amazon Polly"
        tts_platform_documentation = "https://www.home-assistant.io/integrations/amazon_polly"
    if tts_platform is BAIDU:
        tts_platform_name = "Baidu"
        tts_platform_documentation = "https://www.home-assistant.io/integrations/baidu"
    if tts_platform is ELEVENLABS:
        tts_platform_name = "ElevenLabsTS"
        tts_platform_documentation = "https://www.home-assistant.io/integrations/elevenlabs"
    if tts_platform is GOOGLE_CLOUD:
        tts_platform_name = "Google Cloud"
        tts_platform_documentation = "https://www.home-assistant.io/integrations/google_cloud"
    if tts_platform is GOOGLE_TRANSLATE:
        tts_platform_name = "Google Translate"
        tts_platform_documentation = "https://www.home-assistant.io/integrations/google_translate"
    if tts_platform is IBM_WATSON_TTS:
        tts_platform_name = "Watson TTS"
        tts_platform_documentation = "https://www.home-assistant.io/integrations/watson_tts"
    if tts_platform is MARYTTS:
        tts_platform_name = "MaryTTS"
        tts_platform_documentation = "https://www.home-assistant.io/integrations/marytts"
    if tts_platform is MICROSOFT_TTS:
        tts_platform_name = "Microsoft TTS"
        tts_platform_documentation = "https://www.home-assistant.io/integrations/microsoft"
    if tts_platform is MICROSOFT_EDGE_TTS:
        tts_platform_name = "Microsoft Edge TTS"
        tts_platform_documentation = "https://github.com/hasscc/hass-edge-tts"
    if tts_platform is NABU_CASA_CLOUD_TTS or tts_platform is NABU_CASA_CLOUD_TTS_OLD:
        tts_platform_name = "Nabu Casa Cloud TTS"
        tts_platform_documentation = "https://www.home-assistant.io/integrations/cloud"
    if tts_platform is OPENAI_TTS:
        tts_platform_name = "OpenAI TTS"
        tts_platform_documentation = "https://github.com/sfortis/openai_tts"
    if tts_platform is PICOTTS:
        tts_platform_name = "PicoTTS"
        tts_platform_documentation = "https://www.home-assistant.io/integrations/picotts"
    if tts_platform is PIPER:
        tts_platform_name = "Piper"
        tts_platform_documentation = "https://www.home-assistant.io/integrations/piper"
    if tts_platform is VOICE_RSS:
        tts_platform_name = "VoiceRSS"
        tts_platform_documentation = "https://www.home-assistant.io/integrations/voicerss"
    if tts_platform is YANDEX_TTS:
        tts_platform_name = "Yandex TTS"
        tts_platform_documentation = "https://www.home-assistant.io/integrations/yandextts"
    _LOGGER.error(
        "The %s platform was not found. Please check that it has been configured correctly: %s",
        tts_platform_name,
        tts_platform_documentation
    )
