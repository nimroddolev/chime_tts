"""Tests for service registration, config validation, storage helpers, and replay behavior."""

from __future__ import annotations

import importlib
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from custom_components.chime_tts.const import CUSTOM_CHIMES_PATH_KEY
from custom_components.chime_tts.const import DATA_STORAGE_KEY
from custom_components.chime_tts.const import DOMAIN
from custom_components.chime_tts.const import QUEUE_TIMEOUT_KEY
from custom_components.chime_tts.const import SERVICE_REPLAY
from custom_components.chime_tts.const import SERVICE_SAY
from custom_components.chime_tts.const import SERVICE_SAY_URL
from custom_components.chime_tts.const import TEMP_PATH_KEY
from custom_components.chime_tts.const import WWW_PATH_KEY
from homeassistant.components.media_player.const import ATTR_MEDIA_CONTENT_ID
from homeassistant.core import SupportsResponse
from homeassistant.exceptions import HomeAssistantError

config_flow_module = importlib.import_module("custom_components.chime_tts.config_flow")
integration_module = importlib.import_module("custom_components.chime_tts.__init__")
services_helper_module = importlib.import_module("custom_components.chime_tts.helpers.services_helper")


class FakeServices:
    """Track service registration and calls."""

    def __init__(self) -> None:
        """Initialise the registry."""
        self.registered: dict[tuple[str, str], tuple[object, dict]] = {}
        self.removed: list[tuple[str, str]] = []
        self.calls: list[dict] = []
        self.error_to_raise: Exception | None = None

    def async_register(self, domain: str, service: str, func, **kwargs) -> None:
        """Store registered service callables."""
        self.registered[(domain, service)] = (func, kwargs)

    def async_remove(self, domain: str, service: str) -> None:
        """Track removed services."""
        self.removed.append((domain, service))

    async def async_call(self, domain: str, service: str, service_data: dict) -> None:
        """Record service calls and optionally raise a configured error."""
        self.calls.append(
            {"domain": domain, "service": service, "service_data": service_data}
        )
        if self.error_to_raise is not None:
            raise self.error_to_raise


class FakeHass:
    """Simple Home Assistant stand-in for config and service tests."""

    def __init__(self) -> None:
        """Provide the config and service attributes used by the tests."""
        self.config = SimpleNamespace(
            path=lambda *parts: f"/config/{'/'.join(parts)}",
            media_dirs={"media": "/config/media"},
            allowlist_external_dirs=["/config/www", "/config/media"],
        )
        self.data = {"tts_manager": SimpleNamespace(providers={"google_translate": object()})}
        self.services = FakeServices()

    async def async_add_executor_job(self, func, *args):
        """Run executor jobs inline for tests."""
        return func(*args)


def make_services_yaml(options: list[dict[str, str]]) -> dict:
    """Create the services.yaml shape used by the services helper."""
    return {
        "say": {
            "fields": {
                "chime_path": {"selector": {"select": {"options": list(options)}}},
                "end_chime_path": {"selector": {"select": {"options": list(options)}}},
            }
        },
        "say_url": {
            "fields": {
                "chime_path": {"selector": {"select": {"options": list(options)}}},
                "end_chime_path": {"selector": {"select": {"options": list(options)}}},
            }
        },
    }


