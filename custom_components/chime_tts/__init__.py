"""The Chime TTS integration."""

import logging
import os
import io
from datetime import datetime

from pydub import AudioSegment

from homeassistant.components.media_player.const import (
    ATTR_MEDIA_CONTENT_ID,
    ATTR_MEDIA_CONTENT_TYPE,
    ATTR_MEDIA_ANNOUNCE,
    ATTR_MEDIA_VOLUME_LEVEL,
    ATTR_GROUP_MEMBERS,
    SERVICE_PLAY_MEDIA,
    SERVICE_JOIN,
    SERVICE_UNJOIN,
    MEDIA_TYPE_MUSIC,
)
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

from .config_flow import ChimeTTSOptionsFlowHandler
from .helpers import ChimeTTSHelper
from .queue_manager import ChimeTTSQueueManager

from .const import (
    DOMAIN,
    SERVICE_SAY,
    SERVICE_SAY_URL,
    SERVICE_CLEAR_CACHE,
    VERSION,
    DATA_STORAGE_KEY,
    AUDIO_PATH_KEY,
    LOCAL_PATH_KEY,
    PUBLIC_PATH_KEY,
    AUDIO_DURATION_KEY,
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
queue = ChimeTTSQueueManager()


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up an entry."""
    await async_refresh_stored_data(hass)
    update_configuration(config_entry, hass)
    queue.set_timeout(_data[QUEUE_TIMEOUT_KEY])

    config_entry.async_on_unload(config_entry.add_update_listener(async_reload_entry))
    return True


async def async_setup(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up the Chime TTS integration."""
    _LOGGER.info("The Chime TTS integration is set up.")

    ###############
    # Say Service #
    ###############

    async def async_say(service, is_say_url = False):
        if is_say_url is False:
            _LOGGER.debug("----- Chime TTS Say Called. Version %s -----", VERSION)

        # Add service calls to the queue with arguments
        result = await queue.add_to_queue(async_say_execute,service)

        if result is not False:
            return result

        # Service call failed
        return {}


    async def async_say_execute(service):
        """Play TTS audio with local chime MP3 audio."""
        start_time = datetime.now()

        # Parse service parameters & TTS options
        params = await helpers.async_parse_params(service.data, hass)
        options = helpers.parse_options_yaml(service.data)

        media_players_array = params["media_players_array"]

        # Create audio file to play on media player
        local_path = None
        public_path = None
        audio_duration = 0
        audio_dict = await async_get_playback_audio_path(params, options)
        if audio_dict is not None:
            local_path = audio_dict[LOCAL_PATH_KEY] if LOCAL_PATH_KEY in audio_dict else None
            public_path = helpers.create_url_to_public_file(hass, audio_dict[PUBLIC_PATH_KEY]) if PUBLIC_PATH_KEY in audio_dict else None
            audio_duration = audio_dict[AUDIO_DURATION_KEY] if AUDIO_DURATION_KEY in audio_dict else 0

            # Play audio with service_data
            if media_players_array is not False and (public_path is not None or local_path is not None):
                play_result = await async_play_media(
                    hass,
                    audio_dict,
                    params["entity_ids"],
                    params["announce"],
                    params["force_announce"],
                    params["join_players"],
                    media_players_array,
                    params["volume_level"],
                )
                if play_result is True:
                    await async_post_playback_actions(
                        hass,
                        audio_duration,
                        params["final_delay"],
                        media_players_array,
                        params["volume_level"],
                        params["unjoin_players"],
                    )

            # Remove temporary local generated mp3
            if params["cache"] is False and local_path is not None:
                helpers.delete_file(local_path)

        end_time = datetime.now()
        elapsed_time = (end_time - start_time).total_seconds() * 1000

        # Convert public file path to external URL for chime_tts.say_url
        if public_path is not None and audio_duration:
            _LOGGER.debug("Final URL = %s", public_path)
            _LOGGER.debug("----- Chime TTS Say URL Completed in %s ms -----", str(elapsed_time))
            return {
                "url": public_path,
                "duration": audio_duration,
                "success": True
            }

        _LOGGER.debug("----- Chime TTS Say Completed in %s ms -----", str(elapsed_time))


    hass.services.async_register(DOMAIN, SERVICE_SAY, async_say)

    ###################
    # Say URL Service #
    ###################

    async def async_say_url(service) -> ServiceResponse:
        """Create a public URL to an audio file generated with the `chime_tts.say` service."""
        _LOGGER.debug("----- Chime TTS Say URL Called. Version %s -----", VERSION)
        return await async_say(service, True)

    hass.services.async_register(DOMAIN,
                                 SERVICE_SAY_URL,
                                 async_say_url,
                                 supports_response=SupportsResponse.ONLY)

    #######################
    # Clear Cahce Service #
    #######################

    async def async_clear_cache(service):
        """Play TTS audio with local chime MP3 audio."""
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
        cached_dicts = dict(_data[DATA_STORAGE_KEY])
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

    hass.services.async_register(DOMAIN, SERVICE_CLEAR_CACHE, async_clear_cache)

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    return True


async def async_reload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Reload the Chime TTS config entry."""
    _LOGGER.debug("Reloading integration")
    await async_unload_entry(hass, config_entry)
    await async_setup_entry(hass, config_entry)
    await async_setup(hass, config_entry)


async def async_post_playback_actions(
    hass: HomeAssistant,
    audio_duration: float,
    final_delay: float,
    media_players_array: list,
    volume_level: float,
    unjoin_players: bool,
):
    """Run post playback actions."""
    # Wait the audio playback duration
    _LOGGER.debug("Waiting %ss for audio playback to complete...", str(audio_duration))
    await hass.async_add_executor_job(helpers.sleep, audio_duration)
    if final_delay > 0:
        final_delay_s = float(final_delay / 1000)
        _LOGGER.debug("Waiting %ss for final_delay to complete...", str(final_delay_s))
        await hass.async_add_executor_job(helpers.sleep, final_delay_s)

    # Ensure playback has ended
    playback_ended = True
    for media_player_dict in media_players_array:
        entity_id = media_player_dict["entity_id"]
        result = await helpers.async_wait_until_not_media_plater_state(hass, entity_id, "playing", 10) is True
        if result is False:
            playback_ended = False
    if playback_ended is False:
        _LOGGER.warning("Timed out waiting for playback to complete")

    # Resume previous playback
    for media_player_dict in media_players_array:
        if media_player_dict["resume_media_player"] is True:
            entity_id = media_player_dict["entity_id"]
            if await helpers.async_wait_until_media_player_state(hass, entity_id, "paused") is True:
                _LOGGER.debug("- Resuming playback on %s", entity_id)
                # Set volume to 0
                await hass.services.async_call(
                    domain="media_player",
                    service=SERVICE_VOLUME_SET,
                    service_data={
                        ATTR_MEDIA_VOLUME_LEVEL: 0,
                        CONF_ENTITY_ID: entity_id
                    },
                    blocking=True
                )
                # Resume audio
                duration = 10
                delay = 0.2
                while hass.states.get(entity_id).state != "playing" and duration > 0:
                    await hass.services.async_call(
                        domain="media_player",
                        service="media_play",
                        service_data={CONF_ENTITY_ID: entity_id},
                        blocking=True,
                    )
                    await hass.async_add_executor_job(helpers.sleep, delay)
                    duration = duration - delay

            if hass.states.get(entity_id).state != "playing":
                _LOGGER.warning(" - Failed to resume playback on %s", entity_id)

    # Reset volume
    for media_player_dict in media_players_array:
        entity_id = media_player_dict["entity_id"]
        should_change_volume = bool(media_player_dict["should_change_volume"])
        should_fade_in = media_player_dict["resume_media_player"]
        initial_volume_level = media_player_dict["initial_volume_level"]
        if should_change_volume and initial_volume_level >= 0:
            await async_set_volume_level(
                hass,
                entity_id,
                initial_volume_level,
                (0 if should_fade_in else volume_level),
                (1.5 if should_fade_in else 0)
            )

    # Unjoin entity_ids
    if (
        unjoin_players is True
        and "joint_media_player_entity_id" in _data
        and _data["joint_media_player_entity_id"] is not None
    ):
        _LOGGER.debug(" - Calling media_player.unjoin service...")
        for media_player_dict in media_players_array:
            if media_player_dict["group_members_supported"] is True:
                entity_id = media_player_dict["entity_id"]
                _LOGGER.debug("   - media_player.unjoin: %s", entity_id)
                try:
                    await hass.services.async_call(
                        domain="media_player",
                        service=SERVICE_UNJOIN,
                        service_data={CONF_ENTITY_ID: entity_id},
                        blocking=True,
                    )
                    _LOGGER.debug("   ...done")
                except Exception as error:
                    _LOGGER.warning(
                        " - Error calling unjoin service for %s: %s", entity_id, error
                    )

async def async_join_media_players(hass, entity_ids):
    """Join media players."""
    _LOGGER.debug(
        " - Calling media_player.join service for %s media_player entities...",
        len(entity_ids),
    )

    supported_entity_ids = []
    for entity_id in entity_ids:
        entity = hass.states.get(entity_id)
        if helpers.get_supported_feature(entity, ATTR_GROUP_MEMBERS):
            supported_entity_ids.append(entity_id)

    if len(supported_entity_ids) > 1:
        _LOGGER.debug(
            " - Joining %s media_player entities...", str(len(supported_entity_ids))
        )
        try:
            _data["joint_media_player_entity_id"] = supported_entity_ids[0]
            await hass.services.async_call(
                domain="media_player",
                service=SERVICE_JOIN,
                service_data={
                    CONF_ENTITY_ID: _data["joint_media_player_entity_id"],
                    ATTR_GROUP_MEMBERS: supported_entity_ids,
                },
                blocking=True,
            )
            _LOGGER.debug("   ...done")
            return _data["joint_media_player_entity_id"]
        except Exception as error:
            _LOGGER.warning("   - Error joining media_player entities: %s", error)
    else:
        _LOGGER.warning(" - Only 1 media_player entity provided. Unable to join.")

    return False


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
    tts_playback_speed: float = 0.0,
):
    """Send an API request for TTS audio and return the audio file's local filepath."""

    start_time = datetime.now()

    # Data validation

    tts_options = options.copy() if isinstance(options, dict) else (str(options) if isinstance(options, str) else options)

    if message is False or message == "":
        _LOGGER.warning("No message text provided for TTS audio")
        return None

    if tts_platform is False or tts_platform == "":
        _LOGGER.warning("No TTS platform selected")
        return None
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
        if tts_platform is IBM_WATSON_TTS:
            tts_options["voice"] = language
    else:
        language = None

    # Cache
    use_cache = True if cache is True and tts_platform not in [GOOGLE_TRANSLATE, NABU_CASA_CLOUD_TTS] else False

    # tld
    if "tld" in tts_options and tts_platform not in [GOOGLE_TRANSLATE]:
        del tts_options["tld"]

    # Gender
    if "gender" in tts_options and tts_platform not in [NABU_CASA_CLOUD_TTS]:
        del tts_options["gender"]


    # Debug log
    _LOGGER.debug(" - Generating new TTS audio with parameters:")
    for key, value in {
        "tts_platform":  f"'{tts_platform}'",
        "message":  f"'{message}'",
        "tts_playback_speed":  str(tts_playback_speed),
        "cache":  str(use_cache),
        "language":  f"'{str(language) if language is not None else 'None'}'",
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
        _LOGGER.error(" - Error: Unable to generate media_source_id")
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
                _LOGGER.error(" - ...could not convert TTS bytes to audio")
                return None
            audio = AudioSegment.from_file(file)
            if audio is not None:
                if tts_playback_speed != 100:
                    _LOGGER.debug(
                        " -  ...changing TTS playback speed to %s percent",
                        str(tts_playback_speed),
                    )
                    playback_speed = float(tts_playback_speed / 100)
                    if tts_playback_speed > 150:
                        audio = audio.speedup(
                            playback_speed=playback_speed, chunk_size=50
                        )
                    else:
                        audio = audio.speedup(playback_speed=playback_speed)
                end_time = datetime.now()
                _LOGGER.debug(
                    "   ...TTS audio completed in %s ms",
                    str((end_time - start_time).total_seconds() * 1000),
                )
                return audio
            _LOGGER.error(" - ...could not extract TTS audio from file")
        else:
            _LOGGER.error(" - ...audio_data did not contain audio bytes")
    else:
        _LOGGER.error(" - ...audio_data generation failed")
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

    hass = params["hass"]
    chime_path = params["chime_path"]
    end_chime_path = params["end_chime_path"]
    offset = params["offset"]
    message = params["message"]
    cache = params["cache"]
    entity_ids = params["entity_ids"]
    ffmpeg_args = params["ffmpeg_args"]

    # Produce local and/or public mp3s?
    alexa_media_player_count = helpers.get_alexa_media_player_count(hass, entity_ids)

    is_public = alexa_media_player_count > 0 or (entity_ids is None or len(entity_ids) == 0)
    is_local = entity_ids is not None and len(entity_ids) > 0 and alexa_media_player_count != len(entity_ids)

    filepath_hash = get_filename_hash_from_service_data({**params}, {**options})
    _data["generated_filename"] = filepath_hash

    # Load previously generated audio from cache
    if cache is True:
        _LOGGER.debug(" - Attempting to retrieve previously cached audio...")
        audio_dict = await async_get_cached_audio_data(hass, filepath_hash)
        if audio_dict is not None and AUDIO_DURATION_KEY in audio_dict:
            duration = audio_dict[AUDIO_DURATION_KEY]

            # Make a local copy of the public file
            if is_local and audio_dict[LOCAL_PATH_KEY] is None and audio_dict[PUBLIC_PATH_KEY] is not None:
                _LOGGER.debug("   - Copying public file to local directory")
                audio_dict[LOCAL_PATH_KEY] = helpers.copy_file(audio_dict[PUBLIC_PATH_KEY], _data[TEMP_PATH_KEY])
                await add_audio_file_to_cache(hass, audio_dict[LOCAL_PATH_KEY], duration, params, options)
            else:
                audio_dict[LOCAL_PATH_KEY] = None

            # Make a public copy of the local file
            if is_public and audio_dict[PUBLIC_PATH_KEY] is None and audio_dict[LOCAL_PATH_KEY] is not None:
                _LOGGER.debug("    - Copying local file to public directory")
                audio_dict[PUBLIC_PATH_KEY] = helpers.copy_file(audio_dict[LOCAL_PATH_KEY], _data[WWW_PATH_KEY])
                await add_audio_file_to_cache(hass, audio_dict[PUBLIC_PATH_KEY], duration, params, options)
            else:
                audio_dict[PUBLIC_PATH_KEY] = None

            if (is_local is False or audio_dict[LOCAL_PATH_KEY] is not None) and (is_public is False or audio_dict[PUBLIC_PATH_KEY] is not None):
                _LOGGER.debug("   ...cached audio retrieved: %s", str(audio_dict))
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
        "public_path": None,
        "local_path": None
    }
    if output_audio is not None:
        initial_save_folder_key = TEMP_PATH_KEY if is_local else WWW_PATH_KEY
        _LOGGER.debug(" - Saving mp3 file to folder: %s...", _data[initial_save_folder_key])
        new_audio_file = helpers.save_audio_to_folder(output_audio, _data[initial_save_folder_key])
        if new_audio_file is None:
            _LOGGER.debug("   ...error saving file")
            return None
        duration = float(len(output_audio) / 1000.0)
        audio_dict[AUDIO_DURATION_KEY] = duration

        audio_dict[LOCAL_PATH_KEY if is_local else PUBLIC_PATH_KEY] = new_audio_file

        # Perform FFmpeg conversion
        if ffmpeg_args:
            _LOGGER.debug("  - Performing FFmpeg audio conversion...")
            converted_audio_file = helpers.ffmpeg_convert_from_file(new_audio_file,
                                                                    ffmpeg_args)
            if converted_audio_file is not False:
                _LOGGER.debug("    ...FFmpeg audio conversion completed.")
                new_audio_file = converted_audio_file
            else:
                _LOGGER.warning("    ...FFmpeg audio conversion failed. Using unconverted audio file")

        # Save local and/or public mp3s and update cache
        for location in [
            {
                "enabled": is_public,
                "dest_folder_key": WWW_PATH_KEY,
                "origin_folder_key": TEMP_PATH_KEY,
                "location_key": PUBLIC_PATH_KEY
            },
            {
                "enabled": is_local,
                "dest_folder_key": TEMP_PATH_KEY,
                "origin_folder_key": WWW_PATH_KEY,
                "location_key": LOCAL_PATH_KEY
            }
        ]:
            if location["enabled"] is True and initial_save_folder_key is location["origin_folder_key"]:
                new_path = new_audio_file.replace(_data[location["origin_folder_key"]], _data[location["dest_folder_key"]])
                _LOGGER.debug(" - Saving mp3 file to folder: %s", _data[location["dest_folder_key"]])
                audio_dict[location["location_key"]] = helpers.copy_file(new_path, _data[location["dest_folder_key"]])
            if audio_dict[location["location_key"]] is not None and cache is True:
                await add_audio_file_to_cache(hass, audio_dict[location["location_key"]], duration, params, options)

    # Valdiation
    if audio_dict[AUDIO_DURATION_KEY] == 0:
        _LOGGER.error("async_get_playback_audio_path --> Audio has no duration")
        audio_dict = None
    if audio_dict[LOCAL_PATH_KEY] is None and audio_dict[PUBLIC_PATH_KEY] is None:
        _LOGGER.error(
            "async_get_playback_audio_path --> No audio file generated"
        )
        audio_dict = None

    return audio_dict


def get_segment_offset(output_audio, segment, params):
    """Offset value for segment."""
    segment_offset = 0
    if output_audio is not None:
        # Get "offset" parameter
        if "offset" in segment:
            segment_offset = segment["offset"]

        # Support deprecated "delay" parmeter
        else:
            if "delay" in segment:
                segment_offset = segment["delay"]
            elif "delay" in params:
                segment_offset = params["delay"]
            elif "offset" in params:
                segment_offset = params["offset"]

    return segment_offset


async def async_process_segments(hass, message, output_audio, params, options):
    """Process all message segments and add the audio."""
    segments = helpers.parse_message(message)
    if segments is None or len(segments) == 0:
        return output_audio

    for index, segment in enumerate(segments):
        segment_cache = segment["cache"] if "cache" in segment else params["cache"]
        segment_audio_conversion = segment["audio_conversion"] if "audio_conversion" in segment else None
        segment_offset = get_segment_offset(output_audio, segment, params)

        # Chime tag
        if segment["type"] == "chime":
            if "path" in segment:
                output_audio = await async_get_audio_from_path(hass=hass,
                                                               filepath=segment["path"],
                                                               cache=segment_cache,
                                                               offset=segment_offset,
                                                               audio=output_audio)
            else:
                _LOGGER.warning("Chime path missing from messsage segment #%s", str(index+1))

        # Delay tag
        if segment["type"] == "delay":
            if "length" in segment:
                segment_delay_length = float(segment["length"])
                output_audio = output_audio + AudioSegment.silent(duration=segment_delay_length)
            else:
                _LOGGER.warning("Delay length missing from messsage segment #%s", str(index+1))

        # Request TTS audio file
        if segment["type"] == "tts":
            if "message" in segment and len(segment["message"]) > 0:
                segment_message = segment["message"]
                if len(segment_message) == 0 or segment_message == "None":
                    continue

                segment_tts_platform = segment["tts_platform"] if "tts_platform" in segment else params["tts_platform"]
                segment_language = segment["language"] if "language" in segment else params["language"]
                segment_tts_playback_speed = segment["tts_playback_speed"] if "tts_playback_speed" in segment else params["tts_playback_speed"]

                # Use exposed parameters if not present in the options dictionary
                segment_options = segment["options"] if "options" in segment else {}
                exposed_option_keys = ["gender", "tld", "voice"]
                for exposed_option_key in exposed_option_keys:
                    value = None
                    if exposed_option_key in segment_options:
                        value = segment_options[exposed_option_key]
                    elif exposed_option_key in segment:
                        value = segment[exposed_option_key]
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
                    "tts_playback_speed": segment_tts_playback_speed
                }
                segment_filepath_hash = get_filename_hash_from_service_data({**segment_params}, {**segment_options})

                tts_audio = None

                # Use cached TTS audio
                if segment_cache is True:
                    _LOGGER.debug(" - Attempting to retrieve TTS audio from cache...")
                    audio_dict = await async_get_cached_audio_data(hass, segment_filepath_hash)
                    if audio_dict is not None:
                        tts_audio = await async_get_audio_from_path(hass=hass,
                                                                    filepath=audio_dict[LOCAL_PATH_KEY],
                                                                    cache=segment_cache,
                                                                    audio=None)

                        tts_audio_duration = audio_dict[AUDIO_DURATION_KEY]
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
                        options=segment_options,
                        tts_playback_speed=segment_tts_playback_speed,
                    )


                # Combine audio
                if tts_audio is not None:
                    tts_audio_duration = float(len(tts_audio) / 1000.0)
                    output_audio = helpers.combine_audio(output_audio, tts_audio, segment_offset)

                    # Cache the new TTS audio?
                    if segment_cache is True and audio_dict is None:
                        _LOGGER.debug(" - Saving generated TTS audio to cache...")
                        tts_audio_full_path = helpers.save_audio_to_folder(
                            tts_audio, _data[TEMP_PATH_KEY])
                        if tts_audio_full_path is not None:
                            audio_dict = {
                                LOCAL_PATH_KEY: tts_audio_full_path,
                                AUDIO_DURATION_KEY: tts_audio_duration
                            }
                            await async_store_data(hass, segment_filepath_hash, audio_dict)
                            _LOGGER.debug("  ...TTS audio saved to cache")

                        else:
                            _LOGGER.warning("Unable to save generated TTS audio to cache")

                else:
                    _LOGGER.warning("Error generating TTS audio from messsage segment #%s: %s",
                                    str(index+1), str(segment))
            else:
                _LOGGER.warning("TTS message missing from messsage segment #%s: %s",
                                str(index+1), str(segment))

        # Audio Conversion with FFmpeg
        if segment_audio_conversion is not None:
            _LOGGER.debug("Converting audio segment with FFmpeg...")
            temp_folder = _data[TEMP_PATH_KEY]
            output_audio = helpers.ffmpeg_convert_from_audio_segment(output_audio, segment_audio_conversion, temp_folder)

    return output_audio

