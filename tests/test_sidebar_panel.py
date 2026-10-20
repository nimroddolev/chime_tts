"""Tests for the Chime TTS sidebar settings backend."""

from __future__ import annotations

import errno
import inspect
import importlib
import logging
import os
from datetime import timedelta
from datetime import timezone
from pathlib import Path
import stat
import time
from types import SimpleNamespace
import yaml

import pytest
from homeassistant.components.notify.legacy import NOTIFY_SERVICES

from custom_components.chime_tts.const import (
    CHIME_OFFSETS_KEY,
    CHIME_SETS_KEY,
    CUSTOM_CHIMES_PATH_KEY,
    DEFAULT_CHIME_OFFSETS,
)
from custom_components.chime_tts.const import TEMP_CHIMES_PATH_KEY
from custom_components.chime_tts.const import TEMP_PATH_KEY
from custom_components.chime_tts.const import TTS_PLATFORM_KEY
from custom_components.chime_tts.const import WWW_PATH_KEY
from custom_components.chime_tts.const import DOMAIN
from custom_components.chime_tts.const import INITIAL_DELAY_KEY

panel_module = importlib.import_module("custom_components.chime_tts.helpers.panel")
panel_logs_module = importlib.import_module("custom_components.chime_tts.helpers.panel_logs")
settings_module = importlib.import_module("custom_components.chime_tts.settings")
save_settings_handler = inspect.unwrap(panel_module.websocket_save_settings)
repeat_log_action_handler = inspect.unwrap(panel_module.websocket_repeat_log_action)
get_logs_handler = inspect.unwrap(panel_module.websocket_get_logs)
get_debug_log_status_handler = inspect.unwrap(panel_module.websocket_get_debug_log_status)
get_settings_handler = inspect.unwrap(panel_module.websocket_get_settings)
get_notify_profiles_handler = inspect.unwrap(panel_module.websocket_get_notify_profiles)
browse_path_handler = inspect.unwrap(panel_module.websocket_browse_path)
create_folder_handler = inspect.unwrap(panel_module.websocket_browser_create_folder)
rename_entry_handler = inspect.unwrap(panel_module.websocket_browser_rename_entry)
delete_entry_handler = inspect.unwrap(panel_module.websocket_browser_delete_entry)


def test_browser_upload_accepts_supported_audio_extensions_only() -> None:
    """Reject non-audio uploads before they reach the custom chimes folder."""
    assert panel_module._is_supported_audio_upload("doorbell.mp3")
    assert panel_module._is_supported_audio_upload("DOORBELL.WAV")
    assert panel_module._is_supported_audio_upload("doorbell.aiff")
    assert panel_module._is_supported_audio_upload("doorbell.oga")
    assert not panel_module._is_supported_audio_upload("doorbell.txt")
    assert not panel_module._is_supported_audio_upload("doorbell.mp3.exe")


