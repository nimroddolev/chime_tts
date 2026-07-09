"""Tests for the Chime TTS sidebar settings backend."""

from __future__ import annotations

import inspect
import importlib
from pathlib import Path
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
settings_module = importlib.import_module("custom_components.chime_tts.settings")
save_settings_handler = inspect.unwrap(panel_module.websocket_save_settings)


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
        path=lambda *parts: str(config_dir.joinpath(*parts)),
        media_dirs={"media": str(media_dir)},
        allowlist_external_dirs=[str(www_dir), str(media_dir)],
    )
    hass.data = {
        "tts_manager": SimpleNamespace(providers={"google_translate": object()}),
    }

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
    ]

    voice_section = next(section for section in payload["sections"] if section["key"] == "voice")
    language_field = next(
        field for field in voice_section["fields"] if field["key"] == "default_language_key"
    )
    custom_chimes_field = next(
        field for field in payload["sections"][0]["fields"] if field["key"] == CUSTOM_CHIMES_PATH_KEY
    )

    assert language_field["provider_hint"]["tone"] == "info"
    assert "Google Translate" in language_field["provider_hint"]["message"]
    assert custom_chimes_field["icon_url"].endswith(f"/option_icons/{CUSTOM_CHIMES_PATH_KEY}.svg")
    assert custom_chimes_field["can_browse"] is True
    assert (
        custom_chimes_field["path_validation"]["message"]
        == "Folder path is valid for this setting."
    )


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
    assert notify_profile_fields["tts_platform"]["docs_url"].endswith(
        "/documentation/configuration/#default-tts-platform"
    )
    assert notify_profile_fields["crossfade"]["docs_url"].endswith(
        "/documentation/actions/say-action/parameters/#crossfade"
    )
    assert notify_profile_fields["announce"]["docs_url"].endswith(
        "/documentation/actions/say-action/parameters/#announce"
    )
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
