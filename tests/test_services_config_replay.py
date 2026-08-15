"""Tests for service registration, config validation, storage helpers, and replay behavior."""

from __future__ import annotations

import importlib
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, call

import pytest

from custom_components.chime_tts.const import CUSTOM_CHIMES_PATH_KEY
from custom_components.chime_tts.const import ADD_COVER_ART_KEY
from custom_components.chime_tts.const import CROSSFADE_KEY
from custom_components.chime_tts.const import DATA_STORAGE_KEY
from custom_components.chime_tts.const import DEFAULT_LANGUAGE_KEY
from custom_components.chime_tts.const import DEFAULT_OFFSET_MS
from custom_components.chime_tts.const import DEFAULT_POST_SCRIPT_KEY
from custom_components.chime_tts.const import DEFAULT_POST_SCRIPT_SAY_URL_KEY
from custom_components.chime_tts.const import DEFAULT_POST_SCRIPT_SHARED_KEY
from custom_components.chime_tts.const import DEFAULT_PRE_SCRIPT_KEY
from custom_components.chime_tts.const import DEFAULT_PRE_SCRIPT_SAY_URL_KEY
from custom_components.chime_tts.const import DEFAULT_PRE_SCRIPT_SHARED_KEY
from custom_components.chime_tts.const import DEFAULT_TLD_KEY
from custom_components.chime_tts.const import DEFAULT_VOICE_KEY
from custom_components.chime_tts.const import DOMAIN
from custom_components.chime_tts.const import FADE_TRANSITION_KEY
from custom_components.chime_tts.const import FALLBACK_TTS_PLATFORM_KEY
from custom_components.chime_tts.const import OFFSET_KEY
from custom_components.chime_tts.const import QUEUE_TIMEOUT_KEY
from custom_components.chime_tts.const import REMOVE_TEMP_FILE_DELAY_KEY
from custom_components.chime_tts.const import SERVICE_REPLAY
from custom_components.chime_tts.const import SERVICE_CLEAR_CACHE
from custom_components.chime_tts.const import SERVICE_SAY
from custom_components.chime_tts.const import SERVICE_SAY_URL
from custom_components.chime_tts.const import TEMP_PATH_KEY
from custom_components.chime_tts.const import TEMP_CHIMES_PATH_KEY
from custom_components.chime_tts.const import TTS_PLATFORM_KEY
from custom_components.chime_tts.const import TTS_TIMEOUT_KEY
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

    def has_service(self, domain: str, service: str) -> bool:
        """Report whether a service is currently registered."""
        return (domain, service) in self.registered


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