def test_chime_set_offset_preview_combines_chime_and_sample(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The offset preview renders the selected chime with the bundled TTS sample."""
    source_paths: list[str] = []
    combine_calls: list[tuple[object, object, int]] = []

    class FakeCombinedAudio:
        def export(self, output, *, format: str) -> None:
            assert format == "mp3"
            output.write(b"preview-mp3")

    class FakeAudioSegment:
        @staticmethod
        def from_file(path: str | Path) -> str:
            source_paths.append(str(path))
            return str(path)

    class FakeHelper:
        def combine_audio(self, chime: object, sample: object, offset: int) -> FakeCombinedAudio:
            combine_calls.append((chime, sample, offset))
            return FakeCombinedAudio()

    monkeypatch.setattr(panel_module, "AudioSegment", FakeAudioSegment)
    monkeypatch.setattr(panel_module, "ChimeTTSHelper", FakeHelper)
    chime_path = tmp_path / "doorbell.mp3"
    sample_path = tmp_path / "tts_audio.mp3"

    assert panel_module._render_chime_set_offset_preview(chime_path, sample_path, -250) == b"preview-mp3"
    assert source_paths == [str(chime_path), str(sample_path)]
    assert combine_calls == [(str(chime_path), str(sample_path), -250)]


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


class FakeNotifyProfileService:
    """Represent a registered notify profile for panel re-registration tests."""

    def __init__(self, service_name: str, config: dict) -> None:
        self._service_name = service_name
        self._config = config
        self.unregister_calls = 0
        self.register_calls = 0

    async def async_unregister_services(self) -> None:
        self.unregister_calls += 1

    async def async_register_services(self) -> None:
        self.register_calls += 1


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
    assert payload["restart_required_field_keys"] == []
    assert [section["key"] for section in payload["sections"]] == [
        "chimes",
        "chime_sets",
        "voice",
        "playback",
        "audio_folders",
        "general",
        "notify_profiles",
        "logs",
        "about",
    ]
    assert payload["log_events"] == []

    chime_sets_section = next(
        section for section in payload["sections"] if section["key"] == "chime_sets"
    )
    assert chime_sets_section["docs_url"].endswith("/chime-sets/")

    chimes_section = next(section for section in payload["sections"] if section["key"] == "chimes")
    assert chimes_section["kind"] == "chimes"
    assert chimes_section["docs_url"].endswith("/chimes/")
    assert chimes_section["folder_section"]["key"] == "paths"
    assert [field["key"] for field in chimes_section["folder_section"]["fields"]] == [
        CUSTOM_CHIMES_PATH_KEY,
        TEMP_CHIMES_PATH_KEY,
    ]
    assert chimes_section["available_chimes"]

    audio_folders_section = next(section for section in payload["sections"] if section["key"] == "audio_folders")
    assert [field["key"] for field in audio_folders_section["fields"]] == [
        TEMP_PATH_KEY,
        WWW_PATH_KEY,
    ]

    voice_section = next(section for section in payload["sections"] if section["key"] == "voice")
    language_field = next(
        field for field in voice_section["fields"] if field["key"] == "default_language_key"
    )
    paths_section = chimes_section["folder_section"]
    custom_chimes_field = next(
        field for field in paths_section["fields"] if field["key"] == CUSTOM_CHIMES_PATH_KEY
    )

    assert language_field["provider_hint"]["tone"] == "info"
    assert "Google Translate" in language_field["provider_hint"]["message"]
    assert language_field["advanced"] is False
    assert next(
        field for field in voice_section["fields"] if field["key"] == "default_voice_key"
    )["advanced"] is False
    assert next(
        field for field in voice_section["fields"] if field["key"] == "default_tld_key"
    )["advanced"] is False
    assert language_field["icon_url"].startswith(
        f"/api/{DOMAIN}/images/option_icons/language.svg"
    )
    assert (
        f"?v={settings_module.VERSION.lstrip('v') or settings_module.VERSION}&asset="
        in language_field["icon_url"]
    )
    assert custom_chimes_field["icon_url"].startswith(
        f"/api/{DOMAIN}/images/option_icons/{CUSTOM_CHIMES_PATH_KEY}.svg"
    )
    assert (
        f"?v={settings_module.VERSION.lstrip('v') or settings_module.VERSION}&asset="
        in custom_chimes_field["icon_url"]
    )
    assert custom_chimes_field["can_browse"] is True
    assert (
        custom_chimes_field["path_validation"]["message"]
        == "Folder path is valid for this setting."
    )
    playback_section = next(
        section for section in payload["sections"] if section["key"] == "playback"
    )
    crossfade_field = next(
        field for field in playback_section["fields"] if field["key"] == "crossfade"
    )
    initial_delay_field = next(
        field for field in playback_section["fields"] if field["key"] == INITIAL_DELAY_KEY
    )
    assert crossfade_field["docs_url"].endswith(
        "/documentation/configuration/playback-options/#default-crossfade"
    )
    assert initial_delay_field["min"] == 0
    assert initial_delay_field["icon_url"].startswith(
        f"/api/{DOMAIN}/images/option_icons/{INITIAL_DELAY_KEY}.svg"
    )
    about_section = next(section for section in payload["sections"] if section["key"] == "about")
    assert about_section["kind"] == "about"
    assert about_section["version"] == payload["version"]
    assert all(item["title"] != "Version" for item in about_section["about_items"])
    assert any(item["title"] == "Buy Me a Coffee" for item in about_section["about_items"])


def test_chime_offsets_are_normalized_from_panel_values(tmp_path: Path) -> None:
    """Per-chime offsets override the tuned defaults in panel configuration."""
    hass, config_entry, _paths = make_hass(tmp_path)
    values = settings_module.get_settings_data(
        hass,
        config_entry,
        {CHIME_OFFSETS_KEY: {"bells": "125", "custom/doorbell.mp3": -50}},
    )

    assert values[CHIME_OFFSETS_KEY] == {
        **DEFAULT_CHIME_OFFSETS,
        "bells": 125,
        "custom/doorbell.mp3": -50,
    }


@pytest.mark.asyncio
async def test_websocket_save_settings_persists_only_custom_chime_offset_overrides(
    tmp_path: Path,
) -> None:
    """A changed per-chime offset survives restarts without pinning defaults."""
    hass, config_entry, _paths = make_hass(tmp_path)
    values = settings_module.get_settings_data(hass, config_entry)
    values[CHIME_OFFSETS_KEY]["bells"] = 125
    connection = FakeConnection()

    await save_settings_handler(
        hass,
        connection,
        {
            "id": 3,
            "type": "chime_tts/save_settings",
            "values": values,
            "notify_profiles": [],
        },
    )

    assert connection.errors == []
    assert config_entry.options[CHIME_OFFSETS_KEY] == {"bells": 125}
    assert settings_module.get_settings_data(hass, config_entry)[CHIME_OFFSETS_KEY] == {
        **DEFAULT_CHIME_OFFSETS,
        "bells": 125,
    }


@pytest.mark.asyncio
async def test_websocket_save_settings_persists_new_chime_set_and_requires_restart(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A saved Chime Set responds without waiting for a full panel refresh."""
    hass, config_entry, _paths = make_hass(tmp_path)
    values = settings_module.get_settings_data(hass, config_entry)
    values[CHIME_SETS_KEY] = [
        {
            "id": "soft",
            "name": "Soft",
            "chimes": ["bells", "marimba"],
            "offsets": {},
        }
    ]
    connection = FakeConnection()

    async def fail_if_panel_refresh_is_requested(*args, **kwargs):
        raise AssertionError("Save responses must not wait for a panel refresh")

    monkeypatch.setattr(panel_module, "async_build_panel_payload", fail_if_panel_refresh_is_requested)

    async def fail_if_background_tasks_are_waited_on():
        raise AssertionError("Save responses must not wait for background tasks")

    hass.async_block_till_done = fail_if_background_tasks_are_waited_on

    await save_settings_handler(
        hass,
        connection,
        {
            "id": 4,
            "type": "chime_tts/save_settings",
            "values": values,
            "notify_profiles": [],
        },
    )

    assert connection.errors == []
    payload = connection.results[-1][1]
    assert payload["message_type"] == "success"
    assert payload["restart_required"] is True
    assert config_entry.options[CHIME_SETS_KEY] == values[CHIME_SETS_KEY]


@pytest.mark.asyncio
async def test_websocket_save_settings_leaves_configuration_yaml_untouched_when_profiles_unchanged(
    tmp_path: Path,
) -> None:
    """Saving an ordinary setting must not rewrite configuration.yaml (#352)."""
    hass, config_entry, paths = make_hass(tmp_path)
    config_file = paths["config_dir"].joinpath("configuration.yaml")
    original = (
        "# Keep this operational note.\n"
        "default_config:\n"
        "\n"
        "# Disabled configuration must not disappear.\n"
        "# recorder:\n"
        "#   purge_keep_days: 5\n"
        "\n"
        "shell_command:\n"
        "  formatting_example: |-\n"
        "    printf '%s\\n' 'first line'\n"
        "    printf '%s\\n' 'second line'\n"
    )
    config_file.write_text(original, encoding="utf-8")
    values = settings_module.get_settings_data(hass, config_entry)
    values[CHIME_OFFSETS_KEY]["bells"] = 125
    connection = FakeConnection()

    await save_settings_handler(
        hass,
        connection,
        {
            "id": 4,
            "type": "chime_tts/save_settings",
            "values": values,
            "notify_profiles": [],
        },
    )

    assert connection.errors == []
    assert connection.results[-1][1]["message_type"] == "success"
    assert config_entry.options[CHIME_OFFSETS_KEY] == {"bells": 125}
    assert config_file.read_text(encoding="utf-8") == original


@pytest.mark.asyncio
async def test_websocket_save_custom_chimes_path_does_not_require_restart(tmp_path: Path) -> None:
    """A custom chimes folder update is applied without a restart prompt."""
    hass, config_entry, paths = make_hass(tmp_path)
    new_custom_chimes_dir = paths["config_dir"] / "alternate_chimes"
    new_custom_chimes_dir.mkdir()
    values = dict(config_entry.options)
    values[CUSTOM_CHIMES_PATH_KEY] = str(new_custom_chimes_dir)
    connection = FakeConnection()

    await save_settings_handler(
        hass,
        connection,
        {
            "id": 2,
            "type": "chime_tts/save_settings",
            "values": values,
            "notify_profiles": [],
        },
    )

    assert connection.errors == []
    payload = connection.results[-1][1]
    assert payload["message_type"] == "success"
    assert payload["restart_required"] is False
    assert config_entry.options[CUSTOM_CHIMES_PATH_KEY] == str(new_custom_chimes_dir)


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


@pytest.mark.asyncio
async def test_issue_318_websocket_validate_path_runs_off_event_loop(tmp_path: Path) -> None:
    """Path validation stats the filesystem in the executor, not on the loop (#318)."""
    import asyncio
    import threading

    hass, _config_entry, paths = make_hass(tmp_path)
    loop_thread = threading.get_ident()
    validate_threads: list[bool] = []
    original_validate = settings_module.validate_path_field

    def tracked_validate(*args):
        validate_threads.append(threading.get_ident() != loop_thread)
        return original_validate(*args)

    async def threaded_executor(func, *args):
        if func is original_validate:
            func = tracked_validate
        return await asyncio.get_running_loop().run_in_executor(None, func, *args)

    hass.async_add_executor_job = threaded_executor
    connection = FakeConnection()
    msg = {
        "id": 7,
        "type": "chime_tts/validate_path",
        "field_key": CUSTOM_CHIMES_PATH_KEY,
        "path": str(paths["custom_chimes_dir"]),
    }

    await inspect.unwrap(panel_module.websocket_validate_path)(hass, connection, msg)

    assert validate_threads == [True]
    assert connection.errors == []
    assert connection.results[-1][0] == 7
    assert connection.results[-1][1]["tone"] == "success"


def test_websocket_validate_path_still_requires_admin(tmp_path: Path) -> None:
    """Non-admin users are rejected before any validation work is scheduled."""
    from homeassistant.exceptions import Unauthorized

    hass, _config_entry, paths = make_hass(tmp_path)
    connection = FakeConnection(is_admin=False)

    with pytest.raises(Unauthorized):
        panel_module.websocket_validate_path(
            hass,
            connection,
            {
                "id": 8,
                "type": "chime_tts/validate_path",
                "field_key": CUSTOM_CHIMES_PATH_KEY,
                "path": str(paths["custom_chimes_dir"]),
            },
        )
    assert connection.results == []


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


def test_directory_browser_includes_filesystem_root_without_expanding_access(
    tmp_path: Path,
) -> None:
    """The root location supports navigation without allowing it as a media path."""
    hass, config_entry, paths = make_hass(tmp_path)

    payload = settings_module.build_directory_browser_payload(
        hass,
        config_entry,
        TEMP_PATH_KEY,
        str(paths["temp_audio_dir"]),
    )

    assert any(root["path"] == "/" for root in payload["roots"])
    assert settings_module.is_path_navigable_for_field(
        hass, config_entry, TEMP_PATH_KEY, "/"
    )
    assert not settings_module.is_path_allowed_for_field(
        hass, config_entry, TEMP_PATH_KEY, "/"
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
async def test_websocket_create_folder_reports_an_existing_folder_name(
    tmp_path: Path,
) -> None:
    """Creating an existing folder returns an error the modal can display."""
    hass, _config_entry, paths = make_hass(tmp_path)
    connection = FakeConnection()
    (paths["temp_audio_dir"] / "uploads").mkdir()

    await create_folder_handler(
        hass,
        connection,
        {
            "id": 13,
            "type": "chime_tts/browser_create_folder",
            "field_key": TEMP_PATH_KEY,
            "path": str(paths["temp_audio_dir"]),
            "name": "uploads",
        },
    )

    assert connection.errors == [
        (13, "already_exists", "A folder with that name already exists."),
    ]


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
                        "pre_script": "script.prepare_speakers",
                        "post_script": "script.restore_speakers",
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
            "pre_script": "script.prepare_speakers",
            "post_script": "script.restore_speakers",
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
            "pre_script": "",
            "post_script": "",
            "announce": False,
            "cache": False,
            "fade_audio": False,
            "join_players": False,
            "unjoin_players": False,
        }
    ]


