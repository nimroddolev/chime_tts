"""The Chime TTS integration."""

import logging
import tempfile
import time
import os
import hashlib
import io
import yaml

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
from homeassistant.const import (
    CONF_ENTITY_ID,
    SERVICE_VOLUME_SET,
    SERVICE_TURN_ON)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.core import State
from homeassistant.helpers import storage
from homeassistant.components import tts
from homeassistant.exceptions import (
    HomeAssistantError,
    ServiceNotFound,
    TemplateError,
)

from .const import (
    DOMAIN,
    SERVICE_SAY,
    SERVICE_CLEAR_CACHE,
    VERSION,
    PAUSE_DURATION_MS,
    DATA_STORAGE_KEY,
    AUDIO_PATH_KEY,
    AUDIO_DURATION_KEY,
    TEMP_PATH,
    MP3_PRESET_PATH,
    MP3_PRESET_PATH_PLACEHOLDER,
    QUEUE,
    QUEUE_STATUS,
    QUEUE_IDLE,
    QUEUE_RUNNING,
    QUEUE_CURRENT_ID,
    QUEUE_LAST_ID,
    QUEUE_TIMEOUT_S,
    # AMAZON_POLLY,
    # BAIDU,
    # GOOGLE_CLOUD,
    GOOGLE_TRANSLATE,
    IBM_WATSON_TTS,
    # MARYTTS,
    # MICROSOFT_TTS,
    NABU_CASA_CLOUD_TTS,
    NABU_CASA_CLOUD_TTS_OLD,
    # PICOTTS,
    # PIPER,
    # VOICE_RSS,
    # YANDEX_TTS,
)
_LOGGER = logging.getLogger(__name__)
_data = {}

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up an entry."""
    await async_init_stored_data(hass)
    init_queue()
    config_entry.async_on_unload(
        config_entry.add_update_listener(async_reload_entry))
    return True

async def async_setup(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up the Chime TTS integration."""
    _LOGGER.info("The Chime TTS integration is set up.")

    ###############
    # Say Service #
    ###############

    async def async_say(service):
        service_dict = queue_new_service_call(service)

        while _data[QUEUE_CURRENT_ID] < service_dict["id"]:
            # Wait for the previous service call to end
            if _data[QUEUE_STATUS] is QUEUE_RUNNING:
                # Wait until current job is completed
                previous_jobs_count = int(int(service_dict["id"]) - int(_data[QUEUE_CURRENT_ID]))
                _LOGGER.debug("...waiting for %s previous queued job%s to complete.",
                              "a" if previous_jobs_count == 1 else str(previous_jobs_count),
                              "s" if previous_jobs_count > 1 else "")
                retry_interval = 0.1
                timeout = QUEUE_TIMEOUT_S * 60 * 1000
                elapsed_time = 0
                while elapsed_time < timeout and _data[QUEUE_STATUS] is QUEUE_RUNNING:
                    await hass.async_add_executor_job(sleep, retry_interval)
                    elapsed_time += retry_interval
                    if _data[QUEUE_STATUS] is QUEUE_IDLE:
                        break
                # Status is still 'running' after timeout
                if _data[QUEUE_STATUS] is QUEUE_RUNNING:
                    _LOGGER.error("Timeout reached on queued job #%s.", str(service_dict["id"]))
                    dequeue_service_call()
                    break

            # Execute the next service call in the queue
            if _data[QUEUE_STATUS] is QUEUE_IDLE:
                next_service_dict = get_queued_service_call()
                if next_service_dict is not None:
                    next_service = next_service_dict["service"]
                    next_service_id = next_service_dict["id"]
                    _data[QUEUE_STATUS] = QUEUE_RUNNING
                    _LOGGER.debug("Executing queued job #%s", str(next_service_id))
                    result = await async_say_execute(next_service)
                    dequeue_service_call()
                    _data[QUEUE_STATUS] = QUEUE_IDLE
                    return result
                _LOGGER.error("Unable to get next queued service call.")
            else:
                _LOGGER.error("Unable to run queued service call.")

        # Remove failed service call from queue
        dequeue_service_call()
        return False

    async def async_say_execute(service):
        """Play TTS audio with local chime MP3 audio."""
        start_time = datetime.now()

        # Parse TTS service options YAML
        options = parse_options_yaml(service.data)

        # Parse entity_id/s
        entity_ids = parse_entity_ids(service.data, hass)
        chime_path = get_chime_path(str(service.data.get("chime_path", "")))
        end_chime_path = get_chime_path(str(service.data.get("end_chime_path", "")))
        delay = float(service.data.get("delay", PAUSE_DURATION_MS))
        final_delay = float(service.data.get("final_delay", 0))
        message = str(service.data.get("message", ""))
        tts_platform = str(service.data.get("tts_platform", ""))
        tts_playback_speed = float(service.data.get("tts_playback_speed", 100))
        volume_level = float(service.data.get(ATTR_MEDIA_VOLUME_LEVEL, -1))
        join_players = service.data.get("join_players", False)
        unjoin_players = service.data.get("unjoin_players", False)
        language = service.data.get("language", False)
        cache = service.data.get("cache", False)
        announce = service.data.get("announce", False)

        params = {
            "entity_ids": entity_ids,
            "hass": hass,
            "chime_path": chime_path,
            "end_chime_path": end_chime_path,
            "cache": cache,
            "delay": delay,
            "message": message,
            "language": language,
            "tts_platform": tts_platform,
            "tts_playback_speed": tts_playback_speed,
            "announce": announce,
            "volume_level": volume_level,
            "join_players": join_players,
            "unjoin_players": unjoin_players,
        }

        for params_list in [params, options]:
            if params_list is params:
                _LOGGER.debug("----- General Parameters -----")
            else:
                _LOGGER.debug("----- TTS-Specific Params -----")
            for key, value in params_list.items():
                if value is not None and len(str(value)) > 0:
                    _LOGGER.debug(' * %s = %s', key, str(value))
        _LOGGER.debug('-------------------------------')

        media_players_dict = await async_initialize_media_players(hass, entity_ids, volume_level)
        if media_players_dict is False:
            return False
        entity_ids = [media_player_dict['entity_id'] for media_player_dict in media_players_dict]
        params["entity_ids"] = entity_ids

        # Create audio file to play on media player
        audio_dict = await async_get_playback_audio_path(params, options)
        if validate_audio_dict(audio_dict) is False:
            return False
        _LOGGER.debug(" - audio_dict = %s", str(audio_dict))
        audio_path = audio_dict[AUDIO_PATH_KEY]
        audio_duration = audio_dict[AUDIO_DURATION_KEY]

        # Set volume to desired level
        await async_set_volume_level_for_media_players(hass, media_players_dict, volume_level)

        # Play audio with service_data
        await async_play_media(hass,
                               audio_path,
                               entity_ids,
                               announce,
                               join_players)

        # Delay by audio playback duration
        delay_duration = float(audio_duration)
        _LOGGER.debug("Waiting %ss for audio playback to complete...", str(delay_duration))
        await hass.async_add_executor_job(sleep, delay_duration)
        if final_delay > 0:
            final_delay_s = float(final_delay/1000)
            _LOGGER.debug("Waiting %ss for final_delay to complete...", str(final_delay_s))
            await hass.async_add_executor_job(sleep, final_delay_s)

        # Reset media player volume levels once finish playing
        await async_reset_media_players(hass, media_players_dict, volume_level, unjoin_players)

        # Save generated temp mp3 file to cache
        if cache is True:
            if _data["is_save_generated"] is True:
                _LOGGER.debug("Saving generated mp3 file to cache")
                filepath_hash = get_filename_hash(_data["generated_filename"])
                await async_store_data(hass, filepath_hash, audio_dict)
        else:
            if os.path.exists(audio_path):
                os.remove(audio_path)

        end_time = datetime.now()
        elapsed_time = (end_time - start_time).total_seconds() * 1000
        _LOGGER.debug(
            '----- Chime TTS Say Completed in %s ms -----', str(elapsed_time))

        return True

    hass.services.async_register(DOMAIN, SERVICE_SAY, async_say)


    #######################
    # Clear Cahce Service #
    #######################

    async def async_clear_cache(service):
        """Play TTS audio with local chime MP3 audio."""
        _LOGGER.debug('----- Chime TTS Clear Cache Called -----')
        start_time = datetime.now()
        cached_dicts = dict(_data[DATA_STORAGE_KEY])

        # Delete generated mp3 files
        _LOGGER.debug('Deleting generated mp3 cache files.')
        for key in cached_dicts:
            await async_remove_cached_audio_data(hass, str(key))

        elapsed_time = (datetime.now() - start_time).total_seconds() * 1000
        _LOGGER.debug(
            '----- Chime TTS Clear Cache Completed in %s ms -----', str(elapsed_time))
        return True

    hass.services.async_register(
        DOMAIN, SERVICE_CLEAR_CACHE, async_clear_cache)

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


