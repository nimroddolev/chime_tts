"""Adds config flow for Chime TTS."""
import logging
from homeassistant import config_entries

from .helpers.helpers import ChimeTTSHelper
from .const import (
    DOMAIN,
    VERSION,
)
from .settings import build_options_schema, validate_settings

LOGGER = logging.getLogger(__name__)
helpers = ChimeTTSHelper()

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
        helpers.debug_title(f"Adding Chime TTS Version {VERSION}")

        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        tts_platforms = helpers.get_installed_tts_platforms(self.hass)
        if len(tts_platforms) == 0:
            LOGGER.debug("No TTS Platforms detected")
            return self.async_show_form(
                        step_id="no_tts_platforms",
                        data_schema=None,
                        description_placeholders=user_input,
                        last_step=True
                    )

        return self.async_create_entry(title="Chime TTS", data={})


    async def async_step_no_tts_platforms(self, user_input=None):
        """Warn the user that no TTS platforms are installed."""
        return self.async_create_entry(title="Chime TTS", data={})

class ChimeTTSOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow Chime TTS integration."""

    data: dict

    def __init__(self, config_entry: config_entries.ConfigEntry):
        """Initialize options flow."""
        helpers.debug_title(f"Chime TTS Version {VERSION} Configuration")
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Initialize the options flow."""
        options_schema = build_options_schema(self.hass, self._config_entry, user_input)
        # Display the configuration form with the current values
        if not user_input:
            return self.async_show_form(
                step_id="init",
                data_schema=options_schema,
                description_placeholders=user_input,
                last_step=True,
            )

        validation = validate_settings(self.hass, self._config_entry, user_input)
        self.data = validation.data

        if validation.errors:
            return self.async_show_form(
                step_id="init", data_schema=options_schema, errors=validation.errors
            )

        # 1st time Custom Chimes Folder path modified
        if validation.restart_required:
            # Show restart reminder step before saving config
            return self.async_show_form(
                step_id="restart_required",
                    data_schema=None,
                    description_placeholders=user_input,
                    last_step=True
                )

        # User input is valid, update the options
        LOGGER.debug("Updating configuration...")
        return self.async_create_entry(
            data=self.data
        )

    async def async_step_restart_required(self, user_input):
        """Warn the user that Home Assistant needs to be restarted."""
        return self.async_create_entry(
            data=self.data
        )

    def get_installed_tts(self):
        """List of installed TTS platforms."""
        return list((self.hass.data["tts_manager"].providers).keys())