@pytest.mark.asyncio
async def test_configuration_loads_default_start_and_end_chimes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Every configured default is loaded into the integration runtime."""
    hass = FakeHass()
    previous_data = dict(integration_module._data)
    monkeypatch.setattr(
        integration_module.services_helper,
        "async_update_services_yaml",
        AsyncMock(),
    )
    integration_module._data["async_say"] = object()
    integration_module._data["async_say_url"] = object()

    try:
        await integration_module.async_update_configuration(
            SimpleNamespace(
                options={
                    QUEUE_TIMEOUT_KEY: 31,
                    TTS_TIMEOUT_KEY: 19,
                    ADD_COVER_ART_KEY: True,
                    TTS_PLATFORM_KEY: "google_translate",
                    DEFAULT_LANGUAGE_KEY: "en-US",
                    DEFAULT_VOICE_KEY: "Jenny",
                    DEFAULT_TLD_KEY: "co.uk",
                    FALLBACK_TTS_PLATFORM_KEY: "cloud",
                    DEFAULT_PRE_SCRIPT_KEY: "script.prepare",
                    DEFAULT_POST_SCRIPT_KEY: "script.restore",
                    DEFAULT_PRE_SCRIPT_SHARED_KEY: False,
                    DEFAULT_POST_SCRIPT_SHARED_KEY: False,
                    DEFAULT_PRE_SCRIPT_SAY_URL_KEY: "script.url_prepare",
                    DEFAULT_POST_SCRIPT_SAY_URL_KEY: "script.url_restore",
                    "chime_path": "bells",
                    "end_chime_path": "tada",
                    OFFSET_KEY: 525,
                    CROSSFADE_KEY: 35,
                    FADE_TRANSITION_KEY: 575,
                    REMOVE_TEMP_FILE_DELAY_KEY: 200,
                    CUSTOM_CHIMES_PATH_KEY: "/custom/chimes",
                    TEMP_CHIMES_PATH_KEY: "/media/chime-downloads",
                    TEMP_PATH_KEY: "/media/chime-temp",
                    WWW_PATH_KEY: "/config/www/chime-output",
                }
            ),
            hass,
        )

        expected_values = {
            QUEUE_TIMEOUT_KEY: 31,
            TTS_TIMEOUT_KEY: 19,
            ADD_COVER_ART_KEY: True,
            TTS_PLATFORM_KEY: "google_translate",
            DEFAULT_LANGUAGE_KEY: "en-US",
            DEFAULT_VOICE_KEY: "Jenny",
            DEFAULT_TLD_KEY: "co.uk",
            FALLBACK_TTS_PLATFORM_KEY: "cloud",
            DEFAULT_PRE_SCRIPT_KEY: "script.prepare",
            DEFAULT_POST_SCRIPT_KEY: "script.restore",
            DEFAULT_PRE_SCRIPT_SHARED_KEY: False,
            DEFAULT_POST_SCRIPT_SHARED_KEY: False,
            DEFAULT_PRE_SCRIPT_SAY_URL_KEY: "script.url_prepare",
            DEFAULT_POST_SCRIPT_SAY_URL_KEY: "script.url_restore",
            "chime_path": "bells",
            "end_chime_path": "tada",
            OFFSET_KEY: 525,
            CROSSFADE_KEY: 35,
            FADE_TRANSITION_KEY: 575,
            REMOVE_TEMP_FILE_DELAY_KEY: 200,
        }
        for key, value in expected_values.items():
            assert integration_module._data[key] == value
        assert integration_module._data[CUSTOM_CHIMES_PATH_KEY] == (
            integration_module.filesystem_helper.make_folder_path_safe("/custom/chimes")
        )
        for key, value in (
            (TEMP_CHIMES_PATH_KEY, "/media/chime-downloads"),
            (TEMP_PATH_KEY, "/media/chime-temp"),
            (WWW_PATH_KEY, "/config/www/chime-output"),
        ):
            assert integration_module._data[key] == (
                integration_module.filesystem_helper.make_folder_path_safe(
                    hass.config.path(value)
                )
            )
    finally:
        integration_module._data.clear()
        integration_module._data.update(previous_data)


@pytest.mark.asyncio
async def test_configuration_uses_the_documented_offset_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A missing legacy offset option uses the same default as the settings UI."""
    hass = FakeHass()
    previous_data = dict(integration_module._data)
    monkeypatch.setattr(
        integration_module.services_helper,
        "async_update_services_yaml",
        AsyncMock(),
    )
    integration_module._data["async_say"] = object()
    integration_module._data["async_say_url"] = object()

    try:
        await integration_module.async_update_configuration(
            SimpleNamespace(options={}), hass
        )

        assert integration_module._data[OFFSET_KEY] == DEFAULT_OFFSET_MS
    finally:
        integration_module._data.clear()
        integration_module._data.update(previous_data)


def make_services_yaml(options: list[dict[str, str]]) -> dict:
    """Create the services.yaml shape used by the services helper."""
    return {
        "say": {
            "target": {"entity": {"domain": "media_player"}},
            "fields": {
                "chime_path": {"selector": {"select": {"options": list(options)}}},
                "end_chime_path": {"selector": {"select": {"options": list(options)}}},
                "tts_platform": {"selector": {"select": {"options": list(options)}}},
            }
        },
        "say_url": {
            "fields": {
                "chime_path": {"selector": {"select": {"options": list(options)}}},
                "end_chime_path": {"selector": {"select": {"options": list(options)}}},
                "tts_platform": {"selector": {"select": {"options": list(options)}}},
            }
        },
    }


