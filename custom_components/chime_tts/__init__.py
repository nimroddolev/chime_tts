"""The Chime TTS integration."""

import logging
import time
from datetime import datetime

from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError

from homeassistant.components.media_player.const import (
    ATTR_MEDIA_CONTENT_ID,
    ATTR_MEDIA_CONTENT_TYPE,
    ATTR_MEDIA_ANNOUNCE,
    SERVICE_PLAY_MEDIA,
    MediaType as MEDIA_TYPE,
)

from .helpers.helpers import ChimeTTSHelper
from .helpers.media_player_helper import (MediaPlayerHelper, ChimeTTSMediaPlayer)
from .helpers.filesystem import FilesystemHelper
from .helpers.services_helper import ChimeTTSServicesHelper
from .helpers.tts_audio_helper import TTSAudioHelper
from .queue_manager import ChimeTTSQueueManager
from .config_flow import ChimeTTSOptionsFlowHandler

from homeassistant.const import CONF_ENTITY_ID
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceResponse, SupportsResponse
from homeassistant.helpers import storage
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
    AUDIO_DURATION_KEY,
    FADE_TRANSITION_KEY,
    REMOVE_TEMP_FILE_DELAY_KEY,
    DEFAULT_FADE_TRANSITION_MS,
    ADD_COVER_ART_KEY,

    ROOT_PATH_KEY,
    CUSTOM_CHIMES_PATH_KEY,
    DEFAULT_TEMP_CHIMES_PATH_KEY,
    TEMP_CHIMES_PATH_KEY,
    TEMP_CHIMES_PATH_DEFAULT,

    DEFAULT_TEMP_PATH_KEY,
    TEMP_PATH_KEY,
    TEMP_PATH_DEFAULT,

    DEFAULT_WWW_PATH_KEY,
    WWW_PATH_KEY,
    WWW_PATH_DEFAULT,

    ALEXA_MEDIA_PLAYER_PLATFORM,
    FFMPEG_ARGS_ALEXA,
    SONOS_PLATFORM,
    MP3_PRESET_CUSTOM_PREFIX,
    MP3_PRESET_CUSTOM_KEY,
    QUEUE_TIMEOUT_KEY,
    QUEUE_TIMEOUT_DEFAULT,
    TTS_TIMEOUT_KEY,
    TTS_TIMEOUT_DEFAULT,
    SPOTIFY_PLATFORM,
    TTS_PLATFORM_KEY,
    DEFAULT_LANGUAGE_KEY,
    DEFAULT_VOICE_KEY,
    DEFAULT_TLD_KEY,
    FALLBACK_TTS_PLATFORM_KEY,
    OFFSET_KEY,
    CROSSFADE_KEY,
)
from .config import SONOS_SNAPSHOT_ENABLED

_LOGGER = logging.getLogger(__name__)
_data = {}

