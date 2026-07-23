"""Tests for the Chime TTS sidebar settings backend."""

from __future__ import annotations

import inspect
import importlib
import logging
from pathlib import Path
import time
from types import SimpleNamespace
import yaml

import pytest

from custom_components.chime_tts.const import CUSTOM_CHIMES_PATH_KEY
from custom_components.chime_tts.const import TEMP_CHIMES_PATH_KEY
from custom_components.chime_tts.const import TEMP_PATH_KEY
from custom_components.chime_tts.const import TTS_PLATFORM_KEY
from custom_components.chime_tts.const import WWW_PATH_KEY
from custom_components.chime_tts.const import DOMAIN

panel_module = importlib.import_module("custom_components.chime_tts.helpers.panel")
panel_logs_module = importlib.import_module("custom_components.chime_tts.helpers.panel_logs")
settings_module = importlib.import_module("custom_components.chime_tts.settings")
save_settings_handler = inspect.unwrap(panel_module.websocket_save_settings)
repeat_log_action_handler = inspect.unwrap(panel_module.websocket_repeat_log_action)
get_logs_handler = inspect.unwrap(panel_module.websocket_get_logs)
get_settings_handler = inspect.unwrap(panel_module.websocket_get_settings)
get_notify_profiles_handler = inspect.unwrap(panel_module.websocket_get_notify_profiles)
browse_path_handler = inspect.unwrap(panel_module.websocket_browse_path)
create_folder_handler = inspect.unwrap(panel_module.websocket_browser_create_folder)
rename_entry_handler = inspect.unwrap(panel_module.websocket_browser_rename_entry)
delete_entry_handler = inspect.unwrap(panel_module.websocket_browser_delete_entry)


class FakeConfigEntries:
    """Simple config entries manager for sidebar tests."""

    def __init__(self, entry) -> None:
        """Store the single config entry under test."""
        self._entry = entry

    def async_entries(self, domain: str):
        """Return the Chime TTS config entry for matching domain requests."""
        return [self._entry] if domain == DOMAIN else []

    def async_update_entry(self, entry, *, options):
        """Update the entry options in place like Home Assistant does."""
        entry.options = dict(options)
        return True


class FakeConnection:
    """Capture websocket results and errors."""

    def __init__(self, *, is_admin: bool = True) -> None:
        """Initialize the connection with an optional admin user."""
        self.user = SimpleNamespace(is_admin=is_admin)
        self.results: list[tuple[int, dict]] = []
        self.errors: list[tuple[int, str, str]] = []

    def send_result(self, message_id: int, payload: dict) -> None:
        """Record a websocket success response."""
        self.results.append((message_id, payload))

    def send_error(self, message_id: int, code: str, message: str) -> None:
        """Record a websocket error response."""
        self.errors.append((message_id, code, message))


class FakeServices:
    """Capture service calls and optional registered service checks."""

    def __init__(self) -> None:
        """Initialise the fake service registry."""
        self.calls: list[dict[str, object]] = []
        self.available_services: set[tuple[str, str]] = set()

    async def async_call(self, domain: str, service: str, *, service_data=None, blocking=False):
        """Record a service call made by the panel handlers."""
        self.calls.append(
            {
                "domain": domain,
                "service": service,
                "service_data": dict(service_data or {}),
                "blocking": blocking,
            }
        )
        return None

    def has_service(self, domain: str, service: str) -> bool:
        """Report whether a given service exists."""
        return (domain, service) in self.available_services


def make_hass(tmp_path: Path):
    """Create a Home Assistant stand-in with real filesystem roots."""
    root_dir = tmp_path / "ha-root"
    config_dir = root_dir / "config"
    media_dir = config_dir / "media"
    www_dir = config_dir / "www"
    temp_audio_dir = media_dir / "sounds" / "temp" / "chime_tts"
    temp_chimes_dir = temp_audio_dir / "chimes"
    custom_chimes_dir = config_dir / "custom_chimes"

    for directory in (
        media_dir,
        www_dir,
        temp_audio_dir,
        temp_chimes_dir,
        custom_chimes_dir,
    ):
        directory.mkdir(parents=True, exist_ok=True)

    hass = SimpleNamespace()
    hass.config = SimpleNamespace(
        config_dir=str(config_dir),
        path=lambda *parts: str(config_dir.joinpath(*parts)),
        media_dirs={"media": str(media_dir)},
        allowlist_external_dirs=[str(www_dir), str(media_dir)],
    )
    hass.data = {
        "tts_manager": SimpleNamespace(providers={"google_translate": object()}),
        DOMAIN: {},
    }
    hass.services = FakeServices()
    recorded_service_calls = hass.services.calls

    async def async_add_executor_job(func, *args):
        return func(*args)

    hass.async_add_executor_job = async_add_executor_job

    config_entry = SimpleNamespace(
        entry_id="entry-1",
        options={
            "queue_timeout": 60,
            "tts_timeout": 30,
            TTS_PLATFORM_KEY: "google_translate",
            "default_language_key": "",
            "default_voice_key": "",
            "default_tld_key": "",
            "fallback_tts_platform_key": "",
            "offset": 450,
            "crossfade": 0,
            "fade_transition_key": 500,
            "remove_temp_file_delay": "",
            CUSTOM_CHIMES_PATH_KEY: str(custom_chimes_dir),
            TEMP_CHIMES_PATH_KEY: str(temp_chimes_dir),
            TEMP_PATH_KEY: str(temp_audio_dir),
            WWW_PATH_KEY: str(www_dir / "chime_tts"),
            "add_cover_art": False,
        },
        data={},
    )
    hass.config_entries = FakeConfigEntries(config_entry)
    hass.data[panel_module.ENTRY_DATA_KEY] = config_entry.entry_id

    return hass, config_entry, {
        "root_dir": root_dir,
        "config_dir": config_dir,
        "media_dir": media_dir,
        "www_dir": www_dir,
        "temp_audio_dir": temp_audio_dir,
        "temp_chimes_dir": temp_chimes_dir,
        "custom_chimes_dir": custom_chimes_dir,
        "recorded_service_calls": recorded_service_calls,
    }


