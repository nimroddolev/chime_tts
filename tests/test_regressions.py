"""Regression tests, one per fixed GitHub issue.

Each fix lands with a test named `test_issue_<number>` that fails against the
unfixed code and passes after the fix.
"""

import asyncio
import importlib
from pathlib import Path
from unittest.mock import AsyncMock

import yaml

from custom_components.chime_tts.const import (
    GOOGLE_CLOUD,
    NABU_CASA_CLOUD_TTS,
    CHIME_OFFSETS_KEY,
    CHIME_SETS_KEY,
)
from custom_components.chime_tts.helpers.helpers import ChimeTTSHelper
from custom_components.chime_tts.helpers.media_player_helper import MediaPlayerHelper
from custom_components.chime_tts.helpers.services_helper import ChimeTTSServicesHelper
from custom_components.chime_tts.helpers.tts_audio_helper import TTSAudioHelper
from custom_components.chime_tts.chime_sets import choose_member, selector_options, set_reference


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


def test_configured_action_defaults_apply_only_when_service_omits_them():
    """Configured chimes and scripts provide defaults while explicit values win."""
    from custom_components.chime_tts import apply_configured_action_defaults
    from custom_components.chime_tts.const import (
        DEFAULT_POST_SCRIPT_KEY,
        DEFAULT_PRE_SCRIPT_KEY,
    )

    defaults = {
        "chime_path": "bells",
        "end_chime_path": "tada",
        DEFAULT_PRE_SCRIPT_KEY: "script.prepare_speakers",
        DEFAULT_POST_SCRIPT_KEY: "script.restore_speakers",
    }
    assert apply_configured_action_defaults({"message": "Hello"}, defaults) == {
        "message": "Hello",
        "chime_path": "bells",
        "end_chime_path": "tada",
        "pre_script": "script.prepare_speakers",
        "post_script": "script.restore_speakers",
    }
    assert apply_configured_action_defaults(
        {
            "chime_path": "",
            "end_chime_path": "custom_end.mp3",
            "pre_script": "script.custom_prepare",
            "post_script": "",
        },
        defaults,
    ) == {
        "chime_path": "",
        "end_chime_path": "custom_end.mp3",
        "pre_script": "script.custom_prepare",
        "post_script": "",
    }


def test_configured_say_url_scripts_can_be_action_specific():
    """say_url uses its own defaults only when script sharing is disabled."""
    from custom_components.chime_tts import apply_configured_action_defaults
    from custom_components.chime_tts.const import (
        DEFAULT_POST_SCRIPT_KEY,
        DEFAULT_POST_SCRIPT_SAY_URL_KEY,
        DEFAULT_POST_SCRIPT_SHARED_KEY,
        DEFAULT_PRE_SCRIPT_KEY,
        DEFAULT_PRE_SCRIPT_SAY_URL_KEY,
        DEFAULT_PRE_SCRIPT_SHARED_KEY,
    )

    defaults = {
        DEFAULT_PRE_SCRIPT_KEY: "script.say_pre",
        DEFAULT_POST_SCRIPT_KEY: "script.say_post",
        DEFAULT_PRE_SCRIPT_SHARED_KEY: False,
        DEFAULT_POST_SCRIPT_SHARED_KEY: False,
        DEFAULT_PRE_SCRIPT_SAY_URL_KEY: "script.url_pre",
        DEFAULT_POST_SCRIPT_SAY_URL_KEY: "script.url_post",
    }
    assert apply_configured_action_defaults({}, defaults, is_say_url=True) == {
        "pre_script": "script.url_pre",
        "post_script": "script.url_post",
    }
    defaults[DEFAULT_PRE_SCRIPT_SHARED_KEY] = True
    assert apply_configured_action_defaults({}, defaults, is_say_url=True) == {
        "pre_script": "script.say_pre",
        "post_script": "script.url_post",
    }


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


def test_chime_sets_use_stable_references_and_avoid_immediate_repeats(monkeypatch):
    """A set's picker should exclude its last successful chime when possible."""
    data = {
       CHIME_SETS_KEY: [
            {"id": "door", "name": "Doorbell", "chimes": ["bells", "ding_dong"]}
        ]
    }
    reference = set_reference("Doorbell")
    assert selector_options(data) == [{"label": "🎲 Doorbell", "value": reference}]

    monkeypatch.setattr("custom_components.chime_tts.chime_sets.random.choice", lambda items: items[0])
    history = {"door": "bells"}
    assert choose_member(data, reference, history) == "ding_dong"