@pytest.mark.asyncio
async def test_async_update_services_yaml_refreshes_options_and_registration(monkeypatch: pytest.MonkeyPatch) -> None:
    """Service helper should refresh both services.yaml option lists and service registrations."""
    hass = FakeHass()
    helper = services_helper_module.ChimeTTSServicesHelper()
    helper._data = {CUSTOM_CHIMES_PATH_KEY: "/custom/chimes"}
    save_yaml = AsyncMock()

    monkeypatch.setattr(
        services_helper_module.filesystem_helper,
        "async_get_chime_options_from_path",
        AsyncMock(return_value=[{"label": "Zulu", "value": "zulu"}]),
    )
    monkeypatch.setattr(helper, "_async_parse_services_yaml", AsyncMock(return_value=make_services_yaml([])))
    monkeypatch.setattr(helper, "_async_save_services_yaml", save_yaml)

    async def say_service(service):
        return service

    async def say_url_service(service):
        return service

    await helper.async_update_services_yaml(hass, say_service, say_url_service)

    saved_yaml = save_yaml.await_args.args[0]
    expected_options = sorted(
        services_helper_module.DEFAULT_CHIME_OPTIONS + [{"label": "Zulu", "value": "zulu"}],
        key=lambda entry: entry["label"].lower(),
    )
    assert saved_yaml["say"]["fields"]["chime_path"]["selector"]["select"]["options"] == expected_options
    assert saved_yaml["say_url"]["fields"]["end_chime_path"]["selector"]["select"]["options"] == expected_options
    assert hass.services.removed == [(DOMAIN, SERVICE_SAY), (DOMAIN, SERVICE_SAY_URL)]
    assert hass.services.registered[(DOMAIN, SERVICE_SAY)][0] is say_service
    assert hass.services.registered[(DOMAIN, SERVICE_SAY_URL)][1] == {
        "supports_response": SupportsResponse.ONLY
    }


@pytest.mark.asyncio
async def test_async_update_chime_lists_adds_placeholder_when_no_custom_options(monkeypatch: pytest.MonkeyPatch) -> None:
    """An empty custom-chime list should append the placeholder guidance option."""
    helper = services_helper_module.ChimeTTSServicesHelper()
    save_yaml = AsyncMock()

    monkeypatch.setattr(helper, "_async_parse_services_yaml", AsyncMock(return_value=make_services_yaml([])))
    monkeypatch.setattr(helper, "_async_save_services_yaml", save_yaml)

    await helper._async_update_chime_lists(FakeHass(), custom_chime_options=[])

    saved_options = save_yaml.await_args.args[0]["say"]["fields"]["chime_path"]["selector"]["select"]["options"]
    assert saved_options[-1] == {
        "label": "*** Add a local folder path in the configuration for your own custom chimes ***",
        "value": "",
    }


def make_options_flow(options: dict | None = None, data: dict | None = None):
    """Return an options flow with simple async_show_form/async_create_entry hooks."""
    flow = config_flow_module.ChimeTTSOptionsFlowHandler(
        SimpleNamespace(options=options or {}, data=data or {})
    )
    flow.hass = FakeHass()
    flow.async_show_form = lambda **kwargs: {"type": "form", **kwargs}
    flow.async_create_entry = lambda **kwargs: {"type": "create_entry", **kwargs}
    flow._async_current_entries = lambda: []
    flow.hass.config.media_dirs = {"media": "/config/media"}
    flow.hass.config.allowlist_external_dirs = ["/config/www", "/config/media"]
    return flow


@pytest.mark.asyncio
async def test_options_flow_rejects_temp_path_outside_media_dirs(monkeypatch: pytest.MonkeyPatch) -> None:
    """Temp paths outside a media directory should be rejected."""
    flow = make_options_flow()

    monkeypatch.setattr(config_flow_module.helpers, "get_installed_tts_platforms", lambda hass: ["google_translate"])
    monkeypatch.setattr(flow, "get_installed_tts", lambda: ["google_translate"])

    result = await flow.async_step_init(
        {
            QUEUE_TIMEOUT_KEY: 60,
            "tts_timeout": 30,
            "tts_platform_key": "",
            "default_language_key": "",
            "default_voice_key": "",
            "default_tld_key": "",
            "fallback_tts_platform_key": "",
            "offset": 450,
            "crossfade": 0,
            "fade_transition_key": 500,
            "remove_temp_file_delay": 0,
            CUSTOM_CHIMES_PATH_KEY: "",
            "temp_chimes_path": "/config/media/chimes",
            TEMP_PATH_KEY: "/not-media/chime_tts",
            WWW_PATH_KEY: "/config/www/chime_tts",
            "add_cover_art": False,
        }
    )

    assert result["type"] == "form"
    assert result["errors"][TEMP_PATH_KEY] == TEMP_PATH_KEY


