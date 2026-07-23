"""Regression tests, one per fixed GitHub issue.

Each fix lands with a test named `test_issue_<number>` that fails against the
unfixed code and passes after the fix.
"""

from pathlib import Path

import yaml

from custom_components.chime_tts.const import GOOGLE_CLOUD, NABU_CASA_CLOUD_TTS
from custom_components.chime_tts.helpers.helpers import ChimeTTSHelper
from custom_components.chime_tts.helpers.media_player_helper import MediaPlayerHelper
from custom_components.chime_tts.helpers.services_helper import ChimeTTSServicesHelper
from custom_components.chime_tts.helpers.tts_audio_helper import TTSAudioHelper


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


def test_configured_playback_scripts_apply_only_when_service_omits_them():
    """Configured scripts provide defaults while explicit service values win."""
    from custom_components.chime_tts import apply_configured_script_defaults
    from custom_components.chime_tts.const import (
        DEFAULT_POST_SCRIPT_KEY,
        DEFAULT_PRE_SCRIPT_KEY,
    )

    defaults = {
        DEFAULT_PRE_SCRIPT_KEY: "script.prepare_speakers",
        DEFAULT_POST_SCRIPT_KEY: "script.restore_speakers",
    }
    assert apply_configured_script_defaults({"message": "Hello"}, defaults) == {
        "message": "Hello",
        "pre_script": "script.prepare_speakers",
        "post_script": "script.restore_speakers",
    }
    assert apply_configured_script_defaults(
        {"pre_script": "script.custom_prepare", "post_script": ""}, defaults
    ) == {"pre_script": "script.custom_prepare", "post_script": ""}


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


def test_services_yaml_exposes_scripts_only_for_say_action():
    """Scripts are playback-only and must not be accepted by say_url."""
    from custom_components.chime_tts.settings import _load_services_yaml

    services_yaml = _load_services_yaml()

    say_fields = services_yaml["say"]["fields"]
    say_url_fields = services_yaml["say_url"]["fields"]
    assert "pre_script" in say_fields
    assert "post_script" in say_fields
    assert "pre_script" not in say_url_fields
    assert "post_script" not in say_url_fields


def test_panel_uploads_use_home_assistants_authenticated_fetch_helper():
    """Panel uploads must use HA's token-aware REST request helper."""
    panel_source = (
        Path(__file__).parents[1]
        / "custom_components"
        / "chime_tts"
        / "panel"
        / "chime-tts-panel.js"
    ).read_text(encoding="utf-8")

    assert "this._hass.fetchWithAuth(url, init)" in panel_source
    assert 'this._fetchPickerWithAuth("/api/chime_tts/browser/upload", {' in panel_source
    assert "this._fetchPickerWithAuth(normalizedUrl)" in panel_source
    assert "this._fetchPickerWithAuth(url)" in panel_source


def test_picker_stops_preview_before_delete_navigation_and_close():
    """Picker audio must not outlive the file or folder it belongs to."""
    panel_source = (
        Path(__file__).parents[1]
        / "custom_components"
        / "chime_tts"
        / "panel"
        / "chime-tts-panel.js"
    ).read_text(encoding="utf-8")

    delete_action = panel_source.index('} else if (this._pickerAction.mode === "delete") {')
    delete_command = panel_source.index('type: "chime_tts/browser_delete_entry",', delete_action)
    assert panel_source.index("this._stopPickerAudio();", delete_action) < delete_command

    close_picker = panel_source.index("  _closePicker() {")
    close_picker_end = panel_source.index("  async _loadPicker(", close_picker)
    assert "this._stopPickerAudio();" in panel_source[close_picker:close_picker_end]

    load_picker = panel_source.index("  async _loadPicker(")
    load_picker_end = panel_source.index("  _beginPickerLoadingDelay()", load_picker)
    assert "this._stopPickerAudio();" in panel_source[load_picker:load_picker_end]


def test_panel_prompts_before_discarding_unsaved_changes():
    """Reset and browser unload must not silently discard panel edits."""
    panel_source = (
        Path(__file__).parents[1]
        / "custom_components"
        / "chime_tts"
        / "panel"
        / "chime-tts-panel.js"
    ).read_text(encoding="utf-8")

    assert "_requestResetAllChanges()" in panel_source
    assert "_renderDiscardChangesConfirmation()" in panel_source
    assert "data-discard-changes-save" in panel_source
    assert "data-discard-changes-confirm" in panel_source
    assert 'window.addEventListener("beforeunload", this._boundBeforeUnload);' in panel_source
    assert "_handleBeforeUnload(event)" in panel_source
    assert 'document.addEventListener("click", this._boundNavigationClick, true);' in panel_source
    assert "_handleNavigationClick(event)" in panel_source
    assert "_navigateAfterDiscard(url)" in panel_source