def test_chime_set_options_are_exposed_to_service_selectors():
    """Service YAML selectors include saved sets alongside individual chimes."""
    helper = ChimeTTSServicesHelper()
    helper._data = {
       CHIME_SETS_KEY: [
            {"id": "alerts", "name": "Alerts", "chimes": ["bells"]}
        ]
    }
    assert {"label": "🎲 Alerts", "value": "Alerts"} in helper._build_chime_options([], helper._data)


def test_chime_set_names_resolve_for_preview_and_playback():
    """A named Chime Set resolves to a member and retains its member offset."""
    from custom_components.chime_tts.helpers.filesystem import FilesystemHelper

    class _ChimeSetFilesystemHelper(FilesystemHelper):
        async def async_get_chime_path(self, chime_path, cache, data, hass):
            if chime_path == "Doorbell":
                return await super().async_get_chime_path(chime_path, cache, data, hass)
            assert chime_path in {"bells", "soft"}
            return f"/tmp/{chime_path}.mp3"

    data = {
        CHIME_SETS_KEY: [
            {
                "id": "door",
                "name": "Doorbell",
                "chimes": ["bells"],
                "offsets": {"bells": 250},
            },
            {"id": "quiet", "name": "Quiet", "chimes": ["soft"]},
        ],
        CHIME_OFFSETS_KEY: {"soft": -540},
    }
    helper = _ChimeSetFilesystemHelper()

    preview_path = asyncio.run(helper.async_get_chime_path("Doorbell", False, data, None))
    playback_path, offset = asyncio.run(
        helper.async_get_chime_path_with_offset("Doorbell", False, data, None)
    )
    soft_path, soft_offset = asyncio.run(
        helper.async_get_chime_path_with_offset("Quiet", False, data, None)
    )

    assert preview_path == "/tmp/bells.mp3"
    assert playback_path == "/tmp/bells.mp3"
    assert offset == 250
    assert soft_path == "/tmp/soft.mp3"
    assert soft_offset == -540


def test_named_chime_set_member_is_used_for_cache_lookup(monkeypatch):
    """Cache lookup uses the selected member, not the Chime Set reference."""
    from custom_components.chime_tts.const import CROSSFADE_KEY, OFFSET_KEY

    integration_module = importlib.import_module("custom_components.chime_tts.__init__")

    resolved_paths = AsyncMock(side_effect=[("bells", None), (None, None)])
    cache_lookup = AsyncMock(return_value={"cached": True})
    monkeypatch.setattr(
        integration_module.filesystem_helper,
        "async_get_chime_path_with_offset",
        resolved_paths,
    )
    monkeypatch.setattr(integration_module, "async_verify_cached_audio", cache_lookup)
    monkeypatch.setattr(
        integration_module.media_player_helper,
        "get_alexa_media_players_count",
        lambda: 0,
    )
    monkeypatch.setattr(integration_module, "_data", {OFFSET_KEY: 0, CROSSFADE_KEY: 0})

    params = {
        "hass": object(),
        "message": "Hello",
        "chime_path": "Doorbell",
        "cache": True,
        "entity_ids": ["media_player.office"],
    }
    assert asyncio.run(integration_module.async_get_playback_audio_path(params, {})) == {"cached": True}

    cache_args = cache_lookup.await_args.args
    assert params["chime_path"] == "bells"
    assert cache_args[2]["chime_path"] == "bells"
    assert cache_args[1] == integration_module.get_filename_hash_from_service_data(params, {})
    assert cache_args[1] != integration_module.get_filename_hash_from_service_data(
        {**params, "chime_path": "Doorbell"},
        {},
    )


