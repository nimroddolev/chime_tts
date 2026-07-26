"""Custom sidebar panel for Chime TTS settings."""

from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import Any

import voluptuous as vol
from aiohttp import web
from homeassistant.components.frontend import (
    add_extra_js_url,
    async_register_built_in_panel,
    async_remove_panel,
)
from homeassistant.components import websocket_api
from homeassistant.components.http import HomeAssistantView
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
import logging

from ..const import DOMAIN, NAME, VERSION
from ..const import (
    LOCAL_PATH_KEY,
    PUBLIC_PATH_KEY,
    SERVICE_CLEAR_CACHE,
    SERVICE_REPLAY,
    SERVICE_SAY,
    SERVICE_SAY_URL,
)
from ..helpers.filesystem import FilesystemHelper
from .panel_logs import (
    async_get_panel_log_events,
    async_setup_panel_log_store,
    get_panel_log_event,
    subscribe_panel_log_events,
)
from ..settings import (
    async_build_panel_payload,
    async_load_notify_profiles,
    async_save_notify_profiles,
    PATH_BROWSABLE_FIELD_KEYS,
    build_directory_browser_payload,
    create_browser_directory,
    delete_browser_entry,
    inspect_browser_upload_conflicts,
    rename_browser_entry,
    resolve_browser_audio_file_path,
    save_browser_upload,
    get_settings_data,
    validate_path_field,
    validate_notify_profiles,
    validate_settings,
)

LOGGER = logging.getLogger(__name__)

PANEL_COMPONENT_NAME = "chime-tts-settings-panel"
PANEL_URL_PATH = "chime-tts"
PANEL_MODULE_URL = f"/api/{DOMAIN}/panel.js"
PANEL_ICON_URL = f"/api/{DOMAIN}/icon.svg"
PANEL_FOOTER_LOGO_URL = f"/api/{DOMAIN}/footer_logo.svg"
PANEL_ICONSET_URL = f"/api/{DOMAIN}/iconset.js"
PANEL_OPTION_ICON_URL = f"/api/{DOMAIN}/option_icons/{{icon_name}}"
PANEL_BROWSER_AUDIO_URL = f"/api/{DOMAIN}/browser/audio"
PANEL_CHIME_PREVIEW_URL = f"/api/{DOMAIN}/chime_preview"
PANEL_BROWSER_UPLOAD_URL = f"/api/{DOMAIN}/browser/upload"
PANEL_VIEW_NAME = f"api:{DOMAIN}:panel"
PANEL_ICON_VIEW_NAME = f"api:{DOMAIN}:icon"
PANEL_FOOTER_LOGO_VIEW_NAME = f"api:{DOMAIN}:footer_logo"
PANEL_ICONSET_VIEW_NAME = f"api:{DOMAIN}:iconset"
PANEL_OPTION_ICON_VIEW_NAME = f"api:{DOMAIN}:option_icon"
PANEL_BROWSER_AUDIO_VIEW_NAME = f"api:{DOMAIN}:browser_audio"
PANEL_CHIME_PREVIEW_VIEW_NAME = f"api:{DOMAIN}:chime_preview"
PANEL_BROWSER_UPLOAD_VIEW_NAME = f"api:{DOMAIN}:browser_upload"
PANEL_DATA_KEY = f"{DOMAIN}_panel_view_registered"
WS_DATA_KEY = f"{DOMAIN}_panel_ws_registered"
ENTRY_DATA_KEY = f"{DOMAIN}_panel_entry_id"
CHIME_PREVIEW_FIELD_KEYS = {"chime_path", "end_chime_path"}

filesystem_helper = FilesystemHelper()


def _build_asset_resource_url(base_url: str, asset_path: Path) -> str:
    """Return a cache-busted resource URL for a panel asset."""
    fallback_version = VERSION.lstrip("v") or VERSION
    try:
        asset_version = str(asset_path.stat().st_mtime_ns)
    except OSError:
        asset_version = fallback_version
    return f"{base_url}?v={asset_version}"


