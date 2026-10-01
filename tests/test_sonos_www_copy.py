"""Sonos plays an unauthenticated www copy instead of a signed media-source URL.

Sonos fetches its last played URL again later. The signed media-source URL
expires after a day, so that fetch fails authentication and Home Assistant
bans the speaker's IP (home-assistant/core#88714).
"""

from __future__ import annotations

import importlib
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import ANY, AsyncMock

import pytest
from pydub import AudioSegment

from custom_components.chime_tts.const import (
    CROSSFADE_KEY,
    LOCAL_PATH_KEY,
    OFFSET_KEY,
    PUBLIC_PATH_KEY,
    SONOS_PLATFORM,
    SONOS_WWW_PATH_KEY,
    TEMP_PATH_KEY,
    WWW_PATH_KEY,
)
from homeassistant.components.media_player.const import ATTR_MEDIA_ANNOUNCE
from homeassistant.components.media_player.const import ATTR_MEDIA_CONTENT_ID
from homeassistant.components.media_player.const import ATTR_MEDIA_CONTENT_TYPE
from homeassistant.components.media_player.const import MediaType
from homeassistant.const import CONF_ENTITY_ID

integration_module = importlib.import_module("custom_components.chime_tts.__init__")

MEDIA_SOURCE_ID = "media-source://media_source/local/chime_tts/generated.mp3"


class Hass:
    """Home Assistant stand-in rooted at a temporary config folder."""

    def __init__(self, root: Path) -> None:
        """Expose config paths under root and run executor jobs inline."""
        self.config = SimpleNamespace(
            path=lambda *parts: str(root.joinpath(*parts)),
            media_dirs={},
        )

    async def async_add_executor_job(self, func, *args):
        """Run executor jobs inline."""
        return func(*args)


@pytest.fixture
def config_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point the integration's www and temp folders into tmp_path."""
    www = tmp_path / "www" / "chime_tts"
    temp = tmp_path / "temp"
    temp.mkdir()
    monkeypatch.setattr(
        integration_module,
        "_data",
        {
            OFFSET_KEY: 0,
            CROSSFADE_KEY: 0,
            TEMP_PATH_KEY: str(temp),
            WWW_PATH_KEY: str(www),
        },
    )
    return tmp_path


def _sonos_only(monkeypatch: pytest.MonkeyPatch) -> None:
    """Treat every targeted entity as a Sonos player."""
    helper = integration_module.media_player_helper
    helper.joined_entity_id = None
    monkeypatch.setattr(helper, "get_is_standard_media_player", lambda entity_id: False)
    monkeypatch.setattr(
        helper,
        "get_media_players_of_platform",
        lambda entity_ids, platform: list(entity_ids or [])
        if platform == SONOS_PLATFORM
        else [],
    )


@pytest.mark.asyncio
async def test_www_copy_is_made_from_the_processed_local_file(
    config_root: Path,
) -> None:
    """The copy comes from LOCAL_PATH_KEY, not the unprocessed public copy."""
    hass = Hass(config_root)
    local = config_root / "temp" / "processed.mp3"
    local.write_bytes(b"processed")
    public = config_root / "www" / "unprocessed.mp3"
    public.parent.mkdir(parents=True)
    public.write_bytes(b"unprocessed")
    audio_dict = {LOCAL_PATH_KEY: str(local), PUBLIC_PATH_KEY: str(public)}

    assert (
        await integration_module.async_ensure_sonos_www_copy(hass, audio_dict) is True
    )

    www_copy = Path(audio_dict[SONOS_WWW_PATH_KEY])
    assert www_copy == config_root / "www" / "chime_tts" / "processed.mp3"
    assert www_copy.read_bytes() == b"processed"
    assert integration_module.get_sonos_media_content_id(hass, audio_dict) == (
        "/local/chime_tts/processed.mp3"
    )

    # An existing copy is reused rather than copied again.
    assert (
        await integration_module.async_ensure_sonos_www_copy(hass, audio_dict) is False
    )
    assert audio_dict[SONOS_WWW_PATH_KEY] == str(www_copy)


@pytest.mark.asyncio
async def test_no_www_copy_without_a_local_file(config_root: Path) -> None:
    """Without a processed local file there is nothing to copy."""
    hass = Hass(config_root)
    audio_dict = {LOCAL_PATH_KEY: None, PUBLIC_PATH_KEY: None}

    assert (
        await integration_module.async_ensure_sonos_www_copy(hass, audio_dict) is False
    )
    assert audio_dict[SONOS_WWW_PATH_KEY] is None
    assert integration_module.get_sonos_media_content_id(hass, audio_dict) is None


def test_no_local_url_for_a_copy_outside_www(config_root: Path) -> None:
    """A www folder configured outside /config/www cannot be served as /local/."""
    hass = Hass(config_root)
    audio_dict = {SONOS_WWW_PATH_KEY: str(config_root / "elsewhere" / "a.mp3")}

    assert integration_module.get_sonos_media_content_id(hass, audio_dict) is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("www_path", "expected_content_id"),
    [
        ("www/chime_tts/generated.mp3", "/local/chime_tts/generated.mp3"),
        (None, MEDIA_SOURCE_ID),
    ],
)
async def test_sonos_play_media_uses_the_www_copy(
    config_root: Path,
    monkeypatch: pytest.MonkeyPatch,
    www_path: str | None,
    expected_content_id: str,
) -> None:
    """Sonos gets the /local/ URL, and falls back to the media-source id without one."""
    _sonos_only(monkeypatch)
    monkeypatch.setattr(
        integration_module.media_player_helper,
        "get_uniform_target_volume_level",
        lambda entity_ids: 0.3,
    )
    audio_dict = {
        PUBLIC_PATH_KEY: None,
        SONOS_WWW_PATH_KEY: str(config_root / www_path) if www_path else None,
    }

    calls = await integration_module.async_prepare_media_service_calls(
        hass=Hass(config_root),
        entity_ids=["media_player.kitchen"],
        service_data={
            CONF_ENTITY_ID: [],
            ATTR_MEDIA_ANNOUNCE: False,
            ATTR_MEDIA_CONTENT_TYPE: MediaType.MUSIC,
            ATTR_MEDIA_CONTENT_ID: MEDIA_SOURCE_ID,
        },
        audio_dict=audio_dict,
    )

    play_calls = [call for call in calls if call["service"] == "play_media"]
    assert len(play_calls) == 1
    assert play_calls[0]["service_data"][ATTR_MEDIA_CONTENT_ID] == expected_content_id


