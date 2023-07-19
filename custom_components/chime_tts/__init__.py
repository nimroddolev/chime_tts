"""The Chime TTS integration."""

import logging
import tempfile
import time
import json
import os
import hashlib

from datetime import datetime
from requests import post
from pydub import AudioSegment

from homeassistant.components.media_player.const import (
    ATTR_MEDIA_CONTENT_ID,
    ATTR_MEDIA_CONTENT_TYPE,
    ATTR_MEDIA_ANNOUNCE,
    ATTR_MEDIA_VOLUME_LEVEL,
    MEDIA_TYPE_MUSIC,
)
from homeassistant.const import HTTP_BEARER_AUTHENTICATION, CONF_ENTITY_ID
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.core import State
from homeassistant.helpers.network import get_url
from homeassistant.helpers import storage
from .const import (
    DOMAIN,
    SERVICE_SAY,
    SERVICE_CLEAR_CACHE,
    PAUSE_DURATION_MS,
    DATA_STORAGE_KEY,
    TEMP_PATH,
    TTS_PATH,
    TTS_API,
    TIMEOUT,
    # AMAZON_POLLY,
    # BAIDU,
    # GOOGLE_CLOUD,
    GOOGLE_TRANSLATE,
    # IBM_WATSON_TTS,
    # MARYTTS,
    # MICROSOFT_TTS,
    NABU_CASA,
    # PICOTTS,
    # VOICE_RSS,
    # YANDEX_TTS,
)
_LOGGER = logging.getLogger(__name__)
_data = {}


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up an entry."""
    await async_init_stored_data(hass)
    _data[HTTP_BEARER_AUTHENTICATION] = config_entry.data[HTTP_BEARER_AUTHENTICATION]
    config_entry.async_on_unload(
        config_entry.add_update_listener(async_reload_entry))
    return True


async def async_setup(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up the Chime TTS integration."""
    _LOGGER.info("The Chime TTS integration is set up.")

    async def async_clear_cache(service):
        """Play TTS audio with local chime MP3 audio."""
        _LOGGER.debug('----- Chime TTS Clear Cache Called -----')
        start_time = datetime.now()
        cache_dict = dict(_data[DATA_STORAGE_KEY])

        # Delete generated mp3 files
        _LOGGER.debug('Deleting generated mp3 cache files.')
        for key in cache_dict.items():
            await async_remove_cached_path(hass, key)

        elapsed_time = (datetime.now() - start_time).total_seconds() * 1000
        _LOGGER.debug(
            '----- Chime TTS Clear Cache Completed in %s ms -----', str(elapsed_time))
        return True

    hass.services.async_register(
        DOMAIN, SERVICE_CLEAR_CACHE, async_clear_cache)

    async def async_say(service):
        """Play TTS audio with local chime MP3 audio."""
        start_time = datetime.now()
        _LOGGER.debug('----- Chime TTS Say Called -----')

        chime_path = str(service.data.get("chime_path", ""))
        end_chime_path = str(service.data.get("end_chime_path", ""))
        delay = float(service.data.get("delay", PAUSE_DURATION_MS))
        message = str(service.data.get("message", ""))
        tts_platform = str(service.data.get("tts_platform", ""))
        tts_playback_speed = float(service.data.get("tts_playback_speed", 100))
        entity_id = str(service.data.get(CONF_ENTITY_ID, ""))
        volume_level = float(service.data.get(ATTR_MEDIA_VOLUME_LEVEL, -1))
        cache = service.data.get("cache", False)
        announce = service.data.get("announce", True)
        language = service.data.get("language", None)
        tld = service.data.get("tld", None)
        gender = service.data.get("gender", None)

        # Validate media player entity_id
        entity = hass.states.get(entity_id)
        if entity is None:
            _LOGGER.error('Media player entity: "%s" not found', entity_id)
            return False

        # Ensure media player is on
        if entity.state == "off":
            _LOGGER.info('Turning on media player entity: "%s"', entity_id)
            await hass.services.async_call(
                "media_player", "turn_on", {CONF_ENTITY_ID: entity_id}, True
            )

        # Store media player's current volume level
        initial_volume_level = -1
        volume_supported = get_supported_feature(entity, ATTR_MEDIA_VOLUME_LEVEL)
        if volume_supported:
            if volume_level >= 0:
                initial_volume_level = float(entity.attributes.get(
                    ATTR_MEDIA_VOLUME_LEVEL, -1))
            else:
                _LOGGER.warning(
                    'Unable to get volume for media player entity: "%s"', entity_id)
        else:
            _LOGGER.warning('Media player entity "%s" does not support changing its volume level', entity_id)

        # Create audio file to play on media player
        params = {
            "hass": hass,
            "chime_path": chime_path,
            "end_chime_path": end_chime_path,
            "delay": delay,
            "tts_platform": tts_platform,
            "tts_playback_speed": tts_playback_speed,
            "cache": cache,
            "message": message,
            "language": language,
            "tld": tld,
            "gender": gender
        }
        audio_path = await async_get_playback_audio_path(params)
        if audio_path is None:
            _LOGGER.error("Unable to generate audio for playback")
            return False

        # Set volume to desired level
        if volume_supported is True and volume_level >= 0:
            await async_set_volume_level(hass, entity_id, volume_level, initial_volume_level)

        # Play the audio on the media player
        media_path = audio_path.replace(
            "/media/", "media-source://media_source/local/")
        _LOGGER.debug('Playing media...')
        _LOGGER.debug('  - media_path = "%s"', media_path)
        _LOGGER.debug('  - entity_id = "%s"', entity_id)
        await hass.services.async_call(
            "media_player",
            "play_media",
            {
                ATTR_MEDIA_CONTENT_ID: media_path,
                ATTR_MEDIA_CONTENT_TYPE: MEDIA_TYPE_MUSIC,
                CONF_ENTITY_ID: entity_id,
                ATTR_MEDIA_ANNOUNCE: announce
            },
            True,
        )
        _LOGGER.debug('...media finished playback:')

        # Save generated temp mp3 file to cache
        if cache is True:
            if _data["is_save_generated"] is True:
                _LOGGER.debug("Saving generated mp3 file to cache")
                filename = _data["generated_filename"]
                filepath_hash = get_filename_hash(TEMP_PATH + filename)
                await async_store_data(hass, filepath_hash, audio_path)
        else:
            if os.path.exists(audio_path):
                os.remove(audio_path)

        # Reset media player volume level once finish playing
        if volume_supported and initial_volume_level != -1:
            _LOGGER.debug("Waiting %ss until returning volume level to %s...", str(
                _data["delay"]), initial_volume_level)
            await hass.async_add_executor_job(sleep, _data["delay"])
            await async_set_volume_level(hass, entity_id, initial_volume_level, volume_level)
            _LOGGER.debug("...volume level restored")

        end_time = datetime.now()
        elapsed_time = (end_time - start_time).total_seconds() * 1000
        _LOGGER.debug(
            '----- Chime TTS Say Completed in %s ms -----', str(elapsed_time))

        return True

    hass.services.async_register(DOMAIN, SERVICE_SAY, async_say)

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