#############
### QUEUE ###
#############

def init_queue():
    """Initialize variables and states for queuing service calls."""
    _data[QUEUE] = []
    _data[QUEUE_STATUS] = QUEUE_IDLE
    _data[QUEUE_CURRENT_ID] = -1
    _data[QUEUE_LAST_ID] = -1

def queue_new_service_call(service):
    """Add a new service call to the queue."""
    _LOGGER.debug('----- Chime TTS Say Called. Version %s -----', VERSION)
    service_id = _data[QUEUE_LAST_ID] + 1
    if _data[QUEUE] is None:
        _data[QUEUE] = []

    service_dict = {
        "service": service,
        "id": service_id
    }
    _data[QUEUE].append(service_dict)
    _data[QUEUE_LAST_ID] = service_id

    _LOGGER.debug("Service call #%s was added to the queue.", service_id)
    return service_dict

def get_queued_service_call():
    """Get the next queued service call from the queue."""
    if len(_data[QUEUE]) > 0:
        return _data[QUEUE][0]
    _LOGGER.debug("Queue empty")
    return None

def dequeue_service_call():
    """Remove the oldest service call from the queue."""
    if _data[QUEUE] and len(_data[QUEUE]) > 0:
        _LOGGER.debug("Removing current queued service call.")
        _data[QUEUE].pop(0)

        # All queued jobs completed
        if len(_data[QUEUE]) == 0:
            _LOGGER.debug("Queue emptied. Reinitializing values.")
            init_queue()
        else:
            # Move on to the next item (queued or in the future)
            _LOGGER.debug("Incrementing to next queued service call.")
            _data[QUEUE_CURRENT_ID] += 1