helpers = ChimeTTSHelper()
tts_audio_helper = TTSAudioHelper()
media_player_helper = MediaPlayerHelper()
filesystem_helper = FilesystemHelper()
queue = ChimeTTSQueueManager()
services_helper = ChimeTTSServicesHelper()


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up an entry."""
    config_entry.async_on_unload(config_entry.add_update_listener(async_reload_entry))
    await async_refresh_stored_data(hass)
    await async_update_configuration(config_entry, hass)
    queue.set_timeout(_data.get(QUEUE_TIMEOUT_KEY, QUEUE_TIMEOUT_DEFAULT))
    queue.start_queue_processor()

    return True

async def async_setup(hass: HomeAssistant, _config_entry: ConfigEntry) -> bool:  # noqa: C901
    """Set up the Chime TTS integration."""
    helpers.debug_title(f"Chime TTS Version {VERSION} is set up")

    # Say Service #

    async def async_say(service, is_say_url = False):
        """chime_tts.say, chime_tts.say_url & chime_tts.replay entry point."""
        if is_say_url is False:
            if service is None:
                helpers.debug_title(f"Chime TTS Replay Called. Version {VERSION}")
                if _data.get("service") is None:
                    raise HomeAssistantError("You must first make a service call to chime_tts.say before you can replay it.")
            else:
                helpers.debug_title(f"Chime TTS Say Called. Version {VERSION}")

        # Add service calls to the queue with arguments
        timeout = _data.get(QUEUE_TIMEOUT_KEY, QUEUE_TIMEOUT_DEFAULT)
        result = False
        try:
            result = await queue.add_to_queue(async_say_execute, timeout, service, is_say_url)
        except Exception as error:
            error_string = f"Error calling chime_tts.say{'_url' if is_say_url else ''} service: {str(error)}"
            _LOGGER.error("%s", str(error_string))
            raise

        if result is not False:
            return result

        # Service call failed
        raise HomeAssistantError("An unknown error occurred")

    async def async_say_execute(service, is_say_url):
        """Play TTS audio with local chime MP3 audio."""
        start_time = datetime.now()
        parse_result = True

        if service is None:
            # Replay service called: use previous service object
            service = _data.get("service")
            if service is None:
                raise HomeAssistantError("A service call to chime_tts.say must be made before you can replay it.")
        else:
            _data["service"] = service

        # Parse service parameters & TTS options
        params = await helpers.async_parse_params(hass, service.data, is_say_url, media_player_helper)
        if params is not None:
            options = helpers.parse_options_yaml(data=service.data, default_data=_data)
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

    _data["async_say"] = async_say

    # Say URL Service #

    async def async_say_url(service) -> ServiceResponse:
        """Create a public URL to an audio file generated with the `chime_tts.say` service."""
        helpers.debug_title(f"Chime TTS Say URL Called. Version {VERSION}")
        return await async_say(service, True)

    hass.services.async_register(DOMAIN,
                                 SERVICE_SAY_URL,
                                 async_say_url,
                                 supports_response=SupportsResponse.ONLY)

    _data["async_say_url"] = async_say_url

    # Replay Service #
    async def async_replay(_service):
        """Repeat the last service call to chime_tts.say with the same parameters."""
        return await async_say(None, False)

    hass.services.async_register(DOMAIN,
                                 SERVICE_REPLAY,
                                 async_replay)

    # Clear Cache Service #

    async def async_clear_cache(service):
        """Clear TTS cache files."""
        helpers.debug_title("Chime TTS Clear Cache Called")
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
            try:
                await hass.services.async_call(
                    domain="TTS",
                    service="clear_cache",
                    blocking=True
                )
            except Exception as error:
                _LOGGER.error("Error when clearing TTS cache: %s", error)

        # Summary
        elapsed_time = (datetime.now() - start_time).total_seconds() * 1000
        elapsed_time = (f"{elapsed_time} s"
                        if elapsed_time >= 1
                        else f"{elapsed_time * 1000} ms")
        helpers.debug_finish(f"Chime TTS Clear Cache Completed in {elapsed_time}")

        return True

    hass.services.async_register(DOMAIN,
                                 SERVICE_CLEAR_CACHE,
                                 async_clear_cache)

    return True

async def async_prepare_media(hass: HomeAssistant, params, options, media_players_array: list[ChimeTTSMediaPlayer], is_say_url, start_time):
    """Prepare and play media."""

    helpers.debug_subtitle("Preparing Audio")
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
                params["announce"]
            )
            if play_result is True:
                await async_post_playback_actions(
                    hass,
                    audio_duration,
                    params["final_delay"],
                    media_players_array,
                )

            # Remove temporary local generated mp3
            if not bool(params.get("cache", False)):
                remove_temp_file_delay_s = float(_data[REMOVE_TEMP_FILE_DELAY_KEY] / 1000)
                if remove_temp_file_delay_s > 0:
                    _LOGGER.debug("Waiting %ss before removing temporary file%s:", str(remove_temp_file_delay_s), "s" if local_path and public_path else "")
                    await hass.async_add_executor_job(time.sleep, remove_temp_file_delay_s)
                else:
                    _LOGGER.debug("Removing temporary file%s:", "s" if local_path and public_path else "")
                filesystem_helper.delete_file(hass, local_path)
                filesystem_helper.delete_file(hass, public_path)


    end_time = datetime.now()
    completion_time = round((end_time - start_time).total_seconds(), 2)
    elapsed_time = (f"{completion_time} s"
                                if completion_time >= 1
                                else f"{completion_time * 1000} ms")

    # Convert public file path to external URL for chime_tts.say_url
    if is_say_url:
        _LOGGER.debug("Final URL = %s", public_path)
        helpers.debug_finish(f"Chime TTS Say URL Completed in {elapsed_time}")
        ret_value = {
            "url": public_path,
            ATTR_MEDIA_CONTENT_ID: media_content_id,
            "duration": audio_duration,
            "success": (public_path is not None or media_content_id is not None)
        }
        if ret_value["success"] is False:
            if public_path is None:
                _LOGGER.warning("No public filepath was found for the generated MP3 file")
            else:
                _LOGGER.warning("The folder path '%s' should be within the public \"www\" folder or the local media folder.", public_path)

        return ret_value

    helpers.debug_finish(f"Chime TTS Say Completed in {elapsed_time}")

async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    return True

async def async_reload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Reload the Chime TTS config entry."""
    _LOGGER.debug("Reloading integration")
    await async_unload_entry(hass, config_entry)
    await async_setup(hass, config_entry)
    await async_refresh_stored_data(hass)
    await async_update_configuration(config_entry, hass)

# Integration options #

async def async_options(self, entry: ConfigEntry):
    """Present current configuration options for modification."""
    # Create an options flow handler and return it
    return ChimeTTSOptionsFlowHandler(entry)

async def async_options_updated(self, entry: ConfigEntry):
    """Handle updated configuration options and update the entry."""
    # Update the queue timeout value
    await async_update_configuration(entry, None)