def test_panel_title_displays_santa_hat_only_in_december():
    """The seasonal title decoration is limited to December and served by the panel."""
    root = Path(__file__).parents[1]
    panel_source = (
        root / "custom_components" / "chime_tts" / "panel" / "chime-tts-panel.js"
    ).read_text(encoding="utf-8")
    panel_backend = (
        root / "custom_components" / "chime_tts" / "helpers" / "panel.py"
    ).read_text(encoding="utf-8")

    assert "new Date().getMonth() === 11" in panel_source
    assert "const SANTA_HAT_SVG = `" in panel_source
    assert '<svg xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"' in panel_source
    assert 'id="path1309"' in panel_source
    assert "topbar-santa-hat" in panel_source
    assert "filter: drop-shadow(0 0 1px #000);" in panel_source
    assert "PANEL_SANTA_HAT_URL" not in panel_backend
    assert "ChimeTTSPanelSantaHatView" not in panel_backend


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


def test_installed_tts_platforms_include_legacy_provider_ids():
    """YAML-configured TTS providers remain selectable without tts entities."""
    helper = ChimeTTSHelper()
    hass = _FakeHass()
    hass.data["tts_manager"] = type(
        "TTSManager", (), {"providers": {"test_support_tts": object()}}
    )()

    assert helper.get_installed_tts_platforms(hass) == ["test_support_tts"]
    assert helper.get_tts_platform(hass, tts_platform="test_support_tts") == (
        "test_support_tts"
    )


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


def test_unavailable_explicit_provider_falls_back_to_configured_default():
    """An unavailable explicit provider should fall back to the configured default."""
    helper = ChimeTTSHelper()
    hass = _FakeHass(entity_ids=["tts.pico_tts_en_us"])
    assert (
        helper.get_tts_platform(
            hass,
            tts_platform="tts.google_translate_en_com",
            default_tts_platform="tts.pico_tts_en_us",
            fallback_tts_platform="tts.some_other_provider",
        )
        == "tts.pico_tts_en_us"
    )