def _set_cache_headers(response: web.StreamResponse) -> None:
    """Cache versioned panel assets aggressively."""
    response.headers["Cache-Control"] = "public, max-age=31536000, immutable"


def _set_panel_module_headers(response: web.StreamResponse) -> None:
    """Serve the panel module with reload-friendly cache headers."""
    response.headers["Cache-Control"] = "no-cache"


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
        _set_panel_module_headers(response)
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
        _set_cache_headers(response)
        return response


class ChimeTTSPanelFooterLogoView(HomeAssistantView):
    """Serve the Chime TTS footer logo image."""

    url = PANEL_FOOTER_LOGO_URL
    name = PANEL_FOOTER_LOGO_VIEW_NAME
    requires_auth = False

    def __init__(self, integration_path: Path) -> None:
        """Initialize the footer logo view."""
        self._integration_path = integration_path

    async def get(self, request) -> web.FileResponse:
        """Return the Chime TTS footer logo image."""
        response = web.FileResponse(self._integration_path / "panel" / "chime_tts.svg")
        _set_cache_headers(response)
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
        _set_cache_headers(response)
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
        _set_cache_headers(response)
        return response


class ChimeTTSPanelBrowserUploadView(HomeAssistantView):
    """Handle file and folder uploads for the panel browser."""

    url = PANEL_BROWSER_UPLOAD_URL
    name = PANEL_BROWSER_UPLOAD_VIEW_NAME
    requires_auth = True

    async def post(self, request) -> web.StreamResponse:
        """Upload one or more files into the currently browsed folder."""
        hass: HomeAssistant = request.app["hass"]
        config_entry = _get_config_entry(hass)
        if config_entry is None:
            raise web.HTTPNotFound(text="Chime TTS is not configured yet.")

        reader = await request.multipart()
        field_key = ""
        destination_path = ""
        overwrite_mode = "prompt"
        uploads: list[tuple[str, bytes]] = []

        while True:
            part = await reader.next()
            if part is None:
                break
            if part.name == "field_key":
                field_key = str(await part.text()).strip()
                continue
            if part.name == "destination_path":
                destination_path = str(await part.text()).strip()
                continue
            if part.name == "overwrite_mode":
                overwrite_mode = str(await part.text()).strip() or "prompt"
                continue
            if part.name == "files":
                uploads.append((part.filename or "", await part.read(decode=False)))

        if field_key not in PATH_BROWSABLE_FIELD_KEYS:
            raise web.HTTPBadRequest(text="Folder browsing is not available for that field.")
        if not uploads:
            raise web.HTTPBadRequest(text="No upload files were provided.")
        if overwrite_mode not in {"prompt", "overwrite", "skip"}:
            raise web.HTTPBadRequest(text="Invalid upload overwrite mode.")

        try:
            conflicts = await hass.async_add_executor_job(
                inspect_browser_upload_conflicts,
                hass,
                config_entry,
                field_key,
                destination_path,
                [filename for filename, _content in uploads],
            )
            if conflicts and overwrite_mode == "prompt":
                return web.json_response(
                    {
                        "error": "upload_conflicts",
                        "conflicts": conflicts,
                        "conflict_count": len(conflicts),
                        "upload_count": len(uploads),
                    },
                    status=409,
                )

            conflict_filenames = {item["filename"] for item in conflicts}
            uploads_to_write = uploads
            if conflicts and overwrite_mode == "skip":
                uploads_to_write = [
                    (filename, content)
                    for filename, content in uploads
                    if filename not in conflict_filenames
                ]

            for filename, content in uploads_to_write:
                await hass.async_add_executor_job(
                    save_browser_upload,
                    hass,
                    config_entry,
                    field_key,
                    destination_path,
                    filename,
                    content,
                )
            payload = await hass.async_add_executor_job(
                build_directory_browser_payload,
                hass,
                config_entry,
                field_key,
                destination_path,
            )
            payload["upload_summary"] = {
                "uploaded_count": len(uploads_to_write),
                "skipped_count": len(uploads) - len(uploads_to_write),
                "conflict_count": len(conflicts),
            }
        except FileNotFoundError as error:
            raise web.HTTPNotFound(text=str(error)) from error
        except FileExistsError as error:
            raise web.HTTPConflict(text=f"An item already exists at {error}.") from error
        except PermissionError as error:
            raise web.HTTPForbidden(text=f"Uploads are not allowed for {error}.") from error
        except ValueError as error:
            raise web.HTTPBadRequest(text=str(error)) from error

        return web.json_response(payload)