async def async_update_configuration(config_entry: ConfigEntry, hass: HomeAssistant = None):
    """Update configurable values."""

    # Prepare default paths
    if hass is not None:
        _data[ROOT_PATH_KEY] = filesystem_helper.make_folder_path_safe(hass.config.path("").replace("/config/", ""))

    if DEFAULT_TEMP_PATH_KEY not in _data:
        _data[DEFAULT_TEMP_PATH_KEY] = filesystem_helper.make_folder_path_safe(f"{_data[ROOT_PATH_KEY]}{TEMP_PATH_DEFAULT}")

    if DEFAULT_TEMP_CHIMES_PATH_KEY not in _data:
        _data[DEFAULT_TEMP_CHIMES_PATH_KEY] = filesystem_helper.make_folder_path_safe(f"{_data[ROOT_PATH_KEY]}{TEMP_CHIMES_PATH_DEFAULT}")

    if DEFAULT_WWW_PATH_KEY not in _data:
        _data[DEFAULT_WWW_PATH_KEY] = filesystem_helper.make_folder_path_safe(f"{_data[ROOT_PATH_KEY]}/{WWW_PATH_DEFAULT}")

    # Set configurable values
    options = config_entry.options

    # Queue timeout
    _data[QUEUE_TIMEOUT_KEY] = options.get(QUEUE_TIMEOUT_KEY, QUEUE_TIMEOUT_DEFAULT)

    # Default TTS Platform
    _data[TTS_PLATFORM_KEY] = options.get(TTS_PLATFORM_KEY, "")

    # TTS timeout
    _data[TTS_TIMEOUT_KEY] = options.get(TTS_TIMEOUT_KEY, TTS_TIMEOUT_DEFAULT)

    # Default language
    _data[DEFAULT_LANGUAGE_KEY] = options.get(DEFAULT_LANGUAGE_KEY, None)

    # Default voice
    _data[DEFAULT_VOICE_KEY] = options.get(DEFAULT_VOICE_KEY, None)

    # Default voice
    _data[DEFAULT_TLD_KEY] = options.get(DEFAULT_TLD_KEY, None)

    # Fallback TTS Platform
    _data[FALLBACK_TTS_PLATFORM_KEY] = options.get(FALLBACK_TTS_PLATFORM_KEY, "")

    # Default offset
    _data[OFFSET_KEY] = options.get(OFFSET_KEY, 0)

    # Default crossfade
    _data[CROSSFADE_KEY] = options.get(CROSSFADE_KEY, 0)

    # Default audio fade transition duration
    _data[FADE_TRANSITION_KEY] = options.get(FADE_TRANSITION_KEY, DEFAULT_FADE_TRANSITION_MS)

    # Delay before removing temporary file
    conf_remove_temp_file_delay = options.get(REMOVE_TEMP_FILE_DELAY_KEY, 0)
    _data[REMOVE_TEMP_FILE_DELAY_KEY] = int(conf_remove_temp_file_delay) if str(conf_remove_temp_file_delay).isdigit() else 0

    # Add cover art to generated MP3 files
    _data[ADD_COVER_ART_KEY] = options.get(ADD_COVER_ART_KEY, False)

    # www / local folder path
    _data[WWW_PATH_KEY] = filesystem_helper.make_folder_path_safe(
        hass.config.path(
            options.get(WWW_PATH_KEY, _data.get(DEFAULT_WWW_PATH_KEY, WWW_PATH_DEFAULT))
        )
    )

    # Temp chimes folder path
    _data[TEMP_CHIMES_PATH_KEY] = filesystem_helper.make_folder_path_safe(
        hass.config.path(
            options.get(TEMP_CHIMES_PATH_KEY, _data.get(DEFAULT_TEMP_CHIMES_PATH_KEY, None))
        )
    )

    # Temp folder path
    _data[TEMP_PATH_KEY] = filesystem_helper.make_folder_path_safe(
        hass.config.path(
            options.get(TEMP_PATH_KEY, _data.get(DEFAULT_TEMP_PATH_KEY, None))
        )
    )

    # Update the services.yaml file with refreshed chimes options
    _data[CUSTOM_CHIMES_PATH_KEY] = filesystem_helper.make_folder_path_safe(options.get(CUSTOM_CHIMES_PATH_KEY))

    # Update _data in helper classes
    tts_audio_helper._data = _data
    services_helper._data = _data

    # Update the services.yaml file with refreshed chimes options
    await services_helper.async_update_services_yaml(
        hass=hass,
        say_service_func=_data["async_say"],
        say_url_service_func=_data["async_say_url"])

    # Custom chime path slots (DEPRECATED SINCE v1.1.0)
    _data[MP3_PRESET_CUSTOM_KEY] = {}
    for i in range(5):
        key = MP3_PRESET_CUSTOM_PREFIX + str(i + 1)
        value = options.get(key)
        if value and len(value) > 0:
            _data[MP3_PRESET_CUSTOM_KEY][key] = value

    # Debug summary
    helpers.debug_subtitle("Chime TTS Configuration Values")

    for key_string in [
        QUEUE_TIMEOUT_KEY,
        TTS_TIMEOUT_KEY,
        TTS_PLATFORM_KEY,
        DEFAULT_LANGUAGE_KEY,
        DEFAULT_VOICE_KEY,
        DEFAULT_TLD_KEY,
        FALLBACK_TTS_PLATFORM_KEY,
        OFFSET_KEY,
        CROSSFADE_KEY,
        FADE_TRANSITION_KEY,
        REMOVE_TEMP_FILE_DELAY_KEY,
        ADD_COVER_ART_KEY,
        TEMP_CHIMES_PATH_KEY,
        TEMP_PATH_KEY,
        WWW_PATH_KEY,
        CUSTOM_CHIMES_PATH_KEY,
        MP3_PRESET_CUSTOM_KEY,
    ]:
        if key_string == MP3_PRESET_CUSTOM_KEY and not _data[MP3_PRESET_CUSTOM_KEY]:
            continue
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
            _LOGGER.debug(" - %s: %s%s%s", str(key_string).replace("_key", ""), quote, str(value), quote)

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
    crossfade = params.get("crossfade", _data[CROSSFADE_KEY])
    message = params.get("message", None)
    cache = params.get("cache", False)
    entity_ids = params.get("entity_ids", [])
    ffmpeg_args = params.get("ffmpeg_args", "")

    # Produce local and/or public mp3s?
    alexa_media_player_count = public_count = media_player_helper.get_alexa_media_players_count()
    is_public = public_count > 0 or (entity_ids is None or len(entity_ids) == 0)
    is_local = entity_ids is not None and len(entity_ids) > 0 and public_count != len(entity_ids)

    filepath_hash = get_filename_hash_from_service_data({**params}, {**options})
    _data["generated_filename"] = filepath_hash

    # Load previously generated audio from cache
    if cache is True:
        _LOGGER.debug(" *** Checking Chime TTS audio cache ***")
        audio_dict: dict = await async_verify_cached_audio(hass, filepath_hash, params, options, is_local, is_public, ffmpeg_args)
        if audio_dict:
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
                                                   crossfade=crossfade,
                                                   audio=output_audio)

    # Save generated audio file
    audio_dict = {
        AUDIO_DURATION_KEY: 0,
        LOCAL_PATH_KEY: None,
        PUBLIC_PATH_KEY: None
    }
    if output_audio is not None:
        folder_path_key = TEMP_PATH_KEY if is_local else WWW_PATH_KEY
        folder_path_default = TEMP_PATH_DEFAULT if is_local else WWW_PATH_DEFAULT
        save_folder = _data.get(folder_path_key, folder_path_default)
        initial_save_folder_name = "local" if is_local else "public"
        if not save_folder:
            _LOGGER.warning("Error saving generated file to %s folder. Check the integration's configuration", initial_save_folder_name)
            return None
        _LOGGER.debug(" - Saving mp3 file to %s folder: %s...", initial_save_folder_name, save_folder)
        new_audio_file = await filesystem_helper.async_save_audio_to_folder(
            hass,
            output_audio,
            save_folder)
        if new_audio_file is None:
            _LOGGER.warning("Error saving file")
            return None

        # Add cover art
        if _data.get(ADD_COVER_ART_KEY):
            if alexa_media_player_count > 0:
                _LOGGER.warning("Unable to add cover art. Alexa Media Player media_players are unable to play MP3 file with cover art")
            else:
                cover_art_filepath = f"{filesystem_helper.path_to_parent_folder('custom_components')}/chime_tts/cover_art.jpg"
                if await hass.async_add_executor_job(filesystem_helper.path_exists, cover_art_filepath):
                    _LOGGER.debug("Adding cover art to %s", new_audio_file)
                    new_audio_file = await helpers.async_ffmpeg_convert_from_file(
                        hass,
                        new_audio_file,
                        f"-i {cover_art_filepath} -c copy -map 0 -map 1")

        # Perform FFmpeg conversion
        if ffmpeg_args:
            _LOGGER.debug("  - Performing FFmpeg audio conversion...")
            converted_audio_file = await helpers.async_ffmpeg_convert_from_file(hass, new_audio_file, ffmpeg_args)
            if converted_audio_file is not False:
                _LOGGER.debug("    ...FFmpeg audio conversion completed.")
                new_audio_file = converted_audio_file
            else:
                _LOGGER.warning("...FFmpeg audio conversion failed. Continuing using the original audio file")

        try:
            new_audio_segment = await filesystem_helper.async_load_audio(new_audio_file)
        except CouldntDecodeError:
            raise ValueError("The file format is not supported or the file is corrupted.")
        except Exception as e:
            raise RuntimeError(f"An unexpected error occurred: {e}")

        duration = len(new_audio_segment) / 1000.0
        audio_dict[AUDIO_DURATION_KEY] = duration
        audio_dict[LOCAL_PATH_KEY if is_local else PUBLIC_PATH_KEY] = new_audio_file
        file_path: str = audio_dict.get(LOCAL_PATH_KEY, None) or audio_dict.get(PUBLIC_PATH_KEY, None)
        audio_dict[ATTR_MEDIA_CONTENT_ID] = media_player_helper.get_media_content_id(hass, file_path)

        # Copy generated audio to local/public folder/s
        audio_dict = await async_save_audio_to_folder(hass, is_local, is_public, audio_dict, output_audio)

        # Convert external URL (for public paths)
        if audio_dict.get(PUBLIC_PATH_KEY, None):
            audio_dict[PUBLIC_PATH_KEY] = await filesystem_helper.async_get_external_url(hass, audio_dict.get(PUBLIC_PATH_KEY, None))

        # Fetch Media Content ID
        if is_local:
            audio_dict[ATTR_MEDIA_CONTENT_ID] = media_player_helper.get_media_content_id(hass, audio_dict.get(LOCAL_PATH_KEY, ''))

    # Valdiation
    is_valid = await hass.async_add_executor_job(validate_audio_dict, hass, is_local, is_public, audio_dict)
    if not is_valid:
        return None

    _LOGGER.debug(" - Chime TTS audio generated:")
    for key, value in audio_dict.items():
        quote = '"' if isinstance(value, str) else ''
        value = f"{quote}{value}{quote}"
        _LOGGER.debug("   * %s = %s", key, value)

    # Save path to cache
    if cache:
        await async_add_audio_file_to_cache(hass, audio_dict.get(PUBLIC_PATH_KEY, None), duration, params, options)
        await async_add_audio_file_to_cache(hass, audio_dict.get(LOCAL_PATH_KEY, None), duration, params, options)

    return audio_dict

