"""Random Chime Set storage and selection helpers."""

from __future__ import annotations

import random
from typing import Any

from .const import CHIME_SET_PREFIX, CHIME_SETS_KEY


def set_reference(set_name: str) -> str:
    """Return the service/YAML value used to reference a Random Chime Set."""
    return str(set_name).strip()


def set_id_from_reference(value: str | None) -> str | None:
    """Return a set ID from a Random Chime Set reference, if it is one."""
    if not isinstance(value, str) or not value.startswith(CHIME_SET_PREFIX):
        return None
    set_id = value.removeprefix(CHIME_SET_PREFIX).strip()
    return set_id or None


def normalize_sets(value: Any) -> list[dict[str, Any]]:
    """Normalize persisted sets while retaining only safe, useful values."""
    if not isinstance(value, list):
        return []

    normalized: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for item in value:
        if not isinstance(item, dict):
            continue
        set_id = str(item.get("id", "")).strip()
        name = str(item.get("name", "")).strip()
        members = item.get("chimes", [])
        if not set_id or not name or set_id in seen_ids or not isinstance(members, list):
            continue
        chimes = [str(member).strip() for member in members if str(member).strip()]
        if not chimes:
            continue
        offsets: dict[str, int] = {}
        if isinstance(item.get("offsets"), dict):
            for member, offset in item["offsets"].items():
                try:
                    offsets[str(member).strip()] = int(offset)
                except (TypeError, ValueError):
                    continue
        seen_ids.add(set_id)
        normalized.append({"id": set_id, "name": name, "chimes": chimes, "offsets": offsets})
    return normalized


def get_set(data: dict[str, Any], set_id: str) -> dict[str, Any] | None:
    """Find one set in integration data."""
    for chime_set in normalize_sets(data.get(CHIME_SETS_KEY)):
        if chime_set["id"] == set_id:
            return chime_set
    return None


def get_set_by_reference(data: dict[str, Any], reference: str | None) -> dict[str, Any] | None:
    """Find a set by its displayed name or its legacy ID reference."""
    legacy_set_id = set_id_from_reference(reference)
    if legacy_set_id:
        return get_set(data, legacy_set_id)
    if not isinstance(reference, str):
        return None
    normalized_reference = reference.strip().casefold()
    if not normalized_reference:
        return None
    return next(
        (
            chime_set
            for chime_set in normalize_sets(data.get(CHIME_SETS_KEY))
            if chime_set["name"].casefold() == normalized_reference
        ),
        None,
    )


def is_set_reference(data: dict[str, Any], reference: str | None) -> bool:
    """Return whether a value resolves to a configured Chime Set."""
    return get_set_by_reference(data, reference) is not None


def selector_options(data: dict[str, Any]) -> list[dict[str, str]]:
    """Build labelled dropdown options for all saved sets."""
    return [
        {"label": f"🎲 {chime_set['name']}", "value": set_reference(chime_set["name"])}
        for chime_set in normalize_sets(data.get(CHIME_SETS_KEY))
    ]


def choose_member(
    data: dict[str, Any],
    reference: str,
    last_choices: dict[str, str],
    *,
    excluded: set[str] | None = None,
) -> str | None:
    """Choose a member, avoiding the previous successful choice where possible."""
    chime_set = get_set_by_reference(data, reference)
    if chime_set is None:
        return None
    set_id = chime_set["id"]
    members = [member for member in chime_set["chimes"] if member not in (excluded or set())]
    if not members:
        return None
    previous = last_choices.get(set_id)
    candidates = [member for member in members if member != previous] or members
    return random.choice(candidates)


def member_offset(data: dict[str, Any], reference: str, member: str) -> int | None:
    """Return a selected member's offset, if the set defines one."""
    chime_set = get_set_by_reference(data, reference)
    if chime_set is None:
        return None
    return chime_set.get("offsets", {}).get(member)
