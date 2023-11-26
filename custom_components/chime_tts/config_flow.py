"""Adds config flow for Chime TTS."""
from homeassistant import config_entries
from .const import DOMAIN, QUEUE_TIMEOUT_S
import voluptuous as vol
import logging
LOGGER = logging.getLogger(__name__)

@config_entries.HANDLERS.register(DOMAIN)

class ChimeTTSFlowHandler(config_entries.ConfigFlow):
    """Config flow for Chime TTS."""

    VERSION = 1

    @staticmethod
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return ChimeTTSOptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None):
        """Chime TTS async_step_user."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        return self.async_create_entry(title="Chime TTS", data={})

class ChimeTTSOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow Chime TTS integration."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Initialize the options flow."""

        # Define the options schema
        # config_options = dict(self.config_entry.options)
        config_data = dict(self.config_entry.data)

        options_schema = vol.Schema({
            vol.Required("timeout",
                         default=self.get_data_key_value("timeout", QUEUE_TIMEOUT_S) # type: ignore
            ): str
        })

        # Show the form with the current options
        if user_input is None:
            return self.async_show_form(
                step_id="init",
                data_schema=options_schema,
                description_placeholders=user_input,
                last_step=True
            )
        
        # User input is valid, update the options
        LOGGER.debug("Updating configuration...")
        # user_input = None
        return self.async_create_entry(
            data=user_input, # type: ignore
            title="",
        )

    def get_data_key_value(self, key, placeholder=None):
        """Get the value for a given key. Options flow 1st, Config flow 2nd."""
        dicts = [dict(self.config_entry.options), dict(self.config_entry.data)]
        for p_dict in dicts:
            if key in p_dict:
                return p_dict[key]
        return placeholder