def test_unavailable_explicit_provider_falls_back_to_configured_fallback():
    """An unavailable explicit/default provider should fall back to the configured fallback."""
    helper = ChimeTTSHelper()
    hass = _FakeHass(entity_ids=["tts.pico_tts_en_us"])
    assert (
        helper.get_tts_platform(
            hass,
            tts_platform="tts.google_translate_en_com",
            default_tts_platform="tts.missing_default",
            fallback_tts_platform="tts.pico_tts_en_us",
        )
        == "tts.pico_tts_en_us"
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


def test_issue_275_sonos_explicit_volume_set_call():
    """Sonos gets an explicit volume_set at the target level before the announce (#275, #256)."""
    from custom_components.chime_tts import _sonos_volume_set_call

    call = _sonos_volume_set_call("media_player.kitchen", 50)
    assert call["service"] == "volume_set"
    assert call["service_data"]["volume_level"] == 0.5
    # out-of-range percentages are clamped to a valid 0.0-1.0 level
    assert _sonos_volume_set_call("x", 150)["service_data"]["volume_level"] == 1.0
    assert _sonos_volume_set_call("x", -5)["service_data"]["volume_level"] == 0.0


def test_media_content_id_missing_path_returns_none():
    helper = MediaPlayerHelper()
    hass = _FakeMediaHass({"media": "/media"})
    assert helper.get_media_content_id(hass, "") is None


def test_issue_210_google_cloud_language_preserved():
    """Google Cloud keeps the requested language instead of discarding it (#210)."""
    helper = TTSAudioHelper()
    assert helper._adjust_language_and_voice(GOOGLE_CLOUD, "nl-BE", {}) == "nl-BE"


def test_issue_242_cloud_language_moved_out_of_options():
    """Cloud TTS gets language as an argument, not in options (#242)."""
    helper = TTSAudioHelper()
    options = {"language": "de"}
    result = helper._adjust_language_and_voice(NABU_CASA_CLOUD_TTS, "", options)
    assert result == "de"
    assert "language" not in options


def test_issue_307_styled_cloud_voice_resolves_language():
    """A styled cloud voice (name||style) resolves the same language as the plain voice (#307)."""
    from hass_nabucasa import voice as nabu_voices

    _lang, voices = next(iter(nabu_voices.TTS_VOICES.items()))
    # The voice collection is a list on older HA and a dict (name -> label) on
    # newer HA; take the first voice name either way.
    first_voice = next(iter(voices))
    helper = TTSAudioHelper()
    styled = helper._adjust_language_and_voice(
        NABU_CASA_CLOUD_TTS, "", {"voice": f"{first_voice}||whispering"}
    )
    plain = helper._adjust_language_and_voice(
        NABU_CASA_CLOUD_TTS, "", {"voice": first_voice}
    )
    assert styled is not None
    assert styled == plain


def test_cloud_entity_id_form_language_handled():
    """Nabu cloud as a full entity id still gets language moved out of options."""
    helper = TTSAudioHelper()
    options = {"language": "fr"}
    result = helper._adjust_language_and_voice("tts.home_assistant_cloud", "", options)
    assert result == "fr"
    assert "language" not in options


def test_non_string_voice_does_not_crash_cloud_language_lookup():
    """A non-string voice must not raise in the cloud language lookup."""
    helper = TTSAudioHelper()
    # Should simply skip the lookup and return None, not raise AttributeError.
    assert (
        helper._adjust_language_and_voice(NABU_CASA_CLOUD_TTS, "", {"voice": 123})
        is None
    )


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
def test_issue_232_tts_timeout_clamped_to_leave_room_for_fallback():
    """The per-platform TTS timeout leaves room for a fallback within the queue timeout (#232)."""
    from custom_components.chime_tts.helpers.tts_audio_helper import (
        _clamped_tts_timeout,
    )

    # With a pending fallback, a 30s primary under a 60s queue is capped so both fit.
    assert _clamped_tts_timeout(30, 60, True) == 29
    # A timeout already under the cap is unchanged.
    assert _clamped_tts_timeout(10, 60, True) == 10
    # Never drops below 1 second.
    assert _clamped_tts_timeout(30, 1, True) == 1
    # With no pending fallback, the full timeout is kept (not halved).
    assert _clamped_tts_timeout(30, 60, False) == 30
    assert _clamped_tts_timeout(55, 60, False) == 55


def test_issue_282_cache_hit_does_not_reapply_baked_in_filter():
    """A cached file's conversion is not re-applied on a cache hit (#282, #280)."""
    from custom_components.chime_tts import _should_reapply_conversion_on_cache_hit
    from custom_components.chime_tts.const import FFMPEG_ARGS_ALEXA

    # A volume-boost filter is already baked into the cached file; never re-apply.
    assert _should_reapply_conversion_on_cache_hit("-af volume=1.5", True) is False
    assert _should_reapply_conversion_on_cache_hit("-af volume=1.5", False) is False
    # Alexa is the only case that back-fills, and only when not yet compatible.
    assert _should_reapply_conversion_on_cache_hit(FFMPEG_ARGS_ALEXA, False) is True
    assert _should_reapply_conversion_on_cache_hit(FFMPEG_ARGS_ALEXA, True) is False


def test_issue_282_conversion_is_part_of_cache_key():
    """Different audio conversions produce different cache keys (#282, #280).

    The conversion is parsed into the params under "ffmpeg_args", so a cache
    entry must be unique per conversion; otherwise skipping re-application on a
    cache hit would serve the wrong conversion.
    """
    from custom_components.chime_tts import get_filename_hash_from_service_data

    base = {"message": "hi"}
    boost = get_filename_hash_from_service_data(
        {**base, "ffmpeg_args": "-af volume=1.5"}, {}
    )
    quiet = get_filename_hash_from_service_data(
        {**base, "ffmpeg_args": "-af volume=0.5"}, {}
    )
    plain = get_filename_hash_from_service_data(base, {})
    assert boost != quiet
    assert boost != plain

def test_issue_314_repeat_is_part_of_cache_key():
    """Different repeat counts produce different cache keys (#314)."""
    from custom_components.chime_tts import get_filename_hash_from_service_data

    base = {"message": "hi"}
    assert get_filename_hash_from_service_data(
        base, {}
    ) != get_filename_hash_from_service_data({**base, "repeat": 3}, {})
    assert get_filename_hash_from_service_data(
        {**base, "repeat": 2}, {}
    ) != get_filename_hash_from_service_data({**base, "repeat": 3}, {})


async def test_issue_310_runs_configured_script_before_after_tts():
    """Configured scripts accept an entity ID or YAML with script variables (#310)."""
    from custom_components.chime_tts import async_run_script

    calls = []

    class _Services:
        async def async_call(self, domain, service, **kwargs):
            calls.append((domain, service, kwargs.get("service_data", {})))

    class _Hass:
        services = _Services()

    hass = _Hass()
    await async_run_script(hass, "script.front_door")
    assert ("script", "front_door", {}) in calls

    await async_run_script(
        hass,
        """script: script.front_door
data:
  volume: 0.5
  announcement: Welcome home
""",
    )
    assert ("script", "front_door", {"volume": 0.5, "announcement": "Welcome home"}) in calls

    # A non-script entity is ignored, and None is a no-op.
    calls.clear()
    await async_run_script(hass, "light.kitchen")
    await async_run_script(hass, None)
    assert calls == []