async def async_get_audio_from_path(hass: HomeAssistant,
                                    filepath: str,
                                    cache=False,
                                    offset=0,
                                    audio=None):
    """Add audio from a given file path to existing audio (optional) with offset (optional)."""
    if filepath is None or filepath == "None" or len(filepath) == 0:
        return audio

    # Load/download audio file & validate local path
    # await async_refresh_stored_data(hass)
    filepath = await helpers.async_get_chime_path(
        chime_path=filepath,
        cache=cache,
        data=_data,
        hass=hass)

    if filepath is not None:
        _LOGGER.debug(' - Retrieving audio from path: "%s"...', filepath)
        try:
            audio_from_path = AudioSegment.from_file(filepath)
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
    return audio


async def async_set_volume_level_for_media_players(
    hass: HomeAssistant,
    media_players_array,
    volume_level: float,
    fade_duration_s: int = 0
):
    """Set the volume level for all media_players."""
    for media_player_dict in media_players_array:
        entity_id = media_player_dict["entity_id"]
        should_change_volume = bool(media_player_dict["should_change_volume"])
        initial_volume_level = media_player_dict["initial_volume_level"]
        if should_change_volume and volume_level >= 0:
            await async_set_volume_level(
                hass,
                entity_id,
                volume_level,
                initial_volume_level,
                fade_duration_s
            )


