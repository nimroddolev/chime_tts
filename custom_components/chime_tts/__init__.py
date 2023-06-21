"""The Chime TTS integration."""

import logging
import tempfile
import time
import json
import os
import base64
from requests import post
from pydub import AudioSegment
from homeassistant.components.media_player.const import (
    ATTR_MEDIA_CONTENT_ID,
    ATTR_MEDIA_CONTENT_TYPE,
    ATTR_MEDIA_VOLUME_LEVEL,
    MEDIA_TYPE_MUSIC,
)
from homeassistant.const import HTTP_BEARER_AUTHENTICATION, CONF_ENTITY_ID
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.network import get_url
from homeassistant.helpers import storage
from .const import (
    DOMAIN,
    SERVICE_SAY,
    PAUSE_DURATION_MS,
    DATA_STORAGE_KEY,
    TTS_API,
    TIMEOUT
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

    async def async_say(service):
        """Play TTS audio with local chime MP3 audio."""
        _LOGGER.debug('async_say(service)')
        chime_path = str(service.data.get("chime_path", ""))
        end_chime_path = str(service.data.get("end_chime_path", ""))
        delay = float(service.data.get("delay", PAUSE_DURATION_MS))
        message = str(service.data.get("message", ""))
        tts_platform = str(service.data.get("tts_platform", ""))
        entity_id = str(service.data.get(CONF_ENTITY_ID, ""))
        volume_level = float(service.data.get(ATTR_MEDIA_VOLUME_LEVEL, -1))

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
        if volume_level >= 0:
            if hasattr(entity, "attributes") and ATTR_MEDIA_VOLUME_LEVEL in dict(entity.attributes):
                if entity.attributes.get(ATTR_MEDIA_VOLUME_LEVEL) > 0:
                    initial_volume_level = entity.attributes.get(
                        ATTR_MEDIA_VOLUME_LEVEL)
                else:
                    _LOGGER.warning(
                        'Unable to get volume for media player entity: "%s"', entity_id)
            else:
                _LOGGER.warning(
                    'Media player entity "%s" does not have attributes', entity_id)

        # Create audio file to play on media player
        params = {
            "hass": hass,
            "chime_path": chime_path,
            "end_chime_path": end_chime_path,
            "delay": delay,
            "tts_platform": tts_platform,
            "message": message
        }
        audio_path = await async_get_playback_audio_path(params)
        if audio_path is None:
            _LOGGER.error("Unable to create audio for playback")
            return False

        # Set volume to desired level
        await async_set_volume_level(hass, entity_id, volume_level)

        # Play the audio on the media player
        _LOGGER.debug('Playing media...')
        _LOGGER.debug('  - audio_path = "%s"', audio_path)
        _LOGGER.debug('  - entity_id = "%s"', entity_id)
        await hass.services.async_call(
            "media_player",
            "play_media",
            {
                ATTR_MEDIA_CONTENT_ID: audio_path,
                ATTR_MEDIA_CONTENT_TYPE: MEDIA_TYPE_MUSIC,
                CONF_ENTITY_ID: entity_id,
            },
            True,
        )
        _LOGGER.debug('...media finished playback:')

        # Wait for audio to finish playing
        # time.sleep(_data["delay"])
        await hass.async_add_executor_job(sleep, _data["delay"])

        # Reset media player volume level
        if initial_volume_level != -1:
            await async_set_volume_level(hass, entity_id, initial_volume_level)

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

async def async_request_tts_audio_filepath(hass: HomeAssistant, tts_platform: str, message: str):
    """Send an API request for TTS audio and return the audio file's local filepath."""
    # Data validation
    _LOGGER.debug(
        'async_request_tts_audio_filepath(hass, tts_platform="%s", message="%s")',
        tts_platform, message)
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

    headers = {
        "Authorization": "Bearer " + str(bearer_token),
        "Content-Type": "application/json",
    }
    data = (
        '{"message": '
        + json.dumps(str(message))
        + ', "platform": "'
        + str(tts_platform)
        + '", "cache": true}'
    )

    # Redact bearer_token before writing log message
    if len(bearer_token) <= 10:
        redacted_bearer_token = "##########"
    else:
        redacted_bearer_token = bearer_token[:5] + \
            '#'*10 + bearer_token[-5:]
    redacted_headers = str(headers).replace(
        bearer_token, redacted_bearer_token)
    _LOGGER.debug(' - Requesting TTS audio:')
    _LOGGER.debug('  - url     = %s', url)
    _LOGGER.debug('  - headers = %s', redacted_headers)
    _LOGGER.debug('  - data    = %s', str(data))
    _LOGGER.debug('  - timeout = %s', str(TIMEOUT))

    response = await hass.async_add_executor_job(post_request, url, headers, data, TIMEOUT)
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
    message = params["message"]
    _data["delay"] = 0

    _LOGGER.debug(
        'async_get_playback_audio_path(params=%s)', str(params))
    # Load chime audio
    output_audio = get_audio_from_path(chime_path)

    # Load TTS audio

    # Check if TTS file file exists in cache
    filename = tts_platform + "-" + message
    filename_bytes = filename.encode('ascii')
    base64_bytes = base64.b64encode(filename_bytes)
    base64_filename = base64_bytes.decode('ascii')
    tts_audio_path = await async_get_tts_cache_path(base64_filename)

    if tts_audio_path is None:
        # tts_audio_path = request_tts_audio_filepath(hass, tts_platform, message)
        tts_audio_path = await async_request_tts_audio_filepath(hass, tts_platform, message)
        _LOGGER.debug(
            " - %s REST API request returned tts_audio_path: '%s'", TTS_API, tts_audio_path)
        if tts_audio_path is not None:
            await async_store_data(hass, base64_filename, tts_audio_path)
    else:
        _LOGGER.debug(" - Using cached TTS mp3 filepath")

    output_audio = get_audio_from_path(
        tts_audio_path, delay, output_audio)

    # Load end chime audio
    output_audio = get_audio_from_path(end_chime_path, delay, output_audio)
    if output_audio is not None:
        duration = float(len(output_audio) / 1000.0)
        _data["delay"] = duration
        _LOGGER.debug(" - Final audio created with duration = %ss", duration)

        # Save temporary MP3 file
        output_path = tempfile.NamedTemporaryFile(suffix=".mp3").name
        output_audio.export(output_path, format="mp3")
        return output_path

    return None


def get_audio_from_path(filepath: str, delay=0, audio=None):
    """Add audio from a given file path to existing audio (optional) with delay (optional)."""
    filepath = str(filepath)
    _LOGGER.debug('get_audio_from_path("%s", %s, audio)', filepath, str(delay))

    if (filepath is None) or (filepath == "None") or (len(filepath) == 0):
        _LOGGER.debug('No filepath provided')
        return audio
    if not os.path.exists(filepath):
        _LOGGER.warning('Audio filepath does not exist: "%s"', str(filepath))
        return audio

    _LOGGER.debug('Retrieving audio from path: "%s"...', filepath)
    audio_from_path = AudioSegment.from_file(filepath)
    if audio_from_path is not None:
        _LOGGER.debug(' - ...audio retrieved successfully')
        if audio is None:
            return audio_from_path
        return (audio + (AudioSegment.silent(duration=delay) + audio_from_path))
    _LOGGER.warning("...unable to find audio from filepath")
    return audio


async def async_set_volume_level(hass: HomeAssistant, entity_id: str, new_volume_level=0):
    """Set the volume_level for a given media player entity."""
    new_volume_level = float(new_volume_level)
    _LOGGER.debug(' - async_set_volume_level("%s", %s)',
                  entity_id, str(new_volume_level))
    if new_volume_level >= 0:
        _LOGGER.debug(' - Seting volume_level of media player "%s" to: %s',
                      entity_id, str(new_volume_level))
        await hass.services.async_call(
            "media_player",
            "volume_set",
            {ATTR_MEDIA_VOLUME_LEVEL: new_volume_level,
                CONF_ENTITY_ID: entity_id},
            True,
        )
        _LOGGER.debug(' - async_set_volume_level: completed')
        return True
    _LOGGER.debug(' - async_set_volume_level: Skipped setting volume')
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


async def async_get_tts_cache_path(base64_filename: str):
    """Return the valid filepath for TTS audio previously stored in the filesystem's cache."""
    _LOGGER.debug(
        "async_get_tts_cache_path('%s')", base64_filename)
    cached_path = await async_retrieve_data(base64_filename)
    if cached_path is not None:
        _LOGGER.debug(
            " - async_get_tts_cache_path('%s') returned value: '%s'", base64_filename, cached_path)
        return cached_path
    else:
        _LOGGER.debug(" - TTS file does not exist in cache.")
    return None


##############################
### Misc. Helper Functions ###
##############################

def sleep(duration: float):
    """Make a synchronous time.sleep call."""
    return time.sleep(duration)
