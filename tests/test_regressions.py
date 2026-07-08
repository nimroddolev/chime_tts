"""Regression tests, one per fixed GitHub issue.

Each fix lands with a test named `test_issue_<number>` that fails against the
unfixed code and passes after the fix.
"""

import yaml

from custom_components.chime_tts.helpers.helpers import ChimeTTSHelper
from custom_components.chime_tts.helpers.media_player_helper import MediaPlayerHelper
from custom_components.chime_tts.helpers.services_helper import ChimeTTSServicesHelper


class _FakeConfig:
    def __init__(self, media_dirs):
        self.media_dirs = media_dirs


class _FakeMediaHass:
    def __init__(self, media_dirs):
        self.config = _FakeConfig(media_dirs)


class _FakeState:
    def __init__(self, entity_id):
        self.entity_id = entity_id


class _FakeStates:
    def __init__(self, entity_ids):
        self._entity_ids = entity_ids

    def async_all(self, *args):
        return [_FakeState(i) for i in self._entity_ids]


class _FakeServices:
    def __init__(self, services=()):
        self._services = set(services)

    def has_service(self, domain, service):
        return f"{domain}.{service}" in self._services


class _FakeHass:
    def __init__(self, entity_ids=(), services=()):
        self.states = _FakeStates(list(entity_ids))
        self.services = _FakeServices(services)
        self.data = {}


def test_issue_294_build_chime_options_coerces_values_to_str():
    """Numeric/boolean-looking chime names stay strings so services.yaml parses (#294)."""
    custom = [
        {"label": "060", "value": "/config/chimes/060.mp3"},
        {"label": 12, "value": 12},  # adversarial non-str entry
        {"label": "yes", "value": "yes"},
        {"value": "/missing/label.mp3"},  # malformed: no label, dropped
        {"label": "no-value", "value": None},  # None value, dropped (not "None")
        "not-a-dict",  # malformed, dropped
    ]
    options = ChimeTTSServicesHelper._build_chime_options(custom)

    assert options
    for option in options:
        assert isinstance(option["label"], str)
        assert isinstance(option["value"], str)

    values = [o["value"] for o in options]
    labels = [o["label"] for o in options]
    assert "12" in values, "int value should be coerced to str"
    assert "/missing/label.mp3" not in values, "entry without a label should be dropped"
    assert "no-value" not in labels, "entry with a None value should be dropped"
    assert "None" not in values, "None must not be coerced to the string 'None'"


def test_issue_294_round_trips_through_yaml_as_str():
    """Options survive a YAML dump/load with their values intact as str (#294)."""
    options = ChimeTTSServicesHelper._build_chime_options(
        [
            {"label": "060", "value": "/m/060.mp3"},
            {"label": "on", "value": "on"},
            {"label": "3.5", "value": "3.5"},
        ]
    )
    reloaded = yaml.safe_load(yaml.safe_dump({"options": options}))["options"]
    for option in reloaded:
        assert isinstance(option["label"], str)
        assert isinstance(option["value"], str)


def test_issue_294_stale_structure_returns_none_not_crash():
    """A services.yaml missing the expected nesting yields None rather than raising (#294)."""
    assert ChimeTTSServicesHelper._get_field_options({}, "say", "chime_path") is None
    assert (
        ChimeTTSServicesHelper._get_field_options(
            {"say": {"fields": {"chime_path": {"selector": {}}}}}, "say", "chime_path"
        )
        is None
    )


def test_issue_291_full_entity_id_matches_installed():
    """A full tts.* entity id selects that entity instead of being rejected (#291)."""
    helper = ChimeTTSHelper()
    hass = _FakeHass(entity_ids=["tts.piper", "tts.home_assistant_cloud"])
    assert helper.get_tts_platform(hass, tts_platform="tts.piper") == "tts.piper"
    # a bare provider name resolves to the matching entity too
    assert helper.get_tts_platform(hass, tts_platform="piper") == "tts.piper"


def test_issue_308_gemini_not_diverted_to_google_translate():
    """A Google Generative AI entity is selected, not swapped for Google Translate (#308)."""
    helper = ChimeTTSHelper()
    hass = _FakeHass(
        entity_ids=["tts.google_generative_ai_01jabc", "tts.google_translate_en_com"]
    )
    selected = helper.get_tts_platform(
        hass, tts_platform="tts.google_generative_ai_01jabc"
    )
    assert selected == "tts.google_generative_ai_01jabc"


