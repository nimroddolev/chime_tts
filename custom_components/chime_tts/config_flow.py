"""Adds config flow for Chime TTS."""
from homeassistant import config_entries
from .const import(
    DOMAIN,
    QUEUE_TIMEOUT_KEY,
    QUEUE_TIMEOUT_DEFAULT,
    MEDIA_DIR_KEY,
    MEDIA_DIR_DEFAULT,
    TEMP_PATH_KEY,
    TEMP_PATH_DEFAULT,
    WWW_PATH_KEY,
    WWW_PATH_DEFAULT)
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

        options_schema = vol.Schema({
            vol.Required(QUEUE_TIMEOUT_KEY,
                         default=self.get_data_key_value(QUEUE_TIMEOUT_KEY, QUEUE_TIMEOUT_DEFAULT) # type: ignore
            ): int,
            vol.Required(MEDIA_DIR_KEY,
                         default=self.get_data_key_value(MEDIA_DIR_KEY, MEDIA_DIR_DEFAULT) # type: ignore
            ): str,
            vol.Required(TEMP_PATH_KEY,
                         default=self.get_data_key_value(TEMP_PATH_KEY, TEMP_PATH_DEFAULT) # type: ignore
            ): str,
            vol.Optional(WWW_PATH_KEY,
                         default=self.get_data_key_value(WWW_PATH_KEY, WWW_PATH_DEFAULT) # type: ignore
            ): str,
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
