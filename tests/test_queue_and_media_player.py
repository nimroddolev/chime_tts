"""Unit tests for the queue manager and media-player state wrapper."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from homeassistant.components.media_player.const import ATTR_MEDIA_ANNOUNCE
from homeassistant.components.media_player.const import ATTR_MEDIA_VOLUME_LEVEL
from homeassistant.components.media_player.const import ATTR_GROUP_MEMBERS
from homeassistant.exceptions import HomeAssistantError

from custom_components.chime_tts.helpers.media_player import ChimeTTSMediaPlayer
from custom_components.chime_tts.queue_manager import ChimeTTSQueueManager


class FakeMediaHass:
    """Minimal Home Assistant facade used by the media-player wrapper."""

    def __init__(self, state: str = "on", attributes: dict | None = None) -> None:
        """Create a state container with a small service and registry surface."""
        self.entity = SimpleNamespace(state=state, attributes=attributes or {})
        self.states = SimpleNamespace(get=lambda entity_id: self.entity)
        self.data = {
            "entity_registry": SimpleNamespace(
                entities={
                    "player": SimpleNamespace(
                        entity_id="media_player.kitchen", platform="sonos"
                    )
                }
            )
        }
        self.services = SimpleNamespace(async_call=AsyncMock())
        self.created_tasks: list[asyncio.Task] = []

    def async_create_task(self, coroutine):
        task = asyncio.create_task(coroutine)
        self.created_tasks.append(task)
        return task


@pytest.mark.asyncio
async def test_media_player_turns_on_off_entity_before_playback() -> None:
    """Turning an off player on is awaited rather than run in the background."""
    hass = FakeMediaHass(
        "off",
        {
            "media_duration": 5,
            "media_position": 1,
            ATTR_MEDIA_VOLUME_LEVEL: 0.2,
            "supported_features": 2 | 1048576 | 524288,
        },
    )

    player = ChimeTTSMediaPlayer(
        hass, "media_player.kitchen", {"media_player.kitchen": 0.5}
    )

    assert player.platform == "sonos"
    assert player.initially_playing is False
    assert player.initial_volume_level == 0.2
    assert player.target_volume_level == 0.5
    assert player.announce_supported is True
    assert player.join_supported is True
    assert player.get_should_change_volume() is True
    assert hass.services.async_call.await_count == 0
    assert await player.async_turn_on() is True
    hass.services.async_call.assert_awaited_once()


@pytest.mark.parametrize(
    ("target", "expected"),
    [
        ([{"media_player.kitchen": 0.4}], 0.4),
        (0.3, 0.3),
        (None, -1.0),
        ({}, -1.0),
        (0, -1.0),
    ],
)
def test_media_player_target_volume_forms(target, expected) -> None:
    """Target volume accepts documented forms and normalizes invalid values."""
    hass = FakeMediaHass("playing", {"media_duration": 1, "media_position": 1})

    player = ChimeTTSMediaPlayer(hass, "media_player.kitchen", target)

    assert player.target_volume_level == expected
    assert player.initially_playing is True
    assert player.get_should_change_volume() is (expected >= 0 and expected != -1.0)


def test_media_player_feature_detection_handles_missing_and_unknown_features() -> None:
    """Feature checks are defensive and only recognize supported capability bits."""
    hass = FakeMediaHass(attributes={"supported_features": 0})
    player = ChimeTTSMediaPlayer(hass, "media_player.kitchen", -1)

    assert player.get_supported_feature(ATTR_MEDIA_VOLUME_LEVEL) is False
    assert player.get_supported_feature(ATTR_MEDIA_ANNOUNCE) is False
    assert player.get_supported_feature(ATTR_GROUP_MEMBERS) is False
    assert player.get_supported_feature("unknown") is False
    hass.entity = None
    assert player.get_supported_feature(ATTR_MEDIA_VOLUME_LEVEL) is False


@pytest.mark.asyncio
async def test_media_player_handles_turn_on_errors_missing_platform_and_dict_setter() -> None:
    """Non-critical service and registry failures leave a usable wrapper."""
    hass = FakeMediaHass("off")
    hass.data["entity_registry"].entities = {}
    hass.services.async_call = AsyncMock(side_effect=RuntimeError("turn on failed"))
    player = ChimeTTSMediaPlayer(hass, "media_player.kitchen", -1)

    assert player.platform is None
    assert await player.async_turn_on() is False
    player.target_volume_level = {"media_player.kitchen": 0.6}
    assert player.target_volume_level == 0.6


@pytest.mark.asyncio
async def test_queue_processes_success_timeout_error_and_cancelled_calls() -> None:
    """Queue processing resolves futures for every worker outcome."""
    manager = ChimeTTSQueueManager(p_timeout_s=1)

    async def successful(value):
        return value

    success = manager.add_to_queue(successful, 1, "ok")
    service_call = await manager.queue.get()
    await manager._process_service_call(service_call)
    assert await success == "ok"

    async def exploding():
        raise ValueError("bad")

    failure = manager.add_to_queue(exploding, 1)
    await manager._process_service_call(await manager.queue.get())
    with pytest.raises(ValueError, match="bad"):
        await failure

    async def slow():
        await asyncio.sleep(1)

    timeout = manager.add_to_queue(slow, 0)
    await manager._process_service_call(await manager.queue.get())
    with pytest.raises(HomeAssistantError, match="timed out"):
        await timeout

    async def cancelled():
        raise asyncio.CancelledError

    cancelled_future = manager.add_to_queue(cancelled, 1)
    await manager._process_service_call(await manager.queue.get())
    with pytest.raises(asyncio.CancelledError):
        await cancelled_future


@pytest.mark.asyncio
async def test_queue_processor_reset_and_stop(monkeypatch: pytest.MonkeyPatch) -> None:
    """Processor lifecycle can be reset, ignores sentinels, and stops cleanly."""
    manager = ChimeTTSQueueManager(p_timeout_s=999999)
    assert manager.timeout_s < 999999
    manager.queue.put_nowait(None)

    task = asyncio.create_task(manager.async_process_queue())
    await asyncio.sleep(0)
    manager._shutdown_event.set()
    await asyncio.wait_for(task, timeout=2)

    future = asyncio.get_running_loop().create_future()
    manager.queue.put_nowait(
        {"function": AsyncMock(), "args": (), "kwargs": {}, "future": future}
    )
    manager._clear_queue()
    assert future.cancelled()

    monkeypatch.setattr(manager, "start_queue_processor", lambda: None)
    manager.reset_queue()
    manager.start_queue_processor()
    await manager.stop_queue_processor()
    assert manager.running_tasks == []


@pytest.mark.asyncio
async def test_queue_handles_set_result_and_put_failures(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Queue errors while completing or enqueuing a call are contained."""
    manager = ChimeTTSQueueManager()

    class BrokenFuture:
        def set_result(self, value):
            raise RuntimeError("already done")

    async def successful():
        return "ok"

    manager.queue.put_nowait(None)
    await manager.queue.get()
    await manager._process_service_call(
        {"function": successful, "args": (), "kwargs": {}, "future": BrokenFuture()}
    )

    class FullQueue:
        def qsize(self):
            return 1

        def put_nowait(self, value):
            raise asyncio.QueueFull

    manager.queue = FullQueue()
    future = manager.add_to_queue(successful, 1)
    with pytest.raises(RuntimeError, match="Queue is full"):
        await future


@pytest.mark.asyncio
async def test_queue_processor_starts_processes_and_cancels_running_task(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The continuous worker invokes processing for pending calls and is cancellable."""
    manager = ChimeTTSQueueManager()
    processed = AsyncMock(side_effect=lambda: manager._shutdown_event.set())
    monkeypatch.setattr(manager, "async_process_queue", processed)
    manager.queue.put_nowait(None)
    manager.start_queue_processor()
    await asyncio.sleep(0.25)
    await manager.stop_queue_processor()
    processed.assert_awaited_once()
