"""Coverage for media-player target-source resolution."""

import importlib.util
from pathlib import Path
from types import SimpleNamespace


def _resolver_module():
    path = Path(__file__).parents[1] / "custom_components/chime_tts/helpers/target_resolver.py"
    spec = importlib.util.spec_from_file_location("chime_tts_target_resolver", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_resolves_entity_device_area_floor_and_label_sources():
    """All supported source types resolve, filter, and deduplicate."""
    resolver = _resolver_module()
    resolver.target_helper = None
    entities = {
        "direct": SimpleNamespace(entity_id="media_player.direct", device_id=None, area_id=None, labels=[]),
        "device": SimpleNamespace(entity_id="media_player.device", device_id="device_1", area_id=None, labels=[]),
        "area": SimpleNamespace(entity_id="media_player.area", device_id="device_2", area_id=None, labels=[]),
        "floor": SimpleNamespace(entity_id="media_player.floor", device_id="device_3", area_id=None, labels=[]),
        "label": SimpleNamespace(entity_id="media_player.label", device_id=None, area_id=None, labels=["label_1"]),
        "label_device": SimpleNamespace(entity_id="media_player.label_device", device_id="device_4", area_id=None, labels=[]),
        "label_area": SimpleNamespace(entity_id="media_player.label_area", device_id="device_5", area_id=None, labels=[]),
        "not_player": SimpleNamespace(entity_id="light.not_player", device_id="device_1", area_id=None, labels=[]),
    }
    devices = {
        "device_1": SimpleNamespace(id="device_1", area_id=None, labels=[]),
        "device_2": SimpleNamespace(id="device_2", area_id="area_1", labels=[]),
        "device_3": SimpleNamespace(id="device_3", area_id="area_2", labels=[]),
        "device_4": SimpleNamespace(id="device_4", area_id=None, labels=["label_1"]),
        "device_5": SimpleNamespace(id="device_5", area_id="area_3", labels=[]),
    }
    areas = {
        "area_1": SimpleNamespace(id="area_1", floor_id="floor_1", labels=[]),
        "area_2": SimpleNamespace(id="area_2", floor_id="floor_1", labels=[]),
        "area_3": SimpleNamespace(id="area_3", floor_id=None, labels=["label_1"]),
    }
    hass = SimpleNamespace(data={
        "entity_registry": SimpleNamespace(entities=entities),
        "device_registry": SimpleNamespace(devices=devices),
        "area_registry": SimpleNamespace(areas=areas),
    })

    assert resolver.resolve_media_player_entity_ids(hass, {
        "entity_id": ["media_player.direct", "media_player.direct"],
        "device_id": "device_1", "area_id": "area_1", "floor_id": "floor_1", "label_id": "label_1",
    }) == [
        "media_player.direct", "media_player.area", "media_player.device", "media_player.floor",
        "media_player.label", "media_player.label_area", "media_player.label_device",
    ]
