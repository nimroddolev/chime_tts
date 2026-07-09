"""Custom sidebar panel for Chime TTS settings."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import voluptuous as vol
from aiohttp import web
from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components import websocket_api
from homeassistant.components.http import HomeAssistantView
from homeassistant.components.panel_custom import async_register_panel
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
import logging

from ..const import DOMAIN, NAME, VERSION
from ..settings import (
    PATH_BROWSABLE_FIELD_KEYS,
    build_directory_browser_payload,
    build_panel_payload,
    load_notify_profiles,
    save_notify_profiles,
    validate_path_field,
    validate_notify_profiles,
    validate_settings,
)

LOGGER = logging.getLogger(__name__)

PANEL_COMPONENT_NAME = "chime-tts-settings-panel"
PANEL_URL_PATH = "chime-tts"
PANEL_MODULE_URL = f"/api/{DOMAIN}/panel.js"
PANEL_ICON_URL = f"/api/{DOMAIN}/icon.svg"
PANEL_ICONSET_URL = f"/api/{DOMAIN}/iconset.js"
PANEL_OPTION_ICON_URL = f"/api/{DOMAIN}/option_icons/{{icon_name}}"
PANEL_VIEW_NAME = f"api:{DOMAIN}:panel"
PANEL_ICON_VIEW_NAME = f"api:{DOMAIN}:icon"
PANEL_ICONSET_VIEW_NAME = f"api:{DOMAIN}:iconset"
PANEL_OPTION_ICON_VIEW_NAME = f"api:{DOMAIN}:option_icon"
PANEL_DATA_KEY = f"{DOMAIN}_panel_view_registered"
WS_DATA_KEY = f"{DOMAIN}_panel_ws_registered"
ENTRY_DATA_KEY = f"{DOMAIN}_panel_entry_id"


def _build_asset_resource_url(base_url: str, asset_path: Path) -> str:
    """Return a cache-busted resource URL for a panel asset."""
    fallback_version = VERSION.lstrip("v") or VERSION
    try:
        asset_version = str(asset_path.stat().st_mtime_ns)
    except OSError:
        asset_version = fallback_version
    return f"{base_url}?v={asset_version}"


class ChimeTTSPanelView(HomeAssistantView):
    """Serve the Chime TTS panel JavaScript module."""

    url = PANEL_MODULE_URL
    name = PANEL_VIEW_NAME
    requires_auth = False

    def __init__(self, panel_path: Path) -> None:
        """Initialize the panel view."""
        self._panel_path = panel_path

    async def get(self, request) -> web.FileResponse:
        """Return the panel JavaScript module."""
        response = web.FileResponse(self._panel_path / "chime-tts-panel.js")
        response.headers["Cache-Control"] = "no-store"
        return response


class ChimeTTSPanelIconView(HomeAssistantView):
    """Serve the Chime TTS icon."""

    url = PANEL_ICON_URL
    name = PANEL_ICON_VIEW_NAME
    requires_auth = False

    def __init__(self, integration_path: Path) -> None:
        """Initialize the icon view."""
        self._integration_path = integration_path

    async def get(self, request) -> web.FileResponse:
        """Return the Chime TTS icon."""
        response = web.FileResponse(self._integration_path / "panel" / "chime-icon.svg")
        response.headers["Cache-Control"] = "no-store"
        return response


class ChimeTTSPanelIconsetView(HomeAssistantView):
    """Serve the Chime TTS custom iconset."""

    url = PANEL_ICONSET_URL
    name = PANEL_ICONSET_VIEW_NAME
    requires_auth = False

    def __init__(self, panel_path: Path) -> None:
        """Initialize the iconset view."""
        self._panel_path = panel_path

    async def get(self, request) -> web.FileResponse:
        """Return the Chime TTS iconset JavaScript."""
        response = web.FileResponse(self._panel_path / "iconset.js")
        response.headers["Cache-Control"] = "no-store"
        return response


class ChimeTTSPanelOptionIconView(HomeAssistantView):
    """Serve per-field option icons for the Chime TTS panel."""

    url = PANEL_OPTION_ICON_URL
    name = PANEL_OPTION_ICON_VIEW_NAME
    requires_auth = False

    def __init__(self, panel_path: Path) -> None:
        """Initialize the option icon view."""
        self._icons_path = panel_path / "option_icons"

    async def get(self, request, icon_name: str) -> web.StreamResponse:
        """Return a single option icon SVG."""
        if not icon_name:
            raise web.HTTPNotFound()

        icon_path = Path(icon_name)
        if icon_path.name != icon_name or icon_path.suffix != ".svg":
            raise web.HTTPNotFound()

        resolved_icon_path = self._icons_path / icon_path.name
        if not resolved_icon_path.exists():
            raise web.HTTPNotFound()

        response = web.FileResponse(resolved_icon_path)
        response.headers["Cache-Control"] = "no-store"
        return response


async def async_setup_panel(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Register the custom settings panel and its backend APIs."""
    integration_path = Path(__file__).resolve().parent.parent
    panel_path = integration_path / "panel"
    panel_module_resource_url = _build_asset_resource_url(
        PANEL_MODULE_URL, panel_path / "chime-tts-panel.js"
    )
    panel_iconset_resource_url = _build_asset_resource_url(
        PANEL_ICONSET_URL, panel_path / "iconset.js"
    )

    if not hass.data.get(PANEL_DATA_KEY):
        hass.http.register_view(ChimeTTSPanelView(panel_path))
        hass.http.register_view(ChimeTTSPanelIconView(integration_path))
        hass.http.register_view(ChimeTTSPanelIconsetView(panel_path))
        hass.http.register_view(ChimeTTSPanelOptionIconView(panel_path))
        add_extra_js_url(hass, panel_iconset_resource_url)
        hass.data[PANEL_DATA_KEY] = True
        LOGGER.debug(
            "Registered Chime TTS panel module view at %s", panel_module_resource_url
        )

    if not hass.data.get(WS_DATA_KEY):
        websocket_api.async_register_command(hass, websocket_get_settings)
        websocket_api.async_register_command(hass, websocket_browse_path)
        websocket_api.async_register_command(hass, websocket_validate_path)
        websocket_api.async_register_command(hass, websocket_save_settings)
        hass.data[WS_DATA_KEY] = True
        LOGGER.debug("Registered Chime TTS panel websocket commands")

    try:
        await async_register_panel(
            hass,
            frontend_url_path=PANEL_URL_PATH,
            webcomponent_name=PANEL_COMPONENT_NAME,
            sidebar_title=NAME,
            sidebar_icon="chime:chime",
            module_url=panel_module_resource_url,
            require_admin=True,
        )
    except ValueError as error:
        LOGGER.debug("Chime TTS sidebar panel already registered: %s", error)
    LOGGER.debug("Registered Chime TTS sidebar panel at /%s", PANEL_URL_PATH)

    hass.data[ENTRY_DATA_KEY] = config_entry.entry_id