async def async_save_audio_to_folder(hass: HomeAssistant, is_local: bool, is_public: bool, audio_dict: dict, output_audio: AudioSegment):
    """Save local/public audio to local/public folder/s."""
    # Save audio to local folder
    if is_local and not audio_dict.get(LOCAL_PATH_KEY, None):
        _LOGGER.debug(" - Saving generated audio to local folder: %s...", _data[TEMP_PATH_KEY])
        audio_dict[LOCAL_PATH_KEY] = await filesystem_helper.async_save_audio_to_folder(
            hass, output_audio, _data[TEMP_PATH_KEY])
    # Save audio to public folder
    if is_public and not audio_dict.get(PUBLIC_PATH_KEY, None):
        _LOGGER.debug(" - Saving generated audio to public folder: %s...", _data[WWW_PATH_KEY])
        audio_dict[PUBLIC_PATH_KEY] = await filesystem_helper.async_save_audio_to_folder(
            hass, output_audio, _data[WWW_PATH_KEY])
    return audio_dict


def validate_audio_dict(hass: HomeAssistant, is_local: bool, is_public: bool, audio_dict: dict):
    """Validate audio contained within an audio_dict."""
    is_valid = True
    if audio_dict[AUDIO_DURATION_KEY] == 0:
        _LOGGER.error("async_get_playback_audio_path --> Audio has no duration")
        is_valid = False
    if is_local:
        if audio_dict.get(LOCAL_PATH_KEY, None) is None:
            _LOGGER.error("async_get_playback_audio_path --> Unable to generate local audio file")
            is_valid = False
        elif not filesystem_helper.path_exists(audio_dict.get(LOCAL_PATH_KEY, "")):
            _LOGGER.error("async_get_playback_audio_path --> Local audio file '%s' not found on filesystem", audio_dict.get(LOCAL_PATH_KEY, ""))
            is_valid = False
        if not audio_dict.get(ATTR_MEDIA_CONTENT_ID, None):
            _LOGGER.error("async_get_playback_audio_path --> Unable to generate Media Content Id")
            is_valid = False
    if is_public:
        if not(audio_dict.get(PUBLIC_PATH_KEY, None)):
            _LOGGER.error("async_get_playback_audio_path --> Unable to generate public audio file")
            is_valid = False
        else:
            _LOGGER.debug("Checking if file '%s' exists locally", audio_dict.get(PUBLIC_PATH_KEY, ""))
            external_local_path: str = filesystem_helper.get_local_path(hass, audio_dict.get(PUBLIC_PATH_KEY, ""))
            if not (external_local_path or external_local_path.startswith("http://localhost") or filesystem_helper.path_exists(external_local_path)):
                _LOGGER.error("async_get_playback_audio_path --> Public audio file not found on filesystem: %s", external_local_path)
                is_valid = False
    return is_valid

