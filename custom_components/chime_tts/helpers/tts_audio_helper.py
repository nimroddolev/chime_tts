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

class TTSAudioHelper:
    """Helper class for generating TTS Audio in Chime TTS."""

    _data = {}

    async def async_request_tts_audio(self, hass: HomeAssistant, tts_platform: str, message: str, language: str, cache: bool, options: dict):
        """Send an API request for TTS audio and return the audio file's local filepath."""
        start_time = datetime.now()

        # Step 1: Input validation and preparation
        tts_platform, tts_options, language = self._prepare_tts_request(hass, tts_platform, message, language, options)
        if not tts_platform:
            return None

        # Step 2: Generate TTS audio
        media_source_id, audio_data = await self._generate_tts_audio(
            hass, tts_platform, message, language, cache, tts_options
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
        voice = tts_options.get("voice", None)
        if (
            (language or tts_options.get("language"))
            and tts_platform
            in [
                AMAZON_POLLY,
                GOOGLE_TRANSLATE,
                NABU_CASA_CLOUD_TTS,
                IBM_WATSON_TTS,
                MICROSOFT_EDGE_TTS,
                MICROSOFT_TTS,
            ]
        ):
            if tts_platform == IBM_WATSON_TTS and voice is None:
                tts_options["voice"] = language
                language = None
            if tts_platform == MICROSOFT_TTS:
                if not language:
                    language = tts_options.get("language")
                tts_options.pop("language", None)
                if voice:
                    tts_options["type"] = voice
                    tts_options.pop("voice", None)
        else:
            language = None

        if (
            tts_platform == NABU_CASA_CLOUD_TTS
            and voice
            and not language
        ):
            for key, value in nabu_voices.TTS_VOICES.items():
                if voice in value:
                    language = key
                    _LOGGER.debug(
                        " - Setting language to '%s' for Nabu Casa TTS voice: '%s'.",
                        language,
                        voice,
                    )
        return language

    async def _generate_tts_audio(self, hass: HomeAssistant, tts_platform, message, language, cache, tts_options):
        media_source_id = None
        audio_data = None
        try:
            timeout = int(self._data.get(TTS_TIMEOUT_KEY, TTS_TIMEOUT_DEFAULT))
            media_source_id = await asyncio.wait_for(
                asyncio.to_thread(
                    tts.media_source.generate_media_source_id,
                    hass=hass,
                    message=message,
                    engine=tts_platform,
                    language=language,
                    cache=cache,
                    options=tts_options,
                ),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            _LOGGER.error("TTS audio generation with %s timed out after %ss. Consider increasing the TTS audio generation timeout value in the configuration.", tts_platform, str(timeout))
        except asyncio.CancelledError:
            _LOGGER.error("TTS audio generation with %s cancelled.", tts_platform)
        except Exception as error:
            _LOGGER.error("Error generating TTS audio with %s.", tts_platform)
            self._handle_generation_error(error, tts_platform, media_source_id)

        return media_source_id, audio_data

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

        if media_source_id:
            try:
                asyncio.run(tts.async_get_media_source_audio(
                    hass=self.hass, media_source_id=media_source_id
                ))
            except Exception as error:
                _LOGGER.error(
                    "   - Error calling tts.async_get_media_source_audio with media_source_id = '%s': %s",
                    str(media_source_id),
                    str(error),
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