def test_saved_chime_offset_is_used_unless_an_action_supplies_one(monkeypatch):
    """Chime-list offsets affect start chimes but explicit action values win."""
    from custom_components.chime_tts.const import CROSSFADE_KEY, OFFSET_KEY

    integration_module = importlib.import_module("custom_components.chime_tts.__init__")
    resolved_paths = AsyncMock(side_effect=[("bells", None), (None, None), ("bells", None), (None, None)])
    monkeypatch.setattr(integration_module.filesystem_helper, "async_get_chime_path_with_offset", resolved_paths)
    monkeypatch.setattr(integration_module, "async_verify_cached_audio", AsyncMock(return_value={"cached": True}))
    monkeypatch.setattr(integration_module.media_player_helper, "get_alexa_media_players_count", lambda: 0)
    monkeypatch.setattr(integration_module, "_data", {OFFSET_KEY: 0, CROSSFADE_KEY: 0, CHIME_OFFSETS_KEY: {"bells": 175}})

    default_params = {"hass": object(), "message": "Hello", "chime_path": "bells", "cache": True, "entity_ids": ["media_player.office"]}
    assert asyncio.run(integration_module.async_get_playback_audio_path(default_params, {})) == {"cached": True}
    assert default_params["offset"] == 175

    explicit_params = {"hass": object(), "message": "Hello", "chime_path": "bells", "offset": 0, "_offset_explicit": True, "cache": True, "entity_ids": ["media_player.office"]}
    assert asyncio.run(integration_module.async_get_playback_audio_path(explicit_params, {})) == {"cached": True}
    assert explicit_params["offset"] == 0


def test_chime_set_member_offset_is_used_by_shared_say_audio_pipeline(monkeypatch):
    """Both say variants use the selected Chime Set member's effective offset."""
    from custom_components.chime_tts.const import CROSSFADE_KEY, OFFSET_KEY

    integration_module = importlib.import_module("custom_components.chime_tts.__init__")
    monkeypatch.setattr(
        integration_module.filesystem_helper,
        "async_get_chime_path_with_offset",
        AsyncMock(side_effect=[("soft", -540), (None, None), ("soft", -540), (None, None)]),
    )
    monkeypatch.setattr(
        integration_module,
        "async_verify_cached_audio",
        AsyncMock(return_value={"cached": True}),
    )
    monkeypatch.setattr(
        integration_module.media_player_helper,
        "get_alexa_media_players_count",
        lambda: 0,
    )
    monkeypatch.setattr(
        integration_module,
        "_data",
        {OFFSET_KEY: 0, CROSSFADE_KEY: 0, CHIME_OFFSETS_KEY: {"soft": -540}},
    )

    for service_name in ("say", "say_url"):
        params = {
            "hass": object(),
            "message": "Hello",
            "chime_path": "Quiet Set",
            "cache": True,
            "entity_ids": ["media_player.office"],
        }
        assert asyncio.run(integration_module.async_get_playback_audio_path(params, {})) == {"cached": True}
        assert params["chime_path"] == "soft", service_name
        assert params["offset"] == -540, service_name


def test_issue_294_stale_structure_returns_none_not_crash():
    """A services.yaml missing the expected nesting yields None rather than raising (#294)."""
    assert not isinstance(
        ChimeTTSServicesHelper._get_field_options({}, "say", "chime_path"), list
    )
    assert not isinstance(
        ChimeTTSServicesHelper._get_field_options(
            {"say": {"fields": {"chime_path": {"selector": {}}}}}, "say", "chime_path"
        ),
        list,
    )


def test_services_yaml_exposes_scripts_for_both_say_actions():
    """Both actions expose pre- and post-script service fields."""
    from custom_components.chime_tts.settings import _load_services_yaml

    services_yaml = _load_services_yaml()

    say_fields = services_yaml["say"]["fields"]
    say_url_fields = services_yaml["say_url"]["fields"]
    assert "pre_script" in say_fields
    assert "post_script" in say_fields
    assert "pre_script" in say_url_fields
    assert "post_script" in say_url_fields


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


