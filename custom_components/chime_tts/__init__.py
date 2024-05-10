"""The Chime TTS integration."""

import logging
import os
import io
import time
from datetime import datetime

from pydub import AudioSegment

from homeassistant.components.media_player.const import (
    ATTR_MEDIA_CONTENT_ID,
    ATTR_MEDIA_CONTENT_TYPE,
    ATTR_MEDIA_ANNOUNCE,
    ATTR_MEDIA_VOLUME_LEVEL,
    SERVICE_PLAY_MEDIA,
    SERVICE_UNJOIN,
    MEDIA_TYPE_MUSIC,
)

from hass_nabucasa import voice
from .helpers.helpers import ChimeTTSHelper
from .helpers.media_player import MediaPlayerHelper
from .helpers.filesystem import FilesystemHelper
from .queue_manager import ChimeTTSQueueManager
from .config_flow import ChimeTTSOptionsFlowHandler

from homeassistant.const import CONF_ENTITY_ID, SERVICE_VOLUME_SET
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceResponse, SupportsResponse
from homeassistant.helpers import storage
from homeassistant.components import tts
from homeassistant.exceptions import (
    HomeAssistantError,
    ServiceNotFound,
    TemplateError,
)

from .const import (
    DOMAIN,
    SERVICE_CLEAR_CACHE,
    SERVICE_REPLAY,
    SERVICE_SAY,
    SERVICE_SAY_URL,
    VERSION,
    DATA_STORAGE_KEY,
    AUDIO_PATH_KEY,
    LOCAL_PATH_KEY,
    PUBLIC_PATH_KEY,
    PAUSE_RESUME_MEDIA_PLAYER_DICTS_KEY,
    SET_VOLUME_MEDIA_PLAYER_DICTS_KEY,
    AUDIO_DURATION_KEY,
    FADE_TRANSITION_KEY,
    DEFAULT_FADE_TRANSITION_MS,
    ROOT_PATH_KEY,
    DEFAULT_TEMP_CHIMES_PATH_KEY,
    TEMP_CHIMES_PATH_KEY,
    TEMP_CHIMES_PATH_DEFAULT,
    DEFAULT_TEMP_PATH_KEY,
    TEMP_PATH_KEY,
    TEMP_PATH_DEFAULT,
    DEFAULT_WWW_PATH_KEY,
    WWW_PATH_KEY,
    WWW_PATH_DEFAULT,
    MEDIA_DIR_KEY,
    MEDIA_DIR_DEFAULT,
    MP3_PRESET_CUSTOM_PREFIX,
    MP3_PRESET_CUSTOM_KEY,
    QUEUE_TIMEOUT_KEY,
    QUEUE_TIMEOUT_DEFAULT,
    TTS_PLATFORM_KEY,
    OFFSET_KEY,
    AMAZON_POLLY,
    BAIDU,
    ELEVENLABS_TTS,
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

_LOGGER = logging.getLogger(__name__)
_data = {}

helpers = ChimeTTSHelper()
media_player_helper = MediaPlayerHelper()
filesystem_helper = FilesystemHelper()
queue = ChimeTTSQueueManager()


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up an entry."""
    await async_refresh_stored_data(hass)
    update_configuration(config_entry, hass)
    queue.set_timeout(_data.get(QUEUE_TIMEOUT_KEY, QUEUE_TIMEOUT_DEFAULT))

    config_entry.async_on_unload(config_entry.add_update_listener(async_reload_entry))
    return True

async def async_setup(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up the Chime TTS integration."""
    _LOGGER.info("The Chime TTS integration is set up.")

    # Say Service #

    async def async_say(service, is_say_url = False):
        if is_say_url is False:
            if service is None:
                _LOGGER.debug("----- Chime TTS Replay Called. Version %s -----", VERSION)
            else:
                _LOGGER.debug("----- Chime TTS Say Called. Version %s -----", VERSION)

        # Add service calls to the queue with arguments
        result = await queue.add_to_queue(async_say_execute, service, is_say_url)

        if result is not False:
            return result

        # Service call failed
        return {}

    async def async_say_execute(service, is_say_url):
        """Play TTS audio with local chime MP3 audio."""
        start_time = datetime.now()
        parse_result = True

        if service is None:
            # Replay service called: use previous service object
            service = _data.get("service")
            if service is None:
                _LOGGER.warning("No previous service call made to chime_tts.say")
                return
        else:
            _data["service"] = service

        # Parse service parameters & TTS options
        params = await helpers.async_parse_params(hass, service.data, is_say_url)
        if params is not None:
            options = helpers.parse_options_yaml(service.data)
            media_players_array = params.get("media_players_array", None)

            if not (params["message"] or params["chime_path"] or params["end_chime_path"]):
                _LOGGER.error("No chime paths or message provided.")
                parse_result = False
        # Unable to continue
        else:
            parse_result = False

        if not parse_result:
            if is_say_url:
                return {
                    "url": None,
                    ATTR_MEDIA_CONTENT_ID: None,
                    "duration": 0,
                    "success": False
                }
            return False

        return await async_prepare_media(hass, params, options, media_players_array, is_say_url, start_time)

    hass.services.async_register(DOMAIN,
                                 SERVICE_SAY,
                                 async_say)

    # Say URL Service #

    async def async_say_url(service) -> ServiceResponse:
        """Create a public URL to an audio file generated with the `chime_tts.say` service."""
        _LOGGER.debug("----- Chime TTS Say URL Called. Version %s -----", VERSION)
        return await async_say(service, True)

    hass.services.async_register(DOMAIN,
                                 SERVICE_SAY_URL,
                                 async_say_url,
                                 supports_response=SupportsResponse.ONLY)

    # Replay Service #
    async def async_replay(service):
        """Repeat the last service call to chime_tts.say with the same parameters."""
        return await async_say(None, False)

    hass.services.async_register(DOMAIN,
                                 SERVICE_REPLAY,
                                 async_replay)

    # Clear Cache Service #

    async def async_clear_cache(service):
        """Clear TTS cache files."""
        _LOGGER.debug("----- Chime TTS Clear Cache Called -----")
        clear_chimes_cache = bool(service.data.get("clear_chimes_cache", False))
        clear_temp_tts_cache = bool(service.data.get("clear_temp_tts_cache", False))
        clear_www_tts_cache = bool(service.data.get("clear_www_tts_cache", False))
        clear_ha_tts_cache = bool(service.data.get("clear_ha_tts_cache", False))

        start_time = datetime.now()

        to_log = []
        if clear_chimes_cache:
            to_log.append("cached downloaded chimes")
        if clear_temp_tts_cache is True:
            to_log.append("cached temporary Chime TTS audio files")
        if clear_www_tts_cache:
            to_log.append("cached publicly accessible Chime TTS audio files")
        if len(to_log) > 0:
            log_message = "Clearing "
            for i in range(len(to_log)):
                elem = to_log[i]
                if i == len(to_log)-1:
                    log_message += " and "
                elif i > 0:
                    log_message += ", "
                log_message += elem
            log_message += "..."
            _LOGGER.debug("%s", log_message)
        else:
            return


        # CLEAR CHIME TTS CACHE #
        cached_dicts = dict(_data.get(DATA_STORAGE_KEY, None))
        for key in cached_dicts:
            await async_remove_cached_audio_data(hass,
                                                 str(key),
                                                 clear_chimes_cache,
                                                 clear_temp_tts_cache,
                                                 clear_www_tts_cache)

        # CLEAR HA TTS CACHE #
        if clear_ha_tts_cache:
            _LOGGER.debug("Clearing cached Home Assistant TTS audio files...")
            await hass.services.async_call(
                domain="TTS",
                service="clear_cache",
                blocking=True
            )

        # Summary
        elapsed_time = (datetime.now() - start_time).total_seconds() * 1000
        _LOGGER.debug(
            "----- Chime TTS Clear Cache Completed in %s ms -----", str(elapsed_time)
        )

        return True

    hass.services.async_register(DOMAIN,
                                 SERVICE_CLEAR_CACHE,
                                 async_clear_cache)

    return True

async def async_prepare_media(hass: HomeAssistant, params, options, media_players_array, is_say_url, start_time):
    """Prepare and play media."""
    # Create audio file to play on media player
    local_path = None
    public_path = None
    media_content_id = None
    audio_duration = 0
    audio_dict = await async_get_playback_audio_path(params, options)
    if audio_dict is not None:
        local_path = audio_dict.get(LOCAL_PATH_KEY, None)
        public_path = audio_dict.get(PUBLIC_PATH_KEY, None)
        media_content_id = audio_dict.get(ATTR_MEDIA_CONTENT_ID, None)
        audio_duration = audio_dict.get(AUDIO_DURATION_KEY, 0)

        if is_say_url is False:

            # Play audio with service_data
            play_result = await async_play_media(
                hass,
                audio_dict,
                params["entity_ids"],
                params["announce"],
                params["fade_audio"],
                params["join_players"],
                media_players_array,
            )
            if play_result is True:
                await async_post_playback_actions(
                    hass,
                    audio_duration,
                    params["final_delay"],
                    media_players_array,
                    params["unjoin_players"],
                )

            # Remove temporary local generated mp3
            if not params.get("cache", False) and local_path is not None:
                filesystem_helper.delete_file(local_path)

    end_time = datetime.now()
    completion_time = round((end_time - start_time).total_seconds(), 2)
    elapsed_time = (f"{completion_time} s"
                                if completion_time >= 1
                                else f"{completion_time * 1000} ms")

    # Convert public file path to external URL for chime_tts.say_url
    if is_say_url:
        _LOGGER.debug("Final URL = %s", public_path)
        _LOGGER.debug("----- Chime TTS Say URL Completed in %s -----", str(elapsed_time))
        ret_value = {
            "url": public_path,
            ATTR_MEDIA_CONTENT_ID: media_content_id,
            "duration": audio_duration,
            "success": (public_path is not None or media_content_id is not None)
        }
        if ret_value["success"] is False:
            _LOGGER.warning("Check that the folder path in the configuration for `chime_tts.say_url` is within the public \"www\" folder or the local media folder")

        return ret_value

    _LOGGER.debug("----- Chime TTS Say Completed in %s -----", str(elapsed_time))

async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    return True

async def async_reload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Reload the Chime TTS config entry."""
    _LOGGER.debug("Reloading integration")
    await async_unload_entry(hass, config_entry)
    await async_setup_entry(hass, config_entry)
    await async_setup(hass, config_entry)

# Integration options #

async def async_options(self, entry: ConfigEntry):
    """Present current configuration options for modification."""
    # Create an options flow handler and return it
    return ChimeTTSOptionsFlowHandler(entry)

async def async_options_updated(self, entry: ConfigEntry):
    """Handle updated configuration options and update the entry."""
    # Update the queue timeout value
    update_configuration(entry, None)

def update_configuration(config_entry: ConfigEntry, hass: HomeAssistant = None):
    """Update configurable values."""

    # Prepare default paths
    if hass is not None:
        _data[ROOT_PATH_KEY] = hass.config.path("").replace("/config/", "")

    if DEFAULT_TEMP_PATH_KEY not in _data:
        _data[DEFAULT_TEMP_PATH_KEY] = f"{_data[ROOT_PATH_KEY]}{TEMP_PATH_DEFAULT}"

    if DEFAULT_TEMP_CHIMES_PATH_KEY not in _data:
        _data[DEFAULT_TEMP_CHIMES_PATH_KEY] = f"{_data[ROOT_PATH_KEY]}{TEMP_CHIMES_PATH_DEFAULT}"

    if DEFAULT_WWW_PATH_KEY not in _data:
        _data[DEFAULT_WWW_PATH_KEY] = f"{_data[ROOT_PATH_KEY]}{WWW_PATH_DEFAULT}"

    # Set configurable values
    options = config_entry.options

    # Queue timeout
    _data[QUEUE_TIMEOUT_KEY] = options.get(QUEUE_TIMEOUT_KEY, QUEUE_TIMEOUT_DEFAULT)

    # Default TTS Platform
    _data[TTS_PLATFORM_KEY] = options.get(TTS_PLATFORM_KEY, "")

    # Default offset
    _data[OFFSET_KEY] = options.get(OFFSET_KEY, 0)

    # Default audio fade transition duration
    _data[FADE_TRANSITION_KEY] = options.get(FADE_TRANSITION_KEY, DEFAULT_FADE_TRANSITION_MS)

    # Media folder (default local)
    _data[MEDIA_DIR_KEY] = options.get(MEDIA_DIR_KEY, MEDIA_DIR_DEFAULT)

    # www / local folder path
    _data[WWW_PATH_KEY] = hass.config.path(
        options.get(WWW_PATH_KEY, _data.get(DEFAULT_WWW_PATH_KEY, WWW_PATH_DEFAULT))
    )
    _data[WWW_PATH_KEY] = (_data.get(WWW_PATH_KEY, "") + "/").replace("//", "/")

    # Temp chimes folder path
    _data[TEMP_CHIMES_PATH_KEY] = hass.config.path(
        options.get(TEMP_CHIMES_PATH_KEY, _data.get(DEFAULT_TEMP_CHIMES_PATH_KEY, None))
    )
    _data[TEMP_CHIMES_PATH_KEY] = (_data.get(TEMP_CHIMES_PATH_KEY, "") + "/").replace("//", "/")

    # Temp folder path
    _data[TEMP_PATH_KEY] = hass.config.path(
        options.get(TEMP_PATH_KEY, _data.get(DEFAULT_TEMP_PATH_KEY, None))
    )
    _data[TEMP_PATH_KEY] = (_data.get(TEMP_PATH_KEY, "") + "/").replace("//", "/")

    # Custom chime paths
    _data[MP3_PRESET_CUSTOM_KEY] = {}
    for i in range(5):
        key = MP3_PRESET_CUSTOM_PREFIX + str(i + 1)
        value = options.get(key, "")
        _data[MP3_PRESET_CUSTOM_KEY][key] = value

    # Debug summary
    _LOGGER.debug("Chime TTS Configuration Values:")
    for key_string in [
        QUEUE_TIMEOUT_KEY,
        TTS_PLATFORM_KEY,
        OFFSET_KEY,
        FADE_TRANSITION_KEY,
        TEMP_CHIMES_PATH_KEY,
        TEMP_PATH_KEY,
        WWW_PATH_KEY,
        MEDIA_DIR_KEY,
        MP3_PRESET_CUSTOM_KEY,
    ]:
        value = _data.get(key_string, None)
        if value and isinstance(value, dict):
            _LOGGER.debug(" - %s:", key_string.replace("_key", ""))
            for dict_key, dict_value in value.items():
                quote = ("'" if (
                    isinstance(dict_value, str)
                    and dict_value is not None
                    and dict_value != ""
                    and dict_value != "None"
                    ) else "")
                _LOGGER.debug("   - %s: %s%s%s", dict_key.replace("_key", ""), quote, str(value.get(dict_key, "None")), quote)
        else:
            quote = "'" if isinstance(value, str) and value is not None and value != 'None' else ""
            _LOGGER.debug(" - %s: %s%s%s", key_string.replace("_key", ""), quote, str(value), quote)

####################################
### Retrieve TTS Audio Functions ###
####################################

async def async_request_tts_audio(
    hass: HomeAssistant,
    tts_platform: str,
    message: str,
    language: str,
    cache: bool,
    options: dict,
):
    """Send an API request for TTS audio and return the audio file's local filepath."""

    start_time = datetime.now()

    # Data validation

    tts_options = options.copy() if isinstance(options, dict) else (str(options) if isinstance(options, str) else options)

    if message is False or message == "":
        _LOGGER.warning("No message text provided for TTS audio")
        return None

    # Determine TTS Platform
    if tts_platform is None or tts_platform == "None" or tts_platform is False or len(tts_platform) <= 1:
        tts_platform = helpers.get_default_tts_platform(hass, _data[TTS_PLATFORM_KEY])

    if tts_platform == NABU_CASA_CLOUD_TTS_OLD:
        tts_platform = NABU_CASA_CLOUD_TTS

    # Add & validate additional parameters

    # Language
    if language is not None and tts_platform in [
        GOOGLE_TRANSLATE,
        NABU_CASA_CLOUD_TTS,
        IBM_WATSON_TTS,
        MICROSOFT_EDGE_TTS,
    ]:
        if tts_platform is IBM_WATSON_TTS and tts_options.get("voice") is None:
            tts_options["voice"] = language
            language = None
    else:
        language = None

    # Assign `language` for Nabu Casa if missing, when `voice` provided
    p_voice = tts_options.get("voice", None)
    if (tts_platform == NABU_CASA_CLOUD_TTS
        and p_voice
        and (language is None or len(language) == 0)):
        for key, value in voice.TTS_VOICES.items():
            if p_voice in value:
                language = key
                _LOGGER.debug(" - languge set to '%s' for voice: '%s'.", language, p_voice)

    # Cache
    use_cache = bool(cache) and tts_platform not in [GOOGLE_TRANSLATE, NABU_CASA_CLOUD_TTS]

    # tld
    if "tld" in tts_options and tts_platform not in [GOOGLE_TRANSLATE]:
        del tts_options["tld"]

    # Debug log
    _LOGGER.debug(" - Generating new TTS audio with parameters:")
    for key, value in {
        "tts_platform":  f"'{tts_platform}'",
        "message":  f"'{message}'",
        "cache":  str(use_cache),
        "language":  '\"'+str(language)+'\"' if language is not None else 'None',
        "options":  str(tts_options)

    }.items():
        _LOGGER.debug("    * %s = %s", key, value)

    media_source_id = None
    try:
        media_source_id = tts.media_source.generate_media_source_id(
            hass=hass,
            message=message,
            engine=tts_platform,
            language=language,
            cache=cache,
            options=tts_options,
        )
    except Exception as error:
        if f"{error}" == "Invalid TTS provider selected":
            missing_tts_platform_error(tts_platform)
        else:
            _LOGGER.error(
                "   - Error calling tts.media_source.generate_media_source_id: %s",
                error,
            )
        return None
    if media_source_id is None:
        _LOGGER.error("Error: Unable to generate media_source_id")
        return None

    audio_data = None
    try:
        audio_data = await tts.async_get_media_source_audio(
            hass=hass, media_source_id=media_source_id
        )
    except Exception as error:
        _LOGGER.error(
            "   - Error calling tts.async_get_media_source_audio: %s", error
        )
        return None

    if audio_data is not None:
        if len(audio_data) == 2:
            audio_bytes = audio_data[1]
            file = io.BytesIO(audio_bytes)
            if file is None:
                _LOGGER.error("...could not convert TTS bytes to audio")
                return None
            audio = AudioSegment.from_file(file)
            if audio is not None:

                # Done
                end_time = datetime.now()
                completion_time = round((end_time - start_time).total_seconds(), 2)
                completion_time_string = (f"{completion_time}s"
                                          if completion_time >= 1
                                          else f"{completion_time * 1000}ms")
                _LOGGER.debug("   ...TTS audio generated in %s", completion_time_string)
                return audio
            _LOGGER.error("...could not extract TTS audio from file")
        else:
            _LOGGER.error("...audio_data did not contain audio bytes")
    else:
        _LOGGER.error("...audio_data generation failed")
    return None


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
    if tts_platform is ELEVENLABS_TTS:
        tts_platform_name = "ElevenLabs TTS"
        tts_platform_documentation = "https://github.com/carleeno/elevenlabs_tts"
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


##############################
### Audio Helper Functions ###
##############################


async def async_get_playback_audio_path(params: dict, options: dict):
    """Create audio to play on media player entity."""
    output_audio = None

    hass: HomeAssistant = params.get("hass", None)
    chime_path = params.get("chime_path", None)
    end_chime_path = params.get("end_chime_path", None)
    offset = params.get("offset", _data[OFFSET_KEY])
    message = params.get("message", None)
    cache = params.get("cache", False)
    entity_ids = params.get("entity_ids", [])
    ffmpeg_args = params.get("ffmpeg_args", "")

    # Produce local and/or public mp3s?
    alexa_media_player_count = media_player_helper.get_alexa_media_player_count(hass, entity_ids)

    is_public = alexa_media_player_count > 0 or (entity_ids is None or len(entity_ids) == 0)
    is_local = entity_ids is not None and len(entity_ids) > 0 and alexa_media_player_count != len(entity_ids)

    filepath_hash = get_filename_hash_from_service_data({**params}, {**options})
    _data["generated_filename"] = filepath_hash

    # Load previously generated audio from cache
    if cache is True:
        _LOGGER.debug(" *** Checking Chime TTS audio cache ***")
        audio_dict = await async_get_cached_audio_data(hass, filepath_hash)
        if audio_dict is not None and AUDIO_DURATION_KEY in audio_dict:
            duration = audio_dict.get(AUDIO_DURATION_KEY, None)

            # Make a local copy of the public file
            if is_local and audio_dict.get(LOCAL_PATH_KEY, None) is None and audio_dict.get(PUBLIC_PATH_KEY, None):
                _LOGGER.debug("   - Copying public file to local directory")
                audio_dict[LOCAL_PATH_KEY] = filesystem_helper.copy_file(audio_dict.get(PUBLIC_PATH_KEY, None), _data.get(TEMP_PATH_KEY, None))
                await async_add_audio_file_to_cache(hass, audio_dict.get(LOCAL_PATH_KEY, None), duration, params, options)

            # Make a public copy of the local file
            if is_public and audio_dict.get(PUBLIC_PATH_KEY, None) is None and audio_dict.get(LOCAL_PATH_KEY, None):
                _LOGGER.debug("    - Copying local file to public directory")
                audio_dict[PUBLIC_PATH_KEY] = filesystem_helper.copy_file(audio_dict.get(LOCAL_PATH_KEY, None), _data.get(WWW_PATH_KEY, None))
                await async_add_audio_file_to_cache(hass, audio_dict.get(PUBLIC_PATH_KEY, None), duration, params, options)

            audio_dict[PUBLIC_PATH_KEY] = filesystem_helper.get_external_url(hass, audio_dict.get(PUBLIC_PATH_KEY, None))
            audio_dict[ATTR_MEDIA_CONTENT_ID] = media_player_helper.get_media_content_id(audio_dict.get(LOCAL_PATH_KEY, None) or
                                                                                         audio_dict.get(PUBLIC_PATH_KEY, None),
                                                                                         _data.get(MEDIA_DIR_KEY, None))

            if (is_local is False or audio_dict.get(LOCAL_PATH_KEY, None)) and (is_public is False or audio_dict.get(PUBLIC_PATH_KEY, None)):
                _LOGGER.debug("   Cached audio found:")
                for key, value in audio_dict.items():
                    quote = '"' if value and isinstance(value, str) else ''
                    value = f"{quote}{value}{quote}"
                    _LOGGER.debug("     - %s = %s", key, value)

                # Apply audio conversion
                if ffmpeg_args is not None and len(ffmpeg_args) > 0:
                    _LOGGER.debug("   Apply audio conversion")
                    if audio_dict.get(LOCAL_PATH_KEY, None):
                        helpers.ffmpeg_convert_from_file(audio_dict.get(LOCAL_PATH_KEY, None), ffmpeg_args)
                    if audio_dict.get(PUBLIC_PATH_KEY, None):
                        # Convert public path to local path
                        local_public_file_path = filesystem_helper.get_local_path(hass, audio_dict.get(PUBLIC_PATH_KEY, None))
                        helpers.ffmpeg_convert_from_file(local_public_file_path, ffmpeg_args)

                return audio_dict
        _LOGGER.debug("   ...no cached audio found")

    ######################
    # Generate new audio #
    ######################

    # Load chime audio
    output_audio = await async_get_audio_from_path(hass=hass,
                                                   filepath=chime_path,
                                                   cache=cache)

    # Process message tags
    output_audio = await async_process_segments(hass,
                                                message,
                                                output_audio,
                                                params,
                                                options)

    # Load end chime audio
    output_audio = await async_get_audio_from_path(hass=hass,
                                                   filepath=end_chime_path,
                                                   cache=cache,
                                                   offset=offset,
                                                   audio=output_audio)

    # Save generated audio file
    audio_dict = {
        AUDIO_DURATION_KEY: 0,
        LOCAL_PATH_KEY: None,
        PUBLIC_PATH_KEY: None
    }
    if output_audio is not None:
        initial_save_folder_key = TEMP_PATH_KEY if is_local else WWW_PATH_KEY
        _LOGGER.debug(" - Saving mp3 file to folder: %s...", _data.get(initial_save_folder_key, ""))
        new_audio_file = filesystem_helper.save_audio_to_folder(output_audio, _data.get(initial_save_folder_key, None))
        if new_audio_file is None:
            _LOGGER.debug("   ...error saving file")
            return None

        # Perform FFmpeg conversion
        if ffmpeg_args:
            _LOGGER.debug("  - Performing FFmpeg audio conversion...")
            converted_audio_file = helpers.ffmpeg_convert_from_file(new_audio_file,
                                                                    ffmpeg_args)
            if converted_audio_file is not False:
                _LOGGER.debug("    ...FFmpeg audio conversion completed.")
                new_audio_file = converted_audio_file
            else:
                _LOGGER.warning("...FFmpeg audio conversion failed. Continuing using the original audio file")

        duration = len(AudioSegment.from_file(new_audio_file)) / 1000.0
        audio_dict[AUDIO_DURATION_KEY] = duration
        audio_dict[LOCAL_PATH_KEY if is_local else PUBLIC_PATH_KEY] = new_audio_file
        audio_dict[ATTR_MEDIA_CONTENT_ID] = media_player_helper.get_media_content_id(audio_dict.get(LOCAL_PATH_KEY, None)
                                                                                     or audio_dict.get(PUBLIC_PATH_KEY, None),
                                                                                     _data.get(MEDIA_DIR_KEY, None))

        # Save audio to local and/or public folders
        for folder_key in [(LOCAL_PATH_KEY if is_local else None), (PUBLIC_PATH_KEY if is_public else None)]:
            if folder_key is not None and audio_dict.get(folder_key, None) is None:
                _LOGGER.debug(" - Saving generated audio to folder %s ...", _data.get(folder_key, ""))
                audio_dict[folder_key] = filesystem_helper.save_audio_to_folder(output_audio, _data.get(folder_key, None))
                if audio_dict[folder_key] is None:
                    _LOGGER.error("Error saving audio to folder %s...", _data.get(LOCAL_PATH_KEY, ""))
            # Save path to cache
            if (cache or folder_key == PUBLIC_PATH_KEY) and audio_dict.get(folder_key, None):
                await async_add_audio_file_to_cache(hass, audio_dict.get(folder_key, None), duration, params, options)

        # Convert external URL (for public paths)
        audio_dict[PUBLIC_PATH_KEY] = filesystem_helper.get_external_url(hass, audio_dict.get(PUBLIC_PATH_KEY, None))

    # Valdiation
    is_valid = True
    if audio_dict[AUDIO_DURATION_KEY] == 0:
        _LOGGER.error("async_get_playback_audio_path --> Audio has no duration")
        is_valid = False
    if is_local and audio_dict.get(LOCAL_PATH_KEY, None) is None:
        _LOGGER.error("async_get_playback_audio_path --> Unable to generate local audio file")
        is_valid = False
    if is_public and not(audio_dict.get(PUBLIC_PATH_KEY, None) or audio_dict.get(ATTR_MEDIA_CONTENT_ID, None)):
        _LOGGER.error("async_get_playback_audio_path --> Unable to generate public audio file")
        is_valid = False
    if is_valid is False:
        return None

    _LOGGER.debug(" - Chime TTS audio generated:")
    for key, value in audio_dict.items():
        quote = '"' if isinstance(value, str) else ''
        value = f"{quote}{value}{quote}"
        _LOGGER.debug("   * %s = %s", key, value)
    return audio_dict


def get_segment_offset(output_audio, segment, params):
    """Offset value for segment."""
    segment_offset: float = 0
    if output_audio is not None:
        # Get "offset" parameter
        if "offset" in segment:
            segment_offset = float(segment["offset"])

        # Support deprecated "delay" parmeter
        else:
            if "delay" in segment:
                segment_offset = float(segment["delay"])
            elif "delay" in params:
                segment_offset = float(params["delay"])
            elif "offset" in params:
                segment_offset = float(params["offset"])

    return segment_offset


async def async_process_segments(hass, message, output_audio, params, options):
    """Process all message segments and add the audio."""
    segments = helpers.parse_message(message)
    if segments is None or len(segments) == 0:
        return output_audio

    for index, segment in enumerate(segments):
        segment_cache: bool = segment.get("cache", params.get("cache", False))
        segment_audio_conversion: str = segment.get("audio_conversion", "")
        segment_offset: float = get_segment_offset(output_audio, segment, params)
        segment_type =  segment.get("type", None)
        if not segment_type:
            _LOGGER.warning("Segment #%s has no type.", str(index+1))
            return output_audio

        # Chime tag
        if segment_type == "chime":
            if len(segment.get("path", "")) > 0:
                output_audio = await async_get_audio_from_path(hass=hass,
                                                               filepath=segment["path"],
                                                               cache=segment_cache,
                                                               offset=segment_offset,
                                                               audio_conversion=segment_audio_conversion,
                                                               audio=output_audio)
            else:
                _LOGGER.warning("Chime path missing from messsage segment #%s", str(index+1))
                continue

        # Delay tag
        if segment_type == "delay":
            if segment.get("length", None):
                segment_delay_length = float(segment["length"])
                delay_audio = AudioSegment.silent(duration=segment_delay_length)
                if output_audio:
                    output_audio = output_audio + delay_audio
                else:
                    output_audio = delay_audio
            else:
                _LOGGER.warning("Delay length missing from messsage segment #%s", str(index+1))
                continue

        # Request TTS audio file
        if segment_type == "tts":
            if len(segment.get("message", "")) > 0:
                segment_message = segment["message"]
                segment_tts_platform = segment.get("tts_platform", params.get("tts_platform", None))
                segment_language = segment.get("language", params.get("language", None))
                segment_tts_speed = float(segment.get("tts_speed", params.get("tts_speed", 100)))
                segment_tts_pitch = float(segment.get("tts_pitch", params.get("tts_pitch", 0)))

                # Use exposed parameters if not present in the options dictionary
                segment_options = segment.get("options", {})
                exposed_option_keys = ["tld", "voice"]
                for exposed_option_key in exposed_option_keys:
                    value = (segment_options.get(exposed_option_key, None) or
                             segment.get(exposed_option_key, None))
                    if value is not None:
                        segment_options[exposed_option_key] = value

                for key, value in options.items():
                    if key not in segment_options:
                        segment_options[key] = value
                segment_params = {
                    "message": segment_message,
                    "tts_platform": segment_tts_platform,
                    "language": segment_language,
                    "cache": segment_cache,
                    "tts_speed": segment_tts_speed,
                    "tts_pitch": segment_tts_pitch
                }
                segment_filepath_hash = get_filename_hash_from_service_data({**segment_params}, {**segment_options})

                tts_audio = None

                # Use cached TTS audio
                if segment_cache is True:
                    _LOGGER.debug(" - Attempting to retrieve TTS audio from cache...")
                    audio_dict = await async_get_cached_audio_data(hass, segment_filepath_hash)
                    if audio_dict is not None:
                        tts_audio = await async_get_audio_from_path(hass=hass,
                                                                    filepath=audio_dict.get(LOCAL_PATH_KEY, None),
                                                                    cache=segment_cache,
                                                                    audio=None)

                        tts_audio_duration = audio_dict.get(AUDIO_DURATION_KEY, None)
                    else:
                        _LOGGER.debug("   ...no cached TTS audio found")


                # Generate new TTS audio
                if tts_audio is None:
                    tts_audio = await async_request_tts_audio(
                        hass=hass,
                        tts_platform=segment_tts_platform,
                        message=segment_message,
                        language=segment_language,
                        cache=segment_cache,
                        options=segment_options
                    )

                    # Cache the new TTS audio?
                    if tts_audio is not None:
                        tts_audio_duration = float(len(tts_audio) / 1000.0)
                        if segment_cache is True and audio_dict is None:
                            _LOGGER.debug(" - Saving generated TTS audio to cache...")
                            tts_audio_full_path = filesystem_helper.save_audio_to_folder(
                                tts_audio, _data.get(TEMP_PATH_KEY, None))
                            if tts_audio_full_path is not None:
                                audio_dict = {
                                    LOCAL_PATH_KEY: tts_audio_full_path,
                                    AUDIO_DURATION_KEY: tts_audio_duration
                                }
                                await async_store_data(hass, segment_filepath_hash, audio_dict)
                                _LOGGER.debug("  ...TTS audio saved to cache")
                            else:
                                _LOGGER.warning("Unable to save generated TTS audio to cache")

                # TTS Audio manipulations
                if tts_audio is not None:
                    temp_folder =  _data.get(TEMP_PATH_KEY, None)
                    tts_audio = helpers.change_speed_of_audiosegment(tts_audio, segment_tts_speed, temp_folder)
                    tts_audio = helpers.change_pitch_of_audiosegment(tts_audio, segment_tts_pitch, temp_folder)
                    tts_audio = helpers.ffmpeg_convert_from_audio_segment(tts_audio, segment_audio_conversion, temp_folder)

                # Combine audio
                if tts_audio is not None:
                    output_audio = helpers.combine_audio(output_audio, tts_audio, segment_offset)
                else:
                    _LOGGER.warning("Error generating TTS audio from messsage segment #%s: %s",
                                    str(index+1), str(segment))
            else:
                _LOGGER.warning("TTS 'message' value missing from messsage segment #%s: %s",
                                str(index+1), str(segment))

    return output_audio

async def async_get_audio_from_path(hass: HomeAssistant,
                                    filepath: str,
                                    cache: bool = False,
                                    offset: float = 0,
                                    audio_conversion: str = "",
                                    audio: AudioSegment = None):
    """Add audio from a given file path to existing audio (optional) with offset (optional)."""
    if filepath is None or filepath == "None" or len(filepath) == 0:
        return audio

    # Load/download audio file & validate local path
    filepath = await filesystem_helper.async_get_chime_path(
        chime_path=filepath,
        cache=cache,
        data=_data,
        hass=hass)

    if filepath is not None:

        # Chime downloaded from URL
        file_hash = None
        if isinstance(filepath, dict):
            audio_dict = filepath["audio_dict"]
            file_hash = filepath["file_hash"]
            filepath = audio_dict.get(LOCAL_PATH_KEY, None)
            if cache:
                _LOGGER.debug(" - Saving reference to downloaded chime")
                await async_add_audio_file_to_cache(hass=hass,
                                                    audio_path=filepath,
                                                    duration=audio_dict.get(AUDIO_DURATION_KEY, None),
                                                    params=None,
                                                    options=None,
                                                    file_hash=file_hash)

        _LOGGER.debug(' - Retrieving audio from path: "%s"...', filepath)
        try:
            audio_from_path: AudioSegment = AudioSegment.from_file(filepath)
            if audio_conversion is not None and len(audio_conversion) > 0:
                _LOGGER.debug("  - Performing FFmpeg audio conversion of audio file...")
                audio_from_path = helpers.ffmpeg_convert_from_audio_segment(audio_from_path)

            # Remove downloaded file when cache=false
            if cache is False and file_hash is not None:
                filesystem_helper.delete_file(filepath)

            if audio_from_path is not None:
                duration = float(len(audio_from_path) / 1000.0)
                _LOGGER.debug(
                    "   ...audio retrieved. Duration: %ss",
                    str(duration),
                )
                if audio is None:
                    return audio_from_path

                # Apply offset
                return helpers.combine_audio(audio, audio_from_path, offset)
            _LOGGER.warning("Unable to find audio at filepath: %s", filepath)
        except Exception as error:
            _LOGGER.warning('Unable to extract audio from file: "%s"', error)

    _LOGGER.warning("Unable to generate local audio filepath")
    return audio

##################

async def async_play_media(
    hass: HomeAssistant,
    audio_dict,
    entity_ids,
    announce,
    fade_audio,
    join_players,
    media_players_array,
):
    """Call the media_player.play_media service."""
    _LOGGER.debug(" *** Pre-Playback Actions *** ")

    service_data = {}

    # media content type
    service_data[ATTR_MEDIA_CONTENT_TYPE] = MEDIA_TYPE_MUSIC

    # media_content_id
    media_content_id = media_player_helper.get_media_content_id(audio_dict.get(LOCAL_PATH_KEY, None) or
                                                                audio_dict.get(PUBLIC_PATH_KEY, None),
                                                                _data.get(MEDIA_DIR_KEY))
    service_data[ATTR_MEDIA_CONTENT_ID] = media_content_id

    # announce
    if announce is True:
        service_data[ATTR_MEDIA_ANNOUNCE] = announce

    # entity_id
    service_data[CONF_ENTITY_ID] = entity_ids

    # Fade out and pause media_players manually if their platforms do not support the `announce` feature
    _data[PAUSE_RESUME_MEDIA_PLAYER_DICTS_KEY] = []
    _data[SET_VOLUME_MEDIA_PLAYER_DICTS_KEY] = []
    for media_player_dict in media_players_array:
        entity_id = media_player_dict["entity_id"]
        # Announce on unsupported media_player platform
        if (media_player_dict["is_playing"] and (fade_audio or (announce and not media_player_dict["announce_supported"])) ):
            media_player_dict["fade_out_volume"] = 0
            _data[PAUSE_RESUME_MEDIA_PLAYER_DICTS_KEY].append(media_player_dict)
        # Volume should be changed
        elif (media_player_dict["should_change_volume"]
              and not media_player_helper.get_is_media_player_spotify(hass, entity_id)):
            _data[SET_VOLUME_MEDIA_PLAYER_DICTS_KEY].append(media_player_dict)

    # FADE OUT & PAUSE

    if len(_data[PAUSE_RESUME_MEDIA_PLAYER_DICTS_KEY]) > 0:

        # Fade out media players manually if platform does not support `announce`
        _LOGGER.debug(" - Fading out media_players currently playing")
        await media_player_helper.async_set_volume_for_media_players(hass=hass,
                                                                     media_player_dicts=_data[PAUSE_RESUME_MEDIA_PLAYER_DICTS_KEY],
                                                                     volume_key="fade_out_volume",
                                                                     fade_duration=_data[FADE_TRANSITION_KEY])

        # Pause playing media_players
        pause_entity_ids = []
        for media_player_dict in _data[PAUSE_RESUME_MEDIA_PLAYER_DICTS_KEY]:
            pause_entity_ids.append(media_player_dict["entity_id"])
        _LOGGER.debug(" - Pausing %s media_player", str(len(pause_entity_ids)))
        try:
            await hass.services.async_call(
                domain="media_player",
                service="media_pause",
                service_data={CONF_ENTITY_ID: pause_entity_ids},
                blocking=True
            )
        except Exception as error:
            _LOGGER.warning("Unable to pause media player%s: %s", ("" if len(pause_entity_ids) == 1 else "s"), str(error))

        # Wait until media_players are actually paused
        await media_player_helper.async_wait_until_media_players_state_is(hass=hass,
                                                                          media_player_dicts=_data[PAUSE_RESUME_MEDIA_PLAYER_DICTS_KEY],
                                                                          target_state="paused",
                                                                          timeout=1.5)

    # Set media_players' volume_level
    await media_player_helper.async_set_volume_for_media_players(hass=hass,
                                                                 media_player_dicts=_data[SET_VOLUME_MEDIA_PLAYER_DICTS_KEY],
                                                                 volume_key="playback_volume_level",
                                                                 fade_duration=0)

    # Join media player entity_ids as a group
    _data["join_media_player_entity_id"] = None
    _data["joined_media_players_entity_ids"] = None
    if join_players is True:
        join_supported_entity_ids = media_player_helper.get_join_suppored_entity_ids(media_players_array)
        if len(join_supported_entity_ids) > 1:
            _data["join_media_player_entity_id"] = await media_player_helper.async_join_media_players(hass, entity_ids)
            _data["joined_media_players_entity_ids"] = join_supported_entity_ids
            if _data["join_media_player_entity_id"] is not False:
                service_data[CONF_ENTITY_ID] = [_data["join_media_player_entity_id"]]
                volume_level = media_players_array[0]["playback_volume_level"]
                # Replace media_player array elements with the new joined media_player dictionary
                joint_media_player_dict = await media_player_helper.async_get_media_player_dict(hass,
                                                                                                _data["join_media_player_entity_id"],
                                                                                                volume_level)
                _data[SET_VOLUME_MEDIA_PLAYER_DICTS_KEY] = [joint_media_player_dict]
            else:
                _LOGGER.warning("Unable to join speakers. Only 1 media_player supported.")
        elif len(join_supported_entity_ids) == 1:
            _LOGGER.warning("Unable to join speakers. Only 1 media_player supported.")
        else:
            _LOGGER.warning("Unable to join speakers. %s supported media_player%s found (minimum is 2).",
                            str(len(join_supported_entity_ids)), ("" if join_supported_entity_ids == 1 else "s"))

    # Play Chime TTS notification
    media_service_calls = prepare_media_service_calls(hass, entity_ids, service_data, audio_dict, media_players_array)
    play_result = await async_fire_media_service_calls(hass, media_service_calls)
    if play_result is False:
        _LOGGER.error("Playback failed")

    return play_result

def prepare_media_service_calls(hass: HomeAssistant, entity_ids, service_data, audio_dict, media_players_array):
    """Prepare the media_player service calls for audio playback."""
    _LOGGER.debug(" *** Chime TTS playback ***")
    standard_media_player_entity_ids = [entity_id for entity_id in entity_ids if media_player_helper.get_is_standard_media_player(hass, entity_id)]
    alexa_media_player_entity_ids = [entity_id for entity_id in entity_ids if media_player_helper.get_is_media_player_alexa(hass, entity_id)]
    sonos_media_player_entity_ids = [entity_id for entity_id in entity_ids if media_player_helper.get_is_media_player_sonos(hass, entity_id)]

    # Remove any joined media_players from the media_player lists
    if _data.get("joined_media_players_entity_ids", None):
        _LOGGER.debug("Removing joined entity_ids: %s", str(_data["joined_media_players_entity_ids"]))
        for joined_media_player_entity_id in _data["joined_media_players_entity_ids"]:
            for media_player_array in [standard_media_player_entity_ids, alexa_media_player_entity_ids, sonos_media_player_entity_ids]:
                if joined_media_player_entity_id in media_player_array:
                    index = media_player_array.index(joined_media_player_entity_id)
                    if index != -1:
                        del media_player_array[index]
        # Add the joined media player entity_id to the list of standard media players
        standard_media_player_entity_ids.append(_data["join_media_player_entity_id"])

    service_calls = []

    # Prepare service call for regular media_players
    if len(standard_media_player_entity_ids) > 0:
        if service_data[ATTR_MEDIA_CONTENT_ID] is None:
            _LOGGER.warning("Error calling `media_player.play_media` service: No media content id found")
        else:
            _LOGGER.debug("   %s Standard media player%s detected:",
                          len(standard_media_player_entity_ids),
                          ("s" if len(standard_media_player_entity_ids) != 1 else ""))
            for entity_id in standard_media_player_entity_ids:
                _LOGGER.debug("     - %s", entity_id)
            service_data[CONF_ENTITY_ID] = standard_media_player_entity_ids
            service_calls.append({
                "domain": "media_player",
                "service": SERVICE_PLAY_MEDIA,
                "service_data": service_data,
                "blocking": True,
                "result": True
            })

    # Prepare service call for Alexa media_players
    if len(alexa_media_player_entity_ids) > 0:
        _LOGGER.debug("   %s Alexa media player%s detected:",
                      len(alexa_media_player_entity_ids),
                      ("s" if len(alexa_media_player_entity_ids) != 1 else ""))
        for entity_id in alexa_media_player_entity_ids:
            _LOGGER.debug("     - %s", entity_id)
        if len(audio_dict.get(PUBLIC_PATH_KEY, '')) > 0:
            message_string = f"<audio src=\"{audio_dict.get(PUBLIC_PATH_KEY, '')}\"/>"
            service_calls.append({
                "domain": "notify",
                "service": "alexa_media",
                "service_data": {
                    "message": message_string,
                    "data": {"type": "tts"},
                    "target": alexa_media_player_entity_ids
                },
                "result": False
            })
        else:
            _LOGGER.warning("Unable to play audio on Alexa device. No public URL found.")

    # Prepare service call for Sonos media_players
    if len(sonos_media_player_entity_ids) > 0:
        if service_data[ATTR_MEDIA_CONTENT_ID] is None:
            _LOGGER.warning("Error calling `media_player.play_media` service: No media content id found")
        else:
            _LOGGER.debug("   %s Sonos media player%s detected:",
                          len(sonos_media_player_entity_ids),
                          ("s" if len(sonos_media_player_entity_ids) != 1 else ""))
            # Determine whether each Sonos should play at the same, or media_player-specific volume
            def find_media_player_dict(p_entity_id: str):
                """Find the media_player dictionary matching the given entity_id."""
                for media_player_dict in media_players_array:
                    if media_player_dict["entity_id"] == p_entity_id:
                        return media_player_dict
                return None

            is_uniform_level = True
            last_volume = -1
            volume_map = {}
            for entity_id in sonos_media_player_entity_ids:
                _LOGGER.debug("     - %s", entity_id)
                if is_uniform_level:
                    sonos_media_player_dict = find_media_player_dict(entity_id)
                    _LOGGER.debug("sonos_media_player_dict = %s", str(sonos_media_player_dict))
                    p_volume = sonos_media_player_dict["playback_volume_level"]
                    volume_map[entity_id] = p_volume
                    if last_volume != p_volume and p_volume != -1:
                        is_uniform_level = False
                        break
            # Add a single service call for all Sonos media_players
            if is_uniform_level:
                service_data[CONF_ENTITY_ID] = sonos_media_player_entity_ids
                if last_volume != -1:
                    service_data["extra"] = {
                        "volume": last_volume
                    }
                service_calls.append({
                    "domain": "media_player",
                    "service": SERVICE_PLAY_MEDIA,
                    "service_data": service_data,
                    "blocking": True,
                    "result": True
                })
            # Add 1 service call for each Sonos media_player
            for key, value in volume_map.items():
                service_data[CONF_ENTITY_ID] = [key]
                if value != -1:
                    service_data["extra"] = {
                        "volume": value
                }
                service_calls.append({
                    "domain": "media_player",
                    "service": SERVICE_PLAY_MEDIA,
                    "service_data": service_data,
                    "blocking": True,
                    "result": True
                })

    return service_calls


async def async_fire_media_service_calls(hass: HomeAssistant, media_service_calls):
    """Fire the array of media service_calls."""
    if media_service_calls is None:
        _LOGGER.error("No service calls to fire")
        return False
    for service_call in media_service_calls:
        _LOGGER.debug("   Calling %s.%s with data:",
                    service_call["domain"],
                    service_call["service"])
        for key, value in service_call["service_data"].items():
            _LOGGER.debug("     - %s: %s", str(key), str(value))
        try:
            await hass.services.async_call(
                domain=service_call["domain"],
                service=service_call["service"],
                service_data=service_call["service_data"]
            )
            continue
        except ServiceNotFound:
            _LOGGER.error("Could not find service `%s.%s`.%s",
                    service_call["domain"],
                    service_call["service"],
                    (" Please install the Alexa Media Player Custom Component: https://github.com/alandtse/alexa_media_player"
                        if service_call["service"] == "alexa_media"
                        else "")
            )
            return False
        except TemplateError as err:
            _LOGGER.error("Error while rendering Jinja2 template for audio playback: %s", err)
            return False
        except HomeAssistantError as err:
            _LOGGER.error("An error occurred: %s", str(err))
            if err == "Unknown source directory":
                _LOGGER.warning(
                    "Please check that media directories are enabled in your configuration.yaml file, e.g:\r\n\r\nmedia_source:\r\n media_dirs:\r\n   local: /media"
                )
            return False
        except Exception as err:
            _LOGGER.error("Unexpected error when playing audio via %s.%s: %s",
                            service_call["domain"],
                            service_call["service"],
                            str(err)
                            )

    return True

async def async_post_playback_actions(
    hass: HomeAssistant,
    audio_duration: float,
    final_delay: float,
    media_players_array: list,
    unjoin_players: bool):
    """Run post playback actions."""
    # Wait the audio playback duration
    total_delay_s = round(audio_duration + ((final_delay/1000) if final_delay > 0 else 0),3)
    _LOGGER.debug(" - Waiting %ss for audio playback to complete...", str(total_delay_s))
    await hass.async_add_executor_job(time.sleep, total_delay_s)

    # Wait for playback to end on all media_players
    playing_media_player_dicts = []
    for media_player_dict in media_players_array:
        if not media_player_helper.get_is_media_player_spotify(hass, media_player_dict["entity_id"]):
            playing_media_player_dicts.append(media_player_dict)
    if not await media_player_helper.async_wait_until_media_players_state_not(hass, playing_media_player_dicts, "playing"):
        _LOGGER.debug(" - Timed out waiting for playback to complete")

    # Write to log if post-playback actions are to be performed
    if (len(_data[PAUSE_RESUME_MEDIA_PLAYER_DICTS_KEY]) > 0
        or len(_data[SET_VOLUME_MEDIA_PLAYER_DICTS_KEY]) > 0
        or (unjoin_players is True and _data.get("join_media_player_entity_id", None))):
        _LOGGER.debug(" *** Post-Playback Actions ***")

    # Resume previous playback
    if len(_data[PAUSE_RESUME_MEDIA_PLAYER_DICTS_KEY]) > 0:
        # 1. Wait until all media_players paused
        if not await media_player_helper.async_wait_until_media_players_state_is(hass=hass,
                                                                                 media_player_dicts=_data[PAUSE_RESUME_MEDIA_PLAYER_DICTS_KEY],
                                                                                 target_state="paused",
                                                                                 timeout=5):
            _LOGGER.warning("Timed out waiting for %s media_player%s to pause",
                            str(len(_data[PAUSE_RESUME_MEDIA_PLAYER_DICTS_KEY])),
                            ("" if len(_data[PAUSE_RESUME_MEDIA_PLAYER_DICTS_KEY]) == 1 else "s"))

        # 2. Set media_players volume to 0
        _LOGGER.debug("     - Setting volume to 0")
        resume_entity_ids = []
        for media_player_dict in _data[PAUSE_RESUME_MEDIA_PLAYER_DICTS_KEY]:
            entity_id = media_player_dict["entity_id"]
            resume_entity_ids.append(entity_id)
        try:
            await hass.services.async_call(
                domain="media_player",
                service=SERVICE_VOLUME_SET,
                service_data={
                    ATTR_MEDIA_VOLUME_LEVEL: 0,
                    CONF_ENTITY_ID: resume_entity_ids
                },
                blocking=True
            )
        except Exception as error:
            _LOGGER.warning("Unable to set %s's volume to 0 for: %s. Error: %s",
                            entity_id, (", ".join(map(str, resume_entity_ids))), error)


        # 3. Call `media_play` until all media_players' states are "playing"
        _LOGGER.debug("   - Resuming %s media_player%s",
                      str(len(resume_entity_ids)),
                      ("" if len(resume_entity_ids) == 1 else "s"))
        retry_duration = 3
        delay_s = 0.2
        is_media_player_playing = False
        while not is_media_player_playing and retry_duration > 0:
            try:
                await hass.services.async_call(
                    domain="media_player",
                    service="media_play",
                    service_data={CONF_ENTITY_ID: resume_entity_ids},
                    blocking=True,
                )
                is_media_player_playing = True
            except Exception as error:
                _LOGGER.warning("Unable to resume playback: %s", error)

            for entity_id in resume_entity_ids:
                is_media_player_playing = is_media_player_playing and hass.states.get(entity_id).state == "playing"
            if not is_media_player_playing:
                await hass.async_add_executor_job(time.sleep, delay_s)
            retry_duration = retry_duration - delay_s

        if is_media_player_playing is False:
            _LOGGER.warning("Failed to resume playback on %s", entity_id)

        # 4. Fade in all media players at the same time
        await media_player_helper.async_set_volume_for_media_players(hass=hass,
                                                                     media_player_dicts=_data[PAUSE_RESUME_MEDIA_PLAYER_DICTS_KEY],
                                                                     volume_key="initial_volume_level",
                                                                     fade_duration=_data[FADE_TRANSITION_KEY])

    # Reset volume
    if len(_data[SET_VOLUME_MEDIA_PLAYER_DICTS_KEY]) > 0:
        await media_player_helper.async_set_volume_for_media_players(hass=hass,
                                                                     media_player_dicts=_data[SET_VOLUME_MEDIA_PLAYER_DICTS_KEY],
                                                                     volume_key="initial_volume_level",
                                                                     fade_duration=0)

    # Unjoin entity_ids
    if unjoin_players is True and _data.get("join_media_player_entity_id", None):
        _LOGGER.debug("   - Calling media_player.unjoin service...")
        for media_player_dict in media_players_array:
            if media_player_dict["group_members_supported"] is True:
                entity_id = media_player_dict["entity_id"]
                _LOGGER.debug("     - media_player.unjoin: %s", entity_id)
                try:
                    await hass.services.async_call(
                        domain="media_player",
                        service=SERVICE_UNJOIN,
                        service_data={CONF_ENTITY_ID: entity_id},
                        blocking=True,
                    )
                    _LOGGER.debug("    ...done")
                except Exception as error:
                    _LOGGER.warning(
                        "   - Error calling unjoin service for %s: %s", entity_id, error
                    )


################################
### Storage Helper Functions ###
################################

async def async_refresh_stored_data(hass: HomeAssistant):
    """Refresh the stored data of the integration."""
    store = storage.Store(hass, 1, DATA_STORAGE_KEY)
    try:
        _data[DATA_STORAGE_KEY] = await store.async_load()
    except Exception as error:
        _LOGGER.error("Unable to retrieve stored data. Error: %s", error)


async def async_store_data(hass: HomeAssistant, key: str, value):
    """Store a key/value pair in the integration's stored data."""
    if hass is not None and key is not None and value is not None:
        _LOGGER.debug(" - Saving data to chime_tts storage:")
        _LOGGER.debug('   - key:   "%s"', key)
        _LOGGER.debug('   - value: "%s"', value)
        if _data[DATA_STORAGE_KEY] is None:
            _data[DATA_STORAGE_KEY] = {}
        _data[DATA_STORAGE_KEY][key] = value
        await async_save_data(hass)


async def async_retrieve_data(hass: HomeAssistant, key: str):
    """Retrieve a value from the integration's stored data based on the provided key."""
    await async_refresh_stored_data(hass)
    if _data.get(DATA_STORAGE_KEY, None):
        return _data[DATA_STORAGE_KEY].get(key, None)
    return None


async def async_save_data(hass: HomeAssistant):
    """Save the provided data to the integration's stored data."""
    store = storage.Store(hass, 1, DATA_STORAGE_KEY)
    await store.async_save(_data[DATA_STORAGE_KEY])


async def async_delete_data(hass: HomeAssistant, key):
    """Delete a key/value from integration's stored data."""
    store = storage.Store(hass, 1, DATA_STORAGE_KEY)
    data = await store.async_load()
    if key in data:
        del data[key]
    await store.async_save(data)


async def async_get_cached_audio_data(hass: HomeAssistant, filepath_hash: str):
    """Return cached audio data previously stored in Chime TTS' cache."""
    audio_dict = await async_retrieve_data(hass, filepath_hash)
    if audio_dict is not None:
        path = None
        duration = None
        # Support previous cache format of path stings
        if isinstance(audio_dict, str):
            path = audio_dict
        # Support previous cache format of AUDIO_PATH_KEY dictionary key values
        else:
            path = audio_dict.get(AUDIO_PATH_KEY, path)
            duration = audio_dict.get(AUDIO_DURATION_KEY, duration)
        if path is not None:
            is_public = filesystem_helper.file_exists_in_directory(path, '/www')
            audio_dict = {
                LOCAL_PATH_KEY: None if is_public else path,
                PUBLIC_PATH_KEY: path if is_public else None,
                AUDIO_DURATION_KEY: duration
            }

        # Validate paths and add duration if missing
        valid_key = None
        for key in [LOCAL_PATH_KEY, PUBLIC_PATH_KEY]:
            audio_dict[key] = audio_dict.get(key, None)
            if audio_dict.get(key, None):
                if os.path.exists(str(audio_dict.get(key, ""))):
                    valid_key = key
                    # Add duration data if audio_dict is old format
                    if audio_dict.get(AUDIO_DURATION_KEY, None) is None:
                        audio = await async_get_audio_from_path(hass=hass,
                                                                filepath=audio_dict.get(key, None),
                                                                cache=True)
                        if audio is not None:
                            audio_dict[AUDIO_DURATION_KEY] = float(len(audio) / 1000.0)
                        else:
                            _LOGGER.warning("Could not load audio from file: %s", audio_dict.get(key, ""))
                            audio.dict[key] = None
                            valid_key = None
        if valid_key is not None:
            return audio_dict

    await async_remove_cached_audio_data(hass, filepath_hash, True, True)
    return None


async def async_remove_cached_audio_data(hass: HomeAssistant,
                                         filepath_hash: str,
                                         clear_chimes_cache: bool = False,
                                         clear_temp_tts_cache: bool = False,
                                         clear_www_tts_cache: bool = False):
    """Remove cached audio data from Chime TTS' cache and deletes audio filepath from filesystem."""
    audio_dict = await async_retrieve_data(hass, filepath_hash)
    if audio_dict is None:
        return
    temp_chimes_path = _data.get(TEMP_CHIMES_PATH_KEY, None)
    temp_path = _data.get(TEMP_PATH_KEY, None)

    for key, value in audio_dict.items():
        if key == LOCAL_PATH_KEY and audio_dict.get(LOCAL_PATH_KEY, None) is not None:
            if clear_chimes_cache and filesystem_helper.file_exists_in_directory(value, temp_chimes_path):
                _LOGGER.debug("...removing chime file %s", value)
                filesystem_helper.delete_file(audio_dict.get(LOCAL_PATH_KEY, None))
                audio_dict[LOCAL_PATH_KEY] = None
            elif clear_temp_tts_cache and filesystem_helper.file_exists_in_directory(value, temp_path):
                _LOGGER.debug("...removing TTS file %s", value)
                filesystem_helper.delete_file(audio_dict.get(LOCAL_PATH_KEY, None))
                audio_dict[LOCAL_PATH_KEY] = None
        elif key == PUBLIC_PATH_KEY and value is not None and clear_www_tts_cache:
            _LOGGER.debug("...removing public file %s", value)
            filesystem_helper.delete_file(audio_dict.get(PUBLIC_PATH_KEY, None))
            audio_dict[PUBLIC_PATH_KEY] = None

    # Remove key/value from integration storage if no paths remain
    if audio_dict.get(LOCAL_PATH_KEY, None) is not None or (audio_dict.get(PUBLIC_PATH_KEY, None)):
        await async_delete_data(hass, filepath_hash)


async def async_add_audio_file_to_cache(hass: HomeAssistant,
                                        audio_path: str,
                                        duration: float,
                                        params,
                                        options,
                                        file_hash: str = None):
    """Add an audio path to the Chime TTS cache."""
    if hass is not None and audio_path is not None and duration is not None:
        if file_hash is not None:
            filepath_hash = file_hash
        else:
            filepath_hash = get_filename_hash_from_service_data({**params}, {**options})

        audio_cache_dict = await async_get_cached_audio_data(hass, filepath_hash)
        if audio_cache_dict is None:
            audio_cache_dict = {}
        if filesystem_helper.file_exists_in_directory(audio_path, _data.get(WWW_PATH_KEY, None)):
            audio_cache_dict[PUBLIC_PATH_KEY] = audio_path
        else:
            audio_cache_dict[LOCAL_PATH_KEY] = audio_path

        if AUDIO_DURATION_KEY not in audio_cache_dict:
            audio_cache_dict[AUDIO_DURATION_KEY] = duration

        await async_store_data(hass, filepath_hash, audio_cache_dict)


def get_filename_hash_from_service_data(params: dict, options: dict):
    """Generate a hash from a unique string."""

    unique_string = ""
    relevant_params = [
        "message",
        "tts_platform",
        "tld",
        "voice",
        "language",
        "chime_path",
        "audio_conversion",
        "end_chime_path",
        "offset",
        "tts_playback_speed",
        "tts_speed",
        "tts_pitch"
    ]
    for param in relevant_params:
        for dictionary in [params, options]:
            if (
                param in dictionary
                and dictionary.get(param, None)
                and len(str(dictionary[param])) > 0
            ):
                unique_string = unique_string + "-" + str(dictionary[param])

    hash_value = filesystem_helper.get_hash_for_string(unique_string)
    return hash_value