class ChimeTTSPanelBrowserAudioView(HomeAssistantView):
    """Stream an audio file for browser preview playback."""

    url = PANEL_BROWSER_AUDIO_URL
    name = PANEL_BROWSER_AUDIO_VIEW_NAME
    requires_auth = True

    async def get(self, request) -> web.StreamResponse:
        """Return an audio file for in-panel playback."""
        hass: HomeAssistant = request.app["hass"]
        config_entry = _get_config_entry(hass)
        if config_entry is None:
            raise web.HTTPNotFound(text="Chime TTS is not configured yet.")

        field_key = str(request.query.get("field_key", "")).strip()
        file_path = str(request.query.get("path", "")).strip()

        if field_key not in PATH_BROWSABLE_FIELD_KEYS:
            raise web.HTTPBadRequest(text="Folder browsing is not available for that field.")

        try:
            resolved_path = await hass.async_add_executor_job(
                resolve_browser_audio_file_path,
                hass,
                config_entry,
                field_key,
                file_path,
            )
        except FileNotFoundError as error:
            raise web.HTTPNotFound(text=str(error)) from error
        except PermissionError as error:
            raise web.HTTPForbidden(text=f"Audio preview is not allowed for {error}.") from error
        except ValueError as error:
            raise web.HTTPBadRequest(text=str(error)) from error

        content_type = mimetypes.guess_type(resolved_path)[0]
        response = web.FileResponse(
            resolved_path,
            headers={"Content-Type": content_type} if content_type else None,
        )
        response.headers["Cache-Control"] = "no-cache"
        return response