##############################
### Media Player Functions ###
##############################

async def async_initialize_media_players(hass: HomeAssistant, entity_ids, volume_level: float):
    """Initialize media player entities."""
    entity_found = False
    _data["group_members_supported"] = 0
    media_players_dict = []
    for entity_id in entity_ids:
        # Validate media player entity_id
        entity = hass.states.get(entity_id)
        if entity is None:
            _LOGGER.warning('Media player entity: "%s" not found', entity_id)
            continue
        else:
            entity_found = True

        # Ensure media player is turned on
        if entity.state == "off":
            _LOGGER.info('Media player entity "%s" is turned off. Turning on...', entity_id)
            await hass.services.async_call(
                "media_player",
                SERVICE_TURN_ON,
                {CONF_ENTITY_ID: entity_id},
                True
            )

        # Store media player's current volume level
        should_change_volume = False
        initial_volume_level = -1
        if volume_level >= 0:
            volume_supported = get_supported_feature(entity, ATTR_MEDIA_VOLUME_LEVEL)
            if volume_supported:
                initial_volume_level = float(entity.attributes.get(
                    ATTR_MEDIA_VOLUME_LEVEL, -1))
                if float(initial_volume_level) == float(volume_level / 100):
                    _LOGGER.debug("%s's volume_level is already %s",
                                entity_id, str(volume_level))
                else:
                    should_change_volume = True
            else:
                _LOGGER.warning('Media player "%s" does not support changing volume levels',
                                entity_id)

        # Group members supported?
        group_member_support =  get_supported_feature(entity, ATTR_GROUP_MEMBERS)
        if group_member_support is True:
            _data["group_members_supported"] += 1

        media_players_dict.append({
            "entity_id": entity_id,
            "should_change_volume": should_change_volume,
            "initial_volume_level": initial_volume_level,
            "group_members_supported": group_member_support
        })
    if entity_found is False:
        _LOGGER.error('No valid media player found')
        return False
    return media_players_dict

async def async_reset_media_players(hass: HomeAssistant,
                                    media_players_dict,
                                    volume_level: float,
                                    unjoin_players: bool):
    """Reset media players back to their original states."""
    entity_ids = []

    # Reset volume
    for media_player_dict in media_players_dict:
        entity_id = media_player_dict["entity_id"]
        entity_ids.append(entity_id)
        should_change_volume = bool(media_player_dict["should_change_volume"])
        initial_volume_level = media_player_dict["initial_volume_level"]
        if should_change_volume and initial_volume_level >= 0:
            _LOGGER.debug("Returning %s's volume level to %s", entity_id, initial_volume_level)
            await async_set_volume_level(hass, entity_id, initial_volume_level, volume_level)

    # Unjoin entity_ids
    if unjoin_players is True and "joint_media_player_entity_id" in _data and _data["joint_media_player_entity_id"] is not None:
        _LOGGER.debug(" - Calling media_player.unjoin service...")
        for media_player_dict in media_players_dict:
            if media_player_dict["group_members_supported"] is True:
                entity_id = media_player_dict["entity_id"]
                _LOGGER.debug("   - media_player.unjoin: %s", entity_id)
                try:
                    await hass.services.async_call(
                        domain="media_player",
                        service=SERVICE_UNJOIN,
                        service_data={CONF_ENTITY_ID: entity_id},
                        blocking=True
                    )
                    _LOGGER.debug("   ...done")
                except Exception as error:
                    _LOGGER.warning(" - Error calling unjoin service for %s: %s", entity_id, error)