async def async_verify_cached_audio(hass: HomeAssistant,
                                    filepath_hash: str,
                                    params: dict,
                                    options: dict,
                                    is_local: bool,
                                    is_public: bool,
                                    ffmpeg_args: str):
    """Return verified audio_dict object from cache."""
    audio_dict = await async_get_cached_audio_data(hass, filepath_hash)

    if audio_dict is not None and AUDIO_DURATION_KEY in audio_dict:
        duration = audio_dict.get(AUDIO_DURATION_KEY, None)

        # Test if cached audio file exists on the filesystem
        local_exists = await hass.async_add_executor_job(filesystem_helper.path_exists, f"{audio_dict.get(LOCAL_PATH_KEY, '')}")
        local_external_filepath = filesystem_helper.get_local_path(hass=hass, file_path=f"{audio_dict.get(PUBLIC_PATH_KEY, '')}")
        public_exists = await hass.async_add_executor_job(filesystem_helper.path_exists, local_external_filepath) or f"{audio_dict.get(PUBLIC_PATH_KEY, '')}".startswith("http://localhost")

        if not (public_exists or local_exists):
            _LOGGER.debug("   No cached audio found on filesystem")
            await async_delete_data(hass=hass, key=filepath_hash)
            return None

        # No local file exists
        if is_local and not local_exists:
            # Make a local copy of the public file
            if public_exists and await hass.async_add_executor_job(filesystem_helper.path_exists, local_external_filepath):
                _LOGGER.debug("   - Copying cached public file %s to local path %s", local_external_filepath, _data[TEMP_PATH_KEY])
                audio_dict[LOCAL_PATH_KEY] = await filesystem_helper.async_copy_file(hass, local_external_filepath, _data[TEMP_PATH_KEY])
                if await hass.async_add_executor_job(filesystem_helper.path_exists, f"{audio_dict.get(LOCAL_PATH_KEY, '')}"):
                    await async_add_audio_file_to_cache(hass, audio_dict.get(LOCAL_PATH_KEY, ""), duration, params, options)
                    local_exists = True
                else:
                    _LOGGER.warning("Unable to copy public file %s to path: '%s'", local_external_filepath, audio_dict.get(LOCAL_PATH_KEY, ""))
                    return None

        # No public file exists
        if is_public and not public_exists and local_exists:
            _LOGGER.debug("    - Copying cached local file %s to public path %s", audio_dict.get(LOCAL_PATH_KEY, ""), _data[WWW_PATH_KEY])
            audio_dict[PUBLIC_PATH_KEY] = await filesystem_helper.async_copy_file(hass, audio_dict.get(LOCAL_PATH_KEY, ""), _data[WWW_PATH_KEY])
            if await hass.async_add_executor_job(filesystem_helper.path_exists, audio_dict.get(PUBLIC_PATH_KEY, "")) or audio_dict.get(PUBLIC_PATH_KEY, "").startswith("http://localhost"):
                await async_add_audio_file_to_cache(hass, audio_dict.get(PUBLIC_PATH_KEY, ""), duration, params, options)
                public_exists = True
            else:
                _LOGGER.warning("Unable to copy cached local file %s to public path: '%s'", audio_dict.get(LOCAL_PATH_KEY, ""), audio_dict.get(PUBLIC_PATH_KEY, ""))
                return None

        # Convert local file path to public file to external address
        if audio_dict.get(PUBLIC_PATH_KEY, None):
            audio_dict[PUBLIC_PATH_KEY] = await filesystem_helper.async_get_external_url(hass=hass, file_path=audio_dict.get(PUBLIC_PATH_KEY, ""))

        # Get media content ID
        audio_dict[ATTR_MEDIA_CONTENT_ID] = media_player_helper.get_media_content_id(hass,
                                                                                     f"{audio_dict.get(LOCAL_PATH_KEY, '')}" or
                                                                                     f"{audio_dict.get(PUBLIC_PATH_KEY, '')}")

        # Apply audio conversion
        if (local_exists or public_exists) and ffmpeg_args:
            for local_path in [audio_dict.get(LOCAL_PATH_KEY), local_external_filepath]:
                if local_path and await hass.async_add_executor_job(filesystem_helper.path_exists, local_path):
                    if not (ffmpeg_args == FFMPEG_ARGS_ALEXA and await filesystem_helper.async_is_audio_alexa_compatible(hass, local_path)):
                        _LOGGER.debug("   Apply audio conversion")
                        await helpers.async_ffmpeg_convert_from_file(hass, local_path, ffmpeg_args)
                    elif local_path == local_external_filepath:
                        _LOGGER.debug("Cached file already Alexa Media Player compatible: '%s'", local_path)

        # Cached audio found
        if public_exists or local_exists:
            _LOGGER.debug("   Using cached audio:")
            for key, value in audio_dict.items():
                _LOGGER.debug("     - %s = %s", key, f'"{value}"' if isinstance(value, str) else value)

            return audio_dict

    return None


