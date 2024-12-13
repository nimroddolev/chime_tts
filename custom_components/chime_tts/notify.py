"""Chime TTS Notify."""

import logging
from .const import (
    DOMAIN,
    SERVICE_SAY
)
from .helpers.helpers import ChimeTTSHelper
from homeassistant.components.notify import BaseNotificationService
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)
helpers = ChimeTTSHelper()

async def async_get_service(hass: HomeAssistant, config, _discovery_info):
    """Retrieve instance of ChimeTTSNotificationService class."""
    _config = config or {}
    return ChimeTTSNotificationService(hass, config)

class ChimeTTSNotificationService(BaseNotificationService):
    """Chime TTS Notify Service class."""

    def __init__(self, hass: HomeAssistant, config: any):
        """Initialize the Chime TTS Notify Service."""
        self.hass = hass
        self._config = config

    async def async_send_message(self, message="", **kwargs):
        """Send a notification with the Chime TTS Notify Service."""
        kwargs["message"] = message
        data = kwargs.get("data", {}) or {}

        for key in [
            "entity_id",
            "chime_path",
            "end_chime_path",
            "offset",
            "crossafade",
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
            kwargs[key] = data.get(key, self._config.get(key))

        helpers.debug_title("Chime TTS Notify")
        for key, value in kwargs.items():
            _LOGGER.debug(f" - {key} = '{value}'" if isinstance(value, str) else f" - {key} = {value}")

        try:
            await self.hass.services.async_call(
                domain=DOMAIN,
                service=SERVICE_SAY,
                service_data=kwargs,
                blocking=True)
        except Exception as error:
            _LOGGER.error("Service `chime_tts.say` error: %s", error)
