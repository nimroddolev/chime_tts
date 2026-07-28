"""Tests for persisted Random Chime Set normalization and selection."""

from __future__ import annotations

from custom_components.chime_tts.chime_sets import choose_member
from custom_components.chime_tts.chime_sets import get_set
from custom_components.chime_tts.chime_sets import get_set_by_reference
from custom_components.chime_tts.chime_sets import is_set_reference
from custom_components.chime_tts.chime_sets import member_offset
from custom_components.chime_tts.chime_sets import normalize_sets
from custom_components.chime_tts.chime_sets import selector_options
from custom_components.chime_tts.chime_sets import set_id_from_reference
from custom_components.chime_tts.chime_sets import set_reference
from custom_components.chime_tts.const import CHIME_SETS_KEY


VALID_SET = {
    "id": "morning",
    "name": "Morning",
    "chimes": [" first.mp3 ", "second.mp3", ""],
    "offsets": {"first.mp3": "4", "bad": "not-a-number"},
}


def test_normalize_sets_discards_invalid_values_and_normalizes_members() -> None:
    """Only complete, unique chime sets with usable members are retained."""
    assert normalize_sets(None) == []
    assert normalize_sets(
        [
            None,
            {},
            {"id": "x", "name": "X", "chimes": "no"},
            {"id": "empty", "name": "Empty", "chimes": [""]},
            {"id": "no-offsets", "name": "No offsets", "chimes": ["a"]},
            VALID_SET,
            VALID_SET,
        ]
    ) == [
        {"id": "no-offsets", "name": "No offsets", "chimes": ["a"], "offsets": {}},
        {
            "id": "morning",
            "name": "Morning",
            "chimes": ["first.mp3", "second.mp3"],
            "offsets": {"first.mp3": 4},
        },
    ]


def test_set_references_lookup_options_and_offsets() -> None:
    """Names and legacy references resolve to the same saved set."""
    data = {CHIME_SETS_KEY: [VALID_SET]}
    assert set_reference("  Morning ") == "Morning"
    assert set_id_from_reference("chime_set: morning") == "morning"
    assert set_id_from_reference("Morning") is None
    assert set_id_from_reference(None) is None
    assert get_set(data, "missing") is None
    assert get_set_by_reference(data, " MORNING ")["id"] == "morning"
    assert get_set_by_reference(data, "chime_set: morning")["name"] == "Morning"
    assert get_set_by_reference(data, "") is None
    assert get_set_by_reference(data, None) is None
    assert is_set_reference(data, "Morning") is True
    assert selector_options(data) == [{"label": "🎲 Morning", "value": "Morning"}]
    assert member_offset(data, "Morning", "first.mp3") == 4
    assert member_offset(data, "unknown", "first.mp3") is None


def test_choose_member_respects_exclusions_and_avoids_last_choice(monkeypatch) -> None:
    """Selection avoids exclusions and a previous choice whenever possible."""
    data = {CHIME_SETS_KEY: [VALID_SET]}
    monkeypatch.setattr(
        "custom_components.chime_tts.chime_sets.random.choice",
        lambda choices: choices[0],
    )
    assert choose_member(data, "Morning", {"morning": "first.mp3"}) == "second.mp3"
    assert (
        choose_member(data, "Morning", {}, excluded={"first.mp3", "second.mp3"}) is None
    )
    assert choose_member(data, "missing", {}) is None