async def async_join_media_players(hass, entity_ids):
    """Join media players."""
    _LOGGER.debug(" - Calling media_player.join service for %s media_player entities...",
                  len(entity_ids))

    supported_entity_ids = []
    for entity_id in entity_ids:
        entity = hass.states.get(entity_id)
        if get_supported_feature(entity, ATTR_GROUP_MEMBERS):
            supported_entity_ids.append(entity_id)

    if len(supported_entity_ids) > 1:
        _LOGGER.debug(" - Joining %s media_player entities...", str(len(supported_entity_ids)))
        try:
            _data["joint_media_player_entity_id"] = supported_entity_ids[0]
            await hass.services.async_call(
                domain="media_player",
                service=SERVICE_JOIN,
                service_data={
                    CONF_ENTITY_ID: _data["joint_media_player_entity_id"],
                    ATTR_GROUP_MEMBERS: supported_entity_ids
                },
                blocking=True
            )
            _LOGGER.debug(" - ...done")
            return _data["joint_media_player_entity_id"]
        except Exception as error:
            _LOGGER.warning("   - Error joining media_player entities: %s", error)
    else:
        _LOGGER.warning(" - Only 1 media_player entity provided. Unable to join.")

    return False

####################################
### Retrieve TTS Audio Functions ###
####################################

async def async_request_tts_audio(hass: HomeAssistant,
                                  tts_platform: str,
                                  message: str,
                                  language: str,
                                  cache: str,
                                  options: dict,
                                  tts_playback_speed: float = 0.0):
    """Send an API request for TTS audio and return the audio file's local filepath."""

    tld = options["tld"] if "tld" in options else None
    gender = options["gender"] if "gender" in options else None

    start_time = datetime.now()
    debug_string = 'hass, tts_platform = ' + tts_platform + \
        ', message = ' + str(message) + \
        ', tts_playback_speed = ' + str(tts_playback_speed) + \
        ', cache = ' + str(cache) + \
        ', language = ' + str(language)
    for key in options:
        debug_string += ', ' + key + " = " + str(options[key])
    _LOGGER.debug(
        'async_request_tts_audio(%s)', debug_string)

    # Data validation

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
    if language is not None and tts_platform in [GOOGLE_TRANSLATE,
                                                 NABU_CASA_CLOUD_TTS,
                                                 IBM_WATSON_TTS]:
        if tts_platform is IBM_WATSON_TTS:
            options["voice"] = language
    else:
        language = None

    # Cache
    if cache is not None and tts_platform not in [GOOGLE_TRANSLATE, NABU_CASA_CLOUD_TTS]:
        cache = None

    # tld
    if tld is not None and tts_platform in [GOOGLE_TRANSLATE]:
        options["tld"] = tld
    else:
        tld = None
        if "tld" in options:
            del options["tld"]

    # Gender
    if gender is not None and tts_platform in [NABU_CASA_CLOUD_TTS]:
        options["gender"] = gender
    else:
        gender = None
        if "gender" in options:
            del options["gender"]

    _LOGGER.debug(" - Generating TTS audio...")
    media_source_id = None
    try:
        media_source_id = tts.media_source.generate_media_source_id(hass=hass,
                                                                    message=message,
                                                                    engine=tts_platform,
                                                                    language=language,
                                                                    cache=cache,
                                                                    options=options)
    except Exception as error:
        _LOGGER.warning("   - Error calling tts.media_source.generate_media_source_id: %s",
                         error)
        return None
    if media_source_id is None:
        _LOGGER.warning(" - ...unable to generate media_source_id")
        return None

    audio_data = None
    try:
        audio_data = await tts.async_get_media_source_audio(hass=hass,
                                                            media_source_id=media_source_id)
    except Exception as error:
        _LOGGER.warning("   - Error calling tts.async_get_media_source_audio: %s",
                         error)
        return None

    if audio_data is not None:
        if len(audio_data) == 2:
            audio_bytes = audio_data[1]
            file = io.BytesIO(audio_bytes)
            if file is None:
                _LOGGER.warning(" - ...could not convert TTS bytes to audio")
                return None
            audio = AudioSegment.from_file(file)
            if audio is not None:
                if tts_playback_speed != 100:
                    _LOGGER.debug("  -  ...changing TTS playback speed to %s percent",
                                str(tts_playback_speed))
                    playback_speed = float(tts_playback_speed / 100)
                    if tts_playback_speed > 150:
                        audio = audio.speedup(playback_speed=playback_speed, chunk_size=50)
                    else:
                        audio = audio.speedup(playback_speed=playback_speed)
                end_time = datetime.now()
                _LOGGER.debug(" - ...TTS audio completed in %s ms",
                            str((end_time - start_time).total_seconds() * 1000))
                return audio
            _LOGGER.warning(" - ...could not extract TTS audio from file")
        else:
            _LOGGER.warning(" - ...audio_data did not contain audio bytes")
    else:
        _LOGGER.warning(" - ...audio_data generation failed")
    return None


