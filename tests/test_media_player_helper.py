"""Deterministic unit tests for media-player helper selection and service paths."""

from __future__ import annotations

import importlib
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from homeassistant.components.media_player.const import ATTR_GROUP_MEMBERS
from homeassistant.components.media_player.const import ATTR_MEDIA_ANNOUNCE
from homeassistant.components.media_player.const import ATTR_MEDIA_VOLUME_LEVEL

from custom_components.chime_tts.const import ALEXA_MEDIA_PLAYER_PLATFORM
from custom_components.chime_tts.const import SONOS_PLATFORM
from custom_components.chime_tts.helpers.media_player_helper import MediaPlayerHelper


class Player:
    """Small, mutable media-player double."""

    def __init__(
        self,
        entity_id: str,
        *,
        platform: str = "cast",
        initial: float = 0.2,
        target: float = 0.5,
        playing: bool = False,
        announce: bool = False,
        join: bool = False,
    ) -> None:
        """Create a media-player value object for helper tests."""
        self.entity_id = entity_id
        self.platform = platform
        self.initial_volume_level = initial
        self.target_volume_level = target
        self.initially_playing = playing
        self.announce_supported = announce
        self.join_supported = join
        self.state = "playing"
        self.volume = initial

    def get_state(self) -> str:
        """Return the simulated player state."""
        return self.state

    def get_current_volume_level(self) -> float:
        """Return the simulated current volume."""
        return self.volume


class Hass:
    """Small HA facade for helper service methods."""

    def __init__(self) -> None:
        """Set up services, state storage, and entity registry."""
        self.services = SimpleNamespace(async_call=AsyncMock())
        self.states = SimpleNamespace(
            get=lambda entity_id: SimpleNamespace(state="playing")
        )
        self.config = SimpleNamespace(
            media_dirs={"media": "/media", "nested": "/media/nested"}
        )
        self.data = {
            "entity_registry": SimpleNamespace(
                entities={
                    "kitchen": SimpleNamespace(
                        entity_id="media_player.kitchen",
                        device_id="device-1",
                        platform="cast",
                    ),
                    "light": SimpleNamespace(
                        entity_id="light.kitchen",
                        device_id="device-1",
                        platform="light",
                    ),
                }
            )
        }

    async def async_add_executor_job(self, func, *args):
        """Avoid real sleeps during retry and transition tests."""
        return func(*args) if getattr(func, "__name__", "") != "sleep" else None


