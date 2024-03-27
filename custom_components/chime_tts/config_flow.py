"""Adds config flow for Chime TTS."""
import logging
import os
import requests
import voluptuous as vol
from homeassistant import config_entries
from .const import (
    DOMAIN,
    QUEUE_TIMEOUT_KEY,
    QUEUE_TIMEOUT_DEFAULT,
    TTS_PLATFORM_KEY,
    OFFSET_KEY,
    DEFAULT_OFFSET_MS,
    MEDIA_DIR_KEY,
    MEDIA_DIR_DEFAULT,
    TEMP_CHIMES_PATH_KEY,
    TEMP_CHIMES_PATH_DEFAULT,
    TEMP_PATH_KEY,
    TEMP_PATH_DEFAULT,
    WWW_PATH_KEY,
    WWW_PATH_DEFAULT,
    MP3_PRESET_CUSTOM_PREFIX
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

        # Installed TTS Providers
        tts_providers = list((self.hass.data["tts_manager"].providers).keys())

        # Installed TTS Platform Entities
        tts_entities = []
        all_entities = self.hass.states.async_all()
        for entity in all_entities:
            if str(entity.entity_id).startswith("tts."):
                tts_entities.append(str(entity.entity_id))

        # TTS Platforms
        tts_platforms = tts_providers + tts_entities
        LOGGER.debug("```Installed TTS platforms: %s", str(tts_platforms))
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

    def __init__(self, config_entry: config_entries.ConfigEntry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input={}):
        """Initialize the options flow."""

        installed_tts = self.get_installed_tts()
        default_tts = installed_tts[0] if len(installed_tts) > 0 else ""
        user_input = user_input if user_input is not None else {}
        root_path = self.hass.config.path("").replace("/config/", "")

        options_schema = vol.Schema(
            {
                vol.Required(
                    QUEUE_TIMEOUT_KEY,
                    default=self.get_data_key_value(QUEUE_TIMEOUT_KEY,
                                                    user_input.get(QUEUE_TIMEOUT_KEY, QUEUE_TIMEOUT_DEFAULT))  # type: ignore
                ): int,
                vol.Optional(
                    TTS_PLATFORM_KEY,
                    default=self.get_data_key_value(TTS_PLATFORM_KEY,
                                                    user_input.get(TTS_PLATFORM_KEY, default_tts)),  # type: ignore
                ): str,
                vol.Optional(
                    OFFSET_KEY,
                    default=self.get_data_key_value(OFFSET_KEY,
                                                    user_input.get(OFFSET_KEY, DEFAULT_OFFSET_MS)),  # type: ignore
                ): int,
                vol.Required(
                    MEDIA_DIR_KEY,
                    default=self.get_data_key_value(MEDIA_DIR_KEY,
                                                    user_input.get(MEDIA_DIR_KEY, MEDIA_DIR_DEFAULT)),  # type: ignore
                ): str,
                vol.Required(
                    TEMP_CHIMES_PATH_KEY,
                    default=self.get_data_key_value(TEMP_CHIMES_PATH_KEY,
                                                    user_input.get(TEMP_CHIMES_PATH_KEY, f"{root_path}{TEMP_CHIMES_PATH_DEFAULT}")),  # type: ignore
                ): str,
                vol.Required(
                    TEMP_PATH_KEY,
                    default=self.get_data_key_value(TEMP_PATH_KEY,
                                                    user_input.get(TEMP_PATH_KEY, f"{root_path}{TEMP_PATH_DEFAULT}")),  # type: ignore
                ): str,
                vol.Required(
                    WWW_PATH_KEY,
                    default=self.get_data_key_value(WWW_PATH_KEY,
                                                    user_input.get(WWW_PATH_KEY, f"{root_path}{WWW_PATH_DEFAULT}")),  # type: ignore
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
        if user_input is None or user_input == {}:
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

        # Default TTS Platform
        if user_input[TTS_PLATFORM_KEY] is not None and len(user_input[TTS_PLATFORM_KEY]) > 0:
            default_tts_provider = user_input[TTS_PLATFORM_KEY]
            installed_tts = self.get_installed_tts()
            if len(installed_tts) == 0:
                 _errors[TTS_PLATFORM_KEY] = "default_tts_platform_none"
            else:
                tts_provider_installed = default_tts_provider in installed_tts
                tts_entity_exists = self.hass.states.get(default_tts_provider) is not None
                if not (tts_provider_installed or tts_entity_exists):
                    _errors[TTS_PLATFORM_KEY] = "default_tts_platform_select"

        # Folder path used for `chime_tts.say_url`
        www_path: str = user_input.get(WWW_PATH_KEY, "")
        if not (www_path.startswith(f"{root_path}/media/") != -1 or
                www_path.startswith(f"{root_path}/config/www/") != -1):
            _errors["www_path"] = "www_path"

        # Custom chime mp3 paths
        for i in range(5):
            key = MP3_PRESET_CUSTOM_PREFIX + str(i + 1)
            value = user_input.get(key, " ")
            LOGGER.debug("%s = %s", key, str(value))
            if value is not None and value != "" and len(value) > 2:

                # URL valid?
                is_valid_url = True
                is_url = value.startswith("http://") or value.startswith("https://")
                if is_url:
                    is_valid_url = await self.ping_url(value)
                    if is_valid_url is False:
                        LOGGER.warning("Cannot load chime URL: %s", value)

                # File not found?
                local_file_valid = os.path.exists(value)

                if (local_file_valid or is_valid_url) is False:
                    # Set main error message
                    if not _errors:
                        _errors["base"] = "invalid_chime_paths"
                    else:
                        _errors["base"] = "multiple"
                    # Add specific custom chime error
                    _errors[key] = key
        if _errors:
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

    def get_installed_tts(self):
        """List of installed TTS platforms."""
        return list((self.hass.data["tts_manager"].providers).keys())