##############################
### Audio Helper Functions ###
##############################

async def async_get_playback_audio_path(params: dict, options: dict):
    """Create audio to play on media player entity."""
    output_audio = None

    hass = params["hass"]
    chime_path = params["chime_path"]
    end_chime_path = params["end_chime_path"]
    delay = params["delay"]
    tts_platform = params["tts_platform"]
    tts_playback_speed = params["tts_playback_speed"]
    message = params["message"]
    language = params["language"]
    cache = params["cache"]
    _data["delay"] = 0
    _data["is_save_generated"] = False
    _LOGGER.debug('async_get_playback_audio_path')

    _data["generated_filename"] = get_generated_filename({**params, **options})

    # Load previously generated audio from cache
    if cache is True:
        _LOGGER.debug("Attempting to retrieve generated mp3 file from cache")
        filepath_hash = get_filename_hash(_data["generated_filename"])
        audio_dict = await async_get_cached_audio_data(hass, filepath_hash)
        if audio_dict is not None:
            filepath = audio_dict[AUDIO_PATH_KEY]
            audio_duration = audio_dict[AUDIO_DURATION_KEY]
            if filepath is not None and audio_duration > 0:
                if os.path.exists(str(filepath)):
                    _LOGGER.debug("Using previously generated mp3 saved in cache")
                    return audio_dict
                _LOGGER.warning(
                    "Could not find previosuly cached generated mp3 file")
        else:
            _LOGGER.debug(" - No previously generated mp3 file found")

    # Load chime audio
    if chime_path is not None:
        output_audio = get_audio_from_path(hass, chime_path)

    # Request TTS audio file
    tts_audio = await async_request_tts_audio(hass=hass,
                                              tts_platform=tts_platform,
                                              message=message,
                                              language=language,
                                              cache=cache,
                                              options=options,
                                              tts_playback_speed=tts_playback_speed)
    if tts_audio is not None:
        if output_audio is not None:
            output_audio = output_audio + (AudioSegment.silent(duration=delay)) + tts_audio
        else:
            output_audio = tts_audio
    else:
        _LOGGER.warning("Unable to generate TTS audio")

    # Load end chime audio
    if end_chime_path is not None and len(end_chime_path) > 0:
        output_audio = get_audio_from_path(hass, end_chime_path, delay, output_audio)

    # Save generated audio file
    if output_audio is not None:
        duration = float(len(output_audio) / 1000.0)
        _data["delay"] = duration
        _LOGGER.debug(" - Final audio created:")
        _LOGGER.debug("   - Duration = %ss", duration)

        # Save temporary MP3 file
        _LOGGER.debug("Creating final audio file")
        root_path = hass.config.path("").replace("/config", "")
        temp_folder_path = (root_path + TEMP_PATH).replace("//", "/")
        if os.path.exists(temp_folder_path) is False:
            _LOGGER.debug(" - Creating temp folder: %s", temp_folder_path)
            try:
                os.makedirs(temp_folder_path)
                _LOGGER.debug("   - Temp folder created")
            except OSError as error:
                _LOGGER.warning("   - An error occurred while creating the folder '%s': %s",
                                temp_folder_path, error)
            except Exception as error:
                _LOGGER.warning("   - An error occurred when creating the folder: %s",
                                error)
        else:
            _LOGGER.debug("   - Temp folder exists: %s", temp_folder_path)


        _LOGGER.debug(" - Creating temporary mp3 file...")
        try:
            with tempfile.NamedTemporaryFile(prefix=temp_folder_path, suffix=".mp3") as temp_obj:
                _LOGGER.debug("   - temp_obj = %s", str(temp_obj))
                output_path = temp_obj.name
            _LOGGER.debug("   - Filepath = '%s'", output_path)
            _data["is_save_generated"] = True
            output_audio.export(output_path, format="mp3")
            _LOGGER.debug("   - File saved successfully")
            return {
                AUDIO_PATH_KEY: output_path,
                AUDIO_DURATION_KEY: duration
            }
        except Exception as error:
            _LOGGER.warning("An error occurred when creating the temp mp3 file: %s",
                          error)

    return None