@pytest.mark.asyncio
async def test_initialize_parse_and_lookup_media_players(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Initialization skips invalid states and lookup helpers classify players."""
    helper = MediaPlayerHelper()
    hass = Hass()
    first = Player("media_player.one", playing=True, announce=False)
    second = Player("media_player.two", platform=SONOS_PLATFORM, target=0.2)
    monkeypatch.setattr(
        helper,
        "async_get_media_player_object",
        AsyncMock(side_effect=[first, None, second]),
    )

    assert (
        await helper.async_initialize_media_players(
            hass, [], 0.5, False, False, False, False
        )
        == []
    )
    assert await helper.async_initialize_media_players(
        hass, ["one", "missing", "two"], 0.5, False, False, True, True
    ) == [first, second]
    assert set(
        helper.parse_entity_ids(
            {"entity_id": "media_player.a,media_player.b", "device_id": "device-1"},
            hass,
        )
    ) == {"media_player.a", "media_player.b", "media_player.kitchen"}
    assert helper.get_fade_in_out_media_players() == [first]
    assert helper.get_set_volume_media_players() == []
    assert helper.get_media_player_target_volume("media_player.one") == 0.5
    assert helper.get_media_player_target_volume("missing") is None
    assert helper.get_media_player_platform(hass, "media_player.kitchen") == "cast"
    assert helper.get_media_player_platform(hass, "missing") is None
    assert helper.get_media_players_from_entity_ids(
        ["media_player.one", "missing"]
    ) == [first]
    assert helper.get_uniform_target_volume_level(["media_player.one"]) == 0.5
    assert (
        helper.get_uniform_target_volume_level(["media_player.one", "media_player.two"])
        == -1
    )
    assert helper.get_is_standard_media_player("media_player.one") is True
    first.platform = ALEXA_MEDIA_PLAYER_PLATFORM
    assert helper.get_is_media_player_alexa("media_player.one") is True
    assert helper.get_is_media_player_sonos("media_player.two") is True
    assert helper.get_is_media_player_spotify("media_player.two") is False
    assert helper.get_alexa_media_players_count() == 1
    assert helper.get_media_players_of_platform(
        ["media_player.one", "media_player.two"], SONOS_PLATFORM
    ) == ["media_player.two"]


def test_media_helper_feature_and_media_source_lookup() -> None:
    """Feature bits and media source ids use the most-specific media directory."""
    helper = MediaPlayerHelper()
    hass = Hass()
    entity = SimpleNamespace(attributes={"supported_features": 2 | 1048576 | 524288})
    assert helper.get_supported_feature(entity, ATTR_MEDIA_VOLUME_LEVEL) is True
    assert helper.get_supported_feature(entity, ATTR_MEDIA_ANNOUNCE) is True
    assert helper.get_supported_feature(entity, ATTR_GROUP_MEMBERS) is True
    assert helper.get_supported_feature(None, "unknown") is False
    assert (
        helper.get_media_content_id(hass, "/media/nested/file.mp3")
        == "media-source://media_source/nested/file.mp3"
    )
    assert helper.get_media_content_id(hass, "/media-other/file.mp3") is None
    assert helper.get_media_content_id(None, "/media/file.mp3") is None
    assert helper.get_media_content_id(hass, "") is None


@pytest.mark.asyncio
async def test_media_helper_volume_join_and_wait_paths() -> None:
    """Volume, waiting, and grouping calls use their expected HA services."""
    helper = MediaPlayerHelper()
    hass = Hass()
    first = Player("media_player.one", join=True)
    second = Player("media_player.two", join=True)
    helper.media_players = [first, second]
    helper.join_players = True
    helper.unjoin_players = True

    assert (
        await helper._async_wait_until_media_players(None, [first], lambda player: True)
        is False
    )
    assert (
        await helper.async_wait_until_media_players_state_is(hass, [first], "playing")
        is True
    )
    await helper.async_set_volume_for_media_players(hass, [first], 0.6, 0)
    await helper.async_set_volume_action(hass, first.entity_id, 0.5, is_retry=True)
    assert await helper.async_join_media_players(hass) == "media_player.one"
    await helper.async_unjoin_media_players(hass)
    calls = hass.services.async_call.await_args_list
    assert any(call.kwargs["service"] == "volume_set" for call in calls)
    assert any(call.kwargs["service"] == "join" for call in calls)
    assert sum(call.kwargs["service"] == "unjoin" for call in calls) == 2


@pytest.mark.asyncio
async def test_media_helper_fade_resume_and_sonos_paths(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Playback transitions pause, resume, and snapshot supported players."""
    helper = MediaPlayerHelper()
    hass = Hass()
    first = Player("media_player.one", platform="cast", playing=True)
    sonos = Player("media_player.sonos", platform=SONOS_PLATFORM, playing=True)
    spotify = Player("media_player.spotify", platform="spotify", playing=True)
    helper.media_players = [first, sonos, spotify]
    helper.fade_audio = True
    helper.announce = False
    helper.sonos_restored = False
    set_volume = AsyncMock()
    monkeypatch.setattr(helper, "async_set_volume_for_media_players", set_volume)
    monkeypatch.setattr(
        helper, "async_wait_until_media_players_state_is", AsyncMock(return_value=False)
    )
    monkeypatch.setattr(helper, "async_sonos_restore", AsyncMock())

    await helper.async_fade_out_and_pause(hass, 100)
    assert set_volume.await_count == 2
    await helper.async_resume_playback(hass, 100)
    assert set_volume.await_count == 3
    assert any(
        call.kwargs["service"] == "media_pause"
        for call in hass.services.async_call.await_args_list
    )
    assert any(
        call.kwargs["service"] == "media_play"
        for call in hass.services.async_call.await_args_list
    )

    module = importlib.import_module(
        "custom_components.chime_tts.helpers.media_player_helper"
    )
    monkeypatch.setattr(module, "SONOS_SNAPSHOT_ENABLED", True)
    await MediaPlayerHelper.async_sonos_snapshot(helper, hass)
    await MediaPlayerHelper.async_sonos_restore(helper, hass)
    assert helper.sonos_restored is True
    assert {
        call.kwargs["service"] for call in hass.services.async_call.await_args_list
    } >= {"snapshot", "restore"}


@pytest.mark.asyncio
async def test_media_helper_wait_volume_and_group_edge_cases(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Transitions handle timeouts, fades, no-op volume updates, and invalid groups."""
    helper = MediaPlayerHelper()
    hass = Hass()
    player = Player("media_player.one", initial=0.2, target=-1)
    helper.media_players = [player]

    assert (
        await helper.async_wait_until_media_players_state_not(hass, [player], "paused")
        is True
    )
    assert (
        await helper.async_wait_until_media_players_volume_level_is(hass, [player], 0.2)
        is True
    )
    assert (
        await helper._async_wait_until_media_players(
            hass, [player], lambda item: False, timeout=0
        )
        is False
    )
    action = AsyncMock()
    monkeypatch.setattr(helper, "async_set_volume_action", action)
    monkeypatch.setattr(helper, "async_wait_until_target_volume_reached", AsyncMock())
    await helper.async_set_volume_for_media_players(hass, [], 0.5, 0)
    await helper.async_set_volume_for_media_players(
        hass, [player], "initial_volume_level", 0
    )
    player.target_volume_level = 0.6
    await helper.async_set_volume_for_media_players(
        hass, [player], "target_volume_level", 200
    )
    assert action.await_count > 1

    helper.join_players = False
    assert await helper.async_join_media_players(hass) is None
    helper.join_players = True
    player.join_supported = False
    assert await helper.async_join_media_players(hass) is None
    player.join_supported = True
    assert await helper.async_join_media_players(hass) is None
