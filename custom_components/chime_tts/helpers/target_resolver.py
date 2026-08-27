"""Resolve Home Assistant target sources to Chime TTS media players."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

try:
    from homeassistant.helpers import target as target_helper
except ImportError:  # pragma: no cover - historical Home Assistant support
    target_helper = None


TARGET_KEYS = ("entity_id", "device_id", "area_id", "floor_id", "label_id")


def _as_list(value: Any, *, split_commas: bool = False) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        values = value.split(",") if split_commas else [value]
    elif isinstance(value, Iterable) and not isinstance(value, Mapping):
        values = value
    else:
        values = [value]
    return [str(item).strip() for item in values if str(item).strip()]


def target_sources(data: Mapping[str, Any]) -> dict[str, list[str]]:
    """Merge flattened and nested service target sources without resolving them."""
    result: dict[str, list[str]] = {}
    nested = data.get("target")
    for key in TARGET_KEYS:
        values = _as_list(
            nested.get(key) if isinstance(nested, Mapping) else None,
            split_commas=key == "entity_id",
        )
        values.extend(_as_list(data.get(key), split_commas=key == "entity_id"))
        if values:
            result[key] = values
    return result


def _fallback_referenced_entities(hass, sources: Mapping[str, list[str]]) -> set[str]:
    """Resolve sources using registries when core's target helper is unavailable."""
    entity_registry = hass.data.get("entity_registry")
    device_registry = hass.data.get("device_registry")
    area_registry = hass.data.get("area_registry")
    if entity_registry is None:
        return set(sources.get("entity_id", []))

    entities = tuple(entity_registry.entities.values())
    areas = getattr(area_registry, "areas", {}) if area_registry else {}
    devices = getattr(device_registry, "devices", {}) if device_registry else {}
    labels = set(sources.get("label_id", []))
    area_ids = set(sources.get("area_id", []))
    area_ids.update(
        area.id for area in areas.values()
        if getattr(area, "floor_id", None) in set(sources.get("floor_id", []))
        or labels.intersection(getattr(area, "labels", []) or [])
    )
    device_ids = set(sources.get("device_id", []))
    device_ids.update(
        device.id for device in devices.values()
        if getattr(device, "area_id", None) in area_ids
        or labels.intersection(getattr(device, "labels", []) or [])
    )
    referenced = set(sources.get("entity_id", []))
    referenced.update(
        entry.entity_id for entry in entities
        if labels.intersection(getattr(entry, "labels", []) or [])
        or getattr(entry, "area_id", None) in area_ids
        or getattr(entry, "device_id", None) in set(sources.get("device_id", []))
        or (
            not getattr(entry, "area_id", None)
            and getattr(entry, "device_id", None) in device_ids
        )
    )
    return referenced


def resolve_media_player_entity_ids(hass, data: Mapping[str, Any]) -> list[str]:
    """Resolve target sources at execution time and return unique media players."""
    sources = target_sources(data)
    if not sources:
        return []
    if target_helper is not None:
        selection = target_helper.TargetSelection(sources)
        selected = target_helper.async_extract_referenced_entity_ids(
            hass, selection, expand_group=True
        )
        referenced = selected.referenced | selected.indirectly_referenced
    else:
        referenced = _fallback_referenced_entities(hass, sources)

    ordered = _as_list(sources.get("entity_id", []), split_commas=True)
    ordered.extend(sorted(referenced - set(ordered)))
    result: list[str] = []
    for entity_id in ordered:
        if entity_id.startswith("media_player.") and entity_id not in result:
            result.append(entity_id)
    return result