async def async_set_volume_level(
    hass: HomeAssistant,
    entity_id: str,
    target_volume_level:int = 0,
    current_volume_level:int = 0,
    fade_duration_s: float = 0
):
    """Set the volume_level for a given media player entity."""
    target_volume_level = max(float(target_volume_level), 0)
    current_volume_level = max(float(current_volume_level), 0)

    if target_volume_level >= 0 and target_volume_level != current_volume_level:
        _LOGGER.debug(
            " - Setting '%s' volume level to %s", entity_id, str(target_volume_level)
        )
        steps = 10 if fade_duration_s > 0 else 1
        volume_step = (target_volume_level - current_volume_level) / steps
        new_volume_level = target_volume_level
        while steps > 0:
            # Gradually change the volume (if specified)
            if fade_duration_s > 1:
                new_volume_level = max(current_volume_level + volume_step, 0)
                current_volume_level = new_volume_level
            try:
                await hass.services.async_call(
                    domain="media_player",
                    service=SERVICE_VOLUME_SET,
                    service_data={
                        ATTR_MEDIA_VOLUME_LEVEL: new_volume_level,
                        CONF_ENTITY_ID: entity_id
                    },
                    blocking=(steps==1),
                )
                if steps > 1 :
                    await hass.async_add_executor_job(helpers.sleep, fade_duration_s / steps)
                steps = steps - 1
            except Exception as error:
                _LOGGER.warning(" - Error setting volume for '%s': %s", entity_id, error)
        return True
    return False