####################################
### Retrieve TTS Audio Functions ###
####################################

async def async_request_tts_audio_filepath(hass: HomeAssistant,
                                           tts_platform: str,
                                           message: str,
                                           language: str = None,
                                           tld: str = None,
                                           gender: str = None):
    """Send an API request for TTS audio and return the audio file's local filepath."""
    debug_string = 'hass, tts_platform="' + tts_platform + '", message="' + message + \
        '", language="' + str(language) + '", tld="' + \
        str(tld) + '", gender="' + str(gender) + '")'
    _LOGGER.debug(
        'async_request_tts_audio_filepath(%s)', debug_string)
    # Data validation
    if message is False or message == "":
        _LOGGER.warning("No message text provided for TTS audio")
        return None
    if tts_platform is False or tts_platform == "":
        _LOGGER.warning("No TTS platform selected")
        return None

    # Send API request for TTS Audio
    instance_url = str(get_url(hass))
    url = instance_url + TTS_API
    bearer_token = _data[HTTP_BEARER_AUTHENTICATION]
    data = {
        "message": str(message),
        "platform": str(tts_platform),
        "cache": True
    }

    # Additional language parameters
    # if tts_platform == AMAZON_POLLY:
    # if tts_platform == BAIDU:
    # if tts_platform == GOOGLE_CLOUD:

    # Google Translate https://www.home-assistant.io/integrations/google_translate/
    if tts_platform == GOOGLE_TRANSLATE:
        if language is not None:
            data["language"] = language
        if tld is not None:
            data["options"] = {
                "tld": tld
            }

    # if tts_platform == IBM_WATSON_TTS:
    # if tts_platform == MARYTTS:
    # if tts_platform == MICROSOFT_TTS:

    # Nabu Casa Cloud TTS https://www.nabucasa.com/config/tts/
    if tts_platform == NABU_CASA:
        if language is not None:
            data["language"] = language
        if gender is not None:
            data["options"] = {
                "gender": gender
            }

    # if tts_platform == PICOTTS:
    # if tts_platform == VOICE_RSS:
    # if tts_platform == YANDEX_TTS:

    headers = {
        "Authorization": "Bearer " + str(bearer_token),
        "Content-Type": "application/json",
    }
    data_string = str(json.dumps(data)).replace(": True", ": true")

    # Redact bearer_token before writing log message
    if len(bearer_token) <= 10:
        redacted_bearer_token = "##########"
    else:
        redacted_bearer_token = bearer_token[:5] + \
            '#'*10 + bearer_token[-5:]
    redacted_headers = str(headers).replace(
        bearer_token, redacted_bearer_token)
    _LOGGER.debug('Requesting TTS audio:')
    _LOGGER.debug(' * url     = %s', url)
    _LOGGER.debug(' * headers = %s', redacted_headers)
    _LOGGER.debug(' * data    = %s', data_string)
    _LOGGER.debug(' * timeout = %s', str(TIMEOUT))

    response = await hass.async_add_executor_job(post_request, url, headers, data_string, TIMEOUT)
    _LOGGER.debug(' - Repsonse status_code: "%s"', response.status_code)
    _LOGGER.debug(' - Repsonse received: "%s"', response.text)
    if response is not None:
        if response.status_code == 200:
            response_json = response.json()
            temp_string = response_json["path"]
            arr = temp_string.split("/")
            filename = "/config/tts/" + arr[len(arr) - 1]
            return filename
        else:
            _LOGGER.warning(
                "TTS Audio request unsuccessful: '%s'", response.text)
    else:
        _LOGGER.warning("TTS Audio request failed")
    return None