def validate_audio_dict(audio_dict: any):
    """Validate the audio_dict. Returns True if passes validation."""
    if audio_dict is not None:
        if AUDIO_PATH_KEY in audio_dict:
            if AUDIO_DURATION_KEY in audio_dict:
                audio_duration = audio_dict[AUDIO_DURATION_KEY]
                if audio_duration == 0:
                    _LOGGER.error("async_get_playback_audio_path --> Audio has no duration")
                    return False
            else:
                _LOGGER.error("async_get_playback_audio_path --> Audio has no duration data")
                return False
        else:
            _LOGGER.error("async_get_playback_audio_path --> Audio has no file path data")
            return False
    else:
        _LOGGER.error("async_get_playback_audio_path --> Unable to generate audio for playback")
        return False

def get_audio_from_path(hass: HomeAssistant,
                        filepath: str,
                        delay=0,
                        audio=None):
    """Add audio from a given file path to existing audio (optional) with delay (optional)."""
    if filepath is None or filepath == "None" or len(filepath) <= 5:
        _LOGGER.debug('Invalid audio filepath provided')
        return audio

    filepath = str(filepath)
    _LOGGER.debug('get_audio_from_path("%s", %s, audio)', filepath, str(delay))

    filepath = get_file_path(hass, filepath)
    if filepath is None:
        _LOGGER.warning('Unable to find audio file')
    else:
        _LOGGER.debug(' - Retrieving audio from path: "%s"...', filepath)
        try:
            audio_from_path = AudioSegment.from_file(filepath)
            if audio_from_path is not None:
                duration = float(len(audio_from_path) / 1000.0)
                _LOGGER.debug('   - ...audio with duration %ss retrieved successfully', str(duration))
                if audio is None:
                    return audio_from_path
                return (audio + (AudioSegment.silent(duration=delay) + audio_from_path))
            _LOGGER.warning("Unable to find audio at filepath: %s", filepath)
        except Exception as error:
            _LOGGER.warning('Unable to extract audio from file: "%s"', error)
    return audio

async def async_set_volume_level_for_media_players(hass: HomeAssistant,
                                                   media_players_dict,
                                                   volume_level: float):
    """Set the volume level for all media_players."""
    for media_player_dict in media_players_dict:
        entity_id = media_player_dict["entity_id"]
        should_change_volume = bool(media_player_dict["should_change_volume"])
        initial_volume_level = media_player_dict["initial_volume_level"]
        if should_change_volume and volume_level >= 0:
            _LOGGER.debug(" - Setting '%s' volume level to %s", entity_id, str(volume_level))
            await async_set_volume_level(hass, entity_id, volume_level, initial_volume_level)


async def async_set_volume_level(hass: HomeAssistant,
                                 entity_id: str,
                                 new_volume_level=-1,
                                 current_volume_level=-1):
    """Set the volume_level for a given media player entity."""
    new_volume_level = float(new_volume_level)
    current_volume_level = float(current_volume_level)
    _LOGGER.debug(' - async_set_volume_level("%s", %s)',
                  entity_id, str(new_volume_level))
    if new_volume_level >= 0 and new_volume_level != current_volume_level:
        _LOGGER.debug(' - Seting volume_level of media player "%s" to: %s',
                       entity_id, str(new_volume_level))
        try:
            await hass.services.async_call(
                "media_player",
                SERVICE_VOLUME_SET,
                {
                    ATTR_MEDIA_VOLUME_LEVEL: new_volume_level,
                    CONF_ENTITY_ID: entity_id
                },
                True,
            )
            _LOGGER.debug(' - Volume set')
        except Exception as error:
            _LOGGER.warning(" - Error setting volume for '%s': %s",
                            entity_id, error)
        return True
    _LOGGER.debug(' - Skipped setting volume')
    return False


################################
### Storage Helper Functions ###
################################

async def async_init_stored_data(hass: HomeAssistant):
    """Retrieve the stored data for the integration."""
    store = storage.Store(hass, 1, DATA_STORAGE_KEY)
    _data[DATA_STORAGE_KEY] = await store.async_load()
    if _data[DATA_STORAGE_KEY] is None:
        _data[DATA_STORAGE_KEY] = {}


async def async_store_data(hass: HomeAssistant, key: str, value: str):
    """Store a key/value pair in the integration's stored data."""
    _LOGGER.debug("Saving to chime_tts storage:")
    _LOGGER.debug(' - key:   "%s"', key)
    _LOGGER.debug(' - value: "%s"', value)
    _data[DATA_STORAGE_KEY][key] = value
    await async_save_data(hass)