async def async_play_media(
    hass: HomeAssistant,
    audio_dict,
    entity_ids,
    announce,
    force_announce,
    join_players,
    media_players_array,
    volume_level,
):
    """Call the media_player.play_media service."""
    service_data = {}

    # media content type
    service_data[ATTR_MEDIA_CONTENT_TYPE] = MEDIA_TYPE_MUSIC

    # media_content_id
    media_source_path = audio_dict[LOCAL_PATH_KEY] if LOCAL_PATH_KEY in audio_dict else (audio_dict[PUBLIC_PATH_KEY] if PUBLIC_PATH_KEY in audio_dict else None)
    media_folder = "/media/"
    media_folder_path_index = media_source_path.find(media_folder)
    if media_folder_path_index != -1:
        media_path = media_source_path[media_folder_path_index + len(media_folder) :].replace("//", "/")
        media_source_path = "media-source://media_source/<media_dir>/<media_path>".replace(
            "<media_dir>", _data[MEDIA_DIR_KEY]
        ).replace(
            "<media_path>", media_path)
    service_data[ATTR_MEDIA_CONTENT_ID] = media_source_path

    # announce
    if announce is True:
        service_data[ATTR_MEDIA_ANNOUNCE] = announce

    # entity_id
    service_data[CONF_ENTITY_ID] = entity_ids
    if join_players is True:
        # join entity_ids as a group
        group_members_suppored = helpers.get_group_members_suppored(media_players_array)
        if group_members_suppored > 1:
            joint_speakers_entity_id = await async_join_media_players(hass, entity_ids)
            if joint_speakers_entity_id is not False:
                service_data[CONF_ENTITY_ID] = joint_speakers_entity_id
            else:
                _LOGGER.warning(
                    "Unable to join speakers. Only 1 media_player supported."
                )
        else:
            if group_members_suppored == 1:
                _LOGGER.warning(
                    "Unable to join speakers. Only 1 media_player supported."
                )
            else:
                _LOGGER.warning(
                    "Unable to join speakers. No supported media_players found."
                )

    # Pause media if media_player's platform does not support `announce`
    for media_player_dict in media_players_array:
        entity_id = media_player_dict["entity_id"]
        if announce and helpers.get_supported_feature(hass.states.get(entity_id), ATTR_MEDIA_ANNOUNCE) is False:
            media_player_dict["resume_media_player"] = hass.states.get(entity_id).state == "playing"
            if hass.states.get(entity_id).state == "playing":

                # Fade out
                _LOGGER.debug(" - Fading out playback on %s...", entity_id)
                initial_volume_level = media_player_dict["initial_volume_level"]
                if await async_set_volume_level(
                    hass, entity_id, 0, initial_volume_level, 1.5
                ):
                    # Wait until volume level updated
                    await helpers.async_wait_until_media_player_volume_level(hass, entity_id, 0)

                # Pause
                _LOGGER.debug(" - Pausing playback on %s...", entity_id)
                await hass.services.async_call(
                    domain="media_player",
                    service="media_pause",
                    service_data={CONF_ENTITY_ID: entity_id},
                    blocking=True
                )
                await helpers.async_wait_until_media_player_state(hass, entity_id, "paused")


    # Set volume to desired level
    await async_set_volume_level_for_media_players(
        hass, media_players_array, volume_level
    )

    # Play the audio (For Alexa media_players call notify.alexa_media, and for non-Alexa media_players, call media_player.play_media)
    alexa_entity_ids = [entity_id for entity_id in entity_ids if helpers.get_media_player_platform(hass, entity_id) == "alexa"]
    non_alexa_entity_ids = [entity_id for entity_id in entity_ids if helpers.get_media_player_platform(hass, entity_id) != "alexa"]
    service_calls = []

    # Prepare service call for Alexa media_players
    if len(alexa_entity_ids) > 0:
        service_calls.append({
            "domain": "notify",
            "service": "alexa_media",
            "service_data": {
                "message": f"<audio src=\"{audio_dict['public_path']}\"/>",
                "data": {
                    "type": "tts"
                    },
                "target": alexa_entity_ids
            },
            "result": False
        })
    # Prepare service call for regular media_players
    if len(non_alexa_entity_ids) > 0:
        service_data[CONF_ENTITY_ID] = non_alexa_entity_ids
        service_calls.append({
            "domain": "media_player",
            "service": SERVICE_PLAY_MEDIA,
            "service_data": service_data,
            "blocking": True,
            "result": False
        })

    # Fire service calls
    retry_count = 3
    for service_call in service_calls:
        for i in range(retry_count):
            if service_call["result"]:
                break
            if i == 0:
                _LOGGER.debug("Calling %s.%s with data:",
                            service_call["domain"],
                            service_call["service"])
                for key, value in service_call["service_data"].items():
                    _LOGGER.debug(" - %s: %s", str(key), str(value))
            else:
                _LOGGER.warning("...playback retry %s/%s", str(i+1), str(retry_count))

            try:
                await hass.services.async_call(
                    domain=service_call["domain"],
                    service=service_call["service"],
                    service_data=service_call["service_data"]
                )
                service_call["result"] = True
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

    for service_call in service_calls:
        if service_call["result"]:
            return True

    _LOGGER.error("Playback failed")
    return False