def post_request(url, headers, data, timeout):
    """Make a synchronous post request."""
    return post(url, headers=headers, data=data, timeout=timeout)


##############################
### Audio Helper Functions ###
##############################

async def async_get_playback_audio_path(params: dict):
    """Create audio to play on media player entity."""
    hass = params["hass"]
    chime_path = params["chime_path"]
    end_chime_path = params["end_chime_path"]
    delay = params["delay"]
    tts_platform = params["tts_platform"]
    tts_playback_speed = params["tts_playback_speed"]
    cache = params["cache"]
    message = params["message"]
    language = params["language"]
    tld = params["tld"]
    gender = params["gender"]
    _data["delay"] = 0
    _data["is_save_generated"] = False
    _LOGGER.debug(
        'async_get_playback_audio_path(params=%s)', str(params))

    # Load previously generated audio from cache
    if cache is True:
        _LOGGER.debug("Attempting to retrieve generated mp3 file from cache")
        _data["generated_filename"] = get_generated_filename(params)
        filepath_hash = get_filename_hash(
            TEMP_PATH + _data["generated_filename"])
        filepath = await async_get_cached_path(hass, filepath_hash)
        if filepath is not None:
            if os.path.exists(str(filepath)):
                _LOGGER.debug("Using previously generated mp3 saved in cache")
                return filepath
            _LOGGER.warning(
                "Could not find previosuly cached generated mp3 file")
        else:
            _LOGGER.debug("No previously generated mp3 file found")

    # Load chime audio
    output_audio = get_audio_from_path(chime_path)

    # Load TTS audio
    tts_audio_path = None
    tts_filename = get_tts_filename(params)
    tts_filepath_hash = get_filename_hash(tts_filename)

    # Retrieve TTS audio file from cache
    if cache is True:
        tts_audio_path = await async_get_cached_path(hass, tts_filepath_hash)
        if tts_audio_path is None:
            _LOGGER.debug(" - Cached TTS mp3 file not found")

    # Request new TTS audio file
    if tts_audio_path is None:
        tts_audio_path = await async_request_tts_audio_filepath(hass,
                                                                tts_platform,
                                                                message,
                                                                language,
                                                                tld,
                                                                gender)
        _LOGGER.debug(
            " - REST API request to %s returned audio path: '%s'", TTS_API, tts_audio_path)
        if tts_audio_path is not None and cache is True:
            await async_store_data(hass, tts_filepath_hash, tts_audio_path)

    output_audio = get_audio_from_path(
        tts_audio_path, delay, output_audio, tts_playback_speed)

    # Load end chime audio
    output_audio = get_audio_from_path(end_chime_path, delay, output_audio)

    # Save generated audio file
    if output_audio is not None:
        duration = float(len(output_audio) / 1000.0)
        _data["delay"] = duration
        _LOGGER.debug(" - Final audio created:")
        _LOGGER.debug("   - Duration = %ss", duration)

        # Save temporary MP3 file
        if os.path.exists(TEMP_PATH) is False:
            os.makedirs(TEMP_PATH)
        with tempfile.NamedTemporaryFile(prefix=TEMP_PATH, suffix=".mp3") as temp_filename_obj:
            output_path = temp_filename_obj.name
        _LOGGER.debug("   - Filepath = '%s'", output_path)
        _data["is_save_generated"] = True
        output_audio.export(output_path, format="mp3")
        return output_path

    return None


