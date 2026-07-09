"""Minimal recorder media_player platform for live E2E tests."""

from __future__ import annotations

import asyncio

from homeassistant.components.media_player import MediaPlayerEntity, MediaPlayerEntityFeature
from homeassistant.const import STATE_IDLE, STATE_PLAYING
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Register the E2E test player."""
    del hass, config, discovery_info
    async_add_entities([E2ETestPlayer()])


class E2ETestPlayer(MediaPlayerEntity):
    """Simple media player that records inbound playback calls."""

    _attr_name = "E2E Test Player"
    _attr_unique_id = "chime_tts_e2e_test_player"
    _attr_supported_features = (
        MediaPlayerEntityFeature.PLAY_MEDIA | MediaPlayerEntityFeature.VOLUME_SET
    )
    _attr_should_poll = False

    def __init__(self) -> None:
        """Set initial entity state."""
        self._attr_state = STATE_IDLE
        self._attr_volume_level = 0.5
        self._last_announce: bool | None = None
        self._last_extra: dict | None = None
        self._last_media_content_id: str | None = None
        self._last_media_content_type: str | None = None
        self._play_count = 0
        self._volume_history = [self._attr_volume_level]

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        """Expose the last playback request for assertions."""
        return {
            "last_announce": self._last_announce,
            "last_extra": self._last_extra,
            "last_media_content_id": self._last_media_content_id,
            "last_media_content_type": self._last_media_content_type,
            "play_count": self._play_count,
            "volume_history": self._volume_history,
        }

    async def async_play_media(
        self,
        media_type: str,
        media_id: str,
        *,
        announce: bool | None = None,
        **kwargs,
    ) -> None:
        """Record the playback payload."""
        self._play_count += 1
        self._attr_state = STATE_PLAYING
        self._last_announce = announce
        self._last_extra = dict(kwargs.get("extra", {})) if kwargs.get("extra") else None
        self._last_media_content_id = media_id
        self._last_media_content_type = media_type
        self.async_write_ha_state()
        self.hass.async_create_task(self._finish_playback())

    async def _finish_playback(self) -> None:
        """Return the player to idle shortly after playback starts."""
        await asyncio.sleep(0.1)
        self._attr_state = STATE_IDLE
        self.async_write_ha_state()

    async def async_set_volume_level(self, volume: float) -> None:
        """Record volume changes."""
        self._attr_volume_level = volume
        self._volume_history.append(volume)
        self.async_write_ha_state()