def test_panel_chapter_titles_use_shared_imported_icons():
    """Top-level panel chapters should use one shared SVG module."""
    root = Path(__file__).parents[1]
    panel_source = (
        root / "custom_components" / "chime_tts" / "panel" / "chime-tts-panel.js"
    ).read_text(encoding="utf-8")
    chapter_icons_source = (
        root / "custom_components" / "chime_tts" / "panel" / "chapter-icons.js"
    ).read_text(encoding="utf-8")
    panel_backend = (
        root / "custom_components" / "chime_tts" / "helpers" / "panel.py"
    ).read_text(encoding="utf-8")

    assert 'import { CHAPTER_ICONS } from "./chapter-icons.js";' in panel_source
    assert 'class="chapter-hero-icon"' in panel_source
    assert ".chime-sets-workspace .chapter-hero-icon" in panel_source
    assert "width: 2.15rem;" in panel_source
    assert "export const CHAPTER_ICONS" in chapter_icons_source
    for chapter in ("configuration", "chimes", "chime_sets", "notify_profiles", "logs", "about"):
        assert f"{chapter}:" in chapter_icons_source
    assert "PANEL_CHAPTER_ICONS_URL" in panel_backend
    assert "ChimeTTSChapterIconsView" in panel_backend
    assert "ChimeTTSChimeSectionIconView" in panel_backend
    assert 'class="chime-section-icon"' in chapter_icons_source
    assert 'mask: url("/api/chime_tts/images/option_icons/chime_section.svg")' in panel_source
    assert '<svg viewBox="0 0 150 150" fill="currentColor" aria-hidden="true"' in chapter_icons_source
    assert 'stroke="currentColor" stroke-width="1.37"' in chapter_icons_source


def test_random_chime_set_name_editor_keeps_actions_in_one_row():
    """Editing a Chime Set name must leave space for its action buttons."""
    panel_source = (
        Path(__file__).parents[1]
        / "custom_components"
        / "chime_tts"
        / "panel"
        / "chime-tts-panel.js"
    ).read_text(encoding="utf-8")

    assert ".random-chime-set-card .notify-profile-header" in panel_source
    assert "flex-wrap: nowrap;" in panel_source
    assert ".random-chime-set-card .notify-profile-title-edit" in panel_source
    assert "flex: 1 1 0;" in panel_source


def test_chime_set_offset_editor_has_preview_and_timing_guards():
    """The visual offset editor keeps preview, reset, and timing safeguards intact."""
    root = Path(__file__).parents[1]
    panel_source = (
        root / "custom_components" / "chime_tts" / "panel" / "chime-tts-panel.js"
    ).read_text(encoding="utf-8")
    panel_backend = (
        root / "custom_components" / "chime_tts" / "helpers" / "panel.py"
    ).read_text(encoding="utf-8")

    assert 'PANEL_CHIME_SET_OFFSET_PREVIEW_URL = f"/api/{DOMAIN}/chime_set_offset_preview"' in panel_backend
    assert "ChimeTTSPanelChimeSetOffsetPreviewView" in panel_backend
    assert "tts_audio.mp3" in panel_backend
    assert "Chime Offset" in panel_source
    assert "data-chime-set-offset-preview" in panel_source
    assert "data-chime-set-offset-reset" in panel_source
    assert "data-chime-set-offset-close" in panel_source
    assert "data-chime-set-offset-value" in panel_source
    assert "data-chime-set-offset-input" in panel_source
    assert "Enter a whole number of milliseconds." in panel_source
    assert "Chime Offset: ${offsetValue}" in panel_source
    assert 'changed ? "Done"' in panel_source
    assert 'const valueInput = this.shadowRoot.querySelector("[data-chime-set-offset-input]");' in panel_source
    assert "valueInput.value = editorValue;" in panel_source
    assert "valueInput.defaultValue = editorValue;" in panel_source
    assert 'this._setChimeSetOffsetEditorValue(offset, { syncInput: false });' in panel_source
    assert '<p class="chime-set-offset-title-hint">Drag either audio block.</p>' in panel_source
    assert ".chime-set-offset-title-hint {" in panel_source
    assert "data-chime-set-offset-status" not in panel_source
    assert 'this._saveChimeSetOffset();' in panel_source
    assert "data-chime-set-offset-save" not in panel_source
    assert "chime-set-offset-playback-head" in panel_source
    assert "chime-set-offset-overlap-line" in panel_source
    assert "Math.max(-chimeDuration, requestedOffset)" in panel_source
    assert "option.count >= 7 && option.count <= 10" in panel_source


def test_restart_with_unsaved_changes_uses_the_discard_confirmation():
    """Restart requests must offer Save or Discard before opening the restart dialog."""
    root = Path(__file__).parents[1]
    panel_source = (
        root / "custom_components" / "chime_tts" / "panel" / "chime-tts-panel.js"
    ).read_text(encoding="utf-8")

    assert "this._pendingRestartReason = restartReason;" in panel_source
    assert "this._discardChangesConfirmOpen = true;" in panel_source
    assert "this._resetAllChanges({ preserveRestart: Boolean(restartReason) });" in panel_source
    assert "this._openRestartConfirmation(restartReason);" in panel_source


