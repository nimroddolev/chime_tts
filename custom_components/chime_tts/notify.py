"""Chime TTS Notify."""

import logging
from .const import (
    DOMAIN,
    SERVICE_SAY
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.notify import BaseNotificationService
from homeassistant.core import HomeAssistant
from homeassistant import exceptions

_LOGGER = logging.getLogger(__name__)

async def async_get_service(hass: HomeAssistant, config, discovery_info=None):
    """Retrieve instance of ChimeTTSNotificationService class."""
    _config = config
    return ChimeTTSNotificationService(hass, config)

class ChimeTTSNotificationService(BaseNotificationService):
    """Chime TTS Notify Service class."""

    def __init__(self, hass: HomeAssistant, config: ConfigEntry = {}):
        """Initialize the Chime TTS Notify Service."""
        self.hass = hass
        self._config = config

    async def async_send_message(self, message="", **kwargs):
        """Send a notification with the Chime TTS Notify Service."""
        kwargs["message"] = message
        data = kwargs.get("data", {})

        for key in [
            "entity_id",
            "chime_path",
            "end_chime_path",
            "offset",
            "final_delay",
            "tts_platform",
            "tts_speed",
            "tts_pitch",
            "volume_level",
            "join_players",
            "unjoin_players",
            "cache",
            "announce",
            "fade_audio",
            "language",
            "tld",
            "voice",
            "options",
            "audio_conversion"
        ]:
            if key in self._config:
                kwargs[key] = self._config.get(key)
            # Override parameters from data dictionary
            if data and key in data:
                kwargs[key] = data[key]

        _LOGGER.debug("----- Chime TTS Notify -----")
        for key in kwargs:
            value = kwargs[key]
            quote = "'" if isinstance(value, str) else ""
            _LOGGER.debug(" - %s = %s%s%s", key, quote, str(value), quote)

        try:
            await self.hass.services.async_call(
                domain=DOMAIN,
                service=SERVICE_SAY,
                service_data=kwargs,
                blocking=True)
        except exceptions.ServiceNotFound as error:
            _LOGGER.error("Service `chime_tts.say` not found: %s", error)
        except exceptions.CallNotAvailable as error:
            _LOGGER.error("Service `chime_tts.say` not available: %s", error)
        except Exception as error:
            _LOGGER.error("Service `chime_tts.say` error: %s", error)