def get_segment_offset(output_audio, segment, params):
    """Offset value for segment."""
    segment_offset: float = 0
    if output_audio is not None:
        # Get "offset" parameter
        if "offset" in segment:
            segment_offset = float(segment["offset"])
        else:
            # Support deprecated "delay" parmeter
            if "delay" in segment:
                segment_offset = float(segment["delay"])
            elif "delay" in params:
                segment_offset = float(params["delay"])
            # Fallback to "offset" in list of parameters
            elif "offset" in params:
                segment_offset = float(params["offset"])

    return segment_offset


async def async_process_segments(hass, message, output_audio=None, params={}, options={}):
    """Process all message segments and add the audio."""
    segments = helpers.parse_message(message)
    if segments is None or len(segments) == 0:
        return output_audio

    for index, segment in enumerate(segments):
        segment_cache: bool = segment.get("cache", params.get("cache", False))
        segment_audio_conversion: str = helpers.parse_ffmpeg_args(segment.get("audio_conversion", ""))
        segment_offset: int = get_segment_offset(output_audio, segment, params)
        segment_crossfade: int = segment.get("crossfade", params.get("crossfade", 0))
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
                                                               crossfade=segment_crossfade,
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
                # Use exposed parameters if not present in the options dictionary
                segment_options = helpers.convert_yaml_str(segment.get("options")) or {}
                exposed_option_keys = ["tld", "voice"]
                for exposed_option_key in exposed_option_keys:
                    value = (segment_options.get(exposed_option_key, None) or
                             segment.get(exposed_option_key, None))
                    if value is not None:
                        segment_options[exposed_option_key] = value

                # Extract parameters
                segment_message = segment["message"]
                segment_tts_platform = segment.get("tts_platform", params.get("tts_platform", None))
                segment_language = segment.get("language", segment_options.get("language", params.get("language", None)))
                segment_tts_speed = float(segment.get("tts_speed", params.get("tts_speed", 100)))
                segment_tts_pitch = float(segment.get("tts_pitch", params.get("tts_pitch", 0)))

                # Generate hash
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

                tts_audio: AudioSegment = None

                # Use cached TTS audio
                if segment_cache is True:
                    _LOGGER.debug(" - Attempting to retrieve TTS audio from cache...")
                    audio_dict = await async_get_cached_audio_data(hass, segment_filepath_hash)
                    if audio_dict and audio_dict.get(LOCAL_PATH_KEY, None):
                        tts_audio = await async_get_audio_from_path(hass=hass,
                                                                    filepath=audio_dict.get(LOCAL_PATH_KEY, None),
                                                                    cache=segment_cache,
                                                                    audio=None)

                        tts_audio_duration = audio_dict.get(AUDIO_DURATION_KEY, None)
                    else:
                        _LOGGER.debug("   ...no cached TTS audio found")


                # Generate new TTS audio
                if tts_audio is None:
                    tts_audio = await tts_audio_helper.async_request_tts_audio(
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
                            tts_audio_full_path = await filesystem_helper.async_save_audio_to_folder(
                                hass,
                                tts_audio,
                                _data.get(TEMP_PATH_KEY, None))
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
                    temp_folder: str = _data.get(TEMP_PATH_KEY, None)
                    tts_audio = await helpers.async_change_speed_of_audiosegment(hass, tts_audio, segment_tts_speed, temp_folder)
                    tts_audio = await helpers.async_change_pitch_of_audiosegment(hass, tts_audio, segment_tts_pitch, temp_folder)
                    tts_audio = await helpers.async_ffmpeg_convert_from_audio_segment(hass, tts_audio, segment_audio_conversion, temp_folder)

                # Combine audio
                if tts_audio is not None:
                    output_audio = helpers.combine_audio(output_audio,
                                                         tts_audio,
                                                         segment_offset,
                                                         segment_crossfade)
                else:
                    _LOGGER.warning("Error generating TTS audio from messsage segment #%s: %s",
                                    str(index+1), str(segment))
            else:
                _LOGGER.warning("TTS 'message' value missing from messsage segment #%s: %s",
                                str(index+1), str(segment))

    return output_audio

async def async_get_audio_from_path(
        hass: HomeAssistant,
        filepath: str,
        cache: bool = False,
        offset: float = 0,
        crossfade: float = 0,
        audio_conversion: str = "",
        audio: AudioSegment = None
    ):
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
                await async_add_audio_file_to_cache(
                    hass=hass,
                    audio_path=filepath,
                    duration=audio_dict.get(AUDIO_DURATION_KEY, None),
                    params=None,
                    options=None,
                    file_hash=file_hash
                )

        _LOGGER.debug(' - Retrieving audio from path: "%s"...', filepath)
        try:
            audio_from_path: AudioSegment = await filesystem_helper.async_load_audio(filepath)

            # Apply audio conversion
            if audio_conversion is not None and len(audio_conversion) > 0:
                _LOGGER.debug("  - Performing FFmpeg audio conversion of audio file: \"%s\"...", audio_conversion)
                temp_folder: str = _data.get(TEMP_PATH_KEY, None)
                audio_from_path = await helpers.async_ffmpeg_convert_from_audio_segment(hass,
                                                                                        audio_from_path,
                                                                                        ffmpeg_args=audio_conversion,
                                                                                        folder=temp_folder)

            # Remove downloaded file when cache=false
            if cache is False and file_hash is not None:
                filesystem_helper.delete_file(hass, filepath)

            if audio_from_path is not None:
                duration = float(len(audio_from_path) / 1000.0)
                _LOGGER.debug(
                    "   ...audio retrieved. Duration: %ss",
                    str(duration),
                )
                if audio is None:
                    return audio_from_path

                # Apply offset
                return helpers.combine_audio(audio, audio_from_path, offset, crossfade)
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
    announce
):
    """Call the media_player.play_media service."""

    has_fade_in_out_media_players = len(media_player_helper.get_fade_in_out_media_players()) > 0
    has_sonos_media_players = len(media_player_helper.get_media_players_of_platform(entity_ids, SONOS_PLATFORM)) and SONOS_SNAPSHOT_ENABLED
    has_set_volume_media_players = len(media_player_helper.get_set_volume_media_players()) > 0
    is_should_join = bool(media_player_helper.join_players)
    if has_fade_in_out_media_players or has_sonos_media_players or has_set_volume_media_players or is_should_join:
        helpers.debug_subtitle("Pre-Playback Actions")

    # Fade out and pause media players
    await media_player_helper.async_fade_out_and_pause(hass, _data[FADE_TRANSITION_KEY])

    # Snapshot Sonos media players
    await media_player_helper.async_sonos_snapshot(hass)

    # Set (immediately) media_players' target volume_level for Chime TTS announcement
    await media_player_helper.async_set_volume_for_media_players(
        hass=hass,
        media_players=media_player_helper.get_set_volume_media_players(),
        volume_key="target_volume_level",
        fade_duration=0
    )

    # Join media players
    await media_player_helper.async_join_media_players(hass)

    # Prepare service call data
    service_data = {}
    service_data[CONF_ENTITY_ID] = entity_ids
    service_data[ATTR_MEDIA_ANNOUNCE] = announce
    service_data[ATTR_MEDIA_CONTENT_TYPE] = MEDIA_TYPE.MUSIC
    file_path = audio_dict.get(LOCAL_PATH_KEY, None) or audio_dict.get(PUBLIC_PATH_KEY, None)
    service_data[ATTR_MEDIA_CONTENT_ID] = media_player_helper.get_media_content_id(hass, file_path)

    # Play Chime TTS notification
    media_service_calls = await  async_prepare_media_service_calls(hass, entity_ids, service_data, audio_dict)
    play_result = await async_fire_media_service_calls(hass, media_service_calls)
    if play_result is False:
        _LOGGER.error("Playback failed")

    return play_result