################################
### Storage Helper Functions ###
################################

async def async_refresh_stored_data(hass: HomeAssistant):
    """Refresh the stored data of the integration."""
    store = storage.Store(hass, 1, DATA_STORAGE_KEY)
    _data[DATA_STORAGE_KEY] = await store.async_load()
    if _data[DATA_STORAGE_KEY] is None:
        _data[DATA_STORAGE_KEY] = {}


async def async_store_data(hass: HomeAssistant, key: str, value: str):
    """Store a key/value pair in the integration's stored data."""
    if hass is not None and key is not None and value is not None:
        _LOGGER.debug(" - Saving data to chime_tts storage:")
        _LOGGER.debug('   - key:   "%s"', key)
        _LOGGER.debug('   - value: "%s"', value)
        _data[DATA_STORAGE_KEY][key] = value
        await async_save_data(hass)


async def async_retrieve_data(hass: HomeAssistant, key: str):
    """Retrieve a value from the integration's stored data based on the provided key."""
    await async_refresh_stored_data(hass)
    if key in _data[DATA_STORAGE_KEY]:
        return _data[DATA_STORAGE_KEY][key]
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
        # Backwards compatibility
        path = None
        duration = None
        # Support previous cache format of path stings
        if type(audio_dict) == "string":
            path = audio_dict
        # Support previous cache format of AUDIO_PATH_KEY dictionary key values
        elif AUDIO_PATH_KEY in audio_dict:
            path = audio_dict[AUDIO_PATH_KEY]
            if AUDIO_DURATION_KEY in audio_dict:
                duration = audio_dict[AUDIO_DURATION_KEY]
        if path is not None:
            is_public = helpers.file_exists_in_directory(path, '/www')
            audio_dict = {
                LOCAL_PATH_KEY: path if is_public else None,
                PUBLIC_PATH_KEY: path if is_public else None,
                AUDIO_DURATION_KEY: duration
            }

        # Validate paths and add duration if missing
        has_valid_path = False
        for key in [LOCAL_PATH_KEY, PUBLIC_PATH_KEY]:
            if key in audio_dict:
                if os.path.exists(str(audio_dict[key])):
                    has_valid_path = True
                    # Add duration data if audio_dict is old format
                    if AUDIO_DURATION_KEY not in audio_dict or audio_dict[AUDIO_DURATION_KEY] is None:
                        audio = await async_get_audio_from_path(hass=hass,
                                                                filepath=audio_dict[key],
                                                                cache=True)
                        if audio is not None:
                            audio_dict[AUDIO_DURATION_KEY] = float(len(audio) / 1000.0)
                        else:
                            _LOGGER.warning("Could not load audio from file: %s", audio_dict[key])
            else:
                audio_dict[key] = None
        # await async_store_data(hass, filepath_hash, audio_dict)
        if has_valid_path:
            return audio_dict
    else:
        _LOGGER.debug(" - No cached audio found with hash %s", filepath_hash)

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
    temp_chimes_path = _data[TEMP_CHIMES_PATH_KEY]
    temp_path = _data[TEMP_PATH_KEY]
    # public_path = _data[WWW_PATH_KEY]

    for key, value in audio_dict.items():
        if key == LOCAL_PATH_KEY and audio_dict[LOCAL_PATH_KEY] is not None:
            if clear_chimes_cache and helpers.file_exists_in_directory(value, temp_chimes_path):
                _LOGGER.debug("...removing chime file %s", value)
                helpers.delete_file(audio_dict[LOCAL_PATH_KEY])
                audio_dict[LOCAL_PATH_KEY] = None
            elif clear_temp_tts_cache and helpers.file_exists_in_directory(value, temp_path):
                _LOGGER.debug("...removing TTS file %s", value)
                helpers.delete_file(audio_dict[LOCAL_PATH_KEY])
                audio_dict[LOCAL_PATH_KEY] = None
        elif key == PUBLIC_PATH_KEY and value is not None and clear_www_tts_cache:
            _LOGGER.debug("...removing public file %s", value)
            helpers.delete_file(audio_dict[PUBLIC_PATH_KEY])
            audio_dict[PUBLIC_PATH_KEY] = None

    # Remove key/value from integration storage if no paths remain
    if (LOCAL_PATH_KEY not in audio_dict or audio_dict[LOCAL_PATH_KEY] is None) and (PUBLIC_PATH_KEY not in audio_dict or audio_dict[PUBLIC_PATH_KEY] is None):
        await async_delete_data(hass, filepath_hash)