def test_browser_refresh_with_unsaved_changes_requests_confirmation():
    """The beforeunload guard must trigger the browser's native confirmation."""
    root = Path(__file__).parents[1]
    panel_source = (
        root / "custom_components" / "chime_tts" / "panel" / "chime-tts-panel.js"
    ).read_text(encoding="utf-8")

    assert "event.returnValue = true;" in panel_source
    assert "return event.returnValue;" in panel_source


def test_notification_profile_structure_changes_rely_on_save_confirmation():
    """Saving profiles opens the existing restart confirmation without an inline banner."""
    root = Path(__file__).parents[1]
    panel_source = (
        root / "custom_components" / "chime_tts" / "panel" / "chime-tts-panel.js"
    ).read_text(encoding="utf-8")

    assert "notify-profiles-restart-banner" not in panel_source
    assert "Creating or deleting a Notification Profile takes effect" not in panel_source
    assert "this._restartConfirmOpen = this._restartPending;" in panel_source


def test_single_notify_field_reset_is_not_a_navigation_link():
    """Resetting one profile field must not be caught by the unsaved-navigation guard."""
    root = Path(__file__).parents[1]
    panel_source = (
        root / "custom_components" / "chime_tts" / "panel" / "chime-tts-panel.js"
    ).read_text(encoding="utf-8")

    assert 'type="button"\n                          class="field-reset-link"' in panel_source
    assert 'href="#"\n                          class="field-reset-link"' not in panel_source


def test_mobile_log_rows_wrap_actions_only_when_needed():
    """Mobile log actions share a row until the natural flex layout wraps."""
    root = Path(__file__).parents[1]
    panel_source = (
        root / "custom_components" / "chime_tts" / "panel" / "chime-tts-panel.js"
    ).read_text(encoding="utf-8")

    assert ":host([narrow]) .log-event-row-content {\n      display: flex;" in panel_source
    assert ":host([narrow]) .log-event-toggle-wrap {\n      align-self: start;" in panel_source
    assert ".log-event-row.actions-wrapped .log-event-actions {\n      flex: 0 0 100%;\n      width: 100%;\n      margin-left: 0;\n      justify-content: flex-start;" in panel_source
    assert 'row.classList.remove("actions-wrapped");\n      const wrapped = actions.offsetTop > main.offsetTop + 2;' in panel_source


def test_workspace_section_accents_follow_the_requested_color_order():
    """Section accents map Configuration to green, Chimes to blue, and Logs to orange."""
    root = Path(__file__).parents[1]
    panel_source = (
        root / "custom_components" / "chime_tts" / "panel" / "chime-tts-panel.js"
    ).read_text(encoding="utf-8")

    assert ".configuration-workspace .chapter-content { --workspace-accent: color-mix(in srgb, var(--configuration-accent) 82%, white 18%); }" in panel_source
    assert ".chimes-workspace .chapter-content { --workspace-accent: var(--primary-color); }" in panel_source
    assert ".logs-workspace .chapter-hero { --chapter-hero-copy-color: color-mix(in srgb, #f97316 86%, white 14%); }" in panel_source
    assert ".chime-sets-workspace .chapter-content { --workspace-accent: #7c3aed; }" in panel_source
    assert ".notify-workspace .chapter-content { --workspace-accent: #b91c1c; }" in panel_source
    assert ".about-workspace .chapter-hero { --chapter-hero-copy-color: color-mix(in srgb, #a16207 88%, white 12%); }" in panel_source
    assert ".logs-workspace .logs-list-actions > a.button-secondary" in panel_source
    assert "color: color-mix(in srgb, #f97316 86%, white 14%);" in panel_source
    assert "background: color-mix(in srgb, #7c3aed 18%, var(--card-background-color));" in panel_source
    assert "background: color-mix(in srgb, #dc2626 18%, var(--card-background-color));" in panel_source
    assert ".chapter-hero-icon :is(svg, .chime-section-icon) {\n      color: var(--chapter-hero-copy-color);" in panel_source
    assert ".chapter-hero-icon {\n      display: inline-grid;" in panel_source
    assert "filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.42));" in panel_source
    assert ".chapter-workspace .chapter-content .field-help-link {\n      color: var(--section-help-color);" in panel_source
    assert "color-mix(in srgb, #b8860b 42%, var(--divider-color))" not in panel_source
    assert ".chapter-workspace .field:not(.error) {\n      border-color: var(--section-help-border);" in panel_source
    assert ".chapter-workspace .field:not(.error) input[type=\"range\"] {\n      accent-color: var(--section-help-color);" in panel_source
    assert ".chapter-workspace .control-checkbox {\n      color: var(--section-help-color);" in panel_source
    assert ".control-range::-webkit-slider-runnable-track" in panel_source
    assert "var(--card-background-color) var(--range-progress, 0%) 100%" in panel_source
    assert "color-mix(in srgb, var(--section-help-color) 84%, black 16%)" in panel_source
    assert "_updateNotifyRangeProgress(rangeInput);" in panel_source


