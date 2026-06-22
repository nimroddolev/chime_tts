"""Pytest configuration for Chime TTS tests."""

from __future__ import annotations

import sys
import types
from pathlib import Path
from unittest.mock import AsyncMock


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


custom_components_pkg = types.ModuleType("custom_components")
custom_components_pkg.__path__ = [str(ROOT / "custom_components")]
sys.modules.setdefault("custom_components", custom_components_pkg)

chime_tts_pkg = types.ModuleType("custom_components.chime_tts")
chime_tts_pkg.__path__ = [str(ROOT / "custom_components" / "chime_tts")]
sys.modules.setdefault("custom_components.chime_tts", chime_tts_pkg)


homeassistant_pkg = types.ModuleType("homeassistant")
homeassistant_pkg.__path__ = []
sys.modules.setdefault("homeassistant", homeassistant_pkg)

homeassistant_core = types.ModuleType("homeassistant.core")
homeassistant_core.HomeAssistant = type("HomeAssistant", (), {})
homeassistant_core.State = type("State", (), {})
homeassistant_core.ServiceResponse = dict
homeassistant_core.SupportsResponse = type("SupportsResponse", (), {"ONLY": "only"})
sys.modules.setdefault("homeassistant.core", homeassistant_core)

homeassistant_const = types.ModuleType("homeassistant.const")
homeassistant_const.CONF_ENTITY_ID = "entity_id"
homeassistant_const.SERVICE_TURN_ON = "turn_on"
homeassistant_const.SERVICE_VOLUME_SET = "volume_set"
sys.modules.setdefault("homeassistant.const", homeassistant_const)

homeassistant_helpers = types.ModuleType("homeassistant.helpers")
homeassistant_helpers.__path__ = []
sys.modules.setdefault("homeassistant.helpers", homeassistant_helpers)

homeassistant_helpers_network = types.ModuleType("homeassistant.helpers.network")
homeassistant_helpers_network.get_url = lambda hass: "http://localhost"
sys.modules.setdefault("homeassistant.helpers.network", homeassistant_helpers_network)

homeassistant_helpers_storage = types.ModuleType("homeassistant.helpers.storage")
homeassistant_helpers_storage.Store = type(
    "Store",
    (),
    {
        "__init__": lambda self, hass, version, key: None,
        "async_save": lambda self, data: None,
        "async_load": lambda self: {},
    },
)
sys.modules.setdefault("homeassistant.helpers.storage", homeassistant_helpers_storage)

homeassistant_components = types.ModuleType("homeassistant.components")
homeassistant_components.__path__ = []
sys.modules.setdefault("homeassistant.components", homeassistant_components)

homeassistant_components_tts = types.ModuleType("homeassistant.components.tts")
homeassistant_components_tts.media_source = types.SimpleNamespace(
    generate_media_source_id=lambda **kwargs: "media-source://stub"
)
homeassistant_components_tts.async_get_media_source_audio = lambda **kwargs: None
sys.modules.setdefault("homeassistant.components.tts", homeassistant_components_tts)

homeassistant_media_player = types.ModuleType("homeassistant.components.media_player")
homeassistant_media_player.__path__ = []
sys.modules.setdefault("homeassistant.components.media_player", homeassistant_media_player)

homeassistant_media_player_const = types.ModuleType("homeassistant.components.media_player.const")
homeassistant_media_player_const.ATTR_GROUP_MEMBERS = "group_members"
homeassistant_media_player_const.ATTR_MEDIA_CONTENT_ID = "media_content_id"
homeassistant_media_player_const.ATTR_MEDIA_CONTENT_TYPE = "media_content_type"
homeassistant_media_player_const.ATTR_MEDIA_ANNOUNCE = "announce"
homeassistant_media_player_const.ATTR_MEDIA_VOLUME_LEVEL = "volume_level"
homeassistant_media_player_const.SERVICE_PLAY_MEDIA = "play_media"
homeassistant_media_player_const.SERVICE_JOIN = "join"
homeassistant_media_player_const.SERVICE_UNJOIN = "unjoin"
homeassistant_media_player_const.MediaType = type("MediaType", (), {"MUSIC": "music"})
sys.modules.setdefault("homeassistant.components.media_player.const", homeassistant_media_player_const)

homeassistant_config_entries = types.ModuleType("homeassistant.config_entries")
homeassistant_config_entries.ConfigEntry = type("ConfigEntry", (), {})
homeassistant_config_entries.OptionsFlow = type("OptionsFlow", (), {})
homeassistant_config_entries.ConfigFlow = type("ConfigFlow", (), {})
homeassistant_config_entries.HANDLERS = types.SimpleNamespace(register=lambda domain: (lambda cls: cls))
sys.modules.setdefault("homeassistant.config_entries", homeassistant_config_entries)

homeassistant_exceptions = types.ModuleType("homeassistant.exceptions")
homeassistant_exceptions.HomeAssistantError = type("HomeAssistantError", (Exception,), {})
homeassistant_exceptions.ServiceNotFound = type("ServiceNotFound", (Exception,), {})
homeassistant_exceptions.TemplateError = type("TemplateError", (Exception,), {})
sys.modules.setdefault("homeassistant.exceptions", homeassistant_exceptions)

homeassistant_selector = types.ModuleType("homeassistant.helpers.selector")
homeassistant_selector.SelectSelector = lambda config: config
homeassistant_selector.SelectSelectorConfig = lambda **kwargs: kwargs
homeassistant_selector.SelectSelectorMode = types.SimpleNamespace(DROPDOWN="dropdown")
sys.modules.setdefault("homeassistant.helpers.selector", homeassistant_selector)

hass_nabucasa = types.ModuleType("hass_nabucasa")
hass_nabucasa.__path__ = []
sys.modules.setdefault("hass_nabucasa", hass_nabucasa)

hass_nabucasa_voice = types.ModuleType("hass_nabucasa.voice")
hass_nabucasa_voice.TTS_VOICES = {}
sys.modules.setdefault("hass_nabucasa.voice", hass_nabucasa_voice)

aiofiles_module = types.ModuleType("aiofiles")
aiofiles_module.open = AsyncMock()
sys.modules.setdefault("aiofiles", aiofiles_module)

aiofiles_os_module = types.ModuleType("aiofiles.os")
sys.modules.setdefault("aiofiles.os", aiofiles_os_module)