@pytest.fixture(autouse=True)
def stub_tts_platforms(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep platform lists deterministic for sidebar tests."""
    monkeypatch.setattr(
        settings_module.helpers,
        "get_installed_tts_platforms",
        lambda hass: ["google_translate", "cloud"],
    )


def test_build_panel_payload_exposes_sidebar_metadata_and_field_hints(tmp_path: Path) -> None:
    """The sidebar payload should include section ordering, hints, and icon URLs."""
    hass, config_entry, _paths = make_hass(tmp_path)

    payload = settings_module.build_panel_payload(hass, config_entry)

    assert payload["version"]
    assert payload["documentation_url"].endswith("/configuration/")
    assert payload["logs_url"] == "/config/logs?filter=chime_tts"
    assert payload["restart_required_field_keys"] == [CUSTOM_CHIMES_PATH_KEY]
    assert [section["key"] for section in payload["sections"]] == [
        "paths",
        "voice",
        "playback",
        "general",
        "notify_profiles",
        "logs",
        "about",
    ]
    assert payload["log_events"] == []

    voice_section = next(section for section in payload["sections"] if section["key"] == "voice")
    language_field = next(
        field for field in voice_section["fields"] if field["key"] == "default_language_key"
    )
    custom_chimes_field = next(
        field for field in payload["sections"][0]["fields"] if field["key"] == CUSTOM_CHIMES_PATH_KEY
    )

    assert language_field["provider_hint"]["tone"] == "info"
    assert "Google Translate" in language_field["provider_hint"]["message"]
    assert language_field["icon_url"].startswith(
        f"/api/{DOMAIN}/option_icons/language.svg"
    )
    assert custom_chimes_field["icon_url"].startswith(
        f"/api/{DOMAIN}/option_icons/{CUSTOM_CHIMES_PATH_KEY}.svg"
    )
    assert custom_chimes_field["can_browse"] is True
    assert (
        custom_chimes_field["path_validation"]["message"]
        == "Folder path is valid for this setting."
    )
    about_section = next(section for section in payload["sections"] if section["key"] == "about")
    assert about_section["kind"] == "about"
    assert about_section["version"] == payload["version"]
    assert all(item["title"] != "Version" for item in about_section["about_items"])
    assert any(item["title"] == "Buy Me a Coffee" for item in about_section["about_items"])


def test_build_panel_payload_shows_restart_alert_for_platforms_added_after_startup(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Providers added after the startup baseline should trigger a restart alert."""
    hass, config_entry, _paths = make_hass(tmp_path)
    hass.data[DOMAIN]["_initial_tts_platforms"] = ["google_translate"]
    monkeypatch.setattr(
        settings_module.helpers,
        "get_installed_tts_platforms",
        lambda hass: ["google_translate", "tts.pico_tts_en_gb"],
    )

    payload = settings_module.build_panel_payload(hass, config_entry)

    assert len(payload["alerts"]) == 1
    alert = payload["alerts"][0]
    assert alert["tone"] == "warning"
    assert alert["title"] == "1 New TTS Provider Detected"
    assert "tts.pico_tts_en_gb" in alert["message"]
    assert "<strong>tts.pico_tts_en_gb</strong>" in alert["message_html"]
    assert alert["action"] == {"kind": "restart", "label": "Restart"}


def test_build_panel_payload_waits_for_startup_tts_baseline(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The panel must not mislabel providers while startup is still settling."""
    hass, config_entry, _paths = make_hass(tmp_path)
    hass.data[DOMAIN].pop("_initial_tts_platforms", None)
    monkeypatch.setattr(
        settings_module.helpers,
        "get_installed_tts_platforms",
        lambda hass: ["tts.pico_tts_en_gb"],
    )

    payload = settings_module.build_panel_payload(hass, config_entry)

    assert payload["alerts"] == []


def test_build_panel_payload_clears_restart_alert_when_provider_is_loaded(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Restart alerts should clear when the provider is part of the startup baseline."""
    hass, config_entry, _paths = make_hass(tmp_path)
    hass.data[DOMAIN]["_initial_tts_platforms"] = [
        "google_translate",
        "tts.pico_tts_en_gb",
    ]
    monkeypatch.setattr(
        settings_module.helpers,
        "get_installed_tts_platforms",
        lambda hass: ["google_translate", "tts.pico_tts_en_gb"],
    )

    payload = settings_module.build_panel_payload(hass, config_entry)

    assert payload["alerts"] == []


def test_build_panel_payload_shows_no_providers_alert_when_none_are_available(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An empty live platform list should show the missing-provider alert."""
    hass, config_entry, _paths = make_hass(tmp_path)
    hass.data[DOMAIN]["_initial_tts_platforms"] = []
    monkeypatch.setattr(
        settings_module.helpers,
        "get_installed_tts_platforms",
        lambda hass: [],
    )

    payload = settings_module.build_panel_payload(hass, config_entry)

    assert payload["alerts"][0]["title"] == "No TTS providers detected"


def test_normalize_tts_provider_identity_matches_pico_tts_entity_id() -> None:
    """Pico TTS entity ids should normalize to the same provider identity."""
    assert (
        settings_module._normalize_tts_provider_identity("tts.pico_tts_en_gb")
        == "picotts"
    )


@pytest.mark.asyncio
async def test_websocket_get_settings_skips_initial_log_backfill(tmp_path: Path) -> None:
    """Initial panel payloads should avoid blocking on log backfill work."""
    hass, _config_entry, _paths = make_hass(tmp_path)
    connection = FakeConnection()

    async def fail_if_called(_hass):
        raise AssertionError("Initial settings load should not request log events")

    panel_logs_module.async_setup_panel_log_store(hass)
    original = settings_module.async_get_panel_log_events
    settings_module.async_get_panel_log_events = fail_if_called
    try:
        await get_settings_handler(
            hass,
            connection,
            {
                "id": 17,
                "type": "chime_tts/get_settings",
            },
        )
    finally:
        settings_module.async_get_panel_log_events = original

    assert connection.errors == []
    assert connection.results[-1][1]["log_events"] == []


@pytest.mark.asyncio
async def test_websocket_get_settings_defers_notify_profile_loading(tmp_path: Path) -> None:
    """Initial panel payloads should avoid blocking on notify profile hydration."""
    hass, _config_entry, _paths = make_hass(tmp_path)
    connection = FakeConnection()

    async def fail_if_called(_hass):
        raise AssertionError("Initial settings load should not request notify profiles")

    original = settings_module.async_load_notify_profiles
    settings_module.async_load_notify_profiles = fail_if_called
    try:
        await get_settings_handler(
            hass,
            connection,
            {
                "id": 18,
                "type": "chime_tts/get_settings",
            },
        )
    finally:
        settings_module.async_load_notify_profiles = original

    assert connection.errors == []
    payload = connection.results[-1][1]
    assert payload["notify_profiles"] == []
    assert payload["notify_profiles_hydrated"] is False


@pytest.mark.asyncio
async def test_websocket_get_notify_profiles_returns_hydrated_profiles(tmp_path: Path) -> None:
    """Deferred notify profile hydration should return the parsed YAML profiles."""
    hass, _config_entry, _paths = make_hass(tmp_path)
    connection = FakeConnection()

    async def fake_load_notify_profiles(_hass):
        return ([{"name": "Front Door", "entity_id": "media_player.kitchen"}], None)

    original = panel_module.async_load_notify_profiles
    panel_module.async_load_notify_profiles = fake_load_notify_profiles
    try:
        await get_notify_profiles_handler(
            hass,
            connection,
            {
                "id": 19,
                "type": "chime_tts/get_notify_profiles",
            },
        )
    finally:
        panel_module.async_load_notify_profiles = original

    assert connection.errors == []
    assert connection.results[-1][1] == {
        "notify_profiles": [{"name": "Front Door", "entity_id": "media_player.kitchen"}],
        "notify_profiles_hydrated": True,
        "notify_profiles_load_error": None,
    }


def test_validate_path_field_suggests_media_directories_for_invalid_media_path(tmp_path: Path) -> None:
    """Invalid media-backed paths should offer valid media directory suggestions."""
    hass, config_entry, paths = make_hass(tmp_path)
    invalid_path = str(paths["root_dir"] / "outside" / "audio")

    result = settings_module.validate_path_field(
        hass,
        config_entry,
        TEMP_PATH_KEY,
        invalid_path,
    )

    assert result["valid"] is False
    assert result["tone"] == "error"
    assert result["message"] == "Select a folder inside a configured media directory."
    assert result["can_use_anyway"] is True
    assert str(paths["media_dir"]).rstrip("/") + "/" in result["suggestion_paths"]


def test_build_directory_browser_payload_includes_previews_and_badges(tmp_path: Path) -> None:
    """Folder browsing should include child directories and a custom-chime preview."""
    hass, config_entry, paths = make_hass(tmp_path)
    custom_dir = paths["custom_chimes_dir"]
    (custom_dir / "alpha.mp3").write_text("a", encoding="utf-8")
    (custom_dir / "beta.wav").write_text("b", encoding="utf-8")
    (custom_dir / "ignore.txt").write_text("x", encoding="utf-8")
    (custom_dir / "Nested").mkdir()

    payload = settings_module.build_directory_browser_payload(
        hass,
        config_entry,
        CUSTOM_CHIMES_PATH_KEY,
        str(custom_dir),
    )

    assert payload["current_path_allowed"] is True
    assert payload["preview_files"] == ["alpha.mp3", "beta.wav"]
    assert any(directory["name"] == "Nested" for directory in payload["directories"])
    assert any(
        root["path"] == str(paths["custom_chimes_dir"]).rstrip("/") + "/"
        for root in payload["roots"]
    )


def test_build_directory_browser_payload_falls_back_to_existing_ancestor_for_missing_path(
    tmp_path: Path,
) -> None:
    """Missing configured folders should open the browser on the nearest existing ancestor."""
    hass, config_entry, paths = make_hass(tmp_path)
    missing_path = paths["custom_chimes_dir"] / "nested" / "missing" / "folder"

    payload = settings_module.build_directory_browser_payload(
        hass,
        config_entry,
        CUSTOM_CHIMES_PATH_KEY,
        str(missing_path),
    )

    assert payload["requested_path"] == f"{missing_path}/"
    assert payload["requested_path_exists"] is False
    assert payload["requested_path_missing"] is True
    assert (
        payload["selected_path_notice"]
        == "The selected folder does not exist. Showing the closest existing folder instead."
    )
    assert payload["current_path"] == f"{paths['custom_chimes_dir']}/"


def test_browser_file_mutations_and_uploads_are_reflected_in_the_listing(
    tmp_path: Path,
) -> None:
    """Folder creation, file uploads, rename, and deletion share one safe browser root."""
    hass, config_entry, paths = make_hass(tmp_path)
    root = paths["temp_audio_dir"]

    settings_module.create_browser_directory(
        hass, config_entry, TEMP_PATH_KEY, str(root), "announcements"
    )
    destination = root / "announcements"
    settings_module.save_browser_upload(
        hass,
        config_entry,
        TEMP_PATH_KEY,
        str(destination),
        "morning/welcome.mp3",
        b"audio",
    )

    uploaded_file = destination / "morning" / "welcome.mp3"
    assert uploaded_file.read_bytes() == b"audio"
    assert settings_module.inspect_browser_upload_conflicts(
        hass,
        config_entry,
        TEMP_PATH_KEY,
        str(destination),
        ["morning/welcome.mp3", "new.wav"],
    ) == [
        {
            "filename": "morning/welcome.mp3",
            "relative_path": "morning/welcome.mp3",
            "existing_path": str(uploaded_file),
        }
    ]

    settings_module.rename_browser_entry(
        hass,
        config_entry,
        TEMP_PATH_KEY,
        str(uploaded_file),
        "hello.mp3",
    )
    renamed_file = uploaded_file.with_name("hello.mp3")
    assert renamed_file.exists()

    settings_module.delete_browser_entry(
        hass, config_entry, TEMP_PATH_KEY, str(destination / "morning")
    )
    payload = settings_module.build_directory_browser_payload(
        hass, config_entry, TEMP_PATH_KEY, str(destination)
    )
    assert not (destination / "morning").exists()
    assert payload["files"] == []


def test_browser_rejects_symlink_escape_from_restricted_roots(tmp_path: Path) -> None:
    """Uploads and audio previews must not follow symlinks outside a media root."""
    hass, config_entry, paths = make_hass(tmp_path)
    outside = paths["root_dir"] / "outside"
    outside.mkdir()
    escape_link = paths["temp_audio_dir"] / "escape"
    escape_link.symlink_to(outside, target_is_directory=True)
    escaped_audio = escape_link / "secret.mp3"
    escaped_audio.write_bytes(b"audio")

    with pytest.raises(PermissionError):
        settings_module.resolve_browser_audio_file_path(
            hass, config_entry, TEMP_PATH_KEY, str(escaped_audio)
        )
    with pytest.raises(PermissionError):
        settings_module.save_browser_upload(
            hass,
            config_entry,
            TEMP_PATH_KEY,
            str(escape_link),
            "uploaded.mp3",
            b"audio",
        )
    with pytest.raises(PermissionError):
        settings_module.create_browser_directory(
            hass, config_entry, TEMP_PATH_KEY, str(escape_link), "nested"
        )


@pytest.mark.asyncio
async def test_browser_mutation_websocket_commands_return_refreshed_payloads(
    tmp_path: Path,
) -> None:
    """The picker receives a fresh listing after each filesystem mutation."""
    hass, _config_entry, paths = make_hass(tmp_path)
    connection = FakeConnection()
    root = paths["temp_audio_dir"]

    await create_folder_handler(
        hass,
        connection,
        {
            "id": 10,
            "type": "chime_tts/browser_create_folder",
            "field_key": TEMP_PATH_KEY,
            "path": str(root),
            "name": "uploads",
        },
    )
    created = root / "uploads"
    (created / "old.mp3").write_bytes(b"audio")

    await rename_entry_handler(
        hass,
        connection,
        {
            "id": 11,
            "type": "chime_tts/browser_rename_entry",
            "field_key": TEMP_PATH_KEY,
            "path": str(created / "old.mp3"),
            "new_name": "new.mp3",
        },
    )
    await delete_entry_handler(
        hass,
        connection,
        {
            "id": 12,
            "type": "chime_tts/browser_delete_entry",
            "field_key": TEMP_PATH_KEY,
            "path": str(created / "new.mp3"),
        },
    )

    assert connection.errors == []
    assert [message_id for message_id, _payload in connection.results] == [10, 11, 12]
    assert not (created / "new.mp3").exists()
    assert connection.results[-1][1]["current_path"] == f"{created}/"


@pytest.mark.asyncio
async def test_websocket_browse_path_returns_missing_path_notice_with_existing_ancestor(
    tmp_path: Path,
) -> None:
    """Folder browsing should return a warning payload instead of a hard error for missing paths."""
    hass, _config_entry, paths = make_hass(tmp_path)
    connection = FakeConnection()
    missing_path = paths["custom_chimes_dir"] / "nested" / "missing" / "folder"

    await browse_path_handler(
        hass,
        connection,
        {
            "id": 1,
            "type": "chime_tts/browse_path",
            "field_key": CUSTOM_CHIMES_PATH_KEY,
            "path": str(missing_path),
        },
    )

    assert connection.errors == []
    assert connection.results
    payload = connection.results[-1][1]
    assert payload["requested_path_missing"] is True
    assert payload["current_path"] == f"{paths['custom_chimes_dir']}/"


@pytest.mark.asyncio
async def test_websocket_save_settings_rejects_invalid_media_path_without_override(
    tmp_path: Path,
) -> None:
    """Saving should return field errors when a restricted path is invalid."""
    hass, _config_entry, paths = make_hass(tmp_path)
    connection = FakeConnection()

    await save_settings_handler(
        hass,
        connection,
        {
            "id": 1,
            "type": "chime_tts/save_settings",
            "values": {
                **hass.config_entries._entry.options,
                TEMP_PATH_KEY: str(paths["root_dir"] / "outside" / "audio"),
            },
        },
    )

    assert connection.errors == []
    assert connection.results
    payload = connection.results[-1][1]
    assert payload["errors"][TEMP_PATH_KEY] == TEMP_PATH_KEY
    assert payload["message_type"] == "error"


@pytest.mark.asyncio
async def test_websocket_save_settings_allows_invalid_media_path_with_override(
    tmp_path: Path,
) -> None:
    """The sidebar override should allow saving an otherwise invalid path field."""
    hass, config_entry, paths = make_hass(tmp_path)
    connection = FakeConnection()
    overridden_path = str(paths["root_dir"] / "outside" / "audio")

    await save_settings_handler(
        hass,
        connection,
        {
            "id": 2,
            "type": "chime_tts/save_settings",
            "values": {
                **config_entry.options,
                TEMP_PATH_KEY: overridden_path,
            },
            "allow_invalid_paths": [TEMP_PATH_KEY],
        },
    )

    assert connection.errors == []
    assert connection.results
    payload = connection.results[-1][1]
    assert payload["errors"] == {}
    assert payload["message_type"] == "success"
    assert payload["values"][TEMP_PATH_KEY] == overridden_path
    assert config_entry.options[TEMP_PATH_KEY] == overridden_path


def test_build_panel_payload_includes_notify_profiles_from_configuration_yaml(
    tmp_path: Path,
) -> None:
    """The sidebar payload should expose YAML-backed Chime TTS notify profiles."""
    hass, config_entry, paths = make_hass(tmp_path)
    paths["config_dir"].joinpath("configuration.yaml").write_text(
        yaml.safe_dump(
            {
                "notify": [
                    {"platform": "file", "name": "archive"},
                    {
                        "platform": DOMAIN,
                        "name": "kitchen",
                        "entity_id": ["media_player.kitchen", "media_player.office"],
                        "crossfade": 125,
                        "options": {"voice": "Amy"},
                        "announce": True,
                    },
                ]
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    payload = settings_module.build_panel_payload(hass, config_entry)

    notify_section = next(
        section for section in payload["sections"] if section["key"] == "notify_profiles"
    )
    notify_profile_fields = {
        field["key"]: field for field in notify_section["profile_fields"]
    }
    assert notify_section["kind"] == "notify_profiles"
    assert notify_section["docs_url"].endswith("/notify/")
    assert {
        key: field["docs_url"] for key, field in notify_profile_fields.items()
    } == settings_module.NOTIFY_FIELD_DOCUMENTATION_URLS
    assert payload["notify_profiles"] == [
        {
            "name": "kitchen",
            "entity_id": "media_player.kitchen, media_player.office",
            "chime_path": "",
            "end_chime_path": "",
            "tts_platform": "",
            "language": "",
            "voice": "",
            "tld": "",
            "offset": "",
            "crossfade": 125,
            "final_delay": "",
            "tts_speed": "",
            "tts_pitch": "",
            "volume_level": "",
            "audio_conversion": "",
            "options": "voice: Amy",
            "announce": True,
            "cache": False,
            "fade_audio": False,
            "join_players": False,
            "unjoin_players": False,
        }
    ]


def test_build_panel_payload_supports_home_assistant_include_notify_yaml(
    tmp_path: Path,
) -> None:
    """The sidebar payload should load notify profiles from HA-style !include YAML."""
    hass, config_entry, paths = make_hass(tmp_path)
    paths["config_dir"].joinpath("configuration.yaml").write_text(
        "notify: !include notify.yaml\n",
        encoding="utf-8",
    )
    paths["config_dir"].joinpath("notify.yaml").write_text(
        yaml.safe_dump(
            [
                {"platform": "file", "name": "archive"},
                {
                    "platform": DOMAIN,
                    "name": "kitchen",
                    "entity_id": ["media_player.kitchen", "media_player.office"],
                    "options": {"voice": "Amy"},
                },
            ],
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    payload = settings_module.build_panel_payload(hass, config_entry)

    assert payload["notify_profiles_load_error"] is None


def test_sidebar_exposes_default_playback_script_fields(tmp_path: Path) -> None:
    """The service section should expose configurable default scripts."""
    hass, config_entry, _paths = make_hass(tmp_path)
    config_entry.options.update(
        {
            "default_pre_script_key": "script.prepare_speakers",
            "default_post_script_key": "script.restore_speakers",
        }
    )

    payload = settings_module.build_panel_payload(hass, config_entry)
    service_section = next(
        section for section in payload["sections"] if section["key"] == "general"
    )
    fields = {field["key"]: field for field in service_section["fields"]}

    assert service_section["title"] == "Action & Script Options"
    assert fields["default_pre_script_key"]["label"] == "Default pre-playback script"
    assert fields["default_post_script_key"]["label"] == "Default post-playback script"
    assert fields["default_pre_script_key"]["advanced"] is False
    assert fields["default_post_script_key"]["advanced"] is False
    assert fields["default_pre_script_key"]["type"] == "textarea"
    assert fields["default_post_script_key"]["type"] == "textarea"
    assert payload["values"]["default_pre_script_key"] == "script.prepare_speakers"
    assert payload["values"]["default_post_script_key"] == "script.restore_speakers"
    assert payload["notify_profiles"] == [
        {
            "name": "kitchen",
            "entity_id": "media_player.kitchen, media_player.office",
            "chime_path": "",
            "end_chime_path": "",
            "tts_platform": "",
            "language": "",
            "voice": "",
            "tld": "",
            "offset": "",
            "crossfade": "",
            "final_delay": "",
            "tts_speed": "",
            "tts_pitch": "",
            "volume_level": "",
            "audio_conversion": "",
            "options": "voice: Amy",
            "announce": False,
            "cache": False,
            "fade_audio": False,
            "join_players": False,
            "unjoin_players": False,
        }
    ]


def test_build_panel_payload_exposes_docs_urls_for_all_notify_profile_fields(
    tmp_path: Path,
) -> None:
    """Every notify profile field should advertise its intended documentation link."""
    hass, config_entry, _paths = make_hass(tmp_path)

    payload = settings_module.build_panel_payload(hass, config_entry)

    notify_section = next(
        section for section in payload["sections"] if section["key"] == "notify_profiles"
    )
    actual_docs_urls = {
        field["key"]: field["docs_url"] for field in notify_section["profile_fields"]
    }

    assert actual_docs_urls == settings_module.NOTIFY_FIELD_DOCUMENTATION_URLS
    assert actual_docs_urls["tts_platform"].endswith(
        "/documentation/configuration/#default-tts-platform"
    )
    assert actual_docs_urls["language"].endswith(
        "/documentation/configuration/#default-language"
    )
    assert actual_docs_urls["voice"].endswith(
        "/documentation/configuration/#default-voice"
    )
    assert actual_docs_urls["tld"].endswith(
        "/documentation/configuration/#default-dialect"
    )
    assert actual_docs_urls["offset"].endswith(
        "/documentation/configuration/#default-offset"
    )
    assert actual_docs_urls["crossfade"].endswith(
        "/documentation/actions/say-action/parameters/#crossfade"
    )
    assert actual_docs_urls["final_delay"].endswith(
        "/documentation/actions/say-action/parameters/#final_delay"
    )
    assert actual_docs_urls["tts_speed"].endswith(
        "/documentation/actions/say-action/parameters/#tts_speed"
    )
    assert actual_docs_urls["tts_pitch"].endswith(
        "/documentation/actions/say-action/parameters/#tts_pitch"
    )
    assert actual_docs_urls["volume_level"].endswith(
        "/documentation/actions/say-action/parameters/#volume_level"
    )
    assert actual_docs_urls["audio_conversion"].endswith(
        "/documentation/actions/say-action/parameters/#audio_conversion"
    )
    assert actual_docs_urls["options"].endswith(
        "/documentation/actions/say-action/parameters/#options"
    )
    assert actual_docs_urls["announce"].endswith(
        "/documentation/actions/say-action/parameters/#announce"
    )
    assert actual_docs_urls["cache"].endswith(
        "/documentation/actions/say-action/parameters/#cache"
    )
    assert actual_docs_urls["fade_audio"].endswith(
        "/documentation/actions/say-action/parameters/#fade_audio"
    )
    assert actual_docs_urls["join_players"].endswith(
        "/documentation/actions/say-action/parameters/#join_players"
    )
    assert actual_docs_urls["unjoin_players"].endswith(
        "/documentation/actions/say-action/parameters/#unjoin_players"
    )


def test_build_panel_payload_includes_session_log_events(tmp_path: Path) -> None:
    """The sidebar payload should include grouped panel log events for this HA session."""
    hass, config_entry, _paths = make_hass(tmp_path)
    panel_logs_module.async_setup_panel_log_store(hass)
    event_id = panel_logs_module.start_panel_log_event(
        hass,
        "action_call",
        "Action call: chime_tts.say",
        row_color="action",
        details=panel_logs_module.build_action_event_details(
            DOMAIN,
            "say",
            {"message": "Testing", "entity_id": ["media_player.office"]},
        ),
    )
    panel_logs_module.finish_panel_log_event(hass, event_id)

    payload = settings_module.build_panel_payload(hass, config_entry)

    logs_section = next(section for section in payload["sections"] if section["key"] == "logs")
    assert logs_section["kind"] == "logs"
    assert payload["log_events"][0]["type"] == "action_call"
    assert payload["log_events"][0]["copy_yaml"].startswith("action: chime_tts.say")
    assert payload["log_events"][0]["can_repeat"] is True


@pytest.mark.asyncio
async def test_websocket_get_logs_returns_session_log_events(tmp_path: Path) -> None:
    """The lightweight logs websocket should return the current session log rows."""
    hass, _config_entry, _paths = make_hass(tmp_path)
    connection = FakeConnection()
    hass.services.available_services.add(("notify", "arrival"))
    panel_logs_module.async_setup_panel_log_store(hass)
    event_id = panel_logs_module.start_panel_log_event(
        hass,
        "configuration_update",
        "Configuration update completed",
        row_color="configuration",
    )
    panel_logs_module.finish_panel_log_event(hass, event_id)

    await get_logs_handler(
        hass,
        connection,
        {
            "id": 99,
            "type": "chime_tts/get_logs",
        },
    )

    assert connection.errors == []
    assert connection.results[-1][1]["log_events"][0]["title"] == "Configuration update completed"


def test_build_backfilled_grouped_events_keeps_notification_and_nested_say_logs_together() -> None:
    """Backfill should keep notify and nested say log lines in one notification row."""
    events = panel_logs_module._build_backfilled_grouped_events(  # noqa: SLF001
        [
            {
                "timestamp": "2026-07-19 10:00:00.000",
                "level": "debug",
                "logger": "custom_components.chime_tts.notify",
                "message": "Chime TTS Notify",
            },
            {
                "timestamp": "2026-07-19 10:00:00.010",
                "level": "debug",
                "logger": "custom_components.chime_tts.notify",
                "message": " - message = 'Doorbell'",
            },
            {
                "timestamp": "2026-07-19 10:00:00.020",
                "level": "debug",
                "logger": "custom_components.chime_tts",
                "message": "Chime TTS Say Called. Version test",
            },
            {
                "timestamp": "2026-07-19 10:00:00.030",
                "level": "debug",
                "logger": "custom_components.chime_tts",
                "message": "Chime TTS Say Completed in 120 ms",
            },
        ]
    )

    assert len(events) == 1
    assert events[0]["type"] == "notification_call"
    assert events[0]["title"] == "Notification profile call"
    assert [log["message"] for log in events[0]["raw_logs"]] == [
        "Chime TTS Notify",
        " - message = 'Doorbell'",
        "Chime TTS Say Called. Version test",
        "Chime TTS Say Completed in 120 ms",
    ]


def test_finish_panel_log_event_merges_nested_say_row_into_active_notification_row(
    tmp_path: Path,
) -> None:
    """Live log grouping should not leave a separate say row under a notify event."""
    hass, _config_entry, _paths = make_hass(tmp_path)
    store = panel_logs_module.async_setup_panel_log_store(hass)
    handler = hass.data[panel_logs_module.PANEL_LOG_HANDLER_KEY]

    now = time.time()

    def emit(logger_name: str, message: str, *, created: float) -> None:
        record = logging.LogRecord(
            logger_name,
            logging.DEBUG,
            __file__,
            1,
            message,
            (),
            None,
        )
        record.created = created
        handler.emit(record)

    notify_event_id = panel_logs_module.start_panel_log_event(
        hass,
        "notification_call",
        "Notification profile call",
        row_color="action",
        details=panel_logs_module.build_notification_event_details(
            "doorbell",
            {"message": "Doorbell"},
        ),
    )
    emit("custom_components.chime_tts.notify", "Chime TTS Notify", created=now)
    emit("custom_components.chime_tts.notify", " - message = 'Doorbell'", created=now + 0.01)

    say_event_id = panel_logs_module.start_panel_log_event(
        hass,
        "action_call",
        "Action call: chime_tts.say",
        row_color="action",
        details=panel_logs_module.build_action_event_details(
            DOMAIN,
            "say",
            {"message": "Doorbell"},
        ),
    )
    emit("custom_components.chime_tts", "Chime TTS Say Called. Version test", created=now + 0.02)
    emit("custom_components.chime_tts", "Chime TTS Say Completed in 120 ms", created=now + 0.03)

    assert panel_logs_module.finish_panel_log_event(hass, say_event_id) is None

    finished_notification = panel_logs_module.finish_panel_log_event(hass, notify_event_id)

    assert finished_notification is not None
    assert len(store.events) == 1
    assert store.events[0]["title"] == "Notification profile call"
    assert [log["message"] for log in store.events[0]["raw_logs"]] == [
        "Chime TTS Notify",
        " - message = 'Doorbell'",
        "Chime TTS Say Called. Version test",
        "Chime TTS Say Completed in 120 ms",
    ]


def test_merge_backfilled_events_merges_live_action_row_with_millisecond_offset() -> None:
    """A live row and backfilled row for the same action should merge despite minor timestamp drift."""
    store = panel_logs_module.PanelLogStore()
    store.events.append(
        {
            "id": "live-1",
            "type": "action_call",
            "title": "Action call: chime_tts.say_url",
            "summary": "say_url",
            "started_at": "2026-07-19T09:07:01.993000+00:00",
            "ended_at": "2026-07-19T09:07:02.500000+00:00",
            "row_color": "action",
            "has_error": False,
            "error_count": 0,
            "raw_logs": [
                {
                    "timestamp": "2026-07-19T09:07:01.994000+00:00",
                    "level": "debug",
                    "logger": "custom_components.chime_tts.helpers.helpers",
                    "message": "Chime TTS Say URL Called. Version v1.2.3",
                },
                {
                    "timestamp": "2026-07-19T09:07:02.500000+00:00",
                    "level": "debug",
                    "logger": "custom_components.chime_tts.helpers.helpers",
                    "message": "Chime TTS Say URL Completed in 500 ms",
                },
            ],
            "copy_yaml": "action: chime_tts.say_url",
            "can_repeat": True,
        }
    )

    panel_logs_module._merge_backfilled_events(  # noqa: SLF001
        store,
        panel_logs_module._build_backfilled_grouped_events(  # noqa: SLF001
            [
                {
                    "timestamp": "2026-07-19 12:07:01.994",
                    "level": "debug",
                    "logger": "custom_components.chime_tts.helpers.helpers",
                    "message": "Chime TTS Say URL Called. Version v1.2.3",
                },
                {
                    "timestamp": "2026-07-19 12:07:02.500",
                    "level": "debug",
                    "logger": "custom_components.chime_tts.helpers.helpers",
                    "message": "Chime TTS Say URL Completed in 500 ms",
                },
            ]
        ),
    )

    events = panel_logs_module._dedupe_events(store.events)  # noqa: SLF001
    assert len(events) == 1
    assert events[0]["title"] == "Action call: chime_tts.say_url"


def test_get_panel_log_events_merges_live_initialization_row_with_backfilled_setup_logs(
    tmp_path: Path,
) -> None:
    """A live initialization row should be enriched with earlier and later setup log lines from backfill."""
    hass, _config_entry, paths = make_hass(tmp_path)
    store = panel_logs_module.async_setup_panel_log_store(hass)
    store.events.append(
        {
            "id": "live-init",
            "type": "integration_initiation",
            "title": "Integration initialization",
            "summary": "Chime TTS Version v1.2.3 is set up",
            "started_at": "2026-07-19T09:36:08.827000+00:00",
            "ended_at": "2026-07-19T09:36:08.827000+00:00",
            "row_color": "configuration",
            "has_error": False,
            "error_count": 0,
            "raw_logs": [
                {
                    "timestamp": "2026-07-19T09:36:08.827000+00:00",
                    "level": "debug",
                    "logger": "custom_components.chime_tts.helpers.helpers",
                    "message": "Chime TTS Version v1.2.3 is set up",
                }
            ],
            "copy_yaml": "",
            "can_repeat": False,
        }
    )

    (paths["config_dir"] / "home-assistant.log").write_text(
        "\n".join(
            [
                "2026-07-19 12:36:08.826 DEBUG (MainThread) [homeassistant.setup] Setting up chime_tts",
                "2026-07-19 12:36:08.827 DEBUG (MainThread) [custom_components.chime_tts.helpers.helpers] Chime TTS Version v1.2.3 is set up",
                "2026-07-19 12:36:08.850 DEBUG (MainThread) [custom_components.chime_tts.helpers.panel] Registered Chime TTS panel module view at /api/chime_tts/panel.js?v=1",
                "2026-07-19 12:36:08.860 DEBUG (MainThread) [custom_components.chime_tts.helpers.panel] Registered Chime TTS panel websocket commands",
                "2026-07-19 12:36:08.873 DEBUG (MainThread) [custom_components.chime_tts.helpers.panel] Registered Chime TTS sidebar panel at /chime-tts",
                "",
            ]
        ),
        encoding="utf-8",
    )

    events = panel_logs_module.get_panel_log_events(hass)

    assert len(events) == 1
    assert [log["message"] for log in events[0]["raw_logs"]] == [
        "Setting up chime_tts",
        "Chime TTS Version v1.2.3 is set up",
        "Registered Chime TTS panel module view at /api/chime_tts/panel.js?v=1",
        "Registered Chime TTS panel websocket commands",
        "Registered Chime TTS sidebar panel at /chime-tts",
    ]


def test_get_panel_log_events_backfills_complete_initialization_row(tmp_path: Path) -> None:
    """Initialization rows should include the full setup sequence from the HA log."""
    hass, _config_entry, paths = make_hass(tmp_path)
    log_path = paths["config_dir"] / "home-assistant.log"
    log_path.write_text(
        "\n".join(
            [
                "2026-07-19 10:00:00.000 DEBUG (MainThread) [homeassistant.setup] Setting up chime_tts",
                "2026-07-19 10:00:00.010 DEBUG (MainThread) [custom_components.chime_tts] Chime TTS Version v1.2.3 is set up",
                "2026-07-19 10:00:00.020 DEBUG (MainThread) [custom_components.chime_tts.helpers.panel] Registered Chime TTS panel module view at /api/chime_tts/panel.js?v=1",
                "2026-07-19 10:00:00.030 DEBUG (MainThread) [custom_components.chime_tts.helpers.panel] Registered Chime TTS panel websocket commands",
                "2026-07-19 10:00:00.040 DEBUG (MainThread) [custom_components.chime_tts.helpers.panel] Registered Chime TTS sidebar panel at /chime-tts",
                "",
            ]
        ),
        encoding="utf-8",
    )

    events = panel_logs_module.get_panel_log_events(hass)

    assert len(events) == 1
    assert events[0]["type"] == "integration_initiation"
    assert [log["message"] for log in events[0]["raw_logs"]] == [
        "Setting up chime_tts",
        "Chime TTS Version v1.2.3 is set up",
        "Registered Chime TTS panel module view at /api/chime_tts/panel.js?v=1",
        "Registered Chime TTS panel websocket commands",
        "Registered Chime TTS sidebar panel at /chime-tts",
    ]


@pytest.mark.asyncio
async def test_websocket_save_settings_updates_notify_profiles_in_configuration_yaml(
    tmp_path: Path,
) -> None:
    """Saving from the panel should rewrite only Chime TTS notify entries."""
    hass, config_entry, paths = make_hass(tmp_path)
    paths["config_dir"].joinpath("configuration.yaml").write_text(
        yaml.safe_dump(
            {
                "notify": [
                    {"platform": "file", "name": "archive"},
                    {
                        "platform": DOMAIN,
                        "name": "old_profile",
                        "entity_id": "media_player.office",
                    },
                ]
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    connection = FakeConnection()

    await save_settings_handler(
        hass,
        connection,
        {
            "id": 3,
            "type": "chime_tts/save_settings",
            "values": dict(config_entry.options),
            "notify_profiles": [
                {
                    "name": "arrival",
                    "entity_id": "media_player.kitchen, media_player.office",
                    "crossfade": "200",
                    "volume_level": "0.65",
                    "options": "voice: Amy\nstyle: cheerful",
                    "announce": True,
                    "cache": True,
                }
            ],
        },
    )

    assert connection.errors == []
    payload = connection.results[-1][1]
    assert payload["message_type"] == "success"
    assert payload["restart_required"] is True
    assert payload["notify_profiles"][0]["name"] == "arrival"

    saved_config = yaml.safe_load(
        paths["config_dir"].joinpath("configuration.yaml").read_text(encoding="utf-8")
    )
    assert saved_config["notify"][0] == {"platform": "file", "name": "archive"}
    assert saved_config["notify"][1] == {
        "platform": DOMAIN,
        "name": "arrival",
        "entity_id": ["media_player.kitchen", "media_player.office"],
        "crossfade": 200,
        "volume_level": 0.65,
        "options": {"voice": "Amy", "style": "cheerful"},
        "announce": True,
        "cache": True,
    }


@pytest.mark.asyncio
async def test_websocket_save_settings_preserves_notify_profile_order_across_reload(
    tmp_path: Path,
) -> None:
    """Saved notify profile order should match the panel order after reloads."""
    hass, config_entry, paths = make_hass(tmp_path)
    paths["config_dir"].joinpath("configuration.yaml").write_text(
        yaml.safe_dump(
            {
                "notify": [
                    {"platform": "file", "name": "archive"},
                    {
                        "platform": DOMAIN,
                        "name": "kitchen",
                        "entity_id": "media_player.kitchen",
                    },
                    {
                        "platform": DOMAIN,
                        "name": "office",
                        "entity_id": "media_player.office",
                    },
                ]
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    connection = FakeConnection()

    await save_settings_handler(
        hass,
        connection,
        {
            "id": 30,
            "type": "chime_tts/save_settings",
            "values": dict(config_entry.options),
            "notify_profiles": [
                {
                    "name": "arrival",
                    "entity_id": "media_player.hallway",
                },
                {
                    "name": "kitchen",
                    "entity_id": "media_player.kitchen",
                },
                {
                    "name": "office",
                    "entity_id": "media_player.office",
                },
            ],
        },
    )

    assert connection.errors == []
    payload = connection.results[-1][1]
    assert [profile["name"] for profile in payload["notify_profiles"]] == [
        "arrival",
        "kitchen",
        "office",
    ]

    reloaded_profiles, load_error = settings_module.load_notify_profiles(hass)

    assert load_error is None
    assert [profile["name"] for profile in reloaded_profiles] == [
        "arrival",
        "kitchen",
        "office",
    ]


@pytest.mark.asyncio
async def test_websocket_save_settings_rejects_invalid_notify_profile_yaml(
    tmp_path: Path,
) -> None:
    """Invalid notify options YAML should be surfaced in the panel payload."""
    hass, config_entry, _paths = make_hass(tmp_path)
    connection = FakeConnection()

    await save_settings_handler(
        hass,
        connection,
        {
            "id": 4,
            "type": "chime_tts/save_settings",
            "values": dict(config_entry.options),
            "notify_profiles": [
                {
                    "name": "arrival",
                    "entity_id": "media_player.kitchen",
                    "options": "voice: [",
                }
            ],
        },
    )

    assert connection.errors == []
    payload = connection.results[-1][1]
    assert payload["message_type"] == "error"
    assert payload["notify_profile_errors"] == [{"options": "invalid_yaml"}]


@pytest.mark.asyncio
async def test_websocket_repeat_log_action_replays_logged_service_call(
    tmp_path: Path,
) -> None:
    """Repeating a logged action should call the original Chime TTS service again."""
    hass, config_entry, _paths = make_hass(tmp_path)
    connection = FakeConnection()
    recorded_say_calls: list[dict[str, object]] = []

    async def fake_async_say(service):
        recorded_say_calls.append(dict(service.data or {}))
        return True

    hass.data[DOMAIN]["async_say"] = fake_async_say
    panel_logs_module.async_setup_panel_log_store(hass)
    event_id = panel_logs_module.start_panel_log_event(
        hass,
        "action_call",
        "Action call: chime_tts.say",
        row_color="action",
        details=panel_logs_module.build_action_event_details(
            DOMAIN,
            "say",
            {"message": "Replay me", "entity_id": ["media_player.office"]},
        ),
    )
    panel_logs_module.finish_panel_log_event(hass, event_id)

    await repeat_log_action_handler(
        hass,
        connection,
        {
            "id": 5,
            "type": "chime_tts/repeat_log_action",
            "event_id": event_id,
        },
    )

    assert connection.errors == []
    assert recorded_say_calls == [
        {"message": "Replay me", "entity_id": ["media_player.office"]}
    ]
    payload = connection.results[-1][1]
    assert payload["message_type"] == "success"


@pytest.mark.asyncio
async def test_websocket_repeat_log_action_replays_logged_notification_call(
    tmp_path: Path,
) -> None:
    """Repeating a logged notification should call the original notify service again."""
    hass, _config_entry, _paths = make_hass(tmp_path)
    connection = FakeConnection()
    hass.services.available_services.add(("notify", "arrival"))
    panel_logs_module.async_setup_panel_log_store(hass)
    event_id = panel_logs_module.start_panel_log_event(
        hass,
        "notification_call",
        "Notification profile call",
        row_color="action",
        details=panel_logs_module.build_notification_event_details(
            "arrival",
            {"message": "Front door open"},
        ),
        summary="notify.arrival",
    )
    panel_logs_module.finish_panel_log_event(hass, event_id)

    await repeat_log_action_handler(
        hass,
        connection,
        {
            "id": 6,
            "type": "chime_tts/repeat_log_action",
            "event_id": event_id,
        },
    )

    assert connection.errors == []
    assert hass.services.calls == [
        {
            "domain": "notify",
            "service": "arrival",
            "service_data": {"message": "Front door open"},
            "blocking": False,
        }
    ]
    payload = connection.results[-1][1]
    assert payload["message_type"] == "success"


@pytest.mark.asyncio
async def test_websocket_repeat_log_action_replays_notification_with_none_data_payload(
    tmp_path: Path,
) -> None:
    """Repeating a logged notification should coerce a None notify data payload away."""
    hass, _config_entry, _paths = make_hass(tmp_path)
    connection = FakeConnection()
    hass.services.available_services.add(("notify", "arrival"))
    panel_logs_module.async_setup_panel_log_store(hass)
    event_id = panel_logs_module.start_panel_log_event(
        hass,
        "notification_call",
        "Notification profile call",
        row_color="action",
        details=panel_logs_module.build_notification_event_details(
            "arrival",
            {"message": "hello", "data": None},
        ),
        summary="notify.arrival",
    )
    panel_logs_module.finish_panel_log_event(hass, event_id)

    await repeat_log_action_handler(
        hass,
        connection,
        {
            "id": 7,
            "type": "chime_tts/repeat_log_action",
            "event_id": event_id,
        },
    )

    assert connection.errors == []
    assert hass.services.calls == [
        {
            "domain": "notify",
            "service": "arrival",
            "service_data": {"message": "hello"},
            "blocking": False,
        }
    ]
    payload = connection.results[-1][1]
    assert payload["message_type"] == "success"