def _get_config_entry(hass: HomeAssistant) -> ConfigEntry | None:
    """Get the Chime TTS config entry used by the panel."""
    entry_id = hass.data.get(ENTRY_DATA_KEY)
    if entry_id is not None:
        for entry in hass.config_entries.async_entries(DOMAIN):
            if entry.entry_id == entry_id:
                return entry

    entries = hass.config_entries.async_entries(DOMAIN)
    return entries[0] if entries else None


@callback
@websocket_api.websocket_command({"type": "chime_tts/get_settings"})
@websocket_api.require_admin
def websocket_get_settings(
    hass: HomeAssistant,
    connection,
    msg: dict[str, Any],
) -> None:
    """Return current settings for the Chime TTS panel."""
    config_entry = _get_config_entry(hass)
    if config_entry is None:
        connection.send_error(
            msg["id"],
            "not_configured",
            "Chime TTS is not configured yet.",
        )
        return

    connection.send_result(msg["id"], build_panel_payload(hass, config_entry))


@callback
@websocket_api.websocket_command(
    {
        "type": "chime_tts/browse_path",
        vol.Required("field_key"): vol.In(PATH_BROWSABLE_FIELD_KEYS),
        vol.Optional("path"): str,
    }
)
@websocket_api.require_admin
def websocket_browse_path(
    hass: HomeAssistant,
    connection,
    msg: dict[str, Any],
) -> None:
    """Return directory contents for the panel folder picker."""
    config_entry = _get_config_entry(hass)
    if config_entry is None:
        connection.send_error(
            msg["id"],
            "not_configured",
            "Chime TTS is not configured yet.",
        )
        return

    try:
        connection.send_result(
            msg["id"],
            build_directory_browser_payload(
                hass,
                config_entry,
                msg["field_key"],
                msg.get("path"),
            ),
        )
    except FileNotFoundError:
        connection.send_error(
            msg["id"],
            "path_not_found",
            "The selected folder does not exist.",
        )
    except PermissionError:
        connection.send_error(
            msg["id"],
            "path_forbidden",
            "Home Assistant does not have permission to read that folder.",
        )
    except ValueError:
        connection.send_error(
            msg["id"],
            "unsupported_field",
            "Folder browsing is not available for that field.",
        )