class ChimeTTSPanelChimePreviewView(HomeAssistantView):
    """Stream a selected start or end chime for panel preview playback."""

    url = PANEL_CHIME_PREVIEW_URL
    name = PANEL_CHIME_PREVIEW_VIEW_NAME
    requires_auth = True

    async def get(self, request) -> web.StreamResponse:
        """Return a selected chime audio file for in-panel playback."""
        hass: HomeAssistant = request.app["hass"]
        config_entry = _get_config_entry(hass)
        if config_entry is None:
            raise web.HTTPNotFound(text="Chime TTS is not configured yet.")

        field_key = str(request.query.get("field_key", "")).strip()
        chime_value = str(request.query.get("value", "")).strip()

        if field_key not in CHIME_PREVIEW_FIELD_KEYS:
            raise web.HTTPBadRequest(text="Chime preview is not available for that field.")
        if not chime_value:
            raise web.HTTPBadRequest(text="A chime value is required for preview playback.")

        settings_data = get_settings_data(hass, config_entry)
        try:
            resolved_chime = await filesystem_helper.async_get_chime_path(
                chime_value,
                True,
                settings_data,
                hass,
            )
        except Exception as error:
            raise web.HTTPBadRequest(text=f"Unable to resolve that chime preview: {error}") from error

        resolved_path: str | None = None
        if isinstance(resolved_chime, dict):
            audio_dict = resolved_chime.get("audio_dict", {}) if isinstance(resolved_chime.get("audio_dict"), dict) else {}
            resolved_path = audio_dict.get(LOCAL_PATH_KEY)
            if not resolved_path:
                public_path = audio_dict.get(PUBLIC_PATH_KEY)
                if public_path:
                    resolved_path = filesystem_helper.get_local_path(hass, public_path)
        elif isinstance(resolved_chime, str):
            resolved_path = resolved_chime

        if not resolved_path:
            raise web.HTTPNotFound(text="Unable to locate the selected chime preview.")

        validated_path = await filesystem_helper.async_validate_path(hass, resolved_path)
        if not validated_path:
            raise web.HTTPNotFound(text="The selected chime preview file could not be found.")

        content_type = mimetypes.guess_type(validated_path)[0]
        response = web.FileResponse(
            validated_path,
            headers={"Content-Type": content_type} if content_type else None,
        )
        response.headers["Cache-Control"] = "no-cache"
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
        hass.http.register_view(ChimeTTSPanelFooterLogoView(integration_path))
        hass.http.register_view(ChimeTTSPanelIconsetView(panel_path))
        hass.http.register_view(ChimeTTSPanelOptionIconView(panel_path))
        hass.http.register_view(ChimeTTSPanelBrowserAudioView())
        hass.http.register_view(ChimeTTSPanelChimePreviewView())
        hass.http.register_view(ChimeTTSPanelBrowserUploadView())
        add_extra_js_url(hass, panel_iconset_resource_url)
        hass.data[PANEL_DATA_KEY] = True
        LOGGER.debug(
            "Registered Chime TTS panel module view at %s", panel_module_resource_url
        )

    if not hass.data.get(WS_DATA_KEY):
        async_setup_panel_log_store(hass)
        websocket_api.async_register_command(hass, websocket_get_settings)
        websocket_api.async_register_command(hass, websocket_get_notify_profiles)
        websocket_api.async_register_command(hass, websocket_browse_path)
        websocket_api.async_register_command(hass, websocket_browser_create_folder)
        websocket_api.async_register_command(hass, websocket_browser_rename_entry)
        websocket_api.async_register_command(hass, websocket_browser_delete_entry)
        websocket_api.async_register_command(hass, websocket_validate_path)
        websocket_api.async_register_command(hass, websocket_get_logs)
        websocket_api.async_register_command(hass, websocket_subscribe_logs)
        websocket_api.async_register_command(hass, websocket_repeat_log_action)
        websocket_api.async_register_command(hass, websocket_save_settings)
        hass.data[WS_DATA_KEY] = True
        LOGGER.debug("Registered Chime TTS panel websocket commands")

    async_remove_panel(hass, PANEL_URL_PATH, warn_if_unknown=False)
    async_register_built_in_panel(
        hass=hass,
        component_name="custom",
        sidebar_title=NAME,
        sidebar_icon="chime:chime",
        frontend_url_path=PANEL_URL_PATH,
        require_admin=True,
        config_panel_domain=DOMAIN,
        config={
            "_panel_custom": {
                "name": PANEL_COMPONENT_NAME,
                "module_url": panel_module_resource_url,
            }
        },
    )
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