async def add_audio_file_to_cache(hass, audio_path, duration, params, options):
    """Add an audio path to the Chime TTS cache."""
    if hass is not None and audio_path is not None and duration is not None:
        filepath_hash = get_filename_hash_from_service_data({**params}, {**options})
        audio_cache_dict = await async_get_cached_audio_data(hass, filepath_hash)
        if audio_cache_dict is None:
            audio_cache_dict = {}
        if helpers.file_exists_in_directory(audio_path, _data[WWW_PATH_KEY]):
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
        "gender",
        "tld",
        "voice",
        "language",
        "chime_path",
        "end_chime_path",
        "offset",
        "tts_playback_speed",
    ]
    for param in relevant_params:
        for dictionary in [params, options]:
            if (
                param in dictionary
                and dictionary[param] is not None
                and len(str(dictionary[param])) > 0
            ):
                unique_string = unique_string + "-" + str(dictionary[param])

    hash_value = helpers.get_hash_for_string(unique_string)
    return hash_value



#######################
# Integration options #
#######################

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
        _data[ROOT_PATH_KEY] = hass.config.path("").replace("/config", "")

    if DEFAULT_TEMP_PATH_KEY not in _data:
        _data[DEFAULT_TEMP_PATH_KEY] = hass.config.path(TEMP_PATH_DEFAULT)

    if DEFAULT_TEMP_CHIMES_PATH_KEY not in _data:
        _data[DEFAULT_TEMP_CHIMES_PATH_KEY] = hass.config.path(TEMP_CHIMES_PATH_DEFAULT)

    if DEFAULT_WWW_PATH_KEY not in _data:
        _data[DEFAULT_WWW_PATH_KEY] = hass.config.path(WWW_PATH_DEFAULT)

    # Set configurable values
    options = config_entry.options

    # Queue timeout
    _data[QUEUE_TIMEOUT_KEY] = options.get(QUEUE_TIMEOUT_KEY, QUEUE_TIMEOUT_DEFAULT)

    # Media folder (default local)
    _data[MEDIA_DIR_KEY] = options.get(MEDIA_DIR_KEY, MEDIA_DIR_DEFAULT)

    # www / local folder path
    _data[WWW_PATH_KEY] = hass.config.path(
        options.get(WWW_PATH_KEY, WWW_PATH_DEFAULT)
    )
    _data[WWW_PATH_KEY] = (_data[WWW_PATH_KEY] + "/").replace("//", "/")

    # Temp chimes folder path
    _data[TEMP_CHIMES_PATH_KEY] = hass.config.path(
        options.get(TEMP_CHIMES_PATH_KEY, _data[DEFAULT_TEMP_CHIMES_PATH_KEY])
    )
    _data[TEMP_CHIMES_PATH_KEY] = (_data[TEMP_CHIMES_PATH_KEY] + "/").replace("//", "/")

    # Temp folder path
    _data[TEMP_PATH_KEY] = hass.config.path(
        options.get(TEMP_PATH_KEY, _data[DEFAULT_TEMP_PATH_KEY])
    )
    _data[TEMP_PATH_KEY] = (_data[TEMP_PATH_KEY] + "/").replace("//", "/")

    # Custom chime paths
    _data[MP3_PRESET_CUSTOM_KEY] = {}
    for i in range(5):
        key = MP3_PRESET_CUSTOM_PREFIX + str(i + 1)
        value = options.get(key, "")
        _data[MP3_PRESET_CUSTOM_KEY][key] = value

    # Debug summary
    for key_string in [
        QUEUE_TIMEOUT_KEY,
        TEMP_CHIMES_PATH_KEY,
        TEMP_PATH_KEY,
        WWW_PATH_KEY,
        MEDIA_DIR_KEY,
        MP3_PRESET_CUSTOM_KEY,
    ]:
        _LOGGER.debug("%s = %s", key_string, str(_data[key_string]))
