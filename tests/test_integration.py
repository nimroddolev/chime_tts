"""Integration import and setup smoke tests.

The import test alone catches the class of breakage behind several reported
issues: when a new HA core release removes or moves an API chime_tts imports at
module load, the integration fails to load entirely (see issues #286, #288).
Running this across the HA version matrix surfaces that before users hit it.
"""

import importlib
from unittest.mock import AsyncMock

import pytest


def test_integration_package_imports():
    """The integration and its helpers import under the installed HA core."""
    pkg = importlib.import_module("custom_components.chime_tts")
    assert pkg is not None

    for module in (
        "custom_components.chime_tts.const",
        "custom_components.chime_tts.helpers.helpers",
        "custom_components.chime_tts.helpers.media_player_helper",
        "custom_components.chime_tts.helpers.filesystem",
        "custom_components.chime_tts.helpers.tts_audio_helper",
        "custom_components.chime_tts.queue_manager",
    ):
        assert importlib.import_module(module) is not None


def test_domain_and_service_names():
    const = importlib.import_module("custom_components.chime_tts.const")
    assert const.DOMAIN == "chime_tts"
    assert const.SERVICE_SAY == "say"
    assert const.SERVICE_SAY_URL == "say_url"
    assert const.SERVICE_CLEAR_CACHE == "clear_cache"


def test_version_matches_manifest():
    const = importlib.import_module("custom_components.chime_tts.const")
    # const.VERSION is read from manifest.json at import time.
    assert const.VERSION, "VERSION should be populated from manifest.json"


@pytest.mark.asyncio
async def test_async_setup_registers_services(hass):
    """Setting up the integration registers its core services on the bus."""
    from custom_components.chime_tts import async_setup
    from custom_components.chime_tts.const import (
        DOMAIN,
        SERVICE_SAY,
        SERVICE_SAY_URL,
        SERVICE_CLEAR_CACHE,
    )

    assert await async_setup(hass, {}) is True
    await hass.async_block_till_done()

    for service in (SERVICE_SAY, SERVICE_SAY_URL, SERVICE_CLEAR_CACHE):
        assert hass.services.has_service(DOMAIN, service), f"{service} not registered"


@pytest.mark.asyncio
async def test_script_continues_after_chime_queue_timeout(hass, monkeypatch):
    """A timed-out Chime action must honor Home Assistant's continue_on_error."""
    from custom_components.chime_tts import async_setup
    from custom_components.chime_tts import queue
    from custom_components.chime_tts.const import DOMAIN, SERVICE_SAY
    from homeassistant.exceptions import HomeAssistantError
    from homeassistant.helpers.script import Script

    monkeypatch.setattr(
        queue,
        "add_to_queue",
        AsyncMock(side_effect=HomeAssistantError("Service call timed out")),
    )
    assert await async_setup(hass, {}) is True

    continued = []
    hass.bus.async_listen("chime_tts_test_continued", lambda event: continued.append(event))
    script = Script(
        hass,
        [
            {
                "action": f"{DOMAIN}.{SERVICE_SAY}",
                "data": {"message": "hello"},
                "continue_on_error": True,
            },
            {"event": "chime_tts_test_continued"},
        ],
        "chime_queue_timeout",
        "test",
        log_exceptions=False,
    )

    await script.async_run()

    assert len(continued) == 1
