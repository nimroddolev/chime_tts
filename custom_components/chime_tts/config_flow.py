"""Adds config flow for Chime TTS."""
import logging
import requests
import os
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector

from .helpers.helpers import ChimeTTSHelper
from .const import (
    DOMAIN,
    VERSION,
    QUEUE_TIMEOUT_KEY,
    QUEUE_TIMEOUT_DEFAULT,
    TTS_TIMEOUT_KEY,
    TTS_TIMEOUT_DEFAULT,
    TTS_PLATFORM_KEY,
    DEFAULT_LANGUAGE_KEY,
    DEFAULT_VOICE_KEY,
    DEFAULT_TLD_KEY,
    FALLBACK_TTS_PLATFORM_KEY,
    OFFSET_KEY,
    DEFAULT_OFFSET_MS,
    CROSSFADE_KEY,
    FADE_TRANSITION_KEY,
    DEFAULT_FADE_TRANSITION_MS,
    REMOVE_TEMP_FILE_DELAY_KEY,
    ADD_COVER_ART_KEY,
    CUSTOM_CHIMES_PATH_KEY,
    TEMP_CHIMES_PATH_KEY,
    TEMP_CHIMES_PATH_DEFAULT,
    TEMP_PATH_KEY,
    TEMP_PATH_DEFAULT,
    WWW_PATH_KEY,
    WWW_PATH_DEFAULT,
)

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

    async def async_step_init(self, user_input):
        """Initialize the options flow."""
        # Default TTS Platform
        stripped_tts_platforms = self.get_installed_tts()
        if self.hass is not None:
            root_path = self.hass.config.path("").replace("/config/", "")
        else:
            LOGGER.warning("Unable to determine root path")
            root_path = ""

        # Installed TTS platforms
        tts_platforms = sorted(helpers.get_installed_tts_platforms(self.hass))

        # TLD Options
        tld_options = ["", "com", "co.uk", "com.au", "ca", "co.in", "ie", "co.za", "fr", "com.br", "pt", "es"]

        self.data = {
            QUEUE_TIMEOUT_KEY: self.get_data_key_value(QUEUE_TIMEOUT_KEY, user_input, QUEUE_TIMEOUT_DEFAULT),
            TTS_TIMEOUT_KEY: self.get_data_key_value(TTS_TIMEOUT_KEY, user_input, TTS_TIMEOUT_DEFAULT),
            TTS_PLATFORM_KEY: self.get_data_key_value(TTS_PLATFORM_KEY, user_input, ""),
            DEFAULT_LANGUAGE_KEY: self.get_data_key_value(DEFAULT_LANGUAGE_KEY, user_input, ""),
            DEFAULT_VOICE_KEY: self.get_data_key_value(DEFAULT_VOICE_KEY, user_input, ""),
            DEFAULT_TLD_KEY: self.get_data_key_value(DEFAULT_TLD_KEY, user_input, ""),
            FALLBACK_TTS_PLATFORM_KEY: self.get_data_key_value(FALLBACK_TTS_PLATFORM_KEY, user_input, ""),
            OFFSET_KEY: self.get_data_key_value(OFFSET_KEY, user_input, DEFAULT_OFFSET_MS),
            CROSSFADE_KEY: self.get_data_key_value(CROSSFADE_KEY, user_input, 0),
            FADE_TRANSITION_KEY: self.get_data_key_value(FADE_TRANSITION_KEY, user_input, DEFAULT_FADE_TRANSITION_MS),
            REMOVE_TEMP_FILE_DELAY_KEY: self.get_data_key_value(REMOVE_TEMP_FILE_DELAY_KEY, user_input, ""),
            CUSTOM_CHIMES_PATH_KEY: self.get_data_key_value(CUSTOM_CHIMES_PATH_KEY, user_input, ""),
            TEMP_CHIMES_PATH_KEY: self.get_data_key_value(TEMP_CHIMES_PATH_KEY, user_input, f"{root_path}{TEMP_CHIMES_PATH_DEFAULT}"),
            TEMP_PATH_KEY: self.get_data_key_value(TEMP_PATH_KEY, user_input, f"{root_path}{TEMP_PATH_DEFAULT}"),
            WWW_PATH_KEY: self.get_data_key_value(WWW_PATH_KEY, user_input, f"{root_path}{WWW_PATH_DEFAULT}"),
            ADD_COVER_ART_KEY: self.get_data_key_value(ADD_COVER_ART_KEY, user_input, False)
        }

        options_schema = vol.Schema(
            {
                vol.Required(QUEUE_TIMEOUT_KEY, default=self.data[QUEUE_TIMEOUT_KEY]): int,
                vol.Optional(TTS_TIMEOUT_KEY, default=self.data[TTS_TIMEOUT_KEY]): int,
                vol.Optional(TTS_PLATFORM_KEY, default=self.data[TTS_PLATFORM_KEY]):selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=tts_platforms,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                        custom_value=True)),
                vol.Optional(DEFAULT_LANGUAGE_KEY, description={"suggested_value": self.data[DEFAULT_LANGUAGE_KEY]}): str,
                vol.Optional(DEFAULT_VOICE_KEY, description={"suggested_value": self.data[DEFAULT_VOICE_KEY]}): str,
                vol.Optional(DEFAULT_TLD_KEY, description={"suggested_value": self.data[DEFAULT_TLD_KEY]}):selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=tld_options,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                        custom_value=False)),
                vol.Optional(FALLBACK_TTS_PLATFORM_KEY, default=self.data[FALLBACK_TTS_PLATFORM_KEY]):selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=tts_platforms,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                        custom_value=True)),
                vol.Optional(OFFSET_KEY, description={"suggested_value": self.data.get(OFFSET_KEY, DEFAULT_OFFSET_MS)}): int,
                vol.Optional(CROSSFADE_KEY, description={"suggested_value": self.data.get(CROSSFADE_KEY, 0)}): int,
                vol.Optional(FADE_TRANSITION_KEY, description={"suggested_value": self.data[FADE_TRANSITION_KEY]}): int,
                vol.Optional(REMOVE_TEMP_FILE_DELAY_KEY, description={"suggested_value": self.data[REMOVE_TEMP_FILE_DELAY_KEY]}): int,
                vol.Optional(CUSTOM_CHIMES_PATH_KEY, description={"suggested_value": self.data[CUSTOM_CHIMES_PATH_KEY]}): str,
                vol.Required(TEMP_CHIMES_PATH_KEY,default=self.data[TEMP_CHIMES_PATH_KEY]): str,
                vol.Required(TEMP_PATH_KEY,default=self.data[TEMP_PATH_KEY]): str,
                vol.Required(WWW_PATH_KEY,default=self.data[WWW_PATH_KEY]): str,
                vol.Required(ADD_COVER_ART_KEY,default=self.data[ADD_COVER_ART_KEY]): bool
            }
        )
        # Display the configuration form with the current values
        if not user_input:
            return self.async_show_form(
                step_id="init",
                data_schema=options_schema,
                description_placeholders=user_input,
                last_step=True,
            )

        # Validation

        _errors = {}

        # Timeout
        if user_input[QUEUE_TIMEOUT_KEY] < 0:
            _errors["base"] = "timeout"
            _errors[QUEUE_TIMEOUT_KEY] = "timeout_sub"

        # TTS timeout
        if user_input[TTS_TIMEOUT_KEY] < -1:
            _errors["base"] = "timeout"
            _errors[TTS_TIMEOUT_KEY] = "timeout_sub"

        # List of TTS platforms
        stripped_tts_platforms = [platform.lower().replace("tts", "").replace(" ", "").replace(" ", "").replace(".", "").replace("-", "").replace("_", "") for platform in helpers.get_installed_tts_platforms(self.hass)]

        # Default TTS Platform
        if len(user_input.get(TTS_PLATFORM_KEY, "")) > 0:

            # Replace friendly name with entity/platform name
            default_tts_provider = helpers.get_stripped_tts_platform(user_input[TTS_PLATFORM_KEY]).lower().replace("tts", "").replace(" ", "").replace(" ", "").replace(" ", "").replace(".", "").replace("-", "").replace("_", "")

            if len(stripped_tts_platforms) == 0:
                _errors[TTS_PLATFORM_KEY] = "tts_platform_none"
            elif default_tts_provider not in stripped_tts_platforms:
                LOGGER.debug("Unable to find TTS platform %s", user_input[TTS_PLATFORM_KEY])
                _errors[TTS_PLATFORM_KEY] = "tts_platform_select"
            else:
                index = stripped_tts_platforms.index(default_tts_provider)
                default_tts_provider = helpers.get_installed_tts_platforms(self.hass)[index]

            user_input[TTS_PLATFORM_KEY] = default_tts_provider

        # Fallback TTS Platform
        if len(user_input.get(FALLBACK_TTS_PLATFORM_KEY, "")) > 0:

            # Replace friendly name with entity/platform name
            fallback_tts_provider = helpers.get_stripped_tts_platform(user_input[FALLBACK_TTS_PLATFORM_KEY]).lower().replace("tts", "").replace(" ", "").replace(" ", "").replace(" ", "").replace(".", "").replace("-", "").replace("_", "")

            if len(stripped_tts_platforms) == 0:
                _errors[FALLBACK_TTS_PLATFORM_KEY] = "tts_platform_none"
            elif fallback_tts_provider not in stripped_tts_platforms:
                LOGGER.debug("Unable to find fallback TTS platform %s", user_input[FALLBACK_TTS_PLATFORM_KEY])
                _errors[FALLBACK_TTS_PLATFORM_KEY] = "tts_platform_select"
            else:
                index = stripped_tts_platforms.index(fallback_tts_provider)
                fallback_tts_provider = helpers.get_installed_tts_platforms(self.hass)[index]

            user_input[FALLBACK_TTS_PLATFORM_KEY] = fallback_tts_provider

        # Temp folder must be a subfolder of a media directory
        temp_folder_in_media_dir = False
        # Get absolute paths of both directories
        sub_dir = os.path.abspath(self.data[TEMP_PATH_KEY])
        # Verify the subdirectory starts with the parent directory path
        media_dirs_dict = self.hass.config.media_dirs or {}
        for _key, value in media_dirs_dict.items():
            parent_dir = os.path.abspath(value)
            if os.path.commonpath([parent_dir]) == os.path.commonpath([parent_dir, sub_dir]):
                temp_folder_in_media_dir = True
        if not temp_folder_in_media_dir:
            _errors[TEMP_PATH_KEY] = TEMP_PATH_KEY
        ###

        # `chime_tts.say_url` folder must be subfolder of an external directory
        external_folder_in_external_dirs = False
        sub_dir = os.path.abspath(self.data[WWW_PATH_KEY])
        # Verify the subdirectory starts with the parent directory path
        external_dirs_dict = self.hass.config.allowlist_external_dirs or {}
        for value in external_dirs_dict:
            parent_dir = os.path.abspath(value)
            if os.path.commonpath([parent_dir]) == os.path.commonpath([parent_dir, sub_dir]):
                external_folder_in_external_dirs = True
        if not external_folder_in_external_dirs:
            # /media or /config/www ?
            www_path: str = user_input.get(WWW_PATH_KEY, "")
            if not (www_path.startswith(f"{root_path}/media/") or
                    www_path.startswith(f"{root_path}/config/www/")):
                _errors[WWW_PATH_KEY] = WWW_PATH_KEY


        if _errors:
            return self.async_show_form(
                step_id="init", data_schema=options_schema, errors=_errors
            )

        if not user_input.get(CUSTOM_CHIMES_PATH_KEY) or len(user_input.get(CUSTOM_CHIMES_PATH_KEY)) == 0:
            self.data[CUSTOM_CHIMES_PATH_KEY] = ""

        # 1st time Custom Chimes Folder path modified
        if (user_input.get(CUSTOM_CHIMES_PATH_KEY) and not self._config_entry.options.get(CUSTOM_CHIMES_PATH_KEY)):
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
            data=user_input
        )

    async def async_step_restart_required(self, user_input):
        """Warn the user that Home Assistant needs to be restarted."""
        return self.async_create_entry(
            data=self.data
        )

    def get_data_key_value(self, key, user_input, default=None):
        """Get the value for a given key. Options flow 1st, Config flow 2nd."""
        if user_input:
            return user_input.get(key, default)
        dicts = [dict(self._config_entry.options), dict(self._config_entry.data)]
        value = None
        for p_dict in dicts:
            if key in p_dict and not value:
                value = p_dict[key]
        if not value:
            value = default
        return value

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