def get_audio_from_path(filepath: str, delay=0, audio=None, tts_playback_speed=100):
    """Add audio from a given file path to existing audio (optional) with delay (optional)."""
    filepath = str(filepath)
    _LOGGER.debug('get_audio_from_path("%s", %s, audio)', filepath, str(delay))

    if (filepath is None) or (filepath == "None") or (len(filepath) == 0):
        return audio
    if not os.path.exists(filepath):
        _LOGGER.warning('Audio filepath does not exist: "%s"', str(filepath))
        return audio

    _LOGGER.debug('Retrieving audio from path: "%s"...', filepath)
    audio_from_path = AudioSegment.from_file(filepath)
    if audio_from_path is not None:
        duration = float(len(audio_from_path) / 1000.0)
        _LOGGER.debug(' - ...audio with duration %ss retrieved successfully', str(duration))
        if tts_playback_speed != 100:
            _LOGGER.debug(" - Changing TTS playback speed to %s percent",
                          str(tts_playback_speed))
            playback_speed = float(tts_playback_speed / 100)
            audio_from_path = audio_from_path.speedup(
                playback_speed=playback_speed)
        if audio is None:
            return audio_from_path
        return (audio + (AudioSegment.silent(duration=delay) + audio_from_path))
    _LOGGER.warning("...unable to find audio from filepath")
    return audio


async def async_set_volume_level(hass: HomeAssistant, entity_id: str, new_volume_level=-1, current_volume_level=-1):
    """Set the volume_level for a given media player entity."""
    new_volume_level = float(new_volume_level)
    current_volume_level = float(current_volume_level)
    _LOGGER.debug(' - async_set_volume_level("%s", %s)',
                  entity_id, str(new_volume_level))
    if new_volume_level >= 0 and new_volume_level != current_volume_level:
        _LOGGER.debug(' - Seting volume_level of media player "%s" to: %s', entity_id, str(new_volume_level))
        await hass.services.async_call(
            "media_player",
            "volume_set",
            {
                ATTR_MEDIA_VOLUME_LEVEL: new_volume_level,
                CONF_ENTITY_ID: entity_id
            },
            True,
        )
        _LOGGER.debug(' - Completed')
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
    _LOGGER.debug('key:   "%s"', key)
    _LOGGER.debug('value: "%s"', value)
    _data[DATA_STORAGE_KEY][key] = value
    await async_save_data(hass)


