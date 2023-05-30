"""The Chime TTS integration."""

import logging
import tempfile
import time
import requests
import json

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

from .const import DOMAIN, SERVICE_SAY

_LOGGER = logging.getLogger(__name__)
_data = {}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up an entry."""
    _data[HTTP_BEARER_AUTHENTICATION] = entry.data[HTTP_BEARER_AUTHENTICATION]
    return True


def setup(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the Chime TTS integration."""
    _LOGGER.info("The Chime TTS integration is set up.")

    def tts_platform(service):
        chime_path = service.data.get("chime_path", "")
        message = service.data.get("message", "")
        end_chime_path = service.data.get("end_chime_path", "")
        tts_platform = service.data.get("tts_platform", "")
        entity_id = service.data.get(CONF_ENTITY_ID, "")
        initial_volume_level = get_initial_volume_level(hass, entity_id)
        volume_level = service.data.get(ATTR_MEDIA_VOLUME_LEVEL, -1)

        # Create audio file to play on media player
        audio_dict = init_playback_audio(
            chime_path, end_chime_path, tts_platform, message
        )
        if audio_dict is False:
            return False
        audio_path = audio_dict["output_path"]
        audio_length = audio_dict["output_length"]

        set_volume_level(entity_id, volume_level)

        # Play the audio on the media player
        play_chime_tts_audio(entity_id, audio_path)

        # Reset media player volume level
        set_volume_level(entity_id, initial_volume_level, audio_length)

        return True

    def get_audio_from_path(path):
        if path and len(path) > 0:
            return AudioSegment.from_mp3(path)
        else:
            return None

    def init_playback_audio(chime_path, end_chime_path, tts_platform, message):
        output_path = tempfile.NamedTemporaryFile(suffix=".mp3").name

        # Load chime audio
        audio_arr = [get_audio_from_path(chime_path)]

        # Load TTS audio
        if message and len(message) > 0:
            tts_data = {
                "tts_platform": tts_platform,
                "message": message,
                "hass": hass,
            }
            tts_audio_path = get_tts_audio_path(tts_data)
            if tts_audio_path is not False:
                audio_arr.append(get_audio_from_path(tts_audio_path))
            else:
                _LOGGER.warn("Unable to create/locate TTS audio file path")

        # Load end chime audio
        audio_arr.append(get_audio_from_path(end_chime_path))

        # Assemble audio
        output_audio = None
        for audio in audio_arr:
            if audio:
                if output_audio is None:
                    output_audio = audio
                else:
                    output_audio = output_audio + audio

        # Save temporary MP3 file
        output_audio.export(output_path, format="mp3")
        output_length = float(len(output_audio) / 1000.0)

        return {"output_path": output_path, "output_length": output_length}

    def play_chime_tts_audio(entity_id, audio_path):
        hass.services.call(
            "media_player",
            "play_media",
            {
                ATTR_MEDIA_CONTENT_ID: audio_path,
                ATTR_MEDIA_CONTENT_TYPE: MEDIA_TYPE_MUSIC,
                CONF_ENTITY_ID: entity_id,
            },
            False,
        )

    def get_tts_audio_path(tts_data):
        message = str(tts_data["message"])
        tts_platform = str(tts_data["tts_platform"])
        if message is False or message == "":
            _LOGGER.warn("No text provided for TTS audio")
            return False
        if tts_platform is False or tts_platform == "":
            _LOGGER.warn("No TTS platform was provided")
            return False

        hass = tts_data["hass"]
        instance_url = str(get_url(hass))
        url = instance_url + "/api/tts_get_url"
        bearer_token = _data[HTTP_BEARER_AUTHENTICATION]
        headers = {
            "Authorization": "Bearer " + str(bearer_token),
            "Content-Type": "application/json",
        }
        data = (
            '{"message": '
            + json.dumps(str(tts_data["message"]))
            + ', "platform": "'
            + str(tts_data["tts_platform"])
            + '", "cache": true}'
        )

        response = requests.post(url, headers=headers, data=data)

        response_json = response.json()
        if response.status_code == 200:
            temp_string = response_json["path"]
            arr = temp_string.split("/")
            path = "/config/tts/" + arr[len(arr) - 1]
            return path
        else:
            _LOGGER.warn(
                'tts_get_url request failed. Response: "' + str(response.text) + '"'
            )
            return False

    def get_initial_volume_level(hass, entity_id):
        entity = hass.states.get(entity_id)
        if entity is None:
            _LOGGER.error("Media player entity: '" + entity_id + "' was not found")
            return -1

        # Ensure media player is on
        if entity.state == "off":
            _LOGGER.info("Turning on media player '" + entity_id + "'")
            hass.services.call(
                "media_player", "turn_on", {CONF_ENTITY_ID: entity_id}, False
            )
            time.sleep(1.5)

        # Get current volume level
        if hasattr(entity, "attributes"):
            volume_level = entity.attributes.get(ATTR_MEDIA_VOLUME_LEVEL)
            if volume_level is not None:
                return volume_level
            else:
                _LOGGER.warn(
                    "Unable to get current volume for media player '" + entity_id + "'"
                )
                return -1

    def set_volume_level(entity_id, volume_level, delay=0):
        if volume_level is None or volume_level < 0:
            return False

        time.sleep(max(0, delay))

        hass.services.call(
            "media_player",
            "volume_set",
            {ATTR_MEDIA_VOLUME_LEVEL: volume_level, CONF_ENTITY_ID: entity_id},
            False,
        )
        return True

    hass.services.register(DOMAIN, SERVICE_SAY, tts_platform)
    return True