async def async_retrieve_data(key: str):
    """Retrieve a value from the integration's stored data based on the provided key."""
    if key in _data[DATA_STORAGE_KEY]:
        _LOGGER.debug(" - Retrieving key/value from chime_tts storage:")
        _LOGGER.debug("   - key: %s", key)
        _LOGGER.debug("   - value: %s", str(_data[DATA_STORAGE_KEY][key]))
        return _data[DATA_STORAGE_KEY][key]
    return None


async def async_save_data(hass: HomeAssistant):
    """Save the provided data to the integration's stored data."""
    store = storage.Store(hass, 1, DATA_STORAGE_KEY)
    await store.async_save(_data[DATA_STORAGE_KEY])


async def async_get_cached_audio_data(hass: HomeAssistant, filepath_hash: str):
    """Return cached audio data previously stored in Chime TTS' cache."""
    _LOGGER.debug(
        " - async_get_cached_audio_data('%s')", filepath_hash)

    audio_dict = await async_retrieve_data(filepath_hash)
    if audio_dict is not None:
        cached_path = None
        # Validate Path
        # Old cache format?
        if AUDIO_PATH_KEY not in audio_dict:
            audio_dict = {AUDIO_PATH_KEY: audio_dict, AUDIO_DURATION_KEY: None}
        cached_path = audio_dict[AUDIO_PATH_KEY]
        if cached_path is not None and os.path.exists(str(cached_path)):
            _LOGGER.debug(" - Cached audio data found")
            if audio_dict[AUDIO_DURATION_KEY] is None:
                # Add duration data if audio_dict is old format
                audio = get_audio_from_path(hass, cached_path)
                if audio is not None:
                    audio_dict[AUDIO_DURATION_KEY] = float(len(audio) / 1000.0)
                    await async_store_data(hass, filepath_hash, audio_dict)

        return audio_dict

    _LOGGER.debug(" - Audio data not found in cache.")
    await async_remove_cached_audio_data(hass, filepath_hash)
    return None


async def async_remove_cached_audio_data(hass: HomeAssistant, filepath_hash: str):
    """Remove cached audio data from Chime TTS' cache and deletes audio filepath from filesystem."""
    audio_dict = await async_retrieve_data(filepath_hash)
    if audio_dict is not None:
        # Old cache format?
        if AUDIO_PATH_KEY not in audio_dict:
            audio_dict = {AUDIO_PATH_KEY: audio_dict}
        cached_path = audio_dict[AUDIO_PATH_KEY]
        if os.path.exists(cached_path):
            os.remove(str(cached_path))
            if os.path.exists(cached_path):
                _LOGGER.warning(
                    " - Unable to delete cached file '%s'.", str(cached_path))
            else:
                _LOGGER.debug(
                    " - Cached file '%s' deleted successfully.", str(cached_path))
        else:
            _LOGGER.debug(
                " - Cached file '%s' not found.", str(cached_path))
        _data[DATA_STORAGE_KEY].pop(filepath_hash)


        await async_save_data(hass)
    else:
        _LOGGER.debug(
            " - filepath_hash %s does not exist in the cache.", str(filepath_hash))



################################
### Audio Filename Functions ###
################################

def get_chime_path(chime_path: str = ""):
    """Retrieve preset chime path if selected."""
    if chime_path.startswith(MP3_PRESET_PATH_PLACEHOLDER):
        chime_path = MP3_PRESET_PATH + chime_path.replace(MP3_PRESET_PATH_PLACEHOLDER, "") + ".mp3"
    return chime_path

def get_generated_filename(params: dict):
    """Generate a unique generated filename based on specific parameters."""
    filename = ""
    relevant_params = ["message",
                       "tts_platform",
                       "gender",
                       "tld",
                       "language",
                       "chime_path",
                       "end_chime_path",
                       "delay",
                       "tts_playback_speed"]
    for param in relevant_params:
        if param in params and params[param] is not None and len(str(params[param])) > 0:
            filename = filename + "-" + str(params[param])
    return filename

def get_filename_hash(string: str):
    """Generate a hash from a filename string."""
    hash_object = hashlib.sha256()
    hash_object.update(string.encode('utf-8'))
    hash_value = str(hash_object.hexdigest())
    return hash_value

