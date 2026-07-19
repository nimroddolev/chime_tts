"""Tests for the Chime TTS notify platform."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from custom_components.chime_tts.const import DOMAIN
from custom_components.chime_tts.notify import ChimeTTSNotificationService


@pytest.mark.asyncio
async def test_notify_service_forwards_crossfade_and_legacy_crossafade() -> None:
    """Notify payloads should support both crossfade spellings."""

    recorded_calls: list[dict] = []

    async def async_call(domain, service, service_data, blocking):
        recorded_calls.append(
            {
                "domain": domain,
                "service": service,
                "service_data": dict(service_data),
                "blocking": blocking,
            }
        )

    hass = SimpleNamespace(
        services=SimpleNamespace(async_call=async_call),
        data={DOMAIN: {}},
    )

    service = ChimeTTSNotificationService(
        hass,
        {"entity_id": "media_player.office", "crossafade": 111},
    )
    await service.async_send_message(
        "hello",
        data={"crossfade": 222},
    )

    legacy_service = ChimeTTSNotificationService(
        hass,
        {"entity_id": "media_player.office", "crossafade": 333},
    )
    await legacy_service.async_send_message("hello again")

    assert recorded_calls[0]["service_data"]["crossfade"] == 222
    assert recorded_calls[1]["service_data"]["crossfade"] == 333