@callback
@websocket_api.websocket_command(
    {
        "type": "chime_tts/validate_path",
        vol.Required("field_key"): vol.In(PATH_BROWSABLE_FIELD_KEYS),
        vol.Required("path"): str,
    }
)
@websocket_api.require_admin
def websocket_validate_path(
    hass: HomeAssistant,
    connection,
    msg: dict[str, Any],
) -> None:
    """Return live validation details for a path field."""
    config_entry = _get_config_entry(hass)
    if config_entry is None:
        connection.send_error(
            msg["id"],
            "not_configured",
            "Chime TTS is not configured yet.",
        )
        return

    connection.send_result(
        msg["id"],
        validate_path_field(
            hass,
            config_entry,
            msg["field_key"],
            msg["path"],
        ),
    )


@websocket_api.websocket_command(
    {
        "type": "chime_tts/save_settings",
        vol.Required("values"): dict,
        vol.Optional("notify_profiles"): [dict],
        vol.Optional("allow_invalid_paths"): [vol.In(PATH_BROWSABLE_FIELD_KEYS)],
    }
)
@websocket_api.async_response
async def websocket_save_settings(
    hass: HomeAssistant,
    connection,
    msg: dict[str, Any],
) -> None:
    """Validate and save settings from the Chime TTS panel."""
    if connection.user is None or not connection.user.is_admin:
        connection.send_error(
            msg["id"],
            "unauthorized",
            "Administrator access is required to save Chime TTS settings.",
        )
        return

    config_entry = _get_config_entry(hass)
    if config_entry is None:
        connection.send_error(
            msg["id"],
            "not_configured",
            "Chime TTS is not configured yet.",
        )
        return

    LOGGER.debug("Received Chime TTS panel save request: %s", msg["values"])
    validation = validate_settings(
        hass,
        config_entry,
        msg["values"],
        allow_invalid_paths=set(msg.get("allow_invalid_paths", [])),
    )
    notify_validation = validate_notify_profiles(msg.get("notify_profiles"))
    restart_required = validation.restart_required
    if notify_validation.data != load_notify_profiles(hass)[0]:
        restart_required = True

    if validation.errors:
        LOGGER.debug("Chime TTS panel validation errors: %s", validation.errors)
        connection.send_result(
            msg["id"],
            build_panel_payload(
                hass,
                config_entry,
                values=validation.data,
                notify_profiles=notify_validation.data,
                notify_profile_errors=notify_validation.errors,
                errors=validation.errors,
                message="Fix the highlighted fields and try again.",
                message_type="error",
                restart_required=restart_required,
            ),
        )
        return

    if any(profile_errors for profile_errors in notify_validation.errors):
        connection.send_result(
            msg["id"],
            build_panel_payload(
                hass,
                config_entry,
                values=validation.data,
                notify_profiles=notify_validation.data,
                notify_profile_errors=notify_validation.errors,
                message="Fix the highlighted notification profiles and try again.",
                message_type="error",
                restart_required=restart_required,
            ),
        )
        return

    try:
        LOGGER.debug("Saving Chime TTS panel settings")
        updated = hass.config_entries.async_update_entry(
            config_entry, options=validation.data
        )
        save_notify_profiles(hass, notify_validation.data)
        LOGGER.debug(
            "Chime TTS panel settings saved=%s options=%s",
            updated,
            dict(config_entry.options),
        )
    except Exception as error:
        LOGGER.exception("Failed to save Chime TTS panel settings")
        connection.send_result(
            msg["id"],
            build_panel_payload(
                hass,
                config_entry,
                values=validation.data,
                notify_profiles=notify_validation.data,
                notify_profile_errors=notify_validation.errors,
                message=f"Save failed: {error}",
                message_type="error",
                restart_required=restart_required,
            ),
        )
        return

    connection.send_result(
        msg["id"],
        build_panel_payload(
            hass,
            config_entry,
            values=dict(config_entry.options),
            notify_profiles=notify_validation.data,
            message=(
                "Settings saved. Restart Home Assistant to apply the updated notify profiles and custom chimes folder."
                if restart_required
                else "Settings saved."
            ),
            message_type="success",
            restart_required=restart_required,
        ),
    )