async def async_prepare_media_service_calls(hass: HomeAssistant, entity_ids, service_data, audio_dict):
    """Prepare the media_player service calls for audio playback."""
    helpers.debug_subtitle("Chime TTS playback")
    service_calls = []

    # List/s of media players by platform/joined group
    joined_media_player_entity_id: str = media_player_helper.joined_entity_id
    standard_media_player_entity_ids: list[str] = [entity_id for entity_id in entity_ids if media_player_helper.get_is_standard_media_player(entity_id)]
    alexa_media_player_entity_ids: list[str] = media_player_helper.get_media_players_of_platform(entity_ids, ALEXA_MEDIA_PLAYER_PLATFORM)
    sonos_media_player_entity_ids: list[str] = media_player_helper.get_media_players_of_platform(entity_ids, SONOS_PLATFORM)

    # Remove speaker group media_players from the media_player lists
    if joined_media_player_entity_id and len(joined_media_player_entity_id) > 0:
        joined_media_player_entity_ids = media_player_helper.joined_media_player_entity_ids
        for array in [standard_media_player_entity_ids, alexa_media_player_entity_ids, sonos_media_player_entity_ids]:
            for media_player_n in joined_media_player_entity_ids:
                while media_player_n in array:
                    array.remove(media_player_n)
        # Make sure the speaker group leader is in the appropriate media player list
        if joined_media_player_entity_id not in (standard_media_player_entity_ids + alexa_media_player_entity_ids + sonos_media_player_entity_ids):
            if media_player_helper.get_media_player_platform(hass, joined_media_player_entity_id) == ALEXA_MEDIA_PLAYER_PLATFORM:
                alexa_media_player_entity_ids.append(joined_media_player_entity_id)
            elif media_player_helper.get_media_player_platform(hass, joined_media_player_entity_id) == SONOS_PLATFORM:
                sonos_media_player_entity_ids.append(joined_media_player_entity_id)
            else:
                standard_media_player_entity_ids.append(joined_media_player_entity_id)

    # Standard media_players
    if len(standard_media_player_entity_ids) > 0:
        standard_service_data = service_data.copy()
        if standard_service_data[ATTR_MEDIA_CONTENT_ID] is None:
            _LOGGER.warning("Error calling `media_player.play_media` service: No media content id found")
        else:
            _LOGGER.debug(
                "   %s Regular media player%s detected:",
                len(standard_media_player_entity_ids),
                ("s" if len(standard_media_player_entity_ids) != 1 else ""))
            for entity_id in standard_media_player_entity_ids:
                _LOGGER.debug("     - %s", entity_id)
            standard_service_data[CONF_ENTITY_ID] = standard_media_player_entity_ids
            service_calls.append({
                "domain": "media_player",
                "service": SERVICE_PLAY_MEDIA,
                "service_data": standard_service_data,
                "blocking": True,
                "result": True
            })

    # Sonos media_players
    if len(sonos_media_player_entity_ids) > 0:
        sonos_service_data = service_data.copy()
        if sonos_service_data[ATTR_MEDIA_CONTENT_ID] is None:
            _LOGGER.warning("Error calling `media_player.play_media` service: No media content id found")
        else:
            _LOGGER.debug(
                "   %s Sonos media player%s detected:",
                len(sonos_media_player_entity_ids),
                ("s" if len(sonos_media_player_entity_ids) != 1 else ""))
            for entity_id in sonos_media_player_entity_ids:
                _LOGGER.debug("     - %s", entity_id)

            # If all media_players have same target volume level
            uniform_target_volume = int(media_player_helper.get_uniform_target_volume_level(sonos_media_player_entity_ids) * 100)
            if uniform_target_volume != -1:
                sonos_service_data[CONF_ENTITY_ID] = sonos_media_player_entity_ids
                if uniform_target_volume >= 0:
                    sonos_service_data["extra"] = {"volume": uniform_target_volume}
                service_calls.append({
                    "domain": "media_player",
                    "service": SERVICE_PLAY_MEDIA,
                    "service_data": sonos_service_data,
                    "blocking": True,
                    "result": True
                })
            else:
                # Else 1 media_player.play_media service call per Sonos media_player, with the media_player's target volume level
                for media_player in media_player_helper.get_media_players_from_entity_ids(sonos_media_player_entity_ids):
                    volume = int(media_player.target_volume_level * 100)
                    individual_service_data = sonos_service_data.copy()
                    individual_service_data[CONF_ENTITY_ID] = media_player.entity_id
                    if volume >= 0:
                        individual_service_data["extra"] = {"volume": volume}
                    service_calls.append({
                        "domain": "media_player",
                        "service": SERVICE_PLAY_MEDIA,
                        "service_data": individual_service_data,
                        "blocking": True,
                        "result": True
                    })

    # Alexa media_players
    public_file = f"{audio_dict.get(PUBLIC_PATH_KEY, '')}"
    if len(alexa_media_player_entity_ids) > 0 and public_file:
        # Debug
        _LOGGER.debug("   %s Alexa media player%s detected:",
                      len(alexa_media_player_entity_ids),
                      ("s" if len(alexa_media_player_entity_ids) != 1 else ""))
        for entity_id in alexa_media_player_entity_ids:
            _LOGGER.debug("     - %s", entity_id)

        # Ensure audio file is Alexa Media Player compatible
        if not await filesystem_helper.async_is_audio_alexa_compatible(hass=hass, file_path=public_file):
            public_file = await helpers.async_ffmpeg_convert_from_file(hass, public_file, FFMPEG_ARGS_ALEXA)

        # Add service call
        if len(public_file) > 0:
            message_string = f"<audio src='{public_file}'/>"
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
            return False

    return True