def test_log_row_toggle_uses_its_event_accent():
    """Log-row chevrons must use each row's own color instead of the Logs palette."""
    panel_source = (
        Path(__file__).parents[1]
        / "custom_components"
        / "chime_tts"
        / "panel"
        / "chime-tts-panel.js"
    ).read_text(encoding="utf-8")

    assert ".logs-workspace .log-event-row .log-event-toggle" in panel_source
    assert "var(--log-row-accent-solid) 44%" in panel_source
    assert "var(--log-row-accent-solid) 14%" in panel_source


def test_mobile_pull_to_refresh_keeps_the_topbar_background_continuous():
    """The sticky topbar surface must extend into the mobile overscroll area."""
    panel_source = (
        Path(__file__).parents[1]
        / "custom_components"
        / "chime_tts"
        / "panel"
        / "chime-tts-panel.js"
    ).read_text(encoding="utf-8")

    assert ".topbar-wrap::before" in panel_source
    assert "top: -100vh;" in panel_source
    assert "background: var(--topbar-background);" in panel_source


def test_panel_uses_an_inline_christmas_footer_logo_only_in_december():
    """The seasonal footer artwork is embedded rather than served as an asset."""
    root = Path(__file__).parents[1]
    panel_source = (
        root / "custom_components" / "chime_tts" / "panel" / "chime-tts-panel.js"
    ).read_text(encoding="utf-8")

    assert "const CHRISTMAS_FOOTER_SVG = `" in panel_source
    assert 'id="CHIME"' in panel_source
    assert "IS_DECEMBER\n        ? CHRISTMAS_FOOTER_SVG" in panel_source


def test_panel_renders_inline_snowflakes_only_in_december_behind_the_ui():
    """Snowfall is a seasonal, non-interactive visual layer with inline artwork."""
    root = Path(__file__).parents[1]
    panel_source = (
        root / "custom_components" / "chime_tts" / "panel" / "chime-tts-panel.js"
    ).read_text(encoding="utf-8")

    assert "const SNOWFLAKE_SVG = `" in panel_source
    assert "_renderSnowfall()" in panel_source
    assert "if (!IS_DECEMBER)" in panel_source
    assert 'class="snowfall"' in panel_source
    assert "pointer-events: none;" in panel_source
    assert "@keyframes snowfall" in panel_source
    assert "this._snowfall.childElementCount > 0" in panel_source


def test_panel_hides_snowfall_and_uses_a_spinner_while_loading():
    """Seasonal decoration waits until the configuration is ready to render."""
    root = Path(__file__).parents[1]
    panel_source = (
        root / "custom_components" / "chime_tts" / "panel" / "chime-tts-panel.js"
    ).read_text(encoding="utf-8")

    assert 'this._snowfall.innerHTML = "";' in panel_source
    assert 'class="loading-spinner"' in panel_source
    assert "Loading Chime TTS settings..." not in panel_source


def test_panel_renders_chime_fields_as_selectable_options_with_preview_controls():
    """Chime fields use selects in both editors and retain their preview controls."""
    panel_source = (
        Path(__file__).parents[1]
        / "custom_components"
        / "chime_tts"
        / "panel"
        / "chime-tts-panel.js"
    ).read_text(encoding="utf-8")

    assert '<select class="control-select" data-field="${this._escapeAttribute(field.key)}">' in panel_source
    assert 'data-notify-field="${this._escapeAttribute(field.key)}"' in panel_source
    assert "_isChimePreviewField(field)" in panel_source
    assert "data-field-audio-toggle" in panel_source
    assert "data-notify-audio-toggle" in panel_source


