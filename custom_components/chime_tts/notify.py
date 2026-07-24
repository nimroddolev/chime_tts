"""Chime TTS Notify."""

import logging
from .const import (
    DOMAIN,
    SERVICE_SAY
)
from .helpers.helpers import ChimeTTSHelper
from .helpers.panel_logs import (
    build_notification_event_details,
    finish_panel_log_event,
    start_panel_log_event,
)
from . import (
    ACTIVE_NOTIFY_LOG_EVENT_ID,
    INTERNAL_NOTIFY_LOG_EVENT_ID,
    INTERNAL_NOTIFY_ORIGIN,
)
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
        original_kwargs = dict(kwargs)
        data = kwargs.get("data", {}) or {}
        notify_name = str(self._config.get("name") or "profile")
        notify_event_id = start_panel_log_event(
            self.hass,
            "notification_call",
            "Notification profile call",
            row_color="action",
            details=build_notification_event_details(notify_name, original_kwargs),
            summary=f"notify.{notify_name}",
        )
        self.hass.data[DOMAIN][ACTIVE_NOTIFY_LOG_EVENT_ID] = notify_event_id

        for key in [
            "entity_id",
            "chime_path",
            "end_chime_path",
            "offset",
            "crossfade",
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
            "audio_conversion",
            "pre_script",
            "post_script",
        ]:
            kwargs[key] = data.get(key, self._config.get(key))

        if kwargs.get("crossfade") in (None, ""):
            kwargs["crossfade"] = data.get(
                "crossafade",
                self._config.get("crossafade"),
            )

        helpers.debug_title("Chime TTS Notify")
        for key, value in kwargs.items():
            _LOGGER.debug(f" - {key} = '{value}'" if isinstance(value, str) else f" - {key} = {value}")

        try:
            service_data = {
                **kwargs,
                INTERNAL_NOTIFY_ORIGIN: True,
                INTERNAL_NOTIFY_LOG_EVENT_ID: notify_event_id,
            }
            await self.hass.services.async_call(
                domain=DOMAIN,
                service=SERVICE_SAY,
                service_data=service_data,
                blocking=True)
        except Exception as error:
            _LOGGER.error("Service `chime_tts.say` error: %s", error)
        finally:
            self.hass.data[DOMAIN].pop(ACTIVE_NOTIFY_LOG_EVENT_ID, None)
            finish_panel_log_event(self.hass, notify_event_id)