@websocket_api.websocket_command({"type": "chime_tts/get_settings"})
@websocket_api.async_response
async def websocket_get_settings(
    hass: HomeAssistant,
    connection,
    msg: dict[str, Any],
) -> None:
    """Return current settings for the Chime TTS panel."""
    if connection.user is None or not connection.user.is_admin:
        connection.send_error(
            msg["id"],
            "unauthorized",
            "Administrator access is required to view Chime TTS settings.",
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

    connection.send_result(
        msg["id"],
        await async_build_panel_payload(
            hass,
            config_entry,
            include_log_events=False,
            include_notify_profiles=False,
            include_path_validations=False,
        ),
    )


@websocket_api.websocket_command({"type": "chime_tts/get_notify_profiles"})
@websocket_api.async_response
async def websocket_get_notify_profiles(
    hass: HomeAssistant,
    connection,
    msg: dict[str, Any],
) -> None:
    """Return notification profiles after the main panel payload has loaded."""
    if connection.user is None or not connection.user.is_admin:
        connection.send_error(
            msg["id"],
            "unauthorized",
            "Administrator access is required to view Chime TTS settings.",
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

    notify_profiles_load_error = None
    try:
        notify_profiles, notify_profiles_load_error = await async_load_notify_profiles(hass)
    except Exception as error:
        LOGGER.exception("Failed to load notify profiles for panel hydration")
        notify_profiles = []
        notify_profiles_load_error = f"Unable to load notify profiles: {error}"

    connection.send_result(
        msg["id"],
        {
            "notify_profiles": notify_profiles,
            "notify_profiles_hydrated": True,
            "notify_profiles_load_error": notify_profiles_load_error,
        },
    )


@callback
@websocket_api.websocket_command(
    {
        "type": "chime_tts/browse_path",
        vol.Required("field_key"): vol.In(PATH_BROWSABLE_FIELD_KEYS),
        vol.Optional("path"): str,
    }
)
@websocket_api.async_response
async def websocket_browse_path(
    hass: HomeAssistant,
    connection,
    msg: dict[str, Any],
) -> None:
    """Return directory contents for the panel folder picker."""
    if connection.user is None or not connection.user.is_admin:
        connection.send_error(
            msg["id"],
            "unauthorized",
            "Administrator access is required.",
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

    try:
        payload = await hass.async_add_executor_job(
            build_directory_browser_payload,
            hass,
            config_entry,
            msg["field_key"],
            msg.get("path"),
        )
        connection.send_result(msg["id"], payload)
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
        "type": "chime_tts/browser_create_folder",
        vol.Required("field_key"): vol.In(PATH_BROWSABLE_FIELD_KEYS),
        vol.Required("path"): str,
        vol.Required("name"): str,
    }
)
@websocket_api.async_response
async def websocket_browser_create_folder(
    hass: HomeAssistant,
    connection,
    msg: dict[str, Any],
) -> None:
    """Create a folder in the browser and return refreshed listing."""
    if connection.user is None or not connection.user.is_admin:
        connection.send_error(msg["id"], "unauthorized", "Administrator access is required.")
        return

    config_entry = _get_config_entry(hass)
    if config_entry is None:
        connection.send_error(msg["id"], "not_configured", "Chime TTS is not configured yet.")
        return

    try:
        payload = await hass.async_add_executor_job(
            create_browser_directory,
            hass,
            config_entry,
            msg["field_key"],
            msg["path"],
            msg["name"],
        )
    except FileExistsError:
        connection.send_error(msg["id"], "already_exists", "A folder with that name already exists.")
        return
    except FileNotFoundError:
        connection.send_error(msg["id"], "path_not_found", "The selected folder does not exist.")
        return
    except PermissionError:
        connection.send_error(msg["id"], "path_forbidden", "That location is outside the allowed browser roots.")
        return
    except ValueError:
        connection.send_error(msg["id"], "invalid_name", "Enter a valid folder name.")
        return

    connection.send_result(msg["id"], payload)


@websocket_api.websocket_command(
    {
        "type": "chime_tts/browser_rename_entry",
        vol.Required("field_key"): vol.In(PATH_BROWSABLE_FIELD_KEYS),
        vol.Required("path"): str,
        vol.Required("new_name"): str,
    }
)
@websocket_api.async_response
async def websocket_browser_rename_entry(
    hass: HomeAssistant,
    connection,
    msg: dict[str, Any],
) -> None:
    """Rename a browser entry and return refreshed listing."""
    if connection.user is None or not connection.user.is_admin:
        connection.send_error(msg["id"], "unauthorized", "Administrator access is required.")
        return

    config_entry = _get_config_entry(hass)
    if config_entry is None:
        connection.send_error(msg["id"], "not_configured", "Chime TTS is not configured yet.")
        return

    try:
        payload = await hass.async_add_executor_job(
            rename_browser_entry,
            hass,
            config_entry,
            msg["field_key"],
            msg["path"],
            msg["new_name"],
        )
    except FileExistsError:
        connection.send_error(msg["id"], "already_exists", "An item with that name already exists.")
        return
    except FileNotFoundError:
        connection.send_error(msg["id"], "path_not_found", "The selected item no longer exists.")
        return
    except PermissionError:
        connection.send_error(msg["id"], "path_forbidden", "That item is outside the allowed browser roots.")
        return
    except ValueError:
        connection.send_error(msg["id"], "invalid_name", "Enter a valid new name.")
        return

    connection.send_result(msg["id"], payload)


@websocket_api.websocket_command(
    {
        "type": "chime_tts/browser_delete_entry",
        vol.Required("field_key"): vol.In(PATH_BROWSABLE_FIELD_KEYS),
        vol.Required("path"): str,
    }
)
@websocket_api.async_response
async def websocket_browser_delete_entry(
    hass: HomeAssistant,
    connection,
    msg: dict[str, Any],
) -> None:
    """Delete a browser entry and return refreshed listing."""
    if connection.user is None or not connection.user.is_admin:
        connection.send_error(msg["id"], "unauthorized", "Administrator access is required.")
        return

    config_entry = _get_config_entry(hass)
    if config_entry is None:
        connection.send_error(msg["id"], "not_configured", "Chime TTS is not configured yet.")
        return

    try:
        payload = await hass.async_add_executor_job(
            delete_browser_entry,
            hass,
            config_entry,
            msg["field_key"],
            msg["path"],
        )
    except FileNotFoundError:
        connection.send_error(msg["id"], "path_not_found", "The selected item no longer exists.")
        return
    except PermissionError:
        connection.send_error(msg["id"], "path_forbidden", "That item is outside the allowed browser roots.")
        return
    except ValueError:
        connection.send_error(msg["id"], "invalid_target", "That item cannot be deleted.")
        return

    connection.send_result(msg["id"], payload)


@websocket_api.websocket_command({"type": "chime_tts/get_logs"})
@websocket_api.async_response
async def websocket_get_logs(
    hass: HomeAssistant,
    connection,
    msg: dict[str, Any],
) -> None:
    """Return current session log rows for the panel."""
    if connection.user is None or not connection.user.is_admin:
        connection.send_error(
            msg["id"],
            "unauthorized",
            "Administrator access is required to view Chime TTS logs.",
        )
        return

    async_setup_panel_log_store(hass)
    connection.send_result(
        msg["id"],
        {
            "log_events": await async_get_panel_log_events(hass),
        },
    )


@callback
@websocket_api.websocket_command({"type": "chime_tts/subscribe_logs"})
@websocket_api.require_admin
def websocket_subscribe_logs(
    hass: HomeAssistant,
    connection,
    msg: dict[str, Any],
) -> None:
    """Subscribe the panel to newly completed log events."""
    async_setup_panel_log_store(hass)

    def forward_log_event(log_event: dict) -> None:
        connection.send_message(
            websocket_api.event_message(
                msg["id"],
                {"log_event": log_event},
            )
        )

    connection.subscriptions[msg["id"]] = subscribe_panel_log_events(
        hass,
        forward_log_event,
    )
    connection.send_result(msg["id"])


@websocket_api.websocket_command(
    {
        "type": "chime_tts/repeat_log_action",
        vol.Required("event_id"): str,
    }
)
@websocket_api.async_response
async def websocket_repeat_log_action(
    hass: HomeAssistant,
    connection,
    msg: dict[str, Any],
) -> None:
    """Repeat a previously logged Chime TTS action."""
    if connection.user is None or not connection.user.is_admin:
        connection.send_error(
            msg["id"],
            "unauthorized",
            "Administrator access is required to repeat Chime TTS actions.",
        )
        return

    event = get_panel_log_event(hass, msg["event_id"])
    if event is None:
        connection.send_error(
            msg["id"],
            "not_found",
            "That log event no longer exists.",
        )
        return

    repeat_service = event.get("_repeat_service")
    repeat_data = event.get("_repeat_data")
    if not repeat_service:
        connection.send_error(
            msg["id"],
            "not_repeatable",
            "This log event cannot be repeated.",
        )
        return

    integration_data = hass.data.get(DOMAIN, {})
    service_func_map = {
        SERVICE_SAY: integration_data.get("async_say"),
        SERVICE_SAY_URL: integration_data.get("async_say_url"),
        SERVICE_REPLAY: integration_data.get("async_replay"),
        SERVICE_CLEAR_CACHE: integration_data.get("async_clear_cache"),
    }
    service_func = service_func_map.get(repeat_service)
    repeat_domain = DOMAIN
    if service_func is None and hass.services.has_service("notify", repeat_service):
        repeat_domain = "notify"
    elif service_func is None:
        connection.send_error(
            msg["id"],
            "unavailable",
            "The requested Chime TTS service is not available right now.",
        )
        return

    service_call = type("PanelLogServiceCall", (), {"data": repeat_data or {}})()
    config_entry = _get_config_entry(hass)
    try:
        if repeat_domain == "notify":
            await hass.services.async_call(
                repeat_domain,
                repeat_service,
                service_data=repeat_data or {},
            )
        else:
            await service_func(service_call)
    except HomeAssistantError as error:
        if config_entry is None:
            connection.send_result(
                msg["id"],
                {
                    "message": str(error),
                    "message_type": "error",
                    "log_events": await async_get_panel_log_events(hass),
                },
            )
            return
        connection.send_result(
            msg["id"],
            await async_build_panel_payload(
                hass,
                config_entry,
                message=str(error),
                message_type="error",
            ),
        )
        return
    except Exception as error:
        LOGGER.exception("Failed to repeat log action %s", msg["event_id"])
        if config_entry is None:
            connection.send_result(
                msg["id"],
                {
                    "message": f"Unable to repeat action: {error}",
                    "message_type": "error",
                    "log_events": await async_get_panel_log_events(hass),
                },
            )
            return
        connection.send_result(
            msg["id"],
            await async_build_panel_payload(
                hass,
                config_entry,
                message=f"Unable to repeat action: {error}",
                message_type="error",
            ),
        )
        return

    if config_entry is None:
        connection.send_result(
            msg["id"],
            {
                "message": "Action repeated.",
                "message_type": "success",
                "log_events": await async_get_panel_log_events(hass),
            },
        )
        return

    connection.send_result(
        msg["id"],
        await async_build_panel_payload(
            hass,
            config_entry,
            message="Action repeated.",
            message_type="success",
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
    loaded_notify_profiles, _ = await async_load_notify_profiles(hass)
    if notify_validation.data != loaded_notify_profiles:
        restart_required = True

    if validation.errors:
        LOGGER.debug("Chime TTS panel validation errors: %s", validation.errors)
        connection.send_result(
            msg["id"],
            await async_build_panel_payload(
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
            await async_build_panel_payload(
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
        await async_save_notify_profiles(hass, notify_validation.data)
        LOGGER.debug(
            "Chime TTS panel settings saved=%s options=%s",
            updated,
            dict(config_entry.options),
        )
    except Exception as error:
        LOGGER.exception("Failed to save Chime TTS panel settings")
        connection.send_result(
            msg["id"],
            await async_build_panel_payload(
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
        await async_build_panel_payload(
            hass,
            config_entry,
            values=dict(config_entry.options),
            notify_profiles=notify_validation.data,
            message=(
                "Settings saved. Restart Home Assistant to apply changes that require it, including updated notify profiles, the custom chimes folder, and added or removed Chime Sets."
                if restart_required
                else "Settings saved."
            ),
            message_type="success",
            restart_required=restart_required,
        ),
    )