async def async_play_media(hass: HomeAssistant,
                           audio_path,
                           entity_ids,
                           announce,
                           join_players):
    """Call the media_player.play_media service."""
    service_data = {}

    # media content type
    service_data[ATTR_MEDIA_CONTENT_TYPE] = MEDIA_TYPE_MUSIC

    # media_content_id
    media_path = audio_path
    media_index = media_path.find("/media/")
    if media_index != -1:
        media_prefix = "media-source://media_source/local/"
        media_path = media_prefix + media_path[media_index + len("/media/"):]
    service_data[ATTR_MEDIA_CONTENT_ID] = media_path

    # announce
    if announce is True:
        service_data[ATTR_MEDIA_ANNOUNCE] = announce

    # entity_id
    service_data[CONF_ENTITY_ID] = entity_ids
    if join_players is True:
        # join entity_ids as a group
        if _data["group_members_supported"] > 1:
            joint_speakers_entity_id = await async_join_media_players(hass, entity_ids)
            if joint_speakers_entity_id is not False:
                service_data[CONF_ENTITY_ID] = joint_speakers_entity_id
            else:
                _LOGGER.warning("Unable to join speakers. Only 1 media_player supported.")
        else:
            if _data["group_members_supported"] == 1:
                _LOGGER.warning("Unable to join speakers. Only 1 media_player supported.")
            else:
                _LOGGER.warning("Unable to join speakers. No supported media_players found.")

    # Play the audio
    _LOGGER.debug('Calling media_player.play_media service with data:')
    for key, value in service_data.items():
        _LOGGER.debug(' - %s: %s', str(key), str(value))
    try:
        await hass.services.async_call(
            "media_player",
            SERVICE_PLAY_MEDIA,
            service_data,
            True,
        )
        _LOGGER.debug('...media_player.play_media completed.')
    except ServiceNotFound:
        _LOGGER.warning("Service 'play_media' not found.")
    except TemplateError:
        _LOGGER.warning("Error while rendering Jinja2 template.")
    except HomeAssistantError as err:
        _LOGGER.warning("An error occurred: %s", str(err))
    except Exception as err:
        _LOGGER.warning("An unexpected error occurred: %s", str(err))


##############################
### Misc. Helper Functions ###
##############################

def parse_options_yaml(data):
    """Parse TTS service options YAML into dict object."""
    try:
        options_string = data.get("options", "")
        options = yaml.safe_load(options_string)
        if options is None:
            return {}
        for key in ["tld", "gender"]:
            if options is not None and key not in options:
                value = data.get(key, None)
                if value is not None:
                    options[key] = value
        return options
    except yaml.YAMLError as error:
        _LOGGER.error("Error parsing options YAML: %s", error)
    return {}

def parse_entity_ids(data, hass):
    """Parse media_player entity_ids into list object."""
    entity_ids = data.get(CONF_ENTITY_ID, [])
    if isinstance(entity_ids, str):
        entity_ids = entity_ids.split(',')

    # Find all media_player entities associated with device/s specified
    device_ids = data.get("device_id", [])
    if isinstance(device_ids, str):
        device_ids = device_ids.split(',')
    entity_registry = hass.data['entity_registry']
    for device_id in device_ids:
        matching_entity_ids = [
            entity.entity_id
            for entity in entity_registry.entities.values()
            if entity.device_id == device_id and entity.entity_id.startswith("media_player.")
        ]
        entity_ids.extend(matching_entity_ids)
    entity_ids = list(set(entity_ids))
    return entity_ids

def get_supported_feature(entity: State, feature: str):
    """Whether a feature is supported by the media_player device."""
    if entity is None or entity.attributes is None:
        return False
    supported_features = entity.attributes.get('supported_features', 0)

    if feature is ATTR_MEDIA_VOLUME_LEVEL:
        return bool(supported_features & 2)

    if feature is ATTR_MEDIA_ANNOUNCE:
        # Announce support detection feature not yet supporting in HA
        # return bool(supported_features & 128)
        return True

    if feature is ATTR_GROUP_MEMBERS:
        return bool(supported_features & 524288)

    return False

def sleep(duration_s: float):
    """Make a synchronous time.sleep call lasting duration_s seconds."""
    return time.sleep(duration_s)

def get_file_path(hass: HomeAssistant, p_filepath: str=""):
    """Return a valid file path string."""
    ret_value = None

    filepaths = [p_filepath]

    # Test for docker/virtual instances filepath
    root_path = hass.config.path("")
    absolute_path = (root_path + p_filepath).replace("/config", "").replace("//", "/")
    if p_filepath is not absolute_path:
        filepaths.append(absolute_path)

    # Test each filepath
    for filepath in filepaths:
        if os.path.exists(filepath) is True:
            ret_value = filepath
        if ret_value is None:
            _LOGGER.debug("File not found at path: %s", filepath)

    return ret_value