@pytest.mark.asyncio
async def test_options_flow_requires_public_path_under_allowlist(monkeypatch: pytest.MonkeyPatch) -> None:
    """WWW paths outside allowed public locations should be rejected."""
    flow = make_options_flow()

    monkeypatch.setattr(config_flow_module.helpers, "get_installed_tts_platforms", lambda hass: ["google_translate"])
    monkeypatch.setattr(flow, "get_installed_tts", lambda: ["google_translate"])

    result = await flow.async_step_init(
        {
            QUEUE_TIMEOUT_KEY: 60,
            "tts_timeout": 30,
            "tts_platform_key": "",
            "default_language_key": "",
            "default_voice_key": "",
            "default_tld_key": "",
            "fallback_tts_platform_key": "",
            "offset": 450,
            "crossfade": 0,
            "fade_transition_key": 500,
            "remove_temp_file_delay": 0,
            CUSTOM_CHIMES_PATH_KEY: "",
            "temp_chimes_path": "/config/media/chimes",
            TEMP_PATH_KEY: "/config/media/chime_tts",
            WWW_PATH_KEY: "/outside/chime_tts",
            "add_cover_art": False,
        }
    )

    assert result["type"] == "form"
    assert result["errors"][WWW_PATH_KEY] == WWW_PATH_KEY


@pytest.mark.asyncio
async def test_options_flow_shows_restart_step_on_first_custom_chimes_path(monkeypatch: pytest.MonkeyPatch) -> None:
    """Adding a custom chimes path for the first time should show the restart step."""
    flow = make_options_flow(options={})

    monkeypatch.setattr(config_flow_module.helpers, "get_installed_tts_platforms", lambda hass: ["google_translate"])
    monkeypatch.setattr(flow, "get_installed_tts", lambda: ["google_translate"])

    result = await flow.async_step_init(
        {
            QUEUE_TIMEOUT_KEY: 60,
            "tts_timeout": 30,
            "tts_platform_key": "",
            "default_language_key": "",
            "default_voice_key": "",
            "default_tld_key": "",
            "fallback_tts_platform_key": "",
            "offset": 450,
            "crossfade": 0,
            "fade_transition_key": 500,
            "remove_temp_file_delay": 0,
            CUSTOM_CHIMES_PATH_KEY: "/config/chimes",
            "temp_chimes_path": "/config/media/chimes",
            TEMP_PATH_KEY: "/config/media/chime_tts",
            WWW_PATH_KEY: "/config/www/chime_tts",
            "add_cover_art": False,
        }
    )

    assert result["type"] == "form"
    assert result["step_id"] == "restart_required"


@pytest.mark.asyncio
async def test_async_fire_media_service_calls_returns_false_on_service_errors() -> None:
    """Playback helper should fail closed when service dispatch raises."""
    hass = FakeHass()
    hass.services.error_to_raise = HomeAssistantError("boom")

    result = await integration_module.async_fire_media_service_calls(
        hass,
        [{"domain": "media_player", "service": "play_media", "service_data": {}}],
    )

    assert result is False


@pytest.mark.asyncio
async def test_async_fire_media_service_calls_returns_false_when_no_calls() -> None:
    """Missing service calls should produce a False result."""
    assert await integration_module.async_fire_media_service_calls(FakeHass(), None) is False


@pytest.mark.asyncio
async def test_storage_helpers_store_retrieve_and_delete(monkeypatch: pytest.MonkeyPatch) -> None:
    """Storage helpers should persist, refresh, and delete cached entries."""
    stored_data = {"existing": {"value": 1}}

    class FakeStore:
        """Simple async store stub with shared data."""

        def __init__(self, hass, version, key) -> None:
            del hass, version, key

        async def async_load(self):
            return dict(stored_data)

        async def async_save(self, data):
            stored_data.clear()
            stored_data.update(data)

    monkeypatch.setattr(integration_module.storage, "Store", FakeStore)
    integration_module._data[DATA_STORAGE_KEY] = None

    await integration_module.async_store_data(FakeHass(), "new", {"value": 2})
    assert stored_data["new"] == {"value": 2}

    retrieved = await integration_module.async_retrieve_data(FakeHass(), "new")
    assert retrieved == {"value": 2}

    await integration_module.async_delete_data(FakeHass(), "new")
    assert "new" not in stored_data