def _stub_generation(monkeypatch: pytest.MonkeyPatch, local: Path) -> AsyncMock:
    """Stub the audio pipeline so async_get_playback_audio_path writes `local`."""
    segment = AudioSegment.silent(duration=100)
    fs = integration_module.filesystem_helper
    monkeypatch.setattr(
        fs, "async_get_chime_path_with_offset", AsyncMock(return_value=(None, None))
    )
    monkeypatch.setattr(
        fs, "async_save_audio_to_folder", AsyncMock(return_value=str(local))
    )
    monkeypatch.setattr(fs, "async_load_audio", AsyncMock(return_value=segment))
    monkeypatch.setattr(
        integration_module.media_player_helper,
        "get_alexa_media_players_count",
        lambda: 0,
    )
    monkeypatch.setattr(
        integration_module.media_player_helper,
        "get_media_content_id",
        lambda *args, **kwargs: MEDIA_SOURCE_ID,
    )
    monkeypatch.setattr(
        integration_module, "async_get_audio_from_path", AsyncMock(return_value=segment)
    )
    monkeypatch.setattr(
        integration_module, "async_process_segments", AsyncMock(return_value=segment)
    )
    monkeypatch.setattr(
        integration_module, "validate_audio_dict", lambda *args, **kwargs: True
    )
    monkeypatch.setattr(
        integration_module, "async_add_audio_file_to_cache", AsyncMock()
    )
    monkeypatch.setattr(integration_module.tts_audio_helper, "_data", {})
    cache_write = AsyncMock()
    monkeypatch.setattr(integration_module, "async_cache_sonos_www_path", cache_write)
    return cache_write


def _params(hass: Hass, cache: bool) -> dict:
    return {
        "hass": hass,
        "message": "Hello",
        "chime_path": None,
        "end_chime_path": None,
        "cache": cache,
        "entity_ids": ["media_player.kitchen"],
    }


@pytest.mark.asyncio
async def test_new_audio_for_sonos_gets_a_cached_www_copy(
    config_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Generated audio for Sonos is copied to www and the copy is cached."""
    _sonos_only(monkeypatch)
    local = config_root / "temp" / "generated.mp3"
    local.write_bytes(b"audio")
    cache_write = _stub_generation(monkeypatch, local)
    monkeypatch.setattr(
        integration_module, "async_verify_cached_audio", AsyncMock(return_value=None)
    )

    audio_dict = await integration_module.async_get_playback_audio_path(
        _params(Hass(config_root), cache=True), {}
    )

    www_copy = config_root / "www" / "chime_tts" / "generated.mp3"
    assert audio_dict[SONOS_WWW_PATH_KEY] == str(www_copy)
    assert www_copy.exists()
    cache_write.assert_awaited_once_with(ANY, ANY, str(www_copy))


@pytest.mark.asyncio
async def test_cached_audio_for_sonos_gets_a_www_copy(
    config_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A cache hit for Sonos gets a www copy, recorded on the cache entry once."""
    _sonos_only(monkeypatch)
    local = config_root / "temp" / "cached.mp3"
    local.write_bytes(b"audio")
    cache_write = _stub_generation(monkeypatch, local)
    cached = {LOCAL_PATH_KEY: str(local), PUBLIC_PATH_KEY: None, "audio_duration": 0.1}
    monkeypatch.setattr(
        integration_module, "async_verify_cached_audio", AsyncMock(return_value=cached)
    )
    hass = Hass(config_root)

    first = await integration_module.async_get_playback_audio_path(
        _params(hass, cache=True), {}
    )
    second = await integration_module.async_get_playback_audio_path(
        _params(hass, cache=True), {}
    )

    www_copy = config_root / "www" / "chime_tts" / "cached.mp3"
    assert first[SONOS_WWW_PATH_KEY] == second[SONOS_WWW_PATH_KEY] == str(www_copy)
    cache_write.assert_awaited_once()


@pytest.mark.asyncio
async def test_clear_www_cache_removes_the_sonos_copy(
    config_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """clear_cache with clear_www_tts_cache also deletes the Sonos www copy."""
    deleted: list[str] = []
    monkeypatch.setattr(
        integration_module,
        "async_retrieve_data",
        AsyncMock(
            return_value={
                LOCAL_PATH_KEY: None,
                PUBLIC_PATH_KEY: None,
                SONOS_WWW_PATH_KEY: "/config/www/chime_tts/cached.mp3",
            }
        ),
    )
    monkeypatch.setattr(integration_module, "async_delete_data", AsyncMock())
    monkeypatch.setattr(
        integration_module.filesystem_helper,
        "delete_file",
        lambda hass, path: deleted.append(path),
    )

    await integration_module.async_remove_cached_audio_data(
        Hass(config_root), "cache-key", clear_www_tts_cache=True
    )

    assert deleted == ["/config/www/chime_tts/cached.mp3"]