def test_sidebar_exposes_default_playback_script_fields(tmp_path: Path) -> None:
    """The service section should expose configurable default scripts."""
    hass, config_entry, _paths = make_hass(tmp_path)
    script_entities = {
        "script.prepare_speakers": SimpleNamespace(entity_id="script.prepare_speakers"),
        "script.restore_speakers": SimpleNamespace(entity_id="script.restore_speakers"),
    }
    hass.states = SimpleNamespace(get=script_entities.get)
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
    assert hass.states.get("script.prepare_speakers") is not None
    assert hass.states.get("script.restore_speakers") is not None


def test_sidebar_keeps_action_scripts_shared_by_default_and_clears_url_scripts(
    tmp_path: Path,
) -> None:
    """The panel supports action-specific scripts without preserving stale URL values."""
    hass, config_entry, _paths = make_hass(tmp_path)
    config_entry.options.update(
        {
            "default_pre_script_key": "script.say_pre",
            "default_post_script_key": "script.say_post",
            "default_scripts_shared_key": False,
            "default_pre_script_say_url_key": "script.url_pre",
            "default_post_script_say_url_key": "script.url_post",
        }
    )

    values = settings_module.get_settings_data(hass, config_entry)
    assert values["default_pre_script_shared_key"] is False
    assert values["default_post_script_shared_key"] is False
    assert values["default_pre_script_say_url_key"] == "script.url_pre"

    validation = settings_module.validate_settings(
        hass,
        config_entry,
        {
            **values,
            "default_pre_script_shared_key": True,
            "default_post_script_shared_key": False,
        },
    )
    assert validation.errors == {}
    assert validation.data["default_pre_script_say_url_key"] == ""
    assert validation.data["default_post_script_say_url_key"] == "script.url_post"

    payload = settings_module.build_panel_payload(hass, config_entry)
    general = next(section for section in payload["sections"] if section["key"] == "general")
    fields = {field["key"]: field for field in general["fields"]}
    assert fields["default_pre_script_shared_key"]["type"] == "boolean"
    assert fields["default_post_script_shared_key"]["type"] == "boolean"
    assert fields["default_pre_script_shared_key"]["label"] == (
        "Use for both chime_tts.say & chime_tts.say_url actions"
    )
    assert fields["default_pre_script_say_url_key"]["type"] == "textarea"
    assert fields["default_post_script_say_url_key"]["type"] == "textarea"


