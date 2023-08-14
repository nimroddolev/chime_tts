"""Adds config flow for Chime TTS."""
from homeassistant import config_entries
from .const import DOMAIN

@config_entries.HANDLERS.register(DOMAIN)

class ChimeTTSFlowHandler(config_entries.ConfigFlow):
    """Config flow for Chime TTS."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Chime TTS async_step_user."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        return self.async_create_entry(title="Chime TTS", data={})