def test_panel_does_not_refocus_native_selects_after_rendering():
    """A chime select must close normally after a mobile selection."""
    panel_source = (
        Path(__file__).parents[1]
        / "custom_components"
        / "chime_tts"
        / "panel"
        / "chime-tts-panel.js"
    ).read_text(encoding="utf-8")

    assert 'const shouldRestoreFocus = activeElement?.tagName !== "SELECT"' in panel_source
    assert "!shouldRestoreFocus" in panel_source


def test_field_preview_buttons_use_their_workspace_accent():
    """Chime preview controls inherit the colour of their containing section."""
    panel_source = (
        Path(__file__).parents[1]
        / "custom_components"
        / "chime_tts"
        / "panel"
        / "chime-tts-panel.js"
    ).read_text(encoding="utf-8")

    assert ".chapter-content .field-preview-button" in panel_source
    assert "background: color-mix(in srgb, var(--workspace-accent) 14%" in panel_source
    assert ".field-preview-button.preview-playing" in panel_source
    assert "background: var(--workspace-accent) !important;" in panel_source
    assert ".field-preview-button.preview-playing::before" in panel_source


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
    assert get_filename_hash_from_service_data(
        {**base, "repeat": 2, "repeat_delay": 100}, {}
    ) != get_filename_hash_from_service_data({**base, "repeat": 2, "repeat_delay": 200}, {})


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


def test_notification_profile_run_button_has_a_clean_darker_green_treatment():
    """The Run icon stays crisp while its notification action is less bright."""
    panel_source = Path(
        "custom_components/chime_tts/panel/chime-tts-panel.js"
    ).read_text()
    run_button_css = panel_source.split(
        ".notify-profile-actions [data-open-notify-test] {", 1
    )[1].split(".notify-profile-actions [data-remove-notify-profile]", 1)[0]

    assert "rgba(21, 128, 61, 0.5)" in run_button_css
    assert "rgba(20, 83, 45, 0.42)" in run_button_css
    assert "filter: drop-shadow(0 0 0.7px #000);" not in run_button_css


def test_chime_set_slot_machine_loops_with_a_new_random_winning_symbol():
    """Each seamless reel cycle promotes its winner and selects another one."""
    slot_machine_source = Path(
        "custom_components/chime_tts/panel/chime-set-slot-machine.js"
    ).read_text()
    panel_source = Path(
        "custom_components/chime_tts/panel/chime-tts-panel.js"
    ).read_text()

    assert "animation:chimeSlotReelSpin 2.97s both;" in slot_machine_source
    assert "animation:chimeSlotReelSpin 2.97s infinite both;" not in slot_machine_source
    assert "this._scheduleEmptyChimeSetReelSpin();" in panel_source
    assert "this._emptyChimeSetSelection = this._emptyChimeSetNextSelection;" in panel_source
    assert "this._randomEmptyChimeSetSelection(" in panel_source
    assert "chime-slot-message-copy" in slot_machine_source
    assert "chime-slot-winner-question" in slot_machine_source
    assert "translate:-50% -50%" in slot_machine_source
    assert "WINNER_ICON_VIEW_BOXES" in slot_machine_source
    assert "chimeSlotWinnerFadeOut" in slot_machine_source
    assert "chimeSlotWinnerQuestion" in slot_machine_source
    assert "chimeSlotWinnerFadeIn" in slot_machine_source
    assert "flex-direction:column; gap:0;" in slot_machine_source
    assert 'transform="translate(-7 0)"' in slot_machine_source
    assert 'href="/api/chime_tts/images/slot.svg"' in slot_machine_source
    slot_art_path = Path("custom_components/chime_tts/panel/images/slot.svg")
    assert slot_art_path.is_file()
    assert 'id="arm"' not in slot_art_path.read_text()
    assert 'clip-path="url(#_clip3)"' not in slot_art_path.read_text()
    assert 'fill="#fff"' not in slot_machine_source


def test_unnamed_chime_set_validation_preserves_the_draft():
    """An invalid Chime Set remains editable instead of being discarded on save."""
    panel_source = Path(
        "custom_components/chime_tts/panel/chime-tts-panel.js"
    ).read_text()

    assert 'errors.chime_sets = "invalid_chime_sets";' in panel_source
    assert "this._draftValues = hasValidationErrors" in panel_source
    assert "? values" in panel_source