def test_sidebar_renders_action_specific_script_controls_with_section_accent() -> None:
    """The panel labels both actions and clears URL scripts when sharing is re-enabled."""
    panel_source = (
        Path(__file__).parents[1]
        / "custom_components"
        / "chime_tts"
        / "panel"
        / "chime-tts-panel.js"
    ).read_text(encoding="utf-8")

    assert 'class="script-action-label">chime_tts.say</p>' in panel_source
    assert 'class="script-action-label">chime_tts.say_url</p>' in panel_source
    assert "var(--section-help-color)" in panel_source
    assert 'key === "default_pre_script_shared_key" && nextValue' in panel_source
    assert 'key === "default_post_script_shared_key" && nextValue' in panel_source
    assert "_captureAncestorScrollPositions(activeElement)" in panel_source
    assert 'activeElement?.type !== "checkbox"' in panel_source
    assert ".layout {" in panel_source
    assert "overflow-anchor: none;" in panel_source
    assert "window.setTimeout(restoreScrollPosition, 100);" in panel_source


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


@pytest.mark.asyncio
async def test_websocket_get_debug_log_status_reads_integration_logger_level(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The panel reports Chime TTS's explicitly configured logger level."""
    hass, _config_entry, _paths = make_hass(tmp_path)
    connection = FakeConnection()

    async def get_loggers(_hass, _domain):
        return {"custom_components.chime_tts"}

    monkeypatch.setattr(
        panel_module,
        "get_integration_loggers",
        get_loggers,
    )
    logger = logging.getLogger("custom_components.chime_tts")
    previous_level = logger.level
    logger.setLevel(logging.DEBUG)
    try:
        await get_debug_log_status_handler(
            hass,
            connection,
            {"id": 100, "type": "chime_tts/get_debug_log_status"},
        )
        assert connection.results[-1][1] == {"debug_enabled": True}

        logger.setLevel(logging.NOTSET)
        await get_debug_log_status_handler(
            hass,
            connection,
            {"id": 101, "type": "chime_tts/get_debug_log_status"},
        )
        assert connection.results[-1][1] == {"debug_enabled": False}
    finally:
        logger.setLevel(previous_level)

    assert connection.errors == []


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


def test_build_backfilled_grouped_events_adds_grouped_unmatched_warning_and_error_rows() -> None:
    """Unmatched Chime TTS warnings/errors should become grouped fallback log rows."""
    events = panel_logs_module._build_backfilled_grouped_events(  # noqa: SLF001
        [
            {
                "timestamp": "2026-07-27T10:00:00+00:00",
                "level": "warning",
                "logger": "homeassistant.core",
                "message": "Chime TTS warning: first unmatched line",
            },
            {
                "timestamp": "2026-07-27T10:00:00.500000+00:00",
                "level": "warning",
                "logger": "system.logger",
                "message": "chime_tts warning: second unmatched line",
            },
            {
                "timestamp": "2026-07-27T10:00:02+00:00",
                "level": "error",
                "logger": "system.logger",
                "message": "chime tts error: unmatched failure",
            },
        ]
    )

    by_type = {event["type"]: event for event in events}
    assert by_type["warning"]["title"] == "Warning"
    assert by_type["warning"]["row_color"] == "warning"
    assert by_type["warning"]["has_error"] is False
    assert [log["message"] for log in by_type["warning"]["raw_logs"]] == [
        "Chime TTS warning: first unmatched line",
        "chime_tts warning: second unmatched line",
    ]
    assert by_type["error"]["title"] == "Error"
    assert by_type["error"]["row_color"] == "error"
    assert by_type["error"]["has_error"] is True
    assert by_type["error"]["error_count"] == 1
    assert [log["message"] for log in by_type["error"]["raw_logs"]] == [
        "chime tts error: unmatched failure",
    ]


def test_panel_logs_omit_home_assistants_generic_custom_integration_warning() -> None:
    """The standard custom-integration disclaimer is not an actionable panel warning."""
    entries = [
        {
            "timestamp": "2026-07-27T10:00:00+00:00",
            "level": "warning",
            "logger": "homeassistant.loader",
            "message": (
                "We found a custom integration chime_tts which has not been tested "
                "by Home Assistant. This component might cause stability problems, "
                "be sure to disable it if you experience issues with Home Assistant"
            ),
        },
        {
            "timestamp": "2026-07-27T10:00:02+00:00",
            "level": "warning",
            "logger": "custom_components.chime_tts",
            "message": "Chime TTS warning: actionable warning",
        },
    ]

    events = panel_logs_module._build_backfilled_grouped_events(entries)  # noqa: SLF001

    assert len(events) == 1
    assert events[0]["type"] == "warning"
    assert [log["message"] for log in events[0]["raw_logs"]] == [
        "Chime TTS warning: actionable warning",
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


def test_panel_log_handler_creates_live_grouped_warning_event_without_active_row(
    tmp_path: Path,
) -> None:
    """Live unmatched Chime TTS warnings should become grouped fallback events."""
    hass, _config_entry, _paths = make_hass(tmp_path)
    store = panel_logs_module.async_setup_panel_log_store(hass)
    handler = hass.data[panel_logs_module.PANEL_LOG_HANDLER_KEY]

    now = time.time()

    def emit(level: int, logger_name: str, message: str, *, created: float) -> None:
        record = logging.LogRecord(
            logger_name,
            level,
            __file__,
            1,
            message,
            (),
            None,
        )
        record.created = created
        handler.emit(record)

    emit(logging.WARNING, "homeassistant.core", "Chime TTS warning: first line", created=now)
    emit(logging.WARNING, "system.logger", "chime_tts warning: second line", created=now + 0.2)

    assert len(store.events) == 1
    assert store.events[0]["type"] == "warning"
    assert store.events[0]["title"] == "Warning"
    assert store.events[0]["row_color"] == "warning"
    assert [log["message"] for log in store.events[0]["raw_logs"]] == [
        "Chime TTS warning: first line",
        "chime_tts warning: second line",
    ]


def test_merge_backfilled_events_merges_live_action_row_with_millisecond_offset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A live row and backfilled row for the same action should merge despite minor timestamp drift."""
    monkeypatch.setattr(
        panel_logs_module,
        "_local_tzinfo",
        lambda: timezone(timedelta(hours=3)),
    )
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
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A live initialization row should be enriched with earlier and later setup log lines from backfill."""
    monkeypatch.setattr(
        panel_logs_module,
        "_local_tzinfo",
        lambda: timezone(timedelta(hours=3)),
    )
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
                    "pre_script": "script.prepare_speakers",
                    "post_script": "script.restore_speakers",
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
        "pre_script": "script.prepare_speakers",
        "post_script": "script.restore_speakers",
        "announce": True,
        "cache": True,
    }


@pytest.mark.asyncio
async def test_websocket_save_settings_reregisters_existing_notify_profile(
    tmp_path: Path,
) -> None:
    """Changing an existing profile applies its new properties without restart."""
    hass, config_entry, paths = make_hass(tmp_path)
    paths["config_dir"].joinpath("configuration.yaml").write_text(
        yaml.safe_dump(
            {
                "notify": [
                    {
                        "platform": DOMAIN,
                        "name": "arrival",
                        "entity_id": "media_player.kitchen",
                        "volume_level": 0.4,
                    }
                ]
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    service = FakeNotifyProfileService(
        "arrival",
        {"platform": DOMAIN, "name": "arrival", "entity_id": "media_player.kitchen"},
    )
    hass.data[NOTIFY_SERVICES] = {DOMAIN: [service]}
    connection = FakeConnection()

    await save_settings_handler(
        hass,
        connection,
        {
            "id": 31,
            "type": "chime_tts/save_settings",
            "values": dict(config_entry.options),
            "notify_profiles": [
                {
                    "name": "arrival",
                    "entity_id": "media_player.kitchen",
                    "volume_level": "0.75",
                }
            ],
        },
    )

    payload = connection.results[-1][1]
    assert payload["restart_required"] is False
    assert service.unregister_calls == 1
    assert service.register_calls == 1
    assert service._config["volume_level"] == 0.75


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


def _write_profile_config(config_file: Path) -> str:
    """Write a configuration.yaml holding one Chime TTS notify profile."""
    original = (
        "# operational note\n"
        "notify:\n"
        "  - platform: chime_tts\n"
        "    name: doorbell\n"
        "    entity_id: media_player.office\n"
    )
    config_file.write_text(original, encoding="utf-8")
    return original


def _new_profile_request(values: dict) -> dict:
    """Return a save request that adds a new notify profile."""
    return {
        "id": 9,
        "type": "chime_tts/save_settings",
        "values": values,
        "notify_profiles": [
            {"name": "arrival", "entity_id": "media_player.kitchen"},
        ],
    }


def _config_dir_files(config_dir: Path) -> list[str]:
    """Return the names of regular files directly inside config_dir."""
    return sorted(path.name for path in config_dir.iterdir() if path.is_file())


@pytest.mark.asyncio
async def test_issue_352_save_without_notify_profiles_key_keeps_profiles(
    tmp_path: Path,
) -> None:
    """A save request that omits notify_profiles must not erase existing profiles."""
    hass, config_entry, paths = make_hass(tmp_path)
    config_file = paths["config_dir"].joinpath("configuration.yaml")
    original = _write_profile_config(config_file)
    connection = FakeConnection()

    await save_settings_handler(
        hass,
        connection,
        {
            "id": 7,
            "type": "chime_tts/save_settings",
            "values": dict(config_entry.options),
        },
    )

    assert connection.errors == []
    payload = connection.results[-1][1]
    assert payload["message_type"] == "success"
    assert payload["restart_required"] is False
    assert [profile["name"] for profile in payload["notify_profiles"]] == ["doorbell"]
    assert config_file.read_text(encoding="utf-8") == original


@pytest.mark.asyncio
async def test_issue_352_failed_write_leaves_configuration_yaml_intact(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A failure while replacing configuration.yaml must not truncate it."""
    hass, config_entry, paths = make_hass(tmp_path)
    config_file = paths["config_dir"].joinpath("configuration.yaml")
    original = _write_profile_config(config_file)

    def fail_replace(src, dst):
        raise OSError(errno.EIO, "I/O error")

    monkeypatch.setattr(settings_module.os, "replace", fail_replace)
    connection = FakeConnection()

    await save_settings_handler(
        hass, connection, _new_profile_request(dict(config_entry.options))
    )

    assert connection.results[-1][1]["message_type"] == "error"
    assert config_file.read_text(encoding="utf-8") == original
    assert _config_dir_files(paths["config_dir"]) == ["configuration.yaml"]


@pytest.mark.asyncio
async def test_issue_352_write_preserves_mode_and_symlink(tmp_path: Path) -> None:
    """The atomic write keeps the file mode and writes through a symlink."""
    hass, config_entry, paths = make_hass(tmp_path)
    real_dir = tmp_path / "repo"
    real_dir.mkdir()
    real_file = real_dir / "configuration.yaml"
    _write_profile_config(real_file)
    real_file.chmod(0o640)
    link = paths["config_dir"].joinpath("configuration.yaml")
    link.symlink_to(real_file)
    connection = FakeConnection()

    await save_settings_handler(
        hass, connection, _new_profile_request(dict(config_entry.options))
    )

    assert connection.results[-1][1]["message_type"] == "success"
    assert link.is_symlink()
    assert stat.S_IMODE(real_file.stat().st_mode) == 0o640
    saved = yaml.safe_load(real_file.read_text(encoding="utf-8"))
    assert [entry["name"] for entry in saved["notify"]] == ["arrival"]


@pytest.mark.asyncio
async def test_issue_352_write_falls_back_when_file_is_a_mount_point(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A bind-mounted configuration.yaml cannot be replaced, so write it in place."""
    hass, config_entry, paths = make_hass(tmp_path)
    config_file = paths["config_dir"].joinpath("configuration.yaml")
    _write_profile_config(config_file)

    def busy_replace(src, dst):
        raise OSError(errno.EBUSY, "Device or resource busy")

    monkeypatch.setattr(settings_module.os, "replace", busy_replace)
    connection = FakeConnection()

    await save_settings_handler(
        hass, connection, _new_profile_request(dict(config_entry.options))
    )

    assert connection.results[-1][1]["message_type"] == "success"
    saved = yaml.safe_load(config_file.read_text(encoding="utf-8"))
    assert [entry["name"] for entry in saved["notify"]] == ["arrival"]
    assert _config_dir_files(paths["config_dir"]) == ["configuration.yaml"]


@pytest.mark.asyncio
async def test_issue_353_read_only_configuration_yaml_reports_clear_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A read-only configuration.yaml keeps the options save and explains the failure."""
    hass, config_entry, paths = make_hass(tmp_path)
    config_file = paths["config_dir"].joinpath("configuration.yaml")
    original = _write_profile_config(config_file)

    def read_only(*args, **kwargs):
        raise OSError(errno.EROFS, "Read-only file system")

    # A read-only mount fails both the temp file and the in-place fallback.
    monkeypatch.setattr(settings_module.tempfile, "mkstemp", read_only)
    monkeypatch.setattr(settings_module, "_write_text_in_place", read_only)
    values = dict(config_entry.options)
    values[INITIAL_DELAY_KEY] = 250
    connection = FakeConnection()

    await save_settings_handler(hass, connection, _new_profile_request(values))

    assert connection.errors == []
    payload = connection.results[-1][1]
    assert payload["message_type"] == "error"
    assert "read-only" in payload["message"]
    assert "notify" in payload["message"]
    assert [profile["name"] for profile in payload["notify_profiles"]] == ["doorbell"]
    assert config_entry.options[INITIAL_DELAY_KEY] == 250
    assert config_file.read_text(encoding="utf-8") == original


@pytest.mark.skipif(os.geteuid() == 0, reason="root ignores file permissions")
def test_issue_353_save_notify_profiles_raises_on_unwritable_directory(
    tmp_path: Path,
) -> None:
    """An unwritable config directory raises the dedicated write error."""
    hass, _config_entry, paths = make_hass(tmp_path)
    config_dir = paths["config_dir"]
    config_file = config_dir.joinpath("configuration.yaml")
    original = _write_profile_config(config_file)
    config_file.chmod(0o444)
    config_dir.chmod(0o555)
    try:
        with pytest.raises(settings_module.ConfigurationYamlWriteError):
            settings_module.save_notify_profiles(
                hass, [{"name": "arrival", "entity_id": "media_player.kitchen"}]
            )
    finally:
        config_dir.chmod(0o755)
        config_file.chmod(0o644)
    assert config_file.read_text(encoding="utf-8") == original


def test_issue_353_read_only_file_mode_is_not_replaced(tmp_path: Path) -> None:
    """A configuration.yaml marked read-only is left alone even in a writable dir."""
    hass, _config_entry, paths = make_hass(tmp_path)
    config_file = paths["config_dir"].joinpath("configuration.yaml")
    original = _write_profile_config(config_file)
    config_file.chmod(0o444)
    try:
        with pytest.raises(settings_module.ConfigurationYamlWriteError, match="read-only"):
            settings_module.save_notify_profiles(
                hass, [{"name": "arrival", "entity_id": "media_player.kitchen"}]
            )
    finally:
        config_file.chmod(0o644)
    assert config_file.read_text(encoding="utf-8") == original
    assert _config_dir_files(paths["config_dir"]) == ["configuration.yaml"]


def _save_arrival_profile(hass) -> None:
    """Save a single notify profile through the configuration.yaml writer."""
    settings_module.save_notify_profiles(
        hass, [{"name": "arrival", "entity_id": "media_player.kitchen"}]
    )


def _saved_profile_names(config_file: Path) -> list[str]:
    """Return the notify profile names stored in config_file."""
    saved = yaml.safe_load(config_file.read_text(encoding="utf-8"))
    return [entry["name"] for entry in saved["notify"]]


def test_issue_352_atomic_write_replaces_the_inode(tmp_path: Path) -> None:
    """The normal path swaps in a new file rather than truncating the old one."""
    hass, _config_entry, paths = make_hass(tmp_path)
    config_file = paths["config_dir"].joinpath("configuration.yaml")
    _write_profile_config(config_file)
    inode = config_file.stat().st_ino

    _save_arrival_profile(hass)

    assert config_file.stat().st_ino != inode
    assert _saved_profile_names(config_file) == ["arrival"]


def test_issue_352_unmatched_owner_writes_in_place(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """If the temp file cannot take the original owner, keep the original file."""
    hass, _config_entry, paths = make_hass(tmp_path)
    config_file = paths["config_dir"].joinpath("configuration.yaml")
    _write_profile_config(config_file)
    inode = config_file.stat().st_ino
    monkeypatch.setattr(settings_module, "_match_owner", lambda temp_path, current: False)

    _save_arrival_profile(hass)

    assert config_file.stat().st_ino == inode
    assert _saved_profile_names(config_file) == ["arrival"]
    assert _config_dir_files(paths["config_dir"]) == ["configuration.yaml"]


def test_issue_352_match_owner_reports_chown_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A different owner that chown cannot set is reported, not ignored."""
    temp_file = tmp_path / "temp"
    temp_file.write_text("x", encoding="utf-8")
    own = temp_file.stat()

    def refuse_chown(path, uid, gid):
        raise PermissionError(errno.EPERM, "Operation not permitted")

    monkeypatch.setattr(settings_module.os, "chown", refuse_chown)

    assert settings_module._match_owner(str(temp_file), own) is True
    other = SimpleNamespace(st_uid=own.st_uid + 1, st_gid=own.st_gid)
    assert settings_module._match_owner(str(temp_file), other) is False


def test_issue_352_temp_file_failure_writes_in_place(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A writable file in a directory that refuses temp files is still saved."""
    hass, _config_entry, paths = make_hass(tmp_path)
    config_file = paths["config_dir"].joinpath("configuration.yaml")
    _write_profile_config(config_file)
    inode = config_file.stat().st_ino

    def denied_mkstemp(*args, **kwargs):
        raise PermissionError(errno.EACCES, "Permission denied")

    monkeypatch.setattr(settings_module.tempfile, "mkstemp", denied_mkstemp)

    _save_arrival_profile(hass)

    assert config_file.stat().st_ino == inode
    assert _saved_profile_names(config_file) == ["arrival"]


@pytest.mark.skipif(os.geteuid() == 0, reason="root ignores file permissions")
def test_issue_352_writable_file_in_read_only_directory(tmp_path: Path) -> None:
    """A bind-mounted writable file in a read-only directory keeps working."""
    hass, _config_entry, paths = make_hass(tmp_path)
    config_dir = paths["config_dir"]
    config_file = config_dir.joinpath("configuration.yaml")
    _write_profile_config(config_file)
    config_dir.chmod(0o555)
    try:
        _save_arrival_profile(hass)
    finally:
        config_dir.chmod(0o755)
    assert _saved_profile_names(config_file) == ["arrival"]


def test_issue_352_new_configuration_yaml_respects_umask(tmp_path: Path) -> None:
    """A newly created configuration.yaml gets the umask-derived mode."""
    hass, _config_entry, paths = make_hass(tmp_path)
    config_file = paths["config_dir"].joinpath("configuration.yaml")
    previous = os.umask(0o027)
    try:
        _save_arrival_profile(hass)
    finally:
        os.umask(previous)

    assert stat.S_IMODE(config_file.stat().st_mode) == 0o640
    assert _saved_profile_names(config_file) == ["arrival"]


def test_issue_352_acl_file_writes_in_place(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A file with a POSIX ACL is rewritten in place so the ACL survives."""
    hass, _config_entry, paths = make_hass(tmp_path)
    config_file = paths["config_dir"].joinpath("configuration.yaml")
    _write_profile_config(config_file)
    inode = config_file.stat().st_ino
    monkeypatch.setattr(settings_module, "_has_posix_acl", lambda path, name="": True)

    _save_arrival_profile(hass)

    assert config_file.stat().st_ino == inode
    assert _saved_profile_names(config_file) == ["arrival"]


def test_issue_352_has_posix_acl_detection(monkeypatch: pytest.MonkeyPatch) -> None:
    """ACL detection reads the access ACL xattr and tolerates unsupported systems."""
    monkeypatch.setattr(
        settings_module.os,
        "listxattr",
        lambda path: ["user.note", "system.posix_acl_access"],
        raising=False,
    )
    assert settings_module._has_posix_acl("/config/configuration.yaml") is True

    monkeypatch.setattr(settings_module.os, "listxattr", lambda path: [], raising=False)
    assert settings_module._has_posix_acl("/config/configuration.yaml") is False

    def unsupported(path):
        raise OSError(errno.ENOTSUP, "Operation not supported")

    monkeypatch.setattr(settings_module.os, "listxattr", unsupported, raising=False)
    assert settings_module._has_posix_acl("/config/configuration.yaml") is False

    monkeypatch.delattr(settings_module.os, "listxattr", raising=False)
    assert settings_module._has_posix_acl("/config/configuration.yaml") is False


def _is_temp_file(path: str) -> bool:
    """Return whether path is the writer's temp file."""
    return os.path.basename(path).startswith(".configuration.yaml.")


def test_issue_352_temp_file_stays_private_until_owner_matches(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The original mode is applied only after ownership is settled."""
    hass, _config_entry, paths = make_hass(tmp_path)
    config_file = paths["config_dir"].joinpath("configuration.yaml")
    _write_profile_config(config_file)
    config_file.chmod(0o664)
    modes_at_owner_check: list[int] = []
    real_match_owner = settings_module._match_owner

    def recording_match_owner(temp_path, current):
        modes_at_owner_check.append(stat.S_IMODE(os.stat(temp_path).st_mode))
        return real_match_owner(temp_path, current)

    monkeypatch.setattr(settings_module, "_match_owner", recording_match_owner)

    _save_arrival_profile(hass)

    assert modes_at_owner_check == [0o600]
    assert stat.S_IMODE(config_file.stat().st_mode) == 0o664


def test_issue_352_failed_owner_match_never_widens_temp_mode(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A temp file that cannot take the owner is discarded before any chmod."""
    hass, _config_entry, paths = make_hass(tmp_path)
    config_file = paths["config_dir"].joinpath("configuration.yaml")
    _write_profile_config(config_file)
    chmod_calls: list[str] = []
    real_chmod = os.chmod

    def recording_chmod(path, mode, *args, **kwargs):
        chmod_calls.append(str(path))
        return real_chmod(path, mode, *args, **kwargs)

    monkeypatch.setattr(settings_module.os, "chmod", recording_chmod)
    monkeypatch.setattr(settings_module, "_match_owner", lambda temp_path, current: False)

    _save_arrival_profile(hass)

    assert not [path for path in chmod_calls if _is_temp_file(path)]
    assert _saved_profile_names(config_file) == ["arrival"]
    assert _config_dir_files(paths["config_dir"]) == ["configuration.yaml"]


@pytest.mark.parametrize("acl_on", ["temp", "directory"])
def test_issue_352_inherited_acl_writes_in_place(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, acl_on: str
) -> None:
    """A default ACL on the directory, or one inherited by the temp file, keeps the file in place."""
    hass, _config_entry, paths = make_hass(tmp_path)
    config_file = paths["config_dir"].joinpath("configuration.yaml")
    _write_profile_config(config_file)
    inode = config_file.stat().st_ino

    def fake_acl(path, name="system.posix_acl_access"):
        if acl_on == "temp":
            return _is_temp_file(path) and name == "system.posix_acl_access"
        return name == "system.posix_acl_default"

    monkeypatch.setattr(settings_module, "_has_posix_acl", fake_acl)

    _save_arrival_profile(hass)

    assert config_file.stat().st_ino == inode
    assert _saved_profile_names(config_file) == ["arrival"]
    assert _config_dir_files(paths["config_dir"]) == ["configuration.yaml"]


@pytest.mark.parametrize(("temp_label", "replaced"), [(b"other_t", False), (b"config_t", True)])
def test_issue_352_selinux_label_mismatch_writes_in_place(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, temp_label: bytes, replaced: bool
) -> None:
    """A temp file with a different SELinux label is not renamed over the original."""
    hass, _config_entry, paths = make_hass(tmp_path)
    config_file = paths["config_dir"].joinpath("configuration.yaml")
    _write_profile_config(config_file)
    inode = config_file.stat().st_ino
    monkeypatch.setattr(
        settings_module,
        "_selinux_label",
        lambda path: temp_label if _is_temp_file(path) else b"config_t",
    )

    _save_arrival_profile(hass)

    assert (config_file.stat().st_ino != inode) is replaced
    assert _saved_profile_names(config_file) == ["arrival"]


def test_issue_352_selinux_label_unsupported(monkeypatch: pytest.MonkeyPatch) -> None:
    """Missing or unsupported xattrs read as no label."""

    def unsupported(path, name):
        raise OSError(errno.ENOTSUP, "Operation not supported")

    monkeypatch.setattr(settings_module.os, "getxattr", unsupported, raising=False)
    assert settings_module._selinux_label("/config/configuration.yaml") is None
    monkeypatch.delattr(settings_module.os, "getxattr", raising=False)
    assert settings_module._selinux_label("/config/configuration.yaml") is None


def test_issue_352_unreadable_selinux_label_writes_in_place(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An unreadable SELinux label must not permit a metadata-dropping rename."""
    hass, _config_entry, paths = make_hass(tmp_path)
    config_file = paths["config_dir"].joinpath("configuration.yaml")
    _write_profile_config(config_file)
    inode = config_file.stat().st_ino

    def unreadable_label(path, name):
        raise OSError(errno.EIO, "I/O error")

    monkeypatch.setattr(settings_module.os, "getxattr", unreadable_label, raising=False)
    _save_arrival_profile(hass)

    assert config_file.stat().st_ino == inode
    assert _saved_profile_names(config_file) == ["arrival"]


@pytest.mark.parametrize("error_number", [errno.ENOSPC, errno.EDQUOT, errno.EIO])
def test_issue_352_temp_file_error_does_not_truncate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, error_number: int
) -> None:
    """A full disk or other mkstemp failure raises without touching the file."""
    hass, _config_entry, paths = make_hass(tmp_path)
    config_file = paths["config_dir"].joinpath("configuration.yaml")
    original = _write_profile_config(config_file)

    def failing_mkstemp(*args, **kwargs):
        raise OSError(error_number, os.strerror(error_number))

    monkeypatch.setattr(settings_module.tempfile, "mkstemp", failing_mkstemp)
    monkeypatch.setattr(
        settings_module,
        "_write_text_in_place",
        lambda path, content: pytest.fail("in-place write must not run"),
    )

    with pytest.raises(settings_module.ConfigurationYamlWriteError):
        _save_arrival_profile(hass)
    assert config_file.read_text(encoding="utf-8") == original


@pytest.mark.asyncio
async def test_issue_352_failed_save_reports_profiles_now_on_disk(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """After a failed write the panel gets what is on disk, not the pre-save list."""
    hass, config_entry, paths = make_hass(tmp_path)
    config_file = paths["config_dir"].joinpath("configuration.yaml")
    _write_profile_config(config_file)

    def partial_save(hass, profiles):
        config_file.write_text(
            "notify:\n  - platform: chime_tts\n    name: half_written\n"
            "    entity_id: media_player.office\n",
            encoding="utf-8",
        )
        raise settings_module.ConfigurationYamlWriteError("disk went away")

    monkeypatch.setattr(settings_module, "save_notify_profiles", partial_save)
    connection = FakeConnection()

    await save_settings_handler(
        hass, connection, _new_profile_request(dict(config_entry.options))
    )

    payload = connection.results[-1][1]
    assert payload["message_type"] == "error"
    assert [profile["name"] for profile in payload["notify_profiles"]] == ["half_written"]
    assert payload["restart_required"] is True


def test_issue_352_hard_linked_configuration_is_written_in_place(tmp_path: Path) -> None:
    """A hard-linked configuration.yaml keeps every link pointing at the new content."""
    config_file = tmp_path / "configuration.yaml"
    config_file.write_text("old: 1\n", encoding="utf-8")
    alias = tmp_path / "alias.yaml"
    os.link(config_file, alias)

    settings_module._write_text_atomically(str(config_file), "new: 2\n")

    assert alias.read_text(encoding="utf-8") == "new: 2\n"
    assert os.stat(alias).st_ino == os.stat(config_file).st_ino


def test_issue_352_replace_fsyncs_the_directory(tmp_path: Path, monkeypatch) -> None:
    """After the rename, the directory entry is flushed too."""
    config_file = tmp_path / "configuration.yaml"
    config_file.write_text("old: 1\n", encoding="utf-8")
    synced: list[str] = []
    monkeypatch.setattr(settings_module, "_fsync_directory", synced.append)

    settings_module._write_text_atomically(str(config_file), "new: 2\n")

    assert config_file.read_text(encoding="utf-8") == "new: 2\n"
    assert synced == [str(tmp_path)]


@pytest.mark.parametrize(("temp_label", "replaced"), [(b"config_t", False), (None, True)])
def test_issue_352_unlabeled_target_keeps_its_selinux_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, temp_label: bytes | None, replaced: bool
) -> None:
    """An unlabeled configuration.yaml is not swapped for a newly labeled temp file."""
    hass, _config_entry, paths = make_hass(tmp_path)
    config_file = paths["config_dir"].joinpath("configuration.yaml")
    _write_profile_config(config_file)
    inode = config_file.stat().st_ino
    monkeypatch.setattr(
        settings_module,
        "_selinux_label",
        lambda path: temp_label if _is_temp_file(path) else None,
    )

    _save_arrival_profile(hass)

    assert (config_file.stat().st_ino != inode) is replaced
    assert _saved_profile_names(config_file) == ["arrival"]


def test_issue_352_file_with_other_xattrs_writes_in_place(tmp_path: Path) -> None:
    """Extended attributes such as user.* tags survive a profile save."""
    config_file = tmp_path / "configuration.yaml"
    config_file.write_text("old: 1\n", encoding="utf-8")
    try:
        os.setxattr(config_file, "user.backup", b"keep")
    except (AttributeError, OSError):
        pytest.skip("user xattrs not supported here")
    inode = config_file.stat().st_ino

    settings_module._write_text_atomically(str(config_file), "new: 2\n")

    assert config_file.stat().st_ino == inode
    assert os.getxattr(config_file, "user.backup") == b"keep"
    assert config_file.read_text(encoding="utf-8") == "new: 2\n"


def test_issue_352_extra_xattr_detection_ignores_selinux(monkeypatch: pytest.MonkeyPatch) -> None:
    """Only attributes other than the separately compared SELinux label count."""
    monkeypatch.setattr(
        settings_module.os, "listxattr", lambda path: ["security.selinux"], raising=False
    )
    assert settings_module._has_extra_xattrs("/config/configuration.yaml") is False
    monkeypatch.setattr(
        settings_module.os,
        "listxattr",
        lambda path: ["security.selinux", "user.note"],
        raising=False,
    )
    assert settings_module._has_extra_xattrs("/config/configuration.yaml") is True


def test_issue_352_xattr_inspection_error_writes_in_place(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Unknown xattrs prevent a replace that could discard metadata."""
    hass, _config_entry, paths = make_hass(tmp_path)
    config_file = paths["config_dir"].joinpath("configuration.yaml")
    _write_profile_config(config_file)
    inode = config_file.stat().st_ino

    def unreadable_xattrs(path):
        raise OSError(errno.EIO, "I/O error")

    monkeypatch.setattr(settings_module.os, "listxattr", unreadable_xattrs, raising=False)
    _save_arrival_profile(hass)

    assert config_file.stat().st_ino == inode
    assert _saved_profile_names(config_file) == ["arrival"]


def test_issue_352_directory_fsync_error_is_reported(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A real directory fsync error is not reported as a durable save."""
    real_fsync = settings_module.os.fsync

    def fail_directory_fsync(file_descriptor):
        raise OSError(errno.EIO, "I/O error")

    monkeypatch.setattr(settings_module.os, "fsync", fail_directory_fsync)
    with pytest.raises(OSError, match="I/O error"):
        settings_module._fsync_directory(str(tmp_path))
    monkeypatch.setattr(settings_module.os, "fsync", real_fsync)
