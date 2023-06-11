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

from .const import DOMAIN, SERVICE_SAY, PAUSE_DURATION_MS

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
        end_chime_path = service.data.get("end_chime_path", "")
        delay = service.data.get("delay", PAUSE_DURATION_MS)
        message = service.data.get("message", "")
        tts_platform = service.data.get("tts_platform", "")
        entity_id = service.data.get(CONF_ENTITY_ID, "")
        initial_volume_level = get_initial_volume_level(hass, entity_id)
        volume_level = service.data.get(ATTR_MEDIA_VOLUME_LEVEL, -1)

        # Create audio file to play on media player
        audio_path = get_playback_audio_path(
            chime_path,
            end_chime_path,
            delay,
            tts_platform,
            message
        )
        if audio_path is False:
            return False

        # Set volume to desired level
        set_volume_level(entity_id, volume_level)

        # Play the audio on the media player
        hass.services.call(
            "media_player",
            "play_media",
            {
                ATTR_MEDIA_CONTENT_ID: audio_path,
                ATTR_MEDIA_CONTENT_TYPE: MEDIA_TYPE_MUSIC,
                CONF_ENTITY_ID: entity_id,
            },
            True,
        )
        delay = _data["delay"]
        time.sleep(delay)

        # Reset media player volume level
        set_volume_level(entity_id, initial_volume_level)

        return True

    def get_audio_from_path(path, delay=0, audio=None):
        """Add audio from a given file path to existing audio (optional) with delay (optional)."""
        if path and len(path) > 0:
            audio_from_path = AudioSegment.from_mp3(path)
            if audio_from_path is not None:
                if audio is None:
                    return audio_from_path
                else:
                    return audio + (AudioSegment.silent(duration=delay) + audio_from_path)
            else:
                _LOGGER.warn("Unable to find audio at path: %s", path)
        return audio

    def get_playback_audio_path(chime_path, end_chime_path, delay, tts_platform, message):
        """Create audio to play on media player entity."""
        # Load chime audio
        output_audio = get_audio_from_path(chime_path)

        # Load TTS audio
        if message and len(message) > 0:
            tts_data = {
                "tts_platform": tts_platform,
                "message": message,
                "hass": hass,
            }
            tts_audio_path = get_tts_audio_path(tts_data)
            if tts_audio_path is not False:
                output_audio = get_audio_from_path(
                    tts_audio_path, delay, output_audio)
            else:
                _LOGGER.warn("Unable to create/locate TTS audio file path")

        # Load end chime audio
        output_audio = get_audio_from_path(end_chime_path, delay, output_audio)
        _data["delay"] = float(len(output_audio) / 1000.0)

        # Save temporary MP3 file
        output_path = tempfile.NamedTemporaryFile(suffix=".mp3").name
        output_audio.export(output_path, format="mp3")
        return output_path

    def get_tts_audio_path(tts_data):
        """Request TTS audio and return local file path to TTS audio file."""
        message = str(tts_data["message"])
        tts_platform = str(tts_data["tts_platform"])
        if message is False or message == "":
            _LOGGER.warn("No message text provided for TTS audio")
            return False
        if tts_platform is False or tts_platform == "":
            _LOGGER.warn("No TTS platform selected")
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
            _LOGGER.info("TTS retrieved. Path: %s", path)
            return path
        else:
            _LOGGER.warn(
                'tts_get_url request failed. Response: "%s"', str(response.text))
            return False

    def get_initial_volume_level(hass, entity_id):
        """Get the current volume level of a given media player entity."""
        entity = hass.states.get(entity_id)
        if entity is None:
            _LOGGER.error('Media player entity: "%s" not found', entity_id)
            return -1

        # Ensure media player is on
        if entity.state == "off":
            _LOGGER.info('Turning on media player entity: "%s"', entity_id)
            hass.services.call(
                "media_player", "turn_on", {CONF_ENTITY_ID: entity_id}, True
            )

        # Get current volume level
        if hasattr(entity, "attributes"):
            volume_level = entity.attributes.get(ATTR_MEDIA_VOLUME_LEVEL)
            if volume_level is not None:
                return volume_level
            else:
                _LOGGER.warn(
                    'Unable to get current volume for media player entity: "%s"', entity_id)
                return -1

    def set_volume_level(entity_id, new_volume_level):
        """Set the volume_level for a given media player entity."""
        if new_volume_level >= 0:
            hass.services.call(
                "media_player",
                "volume_set",
                {ATTR_MEDIA_VOLUME_LEVEL: new_volume_level,
                    CONF_ENTITY_ID: entity_id},
                True,
            )
            return True
        return False

    hass.services.register(DOMAIN, SERVICE_SAY, tts_platform)
    return True