async def async_retrieve_data(key: str):
    """Retrieve a value from the integration's stored data based on the provided key."""
    if key in _data[DATA_STORAGE_KEY]:
        _LOGGER.debug("Retrieving key/value from chime_tts storage:")
        _LOGGER.debug("key: %s", key)
        _LOGGER.debug("value: %s", str(_data[DATA_STORAGE_KEY][key]))
        return str(_data[DATA_STORAGE_KEY][key])
    return None


async def async_save_data(hass: HomeAssistant):
    """Save the provided data to the integration's stored data."""
    store = storage.Store(hass, 1, DATA_STORAGE_KEY)
    await store.async_save(_data[DATA_STORAGE_KEY])


async def async_get_cached_path(hass: HomeAssistant, filepath_hash: str):
    """Return the valid filepath for TTS audio previously stored in the filesystem's cache."""
    _LOGGER.debug(
        "async_get_cached_path('%s')", filepath_hash)
    cached_path = await async_retrieve_data(filepath_hash)
    if cached_path is not None:
        if os.path.exists(str(cached_path)):
            _LOGGER.debug("Returning cached filepath: '%s'", cached_path)
            return str(cached_path)
        _LOGGER.debug(" - Cached filepath does not exist.")
    else:
        _LOGGER.debug(" - Filepath not found in cache.")
    await async_remove_cached_path(hass, filepath_hash)
    return None


async def async_remove_cached_path(hass: HomeAssistant, filepath_hash: str):
    """Remove filepath key/value from Chime TTS cache and delete filepath from filesystem."""
    cached_path = await async_retrieve_data(filepath_hash)
    if cached_path is not None:
        if str(cached_path).startswith(TEMP_PATH) or str(cached_path).startswith(TTS_PATH):
            if os.path.exists(cached_path):
                os.remove(str(cached_path))
                _LOGGER.debug(
                    " - Cached file '%s' deleted successfully.", str(cached_path))
            else:
                _LOGGER.debug(
                    " - Unable to delete cached file '%s'.", str(cached_path))
        _data[DATA_STORAGE_KEY].pop(filepath_hash)

        await async_save_data(hass)


################################
### Audio Filename Functions ###
################################

def get_filename(params: dict, is_generated: bool):
    """Generate a unique filename based on specific parameters."""
    filename = ""
    relevant_params = ["message", "tts_platform", "gender", "tld", "language"]
    if is_generated is True:
        relevant_params.extend(
            ["chime_path", "end_chime_path", "delay", "tts_playback_speed"])
    for param in relevant_params:
        if params[param] is not None:
            filename = filename + "-" + str(params[param])
    return filename


def get_tts_filename(params: dict):
    """Generate a unique TTS filename based on specific parameters."""
    return get_filename(params, False)


def get_generated_filename(params: dict):
    """Generate a unique generated filename based on specific parameters."""
    return get_filename(params, True)


def get_filename_hash(string: str):
    """Generate a hash from a filename string."""
    hash_object = hashlib.sha256()
    hash_object.update(string.encode('utf-8'))
    hash_value = str(hash_object.hexdigest())
    return hash_value

##############################
### Misc. Helper Functions ###
##############################

def get_supported_feature(entity: State, feature: str):
    """Whether a feature is supported by the media_player device."""
    if entity is None or entity.attributes is None:
        return False
    supported_features = entity.attributes.get('supported_features', 0)
    if feature is ATTR_MEDIA_VOLUME_LEVEL:
        return bool(supported_features & 2)
    return False

def sleep(duration: float):
    """Make a synchronous time.sleep call."""
    return time.sleep(duration)