async def async_post_playback_actions(hass: HomeAssistant,
                                      audio_duration: float,
                                      final_delay: float,
                                      media_players_array: list[ChimeTTSMediaPlayer]):
    """Run post playback actions."""
    # Wait the audio playback duration
    total_delay_s = round(audio_duration + ((final_delay/1000) if final_delay > 0 else 0),3)
    _LOGGER.debug(" - Waiting %ss for audio playback to complete...", str(total_delay_s))
    await hass.async_add_executor_job(time.sleep, total_delay_s)

    # Wait for playback to end on all media_players
    playing_media_players: list[ChimeTTSMediaPlayer] = []
    for media_player in media_players_array:
        if not(media_player_helper.announce and (media_player.platform == SPOTIFY_PLATFORM or media_player.platform == SONOS_PLATFORM)):
            playing_media_players.append(media_player)
    if not await media_player_helper.async_wait_until_media_players_state_not(hass, playing_media_players, "playing"):
        _LOGGER.debug(" - Timed out waiting for playback to complete")

    fade_in_media_players: list[ChimeTTSMediaPlayer] = media_player_helper.get_fade_in_out_media_players()
    set_volume_media_players: list[ChimeTTSMediaPlayer] = media_player_helper.get_set_volume_media_players()

    # Write to log if post-playback actions are to be performed
    if (len(fade_in_media_players) > 0
        or len(set_volume_media_players) > 0
        or (media_player_helper.unjoin_players is True and media_player_helper.joined_entity_id)):
        helpers.debug_subtitle("Post-Playback Actions")

    # Resume previous playback
    await media_player_helper.async_resume_playback(
        hass,
        _data[FADE_TRANSITION_KEY])

    # Reset volume
    await media_player_helper.async_set_volume_for_media_players(
        hass=hass,
        media_players=set_volume_media_players,
        volume_key="initial_volume_level",
        fade_duration=0)

    # Unjoin entity_ids
    await media_player_helper.async_unjoin_media_players(hass)

    # Restore from Sonos snapshot
    await media_player_helper.async_sonos_restore(hass)

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
    if (_data is None
        or not isinstance(_data, dict)
        or key is None
        or len(key) == 0):
        return None
    cached_data = _data.get(DATA_STORAGE_KEY, None)
    if cached_data:
        return cached_data.get(key, None)
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
            is_public = await filesystem_helper.async_file_exists_in_directory(path, '/www')
            audio_dict = {
                LOCAL_PATH_KEY: None if is_public else path,
                PUBLIC_PATH_KEY: path if is_public else None,
                AUDIO_DURATION_KEY: duration
            }

        # Validate paths and add duration if missing
        for key in [LOCAL_PATH_KEY, PUBLIC_PATH_KEY]:
            audio_dict[key] = audio_dict.get(key, None)
            if audio_dict.get(key, None):
                if await hass.async_add_executor_job(filesystem_helper.path_exists, str(audio_dict.get(key, ""))):
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
            if clear_chimes_cache and await filesystem_helper.async_file_exists_in_directory(value, temp_chimes_path):
                _LOGGER.debug("...removing chime file %s", value)
                filesystem_helper.delete_file(hass, audio_dict.get(LOCAL_PATH_KEY, None))
                audio_dict[LOCAL_PATH_KEY] = None
            elif clear_temp_tts_cache and await filesystem_helper.async_file_exists_in_directory(value, temp_path):
                _LOGGER.debug("...removing TTS file %s", value)
                filesystem_helper.delete_file(hass, audio_dict.get(LOCAL_PATH_KEY, None))
                audio_dict[LOCAL_PATH_KEY] = None
        elif key == PUBLIC_PATH_KEY and value is not None and clear_www_tts_cache:
            _LOGGER.debug("...removing public file %s", value)
            filesystem_helper.delete_file(hass, audio_dict.get(PUBLIC_PATH_KEY, None))
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
        if not audio_cache_dict:
            audio_cache_dict = {}
        local_audio_path = filesystem_helper.get_local_path(hass=hass, file_path=audio_path)
        if local_audio_path.startswith((_data[WWW_PATH_KEY], "http")):
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
        "crossfade",
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
