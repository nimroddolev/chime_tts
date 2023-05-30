"""Adds config flow for TTS Chime."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector

from homeassistant.const import (
    HTTP_BEARER_AUTHENTICATION,
)
from .const import DOMAIN, NAME, DESCRIPTION, LOGGER


class TTSChimeFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for TTS Chime."""

    VERSION = 1
    _client = None

    data: dict | None = None

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.FlowResult:
        """Request input of long-lived bearer token for REST API."""
        _errors = {}
        if user_input is not None:
            if user_input[HTTP_BEARER_AUTHENTICATION] is not None:
                self.data = user_input
                LOGGER.info("tts_chime - config_flow - Adding integration entry")
                return self.async_create_entry(
                    title=NAME, data=self.data, description=DESCRIPTION
                )

            else:
                LOGGER.warning("No long-lived bearer token entered during setup")
                _errors["base"] = "empty_token"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        HTTP_BEARER_AUTHENTICATION, default=""
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT
                        ),
                    )
                }
            ),
            errors=_errors,
        )