@pytest.mark.asyncio
async def test_async_update_services_yaml_refreshes_options_and_registration(monkeypatch: pytest.MonkeyPatch) -> None:
    """Service helper should refresh both services.yaml option lists and service registrations."""
    hass = FakeHass()
    hass.data["tts_manager"] = SimpleNamespace(
        providers={
            "google_translate": object(),
            "tts.google_generative_ai": object(),
        }
    )
    helper = services_helper_module.ChimeTTSServicesHelper()
    helper._data = {CUSTOM_CHIMES_PATH_KEY: "/custom/chimes"}
    save_yaml = AsyncMock()
    refreshed_schemas: list[tuple[str, str, dict]] = []

    monkeypatch.setattr(
        services_helper_module.filesystem_helper,
        "async_get_chime_options_from_path",
        AsyncMock(return_value=[{"label": "Zulu", "value": "zulu"}]),
    )
    monkeypatch.setattr(
        services_helper_module.service_helper,
        "async_set_service_schema",
        lambda hass, domain, service, schema: refreshed_schemas.append(
            (domain, service, schema)
        ),
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
    assert saved_yaml["say"]["fields"]["tts_platform"]["selector"]["select"]["options"] == []
    assert saved_yaml["say_url"]["fields"]["tts_platform"]["selector"]["select"]["options"] == []
    assert [(domain, service) for domain, service, _schema in refreshed_schemas] == [
        (DOMAIN, SERVICE_SAY),
        (DOMAIN, SERVICE_SAY_URL),
    ]
    assert (
        refreshed_schemas[0][2]["fields"]["chime_path"]["selector"]["select"]["options"]
        == expected_options
    )
    assert refreshed_schemas[0][2]["target"] == {
        "entity": [{"domain": ["media_player"]}]
    }
    assert hass.services.removed == [(DOMAIN, SERVICE_SAY), (DOMAIN, SERVICE_SAY_URL)]
    assert hass.services.registered[(DOMAIN, SERVICE_SAY)][0] is say_service
    assert hass.services.registered[(DOMAIN, SERVICE_SAY_URL)][1] == {
        "supports_response": SupportsResponse.ONLY
    }


@pytest.mark.asyncio
async def test_custom_chimes_monitor_refreshes_services_after_folder_change(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A changed custom-chimes folder refreshes the action selector options."""
    hass = FakeHass()
    refresh_services = AsyncMock()
    fingerprint = AsyncMock(return_value=(("new-chime.mp3", 2, 1024),))
    start_event = Mock(return_value="custom-chimes-update")
    finish_event = Mock()
    subtitle = Mock()
    debug = Mock()

    async def say_service(service):
        return service

    async def say_url_service(service):
        return service

    monkeypatch.setattr(
        integration_module,
        "_data",
        {
            CUSTOM_CHIMES_PATH_KEY: "/custom/chimes",
            integration_module.CUSTOM_CHIMES_FINGERPRINT_KEY: (("old-chime.mp3", 1, 512),),
            "async_say": say_service,
            "async_say_url": say_url_service,
        },
    )
    monkeypatch.setattr(
        integration_module.filesystem_helper,
        "async_get_chime_directory_fingerprint",
        fingerprint,
    )
    monkeypatch.setattr(
        integration_module.services_helper,
        "async_update_services_yaml",
        refresh_services,
    )
    monkeypatch.setattr(integration_module, "start_panel_log_event", start_event)
    monkeypatch.setattr(integration_module, "finish_panel_log_event", finish_event)
    monkeypatch.setattr(integration_module.helpers, "debug_subtitle", subtitle)
    monkeypatch.setattr(integration_module, "_LOGGER", Mock(debug=debug))

    assert await integration_module._async_check_custom_chimes_folder(hass) is True
    start_event.assert_called_once_with(
        hass,
        "custom_chimes_update",
        "Custom Chimes Update",
        row_color="configuration",
    )
    subtitle.assert_called_once_with("Custom Chimes Update")
    assert call("- Added: %s", "new-chime.mp3") in debug.call_args_list
    assert call("- Removed: %s", "old-chime.mp3") in debug.call_args_list
    finish_event.assert_called_once_with(hass, "custom-chimes-update")
    refresh_services.assert_awaited_once_with(
        hass=hass,
        say_service_func=say_service,
        say_url_service_func=say_url_service,
    )


@pytest.mark.asyncio
async def test_custom_chimes_monitor_retries_after_metadata_refresh_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A failed metadata refresh must leave the previous fingerprint for retry."""
    hass = FakeHass()
    previous_fingerprint = (("old-chime.mp3", 1, 512),)
    current_fingerprint = (("new-chime.mp3", 2, 1024),)

    async def say_service(service):
        return service

    async def say_url_service(service):
        return service

    monkeypatch.setattr(
        integration_module,
        "_data",
        {
            CUSTOM_CHIMES_PATH_KEY: "/custom/chimes",
            integration_module.CUSTOM_CHIMES_FINGERPRINT_KEY: previous_fingerprint,
            "async_say": say_service,
            "async_say_url": say_url_service,
        },
    )
    monkeypatch.setattr(
        integration_module.filesystem_helper,
        "async_get_chime_directory_fingerprint",
        AsyncMock(return_value=current_fingerprint),
    )
    monkeypatch.setattr(
        integration_module.services_helper,
        "async_update_services_yaml",
        AsyncMock(return_value=False),
    )
    monkeypatch.setattr(integration_module, "start_panel_log_event", Mock(return_value="event"))
    monkeypatch.setattr(integration_module, "finish_panel_log_event", Mock())

    assert await integration_module._async_check_custom_chimes_folder(hass) is False
    assert (
        integration_module._data[integration_module.CUSTOM_CHIMES_FINGERPRINT_KEY]
        == previous_fingerprint
    )



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
async def test_options_flow_saves_first_custom_chimes_path_without_restart(monkeypatch: pytest.MonkeyPatch) -> None:
    """Adding a custom chimes path takes effect without a Home Assistant restart."""
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

    assert result["type"] == "create_entry"


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
async def test_clear_cache_returns_a_response_when_cache_has_not_been_initialized() -> None:
    """Clearing an empty cache must work from the Developer Tools response UI."""
    hass = FakeHass()
    integration_module._data[DATA_STORAGE_KEY] = None

    await integration_module.async_setup(hass, SimpleNamespace())

    clear_cache_handler, registration = hass.services.registered[
        (DOMAIN, SERVICE_CLEAR_CACHE)
    ]
    response = await clear_cache_handler(
        SimpleNamespace(
            data={"clear_temp_tts_cache": True},
            return_response=True,
        )
    )

    assert registration == {"supports_response": SupportsResponse.OPTIONAL}
    assert response == {
        "success": True,
        "clear_chimes_cache": False,
        "clear_temp_tts_cache": True,
        "clear_www_tts_cache": False,
        "clear_ha_tts_cache": False,
    }


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


@pytest.mark.asyncio
async def test_say_url_accepts_scripts(monkeypatch: pytest.MonkeyPatch) -> None:
    """say_url passes scripts through to media preparation."""
    hass = FakeHass()

    async def run_immediately(func, timeout, service, is_say_url):
        del timeout
        return await func(service, is_say_url)

    params = {
        "message": "Hello",
        "chime_path": "",
        "end_chime_path": "",
        "media_players_array": [],
    }
    prepare_media = AsyncMock(return_value={"url": "https://example.test/out.mp3", "success": True})
    monkeypatch.setattr(integration_module.helpers, "async_parse_params", AsyncMock(return_value=params))
    monkeypatch.setattr(integration_module.helpers, "parse_options_yaml", lambda data, default_data: {})
    monkeypatch.setattr(integration_module, "async_prepare_media", prepare_media)
    monkeypatch.setattr(integration_module.queue, "add_to_queue", AsyncMock(side_effect=run_immediately))
    await integration_module.async_setup(hass, SimpleNamespace())

    say_url_handler = hass.services.registered[(DOMAIN, SERVICE_SAY_URL)][0]

    await say_url_handler(
        SimpleNamespace(
            data={
                "message": "Hello",
                "pre_script": "script.prepare_speakers",
                "post_script": "script.restore_speakers",
            }
        )
    )

    assert integration_module.helpers.async_parse_params.await_args.args[1]["pre_script"] == "script.prepare_speakers"
    assert integration_module.helpers.async_parse_params.await_args.args[1]["post_script"] == "script.restore_speakers"
    assert prepare_media.await_args.args[4] is True
