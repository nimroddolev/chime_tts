"""Adds config flow for Chime TTS."""
from homeassistant import config_entries
import requests
import voluptuous as vol
import logging
import os
from .const import (
    DOMAIN,
    QUEUE_TIMEOUT_KEY,
    QUEUE_TIMEOUT_DEFAULT,
    MEDIA_DIR_KEY,
    MEDIA_DIR_DEFAULT,
    TEMP_CHIMES_PATH_KEY,
    TEMP_CHIMES_PATH_DEFAULT,
    TEMP_PATH_KEY,
    TEMP_PATH_DEFAULT,
    WWW_PATH_KEY,
    WWW_PATH_DEFAULT,
    MP3_PRESET_CUSTOM_PREFIX,
)

LOGGER = logging.getLogger(__name__)


@config_entries.HANDLERS.register(DOMAIN)
class ChimeTTSFlowHandler(config_entries.ConfigFlow):
    """Config flow for Chime TTS."""

    VERSION = 1

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry
    ) -> config_entries.OptionsFlow:
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

        options_schema = vol.Schema(
            {
                vol.Required(
                    QUEUE_TIMEOUT_KEY,
                    default=self.get_data_key_value(
                        QUEUE_TIMEOUT_KEY, QUEUE_TIMEOUT_DEFAULT
                    ),  # type: ignore
                ): int,
                vol.Required(
                    MEDIA_DIR_KEY,
                    default=self.get_data_key_value(MEDIA_DIR_KEY, MEDIA_DIR_DEFAULT),  # type: ignore
                ): str,
                vol.Required(
                    TEMP_CHIMES_PATH_KEY,
                    default=self.get_data_key_value(TEMP_CHIMES_PATH_KEY, TEMP_CHIMES_PATH_DEFAULT),  # type: ignore
                ): str,
                vol.Required(
                    TEMP_PATH_KEY,
                    default=self.get_data_key_value(TEMP_PATH_KEY, TEMP_PATH_DEFAULT),  # type: ignore
                ): str,
                vol.Required(
                    WWW_PATH_KEY,
                    default=self.get_data_key_value(WWW_PATH_KEY, WWW_PATH_DEFAULT),  # type: ignore
                ): str,
                vol.Optional(
                    MP3_PRESET_CUSTOM_PREFIX + str(1),
                    default=self.get_data_key_value(
                        MP3_PRESET_CUSTOM_PREFIX + str(1), ""
                    ),  # type: ignore
                ): str,
                vol.Optional(
                    MP3_PRESET_CUSTOM_PREFIX + str(2),
                    default=self.get_data_key_value(
                        MP3_PRESET_CUSTOM_PREFIX + str(2), ""
                    ),  # type: ignore
                ): str,
                vol.Optional(
                    MP3_PRESET_CUSTOM_PREFIX + str(3),
                    default=self.get_data_key_value(
                        MP3_PRESET_CUSTOM_PREFIX + str(3), ""
                    ),  # type: ignore
                ): str,
                vol.Optional(
                    MP3_PRESET_CUSTOM_PREFIX + str(4),
                    default=self.get_data_key_value(
                        MP3_PRESET_CUSTOM_PREFIX + str(4), ""
                    ),  # type: ignore
                ): str,
                vol.Optional(
                    MP3_PRESET_CUSTOM_PREFIX + str(5),
                    default=self.get_data_key_value(
                        MP3_PRESET_CUSTOM_PREFIX + str(5), ""
                    ),  # type: ignore
                ): str,
            }
        )
        _errors = {}

        # Show the form with the current options
        if user_input is None:
            return self.async_show_form(
                step_id="init",
                data_schema=options_schema,
                description_placeholders=user_input,
                last_step=True,
            )

        # Validation

        # Timeout
        if user_input[QUEUE_TIMEOUT_KEY] < 0:
            _errors["base"] = "timeout"
            _errors[QUEUE_TIMEOUT_KEY] = "timeout_sub"

        # Validate custom chime mp3 paths
        for i in range(5):
            key = MP3_PRESET_CUSTOM_PREFIX + str(i + 1)
            value = user_input.get(key, "")
            if value != "":

                # URL valid?
                is_valid = False
                is_url = True if (value.startswith("http://") or value.startswith("https://")) else False
                if is_url:
                    is_valid = await self.ping_url(value)

                # File not found?
                if os.path.exists(value) is False and is_valid is False:
                    # Set main error message
                    if _errors == {}:
                        _errors["base"] = "invalid_chime_paths"
                    else:
                        _errors["base"] = "multiple"
                    # Add specific custom chime error
                    _errors[key] = key
        if _errors != {}:
            return self.async_show_form(
                step_id="init", data_schema=options_schema, errors=_errors
            )

        # User input is valid, update the options
        LOGGER.debug("Updating configuration...")
        # user_input = None
        return self.async_create_entry(
            data=user_input,  # type: ignore
            title="",
        )

    def get_data_key_value(self, key, placeholder=None):
        """Get the value for a given key. Options flow 1st, Config flow 2nd."""
        dicts = [dict(self.config_entry.options), dict(self.config_entry.data)]
        for p_dict in dicts:
            if key in p_dict:
                return p_dict[key]
        return placeholder


    async def ping_url(self, url: str):
        """Ping a URL and receive a boolean result."""
        if url is None:
            return False
        try:
            response = await self.hass.async_add_executor_job(requests.head, url)
            if 200 <= response.status_code < 300:
                return True
            LOGGER.warning("Error: Received status code %s from %s", str(response.status_code), url)
        except requests.ConnectionError:
            LOGGER.warning("Error: Failed to connect to %s", url)

        return False