@pytest.mark.asyncio
async def test_storage_refresh_loads_store_data(monkeypatch: pytest.MonkeyPatch) -> None:
    """Refreshing stored data should copy the persisted dictionary into `_data`."""
    class FakeStore:
        """Store returning a fixed payload."""

        def __init__(self, hass, version, key) -> None:
            del hass, version, key

        async def async_load(self):
            return {"cached": {"path": "/tmp/test.mp3"}}

    monkeypatch.setattr(integration_module.storage, "Store", FakeStore)

    await integration_module.async_refresh_stored_data(FakeHass())

    assert integration_module._data[DATA_STORAGE_KEY] == {"cached": {"path": "/tmp/test.mp3"}}


@pytest.mark.asyncio
async def test_async_setup_registers_services_and_replay_reuses_previous_service(monkeypatch: pytest.MonkeyPatch) -> None:
    """Replay should invoke the previous `say` request once a service call has been stored."""
    hass = FakeHass()
    prepare_media = AsyncMock(return_value={"url": "https://example.test/out.mp3", "success": True})
    parse_params = AsyncMock(
        return_value={
            "message": "hello",
            "chime_path": "",
            "end_chime_path": "",
            "media_players_array": [],
        }
    )

    async def run_immediately(func, timeout, service, is_say_url):
        del timeout
        return await func(service, is_say_url)

    monkeypatch.setattr(integration_module.helpers, "async_parse_params", parse_params)
    monkeypatch.setattr(integration_module.helpers, "parse_options_yaml", lambda data, default_data: {})
    monkeypatch.setattr(integration_module, "async_prepare_media", prepare_media)
    monkeypatch.setattr(
        integration_module.queue,
        "add_to_queue",
        AsyncMock(side_effect=run_immediately),
    )

    await integration_module.async_setup(hass, SimpleNamespace())

    say_handler = hass.services.registered[(DOMAIN, SERVICE_SAY)][0]
    replay_handler = hass.services.registered[(DOMAIN, SERVICE_REPLAY)][0]
    service = SimpleNamespace(data={"message": "hello"})

    first_result = await say_handler(service)
    replay_result = await replay_handler(SimpleNamespace(data={}))

    assert first_result == {"url": "https://example.test/out.mp3", "success": True}
    assert replay_result == {"url": "https://example.test/out.mp3", "success": True}
    assert parse_params.await_count == 2
    assert integration_module._data["service"] is service


@pytest.mark.asyncio
async def test_replay_raises_before_first_say(monkeypatch: pytest.MonkeyPatch) -> None:
    """Replay should fail until a prior `say` request has been stored."""
    hass = FakeHass()
    integration_module._data.pop("service", None)

    async def run_immediately(func, timeout, service, is_say_url):
        del timeout
        return await func(service, is_say_url)

    monkeypatch.setattr(
        integration_module.queue,
        "add_to_queue",
        AsyncMock(side_effect=run_immediately),
    )

    await integration_module.async_setup(hass, SimpleNamespace())

    replay_handler = hass.services.registered[(DOMAIN, SERVICE_REPLAY)][0]

    with pytest.raises(HomeAssistantError):
        await replay_handler(SimpleNamespace(data={}))


@pytest.mark.asyncio
async def test_say_url_returns_unsuccessful_payload_when_parse_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    """Failed `say_url` parsing should return the explicit unsuccessful response payload."""
    hass = FakeHass()

    async def run_immediately(func, timeout, service, is_say_url):
        del timeout
        return await func(service, is_say_url)

    monkeypatch.setattr(integration_module.helpers, "async_parse_params", AsyncMock(return_value=None))
    monkeypatch.setattr(
        integration_module.queue,
        "add_to_queue",
        AsyncMock(side_effect=run_immediately),
    )

    await integration_module.async_setup(hass, SimpleNamespace())

    say_url_handler = hass.services.registered[(DOMAIN, SERVICE_SAY_URL)][0]
    result = await say_url_handler(SimpleNamespace(data={"message": ""}))

    assert result == {
        "url": None,
        ATTR_MEDIA_CONTENT_ID: None,
        "duration": 0,
        "success": False,
    }