def test_issue_241_installed_list_keeps_full_entity_ids():
    """Installed platforms keep full entity ids rather than first-token truncation (#241)."""
    helper = ChimeTTSHelper()
    hass = _FakeHass(entity_ids=["tts.google_generative_ai_x", "tts.microsoft_edge"])
    installed = helper.get_installed_tts_platforms(hass)
    assert "tts.google_generative_ai_x" in installed
    assert "google" not in installed


def test_google_translate_fallback_for_unmatched_google_request():
    """An unmatched Google request still falls back to an installed Google entity."""
    helper = ChimeTTSHelper()
    hass = _FakeHass(entity_ids=["tts.google_translate_en_com"])
    selected = helper.get_tts_platform(hass, tts_platform="tts.google_cloud")
    assert selected == "tts.google_translate_en_com"


def test_ambiguous_google_name_does_not_pick_generative_ai():
    """A bare 'google' must not silently resolve to a generative-AI entity."""
    helper = ChimeTTSHelper()
    hass = _FakeHass(
        entity_ids=["tts.google_generative_ai_01jabc", "tts.google_translate_en_com"]
    )
    # Bare "google" prefixes both providers, so it is ambiguous and falls through
    # to the Google Translate fallback rather than matching generative AI.
    assert (
        helper.get_tts_platform(hass, tts_platform="google")
        == "tts.google_translate_en_com"
    )


def test_issue_253_media_content_id_keeps_full_relative_path():
    """The relative path is preserved exactly, not off-by-one (#253)."""
    helper = MediaPlayerHelper()
    hass = _FakeMediaHass({"media": "/media"})
    cid = helper.get_media_content_id(hass, "/media/sounds/doorbell.mp3")
    assert cid == "media-source://media_source/media/sounds/doorbell.mp3"


def test_issue_289_longest_media_dir_prefix_wins():
    """The directory with the longest matching path is chosen, regardless of its name (#289)."""
    helper = MediaPlayerHelper()
    # "n"'s short path would beat "media"'s longer path under the old
    # name-length-vs-path-length comparison.
    hass = _FakeMediaHass({"media": "/media/sub", "n": "/media"})
    cid = helper.get_media_content_id(hass, "/media/sub/chime.mp3")
    assert cid == "media-source://media_source/media/chime.mp3"


def test_issue_289_outside_media_dir_returns_none_not_garbage():
    """A file outside any media dir returns None instead of a corrupt id (#289)."""
    helper = MediaPlayerHelper()
    hass = _FakeMediaHass({"media": "/media"})
    assert helper.get_media_content_id(hass, "/config/www/chime.mp3") is None


def test_issue_289_sibling_prefix_directory_not_matched():
    """A dir /media must not claim a sibling path like /media-other (#289)."""
    helper = MediaPlayerHelper()
    hass = _FakeMediaHass({"media": "/media"})
    assert helper.get_media_content_id(hass, "/media-other/chime.mp3") is None


def test_media_content_id_trailing_slash_media_dir():
    """A configured media dir with a trailing slash still resolves correctly."""
    helper = MediaPlayerHelper()
    hass = _FakeMediaHass({"media": "/media/"})
    cid = helper.get_media_content_id(hass, "/media/chime.mp3")
    assert cid == "media-source://media_source/media/chime.mp3"


def test_media_content_id_missing_path_returns_none():
    helper = MediaPlayerHelper()
    hass = _FakeMediaHass({"media": "/media"})
    assert helper.get_media_content_id(hass, "") is None


class _ExecHass:
    """Minimal hass that runs executor jobs inline, for offload tests."""

    async def async_add_executor_job(self, func, *args):
        return func(*args)


async def test_issue_318_async_get_local_path_offloads(monkeypatch):
    """async_get_local_path runs get_local_path through the executor (#318, #258)."""
    from custom_components.chime_tts.helpers.filesystem import FilesystemHelper

    helper = FilesystemHelper()
    hass = _ExecHass()
    calls = {"n": 0}
    original = helper.get_local_path

    def _tracked(h, file_path=""):
        calls["n"] += 1
        return original(h, file_path)

    monkeypatch.setattr(helper, "get_local_path", _tracked)

    # An absolute path short-circuits inside get_local_path without blocking I/O.
    result = await helper.async_get_local_path(hass, "/media/chime.mp3")
    assert result == "/media/chime.mp3"
    assert calls["n"] == 1, "get_local_path should be invoked via the executor"
