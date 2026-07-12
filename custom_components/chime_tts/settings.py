"""Shared settings metadata and validation for Chime TTS."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
import os
from typing import Any

import voluptuous as vol
import yaml
from homeassistant import config_entries
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import selector

from .const import (
    ADD_COVER_ART_KEY,
    AMAZON_POLLY,
    BAIDU,
    CROSSFADE_KEY,
    CUSTOM_CHIMES_PATH_KEY,
    DEFAULT_FADE_TRANSITION_MS,
    DEFAULT_LANGUAGE_KEY,
    DEFAULT_OFFSET_MS,
    DEFAULT_TLD_KEY,
    DEFAULT_VOICE_KEY,
    DOMAIN,
    ELEVENLABS,
    FADE_TRANSITION_KEY,
    FALLBACK_TTS_PLATFORM_KEY,
    GOOGLE_CLOUD,
    GOOGLE_TRANSLATE,
    IBM_WATSON_TTS,
    MARYTTS,
    MICROSOFT_EDGE_TTS,
    MICROSOFT_TTS,
    NABU_CASA_CLOUD_TTS,
    NABU_CASA_CLOUD_TTS_OLD,
    OFFSET_KEY,
    OPENAI_TTS,
    PICOTTS,
    PIPER,
    QUEUE_TIMEOUT_DEFAULT,
    QUEUE_TIMEOUT_KEY,
    REMOVE_TEMP_FILE_DELAY_KEY,
    TEMP_CHIMES_PATH_DEFAULT,
    TEMP_CHIMES_PATH_KEY,
    TEMP_PATH_DEFAULT,
    TEMP_PATH_KEY,
    TTS_PLATFORM_KEY,
    TTS_TIMEOUT_DEFAULT,
    TTS_TIMEOUT_KEY,
    VERSION,
    VOICE_RSS,
    WWW_PATH_DEFAULT,
    WWW_PATH_KEY,
    YANDEX_TTS,
)
from .helpers.helpers import ChimeTTSHelper
from .helpers.panel_logs import async_get_panel_log_events, get_panel_log_events

helpers = ChimeTTSHelper()


@dataclass
class _TaggedYamlValue:
    """Preserve custom YAML tags such as Home Assistant !include directives."""

    tag: str
    value: Any


class _ChimeTTSYamlLoader(yaml.SafeLoader):
    """YAML loader that preserves unknown tags instead of failing on them."""


class _ChimeTTSYamlDumper(yaml.SafeDumper):
    """YAML dumper that writes preserved tags back out."""


def _construct_tagged_yaml_value(
    loader: _ChimeTTSYamlLoader,
    tag_suffix: str,
    node: yaml.nodes.Node,
) -> _TaggedYamlValue:
    """Construct a YAML node while preserving its original tag."""
    del tag_suffix

    if isinstance(node, yaml.ScalarNode):
        value = loader.construct_scalar(node)
    elif isinstance(node, yaml.SequenceNode):
        value = loader.construct_sequence(node, deep=True)
    elif isinstance(node, yaml.MappingNode):
        value = loader.construct_mapping(node, deep=True)
    else:
        raise TypeError(f"Unsupported YAML node type: {type(node)!r}")

    return _TaggedYamlValue(node.tag, value)


def _represent_tagged_yaml_value(
    dumper: _ChimeTTSYamlDumper,
    data: _TaggedYamlValue,
) -> yaml.nodes.Node:
    """Represent a preserved tagged YAML value with its original tag."""
    if isinstance(data.value, dict):
        return dumper.represent_mapping(data.tag, data.value)
    if isinstance(data.value, list):
        return dumper.represent_sequence(data.tag, data.value)
    return dumper.represent_scalar(data.tag, "" if data.value is None else str(data.value))


_ChimeTTSYamlLoader.add_multi_constructor("", _construct_tagged_yaml_value)
_ChimeTTSYamlDumper.add_representer(_TaggedYamlValue, _represent_tagged_yaml_value)

TLD_OPTIONS = [
    {"value": "", "label": "Provider default"},
    {"value": "com", "label": "com"},
    {"value": "co.uk", "label": "co.uk"},
    {"value": "com.au", "label": "com.au"},
    {"value": "ca", "label": "ca"},
    {"value": "co.in", "label": "co.in"},
    {"value": "ie", "label": "ie"},
    {"value": "co.za", "label": "co.za"},
    {"value": "fr", "label": "fr"},
    {"value": "com.br", "label": "com.br"},
    {"value": "pt", "label": "pt"},
    {"value": "es", "label": "es"},
]

PATH_BROWSABLE_FIELD_KEYS = {
    CUSTOM_CHIMES_PATH_KEY,
    TEMP_CHIMES_PATH_KEY,
    TEMP_PATH_KEY,
    WWW_PATH_KEY,
}
RESTART_REQUIRED_FIELD_KEYS = {
    CUSTOM_CHIMES_PATH_KEY,
}
CHIME_FILE_EXTENSIONS = {
    ".aac",
    ".flac",
    ".m4a",
    ".mp3",
    ".ogg",
    ".wav",
    ".wma",
}
FIELD_EMPTY_DEFAULT_HINTS = {
}

FIELD_PLACEHOLDERS = {
    DEFAULT_LANGUAGE_KEY: "Blank means the selected provider chooses the language.",
    DEFAULT_VOICE_KEY: "Blank means the selected provider chooses the voice.",
    DEFAULT_TLD_KEY: "Blank means Google Translate uses its default dialect.",
    REMOVE_TEMP_FILE_DELAY_KEY: "Blank means the integration uses its built-in cleanup timing.",
    CUSTOM_CHIMES_PATH_KEY: "No custom chimes folder is configured.",
}

FIELD_EMPTY_PATH_MESSAGES = {
    CUSTOM_CHIMES_PATH_KEY: "",
}
PROVIDER_HINTS_BY_FIELD = {
    TTS_PLATFORM_KEY: {
        GOOGLE_TRANSLATE: {
            "tone": "info",
            "message": "Google Translate commonly uses language and dialect. Voice selection is usually ignored.",
        },
        GOOGLE_CLOUD: {
            "tone": "info",
            "message": "Google Cloud commonly uses both language and voice. Dialect is usually ignored here.",
        },
        NABU_CASA_CLOUD_TTS: {
            "tone": "info",
            "message": "Nabu Casa Cloud commonly uses language and voice. Dialect is usually ignored here.",
        },
        NABU_CASA_CLOUD_TTS_OLD: {
            "tone": "info",
            "message": "Nabu Casa Cloud commonly uses language and voice. Dialect is usually ignored here.",
        },
        MICROSOFT_EDGE_TTS: {
            "tone": "info",
            "message": "Edge TTS commonly uses language and voice. Dialect is usually ignored here.",
        },
        OPENAI_TTS: {
            "tone": "info",
            "message": "OpenAI TTS typically uses voice selection. Language and dialect are often unnecessary.",
        },
        PIPER: {
            "tone": "info",
            "message": "Piper typically uses voice selection. Language and dialect are often unnecessary.",
        },
    },
    DEFAULT_LANGUAGE_KEY: {
        GOOGLE_TRANSLATE: {
            "tone": "info",
            "message": "Language is commonly used by Google Translate and helps select the right voice family.",
        },
        GOOGLE_CLOUD: {
            "tone": "info",
            "message": "Language is commonly used by Google Cloud and works well alongside an explicit voice.",
        },
        NABU_CASA_CLOUD_TTS: {
            "tone": "info",
            "message": "Language is commonly used by Nabu Casa Cloud and works well alongside an explicit voice.",
        },
        OPENAI_TTS: {
            "tone": "muted",
            "message": "This provider often does not need a language override unless you want to force a specific locale.",
        },
    },
    DEFAULT_VOICE_KEY: {
        GOOGLE_TRANSLATE: {
            "tone": "muted",
            "message": "Google Translate usually ignores explicit voice names, so this can often stay blank.",
        },
        GOOGLE_CLOUD: {
            "tone": "info",
            "message": "Voice is commonly used by Google Cloud to target a specific speaker.",
        },
        NABU_CASA_CLOUD_TTS: {
            "tone": "info",
            "message": "Voice is commonly used by Nabu Casa Cloud to target a specific speaker.",
        },
        MICROSOFT_EDGE_TTS: {
            "tone": "info",
            "message": "Voice is commonly used by Edge TTS to target a specific speaker.",
        },
        PIPER: {
            "tone": "info",
            "message": "Voice is commonly used by Piper and is often the main override to set.",
        },
    },
    DEFAULT_TLD_KEY: {
        GOOGLE_TRANSLATE: {
            "tone": "info",
            "message": "Dialect is mainly useful for Google Translate and can change accent or region.",
        },
        GOOGLE_CLOUD: {
            "tone": "muted",
            "message": "Google Cloud usually ignores this dialect field, so it can normally stay blank.",
        },
        NABU_CASA_CLOUD_TTS: {
            "tone": "muted",
            "message": "Nabu Casa Cloud usually ignores this dialect field, so it can normally stay blank.",
        },
        MICROSOFT_EDGE_TTS: {
            "tone": "muted",
            "message": "Edge TTS usually ignores this dialect field, so it can normally stay blank.",
        },
    },
    FALLBACK_TTS_PLATFORM_KEY: {
        GOOGLE_TRANSLATE: {
            "tone": "info",
            "message": "Google Translate is a lightweight fallback choice when voice-specific providers are unavailable.",
        },
        GOOGLE_CLOUD: {
            "tone": "info",
            "message": "Google Cloud is a stronger fallback when you rely on explicit voice names.",
        },
        NABU_CASA_CLOUD_TTS: {
            "tone": "info",
            "message": "Nabu Casa Cloud is a good fallback when you want managed voice coverage.",
        },
    },
}
PROVIDER_HINT_ALIASES = {
    AMAZON_POLLY: AMAZON_POLLY,
    BAIDU: BAIDU,
    ELEVENLABS: ELEVENLABS,
    GOOGLE_CLOUD: GOOGLE_CLOUD,
    GOOGLE_TRANSLATE: GOOGLE_TRANSLATE,
    IBM_WATSON_TTS: IBM_WATSON_TTS,
    MARYTTS: MARYTTS,
    MICROSOFT_TTS: MICROSOFT_TTS,
    MICROSOFT_EDGE_TTS: MICROSOFT_EDGE_TTS,
    NABU_CASA_CLOUD_TTS: NABU_CASA_CLOUD_TTS,
    NABU_CASA_CLOUD_TTS_OLD: NABU_CASA_CLOUD_TTS,
    OPENAI_TTS: OPENAI_TTS,
    PICOTTS: PICOTTS,
    PIPER: PIPER,
    VOICE_RSS: VOICE_RSS,
    YANDEX_TTS: YANDEX_TTS,
}

CONFIGURATION_DOCS_BASE_URL = (
    "https://nimroddolev.github.io/chime_tts/docs/documentation/configuration/"
)
NOTIFY_DOCS_URL = (
    "https://nimroddolev.github.io/chime_tts/docs/documentation/notify/"
)
SAY_ACTION_PARAMS_DOCS_URL = (
    "https://nimroddolev.github.io/chime_tts/docs/documentation/actions/say-action/parameters/"
)

NOTIFY_PROFILE_SCHEMA_FIELDS: tuple[dict[str, Any], ...] = (
    {"key": "name", "label": "Service name", "type": "text", "required": True},
    {
        "key": "entity_id",
        "label": "Target media players",
        "type": "text",
        "required": True,
        "description": "Select one one or more media_player entities to play the notification.",
        "placeholder": "media_player.kitchen, media_player.office",
    },
    {"key": "chime_path", "label": "Start chime", "type": "select"},
    {"key": "end_chime_path", "label": "End chime", "type": "select"},
    {"key": "tts_platform", "label": "TTS platform", "type": "select"},
    {"key": "language", "label": "Language", "type": "text"},
    {"key": "voice", "label": "Voice", "type": "text"},
    {"key": "tld", "label": "Dialect", "type": "select"},
    {
        "key": "offset",
        "label": "Offset",
        "type": "range",
        "min": -10000,
        "max": 10000,
        "step": 10,
        "unit": "ms",
    },
    {
        "key": "crossfade",
        "label": "Crossfade",
        "type": "range",
        "min": 0,
        "max": 10000,
        "step": 1,
        "unit": "ms",
    },
    {
        "key": "final_delay",
        "label": "Final delay",
        "type": "range",
        "min": 0,
        "max": 10000,
        "step": 1,
        "unit": "ms",
    },
    {
        "key": "tts_speed",
        "label": "TTS speed",
        "type": "range",
        "min": 1,
        "max": 500,
        "step": 5,
        "unit": "%",
    },
    {
        "key": "tts_pitch",
        "label": "TTS pitch",
        "type": "range",
        "min": -100,
        "max": 100,
        "step": 1,
        "unit": "semitones",
    },
    {
        "key": "volume_level",
        "label": "Volume level",
        "type": "range",
        "min": 0,
        "max": 1,
        "step": 0.01,
        "unit": "",
    },
    {
        "key": "audio_conversion",
        "label": "Audio conversion",
        "type": "text",
        "description": "Convert audio for Alexa playback, scale volume with FFmpeg, or provide custom FFmpeg arguments.",
    },
    {
        "key": "options",
        "label": "TTS options YAML",
        "type": "textarea",
        "placeholder": "voice: en-US-Wavenet-D",
    },
    {"key": "announce", "label": "Announce", "type": "boolean"},
    {"key": "cache", "label": "Cache", "type": "boolean"},
    {"key": "fade_audio", "label": "Fade audio", "type": "boolean"},
    {"key": "join_players", "label": "Join players", "type": "boolean"},
    {"key": "unjoin_players", "label": "Unjoin players", "type": "boolean"},
)
NOTIFY_REQUIRED_KEYS = {"name", "entity_id"}
NOTIFY_BOOLEAN_KEYS = {
    "announce",
    "cache",
    "fade_audio",
    "join_players",
    "unjoin_players",
}
NOTIFY_NUMERIC_KEYS = {
    "offset",
    "crossfade",
    "final_delay",
    "tts_speed",
    "tts_pitch",
    "volume_level",
}
NOTIFY_STRING_KEYS = {
    "name",
    "entity_id",
    "chime_path",
    "end_chime_path",
    "tts_platform",
    "language",
    "voice",
    "tld",
    "audio_conversion",
    "options",
}
NOTIFY_EDITABLE_KEYS = (
    tuple(NOTIFY_STRING_KEYS)
    + tuple(NOTIFY_NUMERIC_KEYS)
    + tuple(NOTIFY_BOOLEAN_KEYS)
)
NOTIFY_PROFILE_DEFAULTS = {
    "name": "",
    "entity_id": "",
    "chime_path": "",
    "end_chime_path": "",
    "tts_platform": "",
    "language": "",
    "voice": "",
    "tld": "",
    "offset": "",
    "crossfade": "",
    "final_delay": "",
    "tts_speed": "",
    "tts_pitch": "",
    "volume_level": "",
    "audio_conversion": "",
    "options": "",
    "announce": False,
    "cache": False,
    "fade_audio": False,
    "join_players": False,
    "unjoin_players": False,
}

FIELD_DOCUMENTATION_URLS = {
    QUEUE_TIMEOUT_KEY: f"{CONFIGURATION_DOCS_BASE_URL}#timeout",
    TTS_TIMEOUT_KEY: f"{CONFIGURATION_DOCS_BASE_URL}#tts-audio-generation-timeout",
    ADD_COVER_ART_KEY: f"{CONFIGURATION_DOCS_BASE_URL}#mp3-cover-art",
    TTS_PLATFORM_KEY: f"{CONFIGURATION_DOCS_BASE_URL}#default-tts-platform",
    DEFAULT_LANGUAGE_KEY: f"{CONFIGURATION_DOCS_BASE_URL}#default-language",
    DEFAULT_VOICE_KEY: f"{CONFIGURATION_DOCS_BASE_URL}#default-voice",
    DEFAULT_TLD_KEY: f"{CONFIGURATION_DOCS_BASE_URL}#default-dialect",
    FALLBACK_TTS_PLATFORM_KEY: f"{CONFIGURATION_DOCS_BASE_URL}#fallback-tts-platform",
    OFFSET_KEY: f"{CONFIGURATION_DOCS_BASE_URL}#default-offset",
    CROSSFADE_KEY: f"{CONFIGURATION_DOCS_BASE_URL}#crossfade",
    FADE_TRANSITION_KEY: f"{CONFIGURATION_DOCS_BASE_URL}#fade-transition",
    REMOVE_TEMP_FILE_DELAY_KEY: (
        f"{CONFIGURATION_DOCS_BASE_URL}#delay-before-removing-temporary-files"
    ),
    CUSTOM_CHIMES_PATH_KEY: f"{CONFIGURATION_DOCS_BASE_URL}#custom-chimes-folder",
    TEMP_CHIMES_PATH_KEY: (
        f"{CONFIGURATION_DOCS_BASE_URL}#downloaded-chimes-folder"
    ),
    TEMP_PATH_KEY: f"{CONFIGURATION_DOCS_BASE_URL}#temporary-mp3-folder",
    WWW_PATH_KEY: f"{CONFIGURATION_DOCS_BASE_URL}#chime_ttssay_url-folder",
}

NOTIFY_FIELD_DOCUMENTATION_URLS = {
    "name": NOTIFY_DOCS_URL,
    "entity_id": NOTIFY_DOCS_URL,
    "chime_path": f"{SAY_ACTION_PARAMS_DOCS_URL}#chime_path",
    "end_chime_path": f"{SAY_ACTION_PARAMS_DOCS_URL}#end_chime_path",
    "tts_platform": f"{CONFIGURATION_DOCS_BASE_URL}#default-tts-platform",
    "language": f"{CONFIGURATION_DOCS_BASE_URL}#default-language",
    "voice": f"{CONFIGURATION_DOCS_BASE_URL}#default-voice",
    "tld": f"{CONFIGURATION_DOCS_BASE_URL}#default-dialect",
    "offset": f"{CONFIGURATION_DOCS_BASE_URL}#default-offset",
    "crossfade": f"{SAY_ACTION_PARAMS_DOCS_URL}#crossfade",
    "final_delay": f"{SAY_ACTION_PARAMS_DOCS_URL}#final_delay",
    "tts_speed": f"{SAY_ACTION_PARAMS_DOCS_URL}#tts_speed",
    "tts_pitch": f"{SAY_ACTION_PARAMS_DOCS_URL}#tts_pitch",
    "volume_level": f"{SAY_ACTION_PARAMS_DOCS_URL}#volume_level",
    "audio_conversion": f"{SAY_ACTION_PARAMS_DOCS_URL}#audio_conversion",
    "options": f"{SAY_ACTION_PARAMS_DOCS_URL}#options",
    "announce": f"{SAY_ACTION_PARAMS_DOCS_URL}#announce",
    "cache": f"{SAY_ACTION_PARAMS_DOCS_URL}#cache",
    "fade_audio": f"{SAY_ACTION_PARAMS_DOCS_URL}#fade_audio",
    "join_players": f"{SAY_ACTION_PARAMS_DOCS_URL}#join_players",
    "unjoin_players": f"{SAY_ACTION_PARAMS_DOCS_URL}#unjoin_players",
}


@dataclass(frozen=True)
class SettingsField:
    """Describes a single settings field."""

    key: str
    label: str
    description: str
    field_type: str
    section: str
    required: bool = False
    allow_custom_value: bool = False
    min_value: int | None = None
    step: int = 1
    wide: bool = False
    advanced: bool = False


@dataclass(frozen=True)
class ValidationResult:
    """Result of validating submitted settings."""

    data: dict[str, Any]
    errors: dict[str, str]
    restart_required: bool


@dataclass(frozen=True)
class NotifyProfilesValidationResult:
    """Result of validating submitted notify profiles."""

    data: list[dict[str, Any]]
    errors: list[dict[str, str]]


SETTINGS_FIELDS: tuple[SettingsField, ...] = (
    SettingsField(
        key=QUEUE_TIMEOUT_KEY,
        label="Action timeout",
        description="Maximum seconds to wait for queued Chime TTS work.",
        field_type="number",
        section="general",
        required=True,
        min_value=0,
    ),
    SettingsField(
        key=TTS_TIMEOUT_KEY,
        label="TTS generation timeout",
        description="Maximum seconds to wait for a TTS platform response.",
        field_type="number",
        section="general",
        required=True,
        min_value=-1,
    ),
    SettingsField(
        key=ADD_COVER_ART_KEY,
        label="Add cover art to generated MP3 files",
        description="Embed Chime TTS cover art in generated audio files.",
        field_type="boolean",
        section="playback",
    ),
    SettingsField(
        key=TTS_PLATFORM_KEY,
        label="Default TTS platform",
        description="Used when a service call does not specify a TTS platform.",
        field_type="select",
        section="voice",
        allow_custom_value=True,
    ),
    SettingsField(
        key=DEFAULT_LANGUAGE_KEY,
        label="Default language",
        description="Applied with the default TTS platform when supported.",
        field_type="text",
        section="voice",
        advanced=True,
    ),
    SettingsField(
        key=DEFAULT_VOICE_KEY,
        label="Default voice",
        description="Applied with the default TTS platform when supported.",
        field_type="text",
        section="voice",
        advanced=True,
    ),
    SettingsField(
        key=DEFAULT_TLD_KEY,
        label="Default dialect",
        description="Google Translate TTS dialect fallback.",
        field_type="select",
        section="voice",
        advanced=True,
    ),
    SettingsField(
        key=FALLBACK_TTS_PLATFORM_KEY,
        label="Fallback TTS platform",
        description="Used when the requested TTS platform is unavailable.",
        field_type="select",
        section="voice",
        allow_custom_value=True,
    ),
    SettingsField(
        key=OFFSET_KEY,
        label="Default offset",
        description="Milliseconds between chimes and TTS. Negative values overlay.",
        field_type="number",
        section="playback",
        required=True,
    ),
    SettingsField(
        key=CROSSFADE_KEY,
        label="Default crossfade",
        description="Milliseconds to fade out a segment while fading in the next.",
        field_type="number",
        section="playback",
        required=True,
        min_value=0,
        advanced=True,
    ),
    SettingsField(
        key=FADE_TRANSITION_KEY,
        label="Fade transition",
        description="Milliseconds used for announce and fade_audio transitions.",
        field_type="number",
        section="playback",
        required=True,
        min_value=0,
        advanced=True,
    ),
    SettingsField(
        key=REMOVE_TEMP_FILE_DELAY_KEY,
        label="Temporary file cleanup delay",
        description="Milliseconds to wait before deleting uncached temporary files.",
        field_type="number",
        section="playback",
        min_value=0,
        advanced=True,
    ),
    SettingsField(
        key=CUSTOM_CHIMES_PATH_KEY,
        label="Custom chimes folder",
        description="Folder containing your own chime audio files. Changing it requires a Home Assistant restart.",
        field_type="text",
        section="paths",
        wide=True,
    ),
    SettingsField(
        key=TEMP_CHIMES_PATH_KEY,
        label="Downloaded chimes folder",
        description="Where downloaded chime files are cached.",
        field_type="text",
        section="paths",
        required=True,
        wide=True,
        advanced=True,
    ),
    SettingsField(
        key=TEMP_PATH_KEY,
        label="Temporary audio folder",
        description="Must stay inside a configured media directory.",
        field_type="text",
        section="paths",
        required=True,
        wide=True,
        advanced=True,
    ),
    SettingsField(
        key=WWW_PATH_KEY,
        label="say_url output folder",
        description="Must stay inside an allowlisted external directory, /media, or /config/www.",
        field_type="text",
        section="paths",
        required=True,
        wide=True,
        advanced=True,
    ),
)

SETTINGS_FIELD_MAP = {field.key: field for field in SETTINGS_FIELDS}

SETTINGS_SECTIONS = (
    {
        "key": "paths",
        "title": "Folder Paths",
        "description": "Folder paths for custom chimes, cache chimes and generated audio files.",
        "fields": [
            CUSTOM_CHIMES_PATH_KEY,
            TEMP_CHIMES_PATH_KEY,
            TEMP_PATH_KEY,
            WWW_PATH_KEY,
        ],
    },
    {
        "key": "voice",
        "title": "Default & Fallback Options",
        "description": "Preferred TTS providers and their default language, voice, and dialect settings.",
        "fields": [
            TTS_PLATFORM_KEY,
            DEFAULT_LANGUAGE_KEY,
            DEFAULT_VOICE_KEY,
            DEFAULT_TLD_KEY,
            FALLBACK_TTS_PLATFORM_KEY,
        ],
    },
    {
        "key": "playback",
        "title": "Playback Options",
        "description": "Audio timing and cleanup defaults for generated announcements.",
        "fields": [
            OFFSET_KEY,
            CROSSFADE_KEY,
            FADE_TRANSITION_KEY,
            REMOVE_TEMP_FILE_DELAY_KEY,
            ADD_COVER_ART_KEY,
        ],
    },
    {
        "key": "general",
        "title": "Service Timeout Options",
        "description": "Core timeout behavior used across the integration.",
        "fields": [QUEUE_TIMEOUT_KEY, TTS_TIMEOUT_KEY],
    },
)


def get_root_path(hass) -> str:
    """Get the Home Assistant root path prefix used by existing config defaults."""
    if hass is None:
        return ""
    config_root = hass.config.path("").rstrip("/")
    if config_root.endswith("/config"):
        return config_root[: -len("/config")]
    return config_root


def get_tts_platforms(hass) -> list[str]:
    """Return installed TTS platforms in display order."""
    return sorted(helpers.get_installed_tts_platforms(hass))


def _field_default_value(field_key: str, hass) -> Any:
    """Get the default value for a field."""
    root_path = get_root_path(hass)
    defaults = {
        QUEUE_TIMEOUT_KEY: QUEUE_TIMEOUT_DEFAULT,
        TTS_TIMEOUT_KEY: TTS_TIMEOUT_DEFAULT,
        TTS_PLATFORM_KEY: "",
        DEFAULT_LANGUAGE_KEY: "",
        DEFAULT_VOICE_KEY: "",
        DEFAULT_TLD_KEY: "",
        FALLBACK_TTS_PLATFORM_KEY: "",
        OFFSET_KEY: DEFAULT_OFFSET_MS,
        CROSSFADE_KEY: 0,
        FADE_TRANSITION_KEY: DEFAULT_FADE_TRANSITION_MS,
        REMOVE_TEMP_FILE_DELAY_KEY: "",
        CUSTOM_CHIMES_PATH_KEY: "",
        TEMP_CHIMES_PATH_KEY: f"{root_path}{TEMP_CHIMES_PATH_DEFAULT}",
        TEMP_PATH_KEY: f"{root_path}{TEMP_PATH_DEFAULT}",
        WWW_PATH_KEY: f"{root_path}{WWW_PATH_DEFAULT}",
        ADD_COVER_ART_KEY: False,
    }
    return defaults[field_key]


def _get_entry_value(
    config_entry: config_entries.ConfigEntry,
    key: str,
    hass,
    user_input: dict[str, Any] | None = None,
) -> Any:
    """Get a setting from submitted input, options, data, or defaults."""
    if user_input is not None and key in user_input:
        return user_input[key]

    for source in (dict(config_entry.options), dict(config_entry.data)):
        if key in source:
            return source[key]

    return _field_default_value(key, hass)


def get_settings_data(
    hass,
    config_entry: config_entries.ConfigEntry,
    user_input: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Get current settings data."""
    return {
        field.key: _get_entry_value(config_entry, field.key, hass, user_input)
        for field in SETTINGS_FIELDS
    }


def _configuration_yaml_path(hass) -> str:
    """Return the Home Assistant configuration.yaml path."""
    return hass.config.path("configuration.yaml")


def _load_configuration_yaml(hass) -> dict[str, Any]:
    """Load configuration.yaml as a dictionary."""
    config_path = _configuration_yaml_path(hass)
    if not os.path.exists(config_path):
        return {}

    with open(config_path, encoding="utf-8") as config_file:
        loaded = yaml.load(config_file, Loader=_ChimeTTSYamlLoader) or {}

    if not isinstance(loaded, dict):
        raise ValueError("configuration.yaml must contain a mapping at the root level.")

    return loaded


def _load_configuration_yaml_for_panel(hass) -> dict[str, Any]:
    """Load configuration.yaml using Home Assistant's YAML loader when available."""
    config_path = _configuration_yaml_path(hass)
    if not os.path.exists(config_path):
        return {}

    try:
        from pathlib import Path

        from homeassistant.config import load_yaml_config_file
        from homeassistant.util.yaml.loader import Secrets

        return load_yaml_config_file(
            config_path,
            Secrets(Path(hass.config.config_dir)),
        )
    except ImportError:
        return _load_configuration_yaml(hass)


def _format_panel_configuration_error(error: Exception) -> str:
    """Return a panel-friendly configuration.yaml load error."""
    message = str(error).strip() or "Unable to read configuration.yaml."
    if "could not determine a constructor for the tag" in message:
        return (
            "Unable to read notify profiles from configuration.yaml. "
            "The file uses Home Assistant YAML directives that require "
            "Home Assistant-aware parsing."
        )
    return message


def _load_services_yaml() -> dict[str, Any]:
    """Load the integration services.yaml file as a dictionary."""
    services_path = os.path.join(os.path.dirname(__file__), "services.yaml")
    with open(services_path, encoding="utf-8") as services_file:
        loaded = yaml.safe_load(services_file) or {}
    if not isinstance(loaded, dict):
        raise ValueError("services.yaml must contain a mapping at the root level.")
    return loaded


def get_notify_chime_options() -> list[dict[str, str]]:
    """Return the same chime dropdown options exposed by the say actions."""
    try:
        services_yaml = _load_services_yaml()
        options = (
            services_yaml.get("say", {})
            .get("fields", {})
            .get("chime_path", {})
            .get("selector", {})
            .get("select", {})
            .get("options", [])
        )
    except (OSError, ValueError, yaml.YAMLError):
        options = []

    normalized = [
        {
            "value": _normalize_string(option.get("value")),
            "label": _normalize_string(option.get("label")),
        }
        for option in options
        if isinstance(option, dict)
        and option.get("label") is not None
        and option.get("value") is not None
        and _normalize_string(option.get("value")) != ""
    ]
    return [{"value": "", "label": ""}] + normalized


async def async_get_notify_chime_options(hass) -> list[dict[str, str]]:
    """Load notify chime options without blocking the event loop."""
    return await hass.async_add_executor_job(get_notify_chime_options)


def _normalize_notify_profile_number(value: Any) -> int | float | str:
    """Normalize a notify profile numeric value."""
    if value in (None, ""):
        return ""
    if isinstance(value, bool):
        raise TypeError("invalid_number")

    normalized = float(value)
    return int(normalized) if normalized.is_integer() else normalized


def _normalize_notify_entity_id_for_display(value: Any) -> str:
    """Normalize YAML entity ids into the panel text format."""
    if isinstance(value, (list, tuple)):
        return ", ".join(
            _normalize_string(item) for item in value if _normalize_string(item)
        )
    return _normalize_string(value)


def _parse_notify_entity_id(value: str) -> str | list[str]:
    """Normalize the panel entity id text into YAML-friendly data."""
    entity_ids = [
        entity_id.strip()
        for entity_id in value.replace("\n", ",").split(",")
        if entity_id.strip()
    ]
    if len(entity_ids) <= 1:
        return entity_ids[0] if entity_ids else ""
    return entity_ids


def _normalize_notify_options_for_display(value: Any) -> str:
    """Normalize notify options into YAML text for the panel."""
    if value in (None, ""):
        return ""
    if isinstance(value, str):
        return value.strip()

    dumped = yaml.safe_dump(
        value,
        default_flow_style=False,
        sort_keys=False,
    ).strip()
    return dumped


def _normalize_notify_profile_for_display(profile: dict[str, Any]) -> dict[str, Any]:
    """Convert a YAML notify profile into panel-editable values."""
    normalized = dict(NOTIFY_PROFILE_DEFAULTS)

    for key in NOTIFY_STRING_KEYS:
        if key == "entity_id":
            normalized[key] = _normalize_notify_entity_id_for_display(profile.get(key))
        elif key == "options":
            normalized[key] = _normalize_notify_options_for_display(profile.get(key))
        else:
            normalized[key] = _normalize_string(profile.get(key))

    for key in NOTIFY_NUMERIC_KEYS:
        try:
            normalized[key] = _normalize_notify_profile_number(profile.get(key))
        except (TypeError, ValueError):
            normalized[key] = ""

    for key in NOTIFY_BOOLEAN_KEYS:
        normalized[key] = _normalize_bool(profile.get(key))

    if normalized["crossfade"] == "" and profile.get("crossafade") not in (None, ""):
        try:
            normalized["crossfade"] = _normalize_notify_profile_number(
                profile.get("crossafade")
            )
        except (TypeError, ValueError):
            normalized["crossfade"] = ""

    return normalized


def load_notify_profiles(hass) -> tuple[list[dict[str, Any]], str | None]:
    """Load Chime TTS notify profiles from configuration.yaml."""
    try:
        loaded = _load_configuration_yaml_for_panel(hass)
    except (HomeAssistantError, OSError, ValueError, yaml.YAMLError) as error:
        return [], _format_panel_configuration_error(error)

    notify_entries = loaded.get("notify") or []
    if not isinstance(notify_entries, list):
        return [], "The notify section in configuration.yaml must be a list."

    profiles = [
        _normalize_notify_profile_for_display(entry)
        for entry in notify_entries
        if isinstance(entry, dict) and entry.get("platform") == DOMAIN
    ]
    return profiles, None


def validate_notify_profiles(
    profiles: list[dict[str, Any]] | None,
) -> NotifyProfilesValidationResult:
    """Validate and normalize notify profiles submitted by the panel."""
    normalized_profiles: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []

    for profile in profiles or []:
        normalized = dict(NOTIFY_PROFILE_DEFAULTS)
        profile_errors: dict[str, str] = {}

        for key in NOTIFY_STRING_KEYS:
            normalized[key] = _normalize_string((profile or {}).get(key))

        for key in NOTIFY_BOOLEAN_KEYS:
            normalized[key] = _normalize_bool((profile or {}).get(key))

        for key in NOTIFY_NUMERIC_KEYS:
            try:
                normalized[key] = _normalize_notify_profile_number((profile or {}).get(key))
            except (TypeError, ValueError):
                normalized[key] = ""
                profile_errors[key] = "invalid_number"

        for key in NOTIFY_REQUIRED_KEYS:
            if normalized[key] == "":
                profile_errors[key] = "required"

        if normalized["options"]:
            try:
                yaml.safe_load(normalized["options"])
            except yaml.YAMLError:
                profile_errors["options"] = "invalid_yaml"

        normalized_profiles.append(normalized)
        errors.append(profile_errors)

    return NotifyProfilesValidationResult(
        data=normalized_profiles,
        errors=errors,
    )


def _serialize_notify_profile(profile: dict[str, Any]) -> dict[str, Any]:
    """Convert a normalized panel notify profile into YAML config data."""
    serialized: dict[str, Any] = {"platform": DOMAIN}

    serialized["name"] = _normalize_string(profile.get("name"))
    serialized["entity_id"] = _parse_notify_entity_id(
        _normalize_string(profile.get("entity_id"))
    )

    ordered_optional_keys = (
        "chime_path",
        "end_chime_path",
        "tts_platform",
        "language",
        "voice",
        "tld",
        "offset",
        "crossfade",
        "final_delay",
        "tts_speed",
        "tts_pitch",
        "volume_level",
        "audio_conversion",
        "options",
        "announce",
        "cache",
        "fade_audio",
        "join_players",
        "unjoin_players",
    )

    for key in ordered_optional_keys:
        value = profile.get(key)
        if key == "options":
            if _normalize_string(value):
                serialized[key] = yaml.safe_load(_normalize_string(value))
            continue
        if key in NOTIFY_BOOLEAN_KEYS:
            if _normalize_bool(value):
                serialized[key] = True
            continue
        if key in NOTIFY_NUMERIC_KEYS:
            if value not in ("", None):
                serialized[key] = value
            continue
        normalized_value = _normalize_string(value)
        if normalized_value != "":
            serialized[key] = normalized_value

    return serialized


def save_notify_profiles(hass, profiles: list[dict[str, Any]]) -> None:
    """Persist Chime TTS notify profiles into configuration.yaml."""
    loaded = _load_configuration_yaml(hass)
    notify_entries = loaded.get("notify") or []
    if notify_entries and not isinstance(notify_entries, list):
        raise ValueError("The notify section in configuration.yaml must be a list.")

    remaining_entries = [
        entry
        for entry in notify_entries
        if not (isinstance(entry, dict) and entry.get("platform") == DOMAIN)
    ]
    next_entries = remaining_entries + [
        _serialize_notify_profile(profile) for profile in profiles
    ]

    if next_entries:
        loaded["notify"] = next_entries
    else:
        loaded.pop("notify", None)

    config_path = _configuration_yaml_path(hass)
    with open(config_path, "w", encoding="utf-8") as config_file:
        yaml.dump(
            loaded,
            config_file,
            Dumper=_ChimeTTSYamlDumper,
            allow_unicode=False,
            default_flow_style=False,
            sort_keys=False,
        )


async def async_load_notify_profiles(
    hass,
) -> tuple[list[dict[str, Any]], str | None]:
    """Load notify profiles without blocking the event loop."""
    return await hass.async_add_executor_job(load_notify_profiles, hass)


async def async_save_notify_profiles(
    hass,
    profiles: list[dict[str, Any]],
) -> None:
    """Save notify profiles without blocking the event loop."""
    await hass.async_add_executor_job(save_notify_profiles, hass, profiles)


async def async_build_panel_payload(
    hass,
    config_entry: config_entries.ConfigEntry,
    **kwargs: Any,
) -> dict[str, Any]:
    """Build the panel payload without blocking the event loop."""
    values = kwargs.get("values") or get_settings_data(hass, config_entry)
    include_log_events = kwargs.get("include_log_events", True)
    notify_profiles = kwargs.get("notify_profiles")
    notify_profile_errors = kwargs.get("notify_profile_errors")
    errors = kwargs.get("errors")
    message = kwargs.get("message")
    message_type = kwargs.get("message_type")
    restart_required = kwargs.get("restart_required", False)

    async_jobs = [
        async_load_notify_profiles(hass),
        async_get_notify_chime_options(hass),
    ]
    if include_log_events:
        async_jobs.append(async_get_panel_log_events(hass))

    async_results = await asyncio.gather(*async_jobs)
    loaded_notify_profiles, notify_profiles_load_error = async_results[0]
    chime_options = async_results[1]
    log_events = async_results[2] if include_log_events else []

    if notify_profiles is None:
        notify_profiles = loaded_notify_profiles

    tts_platforms = get_tts_platforms(hass)
    field_options = {
        TTS_PLATFORM_KEY: [{"value": "", "label": "Not set"}]
        + [{"value": option, "label": option} for option in tts_platforms],
        FALLBACK_TTS_PLATFORM_KEY: [{"value": "", "label": "Not set"}]
        + [{"value": option, "label": option} for option in tts_platforms],
        DEFAULT_TLD_KEY: TLD_OPTIONS,
    }
    default_provider = _normalize_string(values.get(TTS_PLATFORM_KEY))
    fallback_provider = _normalize_string(values.get(FALLBACK_TTS_PLATFORM_KEY))

    return {
        "version": VERSION,
        "icon_url": f"/api/{DOMAIN}/icon.svg?v={VERSION.lstrip('v') or VERSION}",
        "documentation_url": CONFIGURATION_DOCS_BASE_URL,
        "logs_url": f"/config/logs?filter={DOMAIN}",
        "fallback_note": "The standard Configure dialog still works and remains available as a fallback.",
        "restart_note": "Changing the custom chimes folder or its contents requires a Home Assistant restart.",
        "message": message,
        "message_type": message_type,
        "restart_required": restart_required,
        "restart_required_field_keys": sorted(RESTART_REQUIRED_FIELD_KEYS),
        "errors": errors or {},
        "values": values,
        "notify_profiles": notify_profiles,
        "notify_profile_errors": notify_profile_errors or [],
        "notify_profiles_load_error": notify_profiles_load_error,
        "log_events": log_events,
        "sections": [
            {
                "key": section["key"],
                "title": section["title"],
                "description": section["description"],
                "fields": [
                    {
                        "key": field.key,
                        "label": field.label,
                        "description": field.description,
                        "docs_url": FIELD_DOCUMENTATION_URLS.get(field.key),
                        "icon_url": f"/api/{DOMAIN}/option_icons/{field.key}.svg?v={VERSION.lstrip('v') or VERSION}",
                        "type": field.field_type,
                        "required": field.required,
                        "allow_custom_value": field.allow_custom_value,
                        "min": field.min_value,
                        "step": field.step,
                        "wide": field.wide,
                        "advanced": field.advanced,
                        "empty_default_hint": FIELD_EMPTY_DEFAULT_HINTS.get(field.key),
                        "placeholder": FIELD_PLACEHOLDERS.get(field.key),
                        "provider_hint": get_provider_hint(
                            field.key,
                            fallback_provider
                            if field.key == FALLBACK_TTS_PLATFORM_KEY
                            else default_provider,
                        ),
                        "provider_hints": PROVIDER_HINTS_BY_FIELD.get(field.key, {}),
                        "can_browse": field.key in PATH_BROWSABLE_FIELD_KEYS,
                        "path_validation": (
                            validate_path_field(
                                hass,
                                config_entry,
                                field.key,
                                _normalize_string(values.get(field.key)),
                                values,
                            )
                            if field.key in PATH_BROWSABLE_FIELD_KEYS
                            else None
                        ),
                        "options": field_options.get(field.key, []),
                    }
                    for field in (
                        SETTINGS_FIELD_MAP[field_key] for field_key in section["fields"]
                    )
                ],
            }
            for section in SETTINGS_SECTIONS
        ]
        + [
            {
                "key": "notify_profiles",
                "kind": "notify_profiles",
                "title": "Notification Profiles",
                "description": "Create and manage notify services for Chime TTS to easily send Chime TTS notifications in automations and scripts. Saving changes requires a Home Assistant restart.",
                "docs_url": NOTIFY_DOCS_URL,
                "profile_fields": [
                    {
                        **field,
                        "docs_url": NOTIFY_FIELD_DOCUMENTATION_URLS.get(
                            field["key"], NOTIFY_DOCS_URL
                        ),
                        "options": (
                            [{"value": "", "label": "Not set"}]
                            + [{"value": option, "label": option} for option in tts_platforms]
                            if field["key"] == "tts_platform"
                            else (
                                TLD_OPTIONS
                                if field["key"] == "tld"
                                else (
                                    chime_options
                                    if field["key"] in {"chime_path", "end_chime_path"}
                                    else []
                                )
                            )
                        ),
                    }
                    for field in NOTIFY_PROFILE_SCHEMA_FIELDS
                ],
            },
            {
                "key": "logs",
                "kind": "logs",
                "title": "Logs",
                "description": "Review Chime TTS events captured during this Home Assistant session, including actions, generated media, and raw log output.",
                "docs_url": CONFIGURATION_DOCS_BASE_URL,
            },
        ],
        "notify_profile_template": dict(NOTIFY_PROFILE_DEFAULTS),
        "notify_chime_options": chime_options,
    }


def build_options_schema(
    hass,
    config_entry: config_entries.ConfigEntry,
    user_input: dict[str, Any] | None = None,
) -> vol.Schema:
    """Build the Home Assistant options flow schema."""
    data = get_settings_data(hass, config_entry, user_input)
    tts_platforms = get_tts_platforms(hass)

    return vol.Schema(
        {
            vol.Required(QUEUE_TIMEOUT_KEY, default=data[QUEUE_TIMEOUT_KEY]): int,
            vol.Required(TTS_TIMEOUT_KEY, default=data[TTS_TIMEOUT_KEY]): int,
            vol.Optional(
                TTS_PLATFORM_KEY,
                default=data[TTS_PLATFORM_KEY],
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=tts_platforms,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                    custom_value=True,
                )
            ),
            vol.Optional(
                DEFAULT_LANGUAGE_KEY,
                description={"suggested_value": data[DEFAULT_LANGUAGE_KEY]},
            ): str,
            vol.Optional(
                DEFAULT_VOICE_KEY,
                description={"suggested_value": data[DEFAULT_VOICE_KEY]},
            ): str,
            vol.Optional(
                DEFAULT_TLD_KEY,
                default=data[DEFAULT_TLD_KEY],
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[option["value"] for option in TLD_OPTIONS],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                    custom_value=False,
                )
            ),
            vol.Optional(
                FALLBACK_TTS_PLATFORM_KEY,
                default=data[FALLBACK_TTS_PLATFORM_KEY],
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=tts_platforms,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                    custom_value=True,
                )
            ),
            vol.Optional(
                OFFSET_KEY,
                description={"suggested_value": data[OFFSET_KEY]},
            ): int,
            vol.Optional(
                CROSSFADE_KEY,
                description={"suggested_value": data[CROSSFADE_KEY]},
            ): int,
            vol.Optional(
                FADE_TRANSITION_KEY,
                description={"suggested_value": data[FADE_TRANSITION_KEY]},
            ): int,
            vol.Optional(
                REMOVE_TEMP_FILE_DELAY_KEY,
                description={"suggested_value": data[REMOVE_TEMP_FILE_DELAY_KEY]},
            ): int,
            vol.Optional(
                CUSTOM_CHIMES_PATH_KEY,
                description={"suggested_value": data[CUSTOM_CHIMES_PATH_KEY]},
            ): str,
            vol.Required(TEMP_CHIMES_PATH_KEY, default=data[TEMP_CHIMES_PATH_KEY]): str,
            vol.Required(TEMP_PATH_KEY, default=data[TEMP_PATH_KEY]): str,
            vol.Required(WWW_PATH_KEY, default=data[WWW_PATH_KEY]): str,
            vol.Required(ADD_COVER_ART_KEY, default=data[ADD_COVER_ART_KEY]): bool,
        }
    )


def _normalize_string(value: Any) -> str:
    """Normalize a string-like value."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _normalize_bool(value: Any) -> bool:
    """Normalize a bool-like value."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in {"1", "true", "yes", "on"}
    return bool(value)


def _normalize_int(value: Any, default: Any, required: bool) -> int | str:
    """Normalize a numeric value."""
    if value in (None, ""):
        return default if required else ""
    if isinstance(value, bool):
        raise TypeError("invalid_int")
    return int(value)


def _normalize_tts_platform(platform: str, installed_tts_platforms: list[str]) -> str:
    """Normalize a selected TTS platform back to its canonical value."""
    if not platform:
        return ""

    stripped_tts_platforms = [
        provider.lower()
        .replace("tts", "")
        .replace(" ", "")
        .replace(".", "")
        .replace("-", "")
        .replace("_", "")
        for provider in installed_tts_platforms
    ]
    selected_platform = (
        helpers.get_stripped_tts_platform(platform)
        .lower()
        .replace("tts", "")
        .replace(" ", "")
        .replace(".", "")
        .replace("-", "")
        .replace("_", "")
    )

    if not stripped_tts_platforms:
        raise LookupError("tts_platform_none")
    if selected_platform not in stripped_tts_platforms:
        raise LookupError("tts_platform_select")

    return installed_tts_platforms[stripped_tts_platforms.index(selected_platform)]


def _is_subdirectory(parent_dir: str, sub_dir: str) -> bool:
    """Return True when sub_dir is inside parent_dir."""
    try:
        parent_path = os.path.abspath(parent_dir)
        sub_path = os.path.abspath(sub_dir)
        return os.path.commonpath([parent_path]) == os.path.commonpath(
            [parent_path, sub_path]
        )
    except ValueError:
        return False


def ensure_trailing_slash(path: str) -> str:
    """Normalize a directory path to include a trailing slash."""
    normalized = _normalize_string(path)
    if not normalized:
        return ""
    if normalized == os.sep:
        return normalized
    return normalized.rstrip("/") + "/"


def _existing_directory_roots(candidates: list[str]) -> list[str]:
    """Return normalized existing directories in first-seen order."""
    roots: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        normalized = ensure_trailing_slash(candidate)
        if (
            normalized
            and normalized not in seen
            and os.path.isdir(normalized.rstrip("/"))
        ):
            seen.add(normalized)
            roots.append(normalized)
    return roots


def _path_badges(
    hass,
    path: str,
) -> list[str]:
    """Return descriptive badges for a path."""
    normalized = ensure_trailing_slash(path)
    if not normalized:
        return []

    badges: list[str] = []
    root_path = get_root_path(hass)
    normalized_path = normalized.rstrip("/") or "/"

    media_dirs = list((hass.config.media_dirs or {}).values())
    media_roots = _existing_directory_roots([*media_dirs, f"{root_path}/media"])
    for media_root in media_roots:
        if _is_subdirectory(media_root.rstrip("/"), normalized_path):
            badges.append("Media dir")
            break

    allowlist_dirs = list(hass.config.allowlist_external_dirs or [])
    for allowlist_dir in _existing_directory_roots(allowlist_dirs):
        if _is_subdirectory(allowlist_dir.rstrip("/"), normalized_path):
            badges.append("Allowlisted")
            break

    web_root = ensure_trailing_slash(f"{root_path}/config/www")
    if web_root and _is_subdirectory(web_root.rstrip("/"), normalized_path):
        badges.append("Web accessible")

    return badges


def _path_validation_message(field_key: str, is_allowed: bool) -> str:
    """Return a human-readable validation message for the picker selection."""
    if is_allowed:
        return "This folder can be selected for this setting."

    if field_key in {TEMP_CHIMES_PATH_KEY, TEMP_PATH_KEY}:
        return "Select a folder inside a configured media directory."

    if field_key == WWW_PATH_KEY:
        return (
            "Select a folder inside an allowlisted external directory, such as /media, or /config/www"
        )

    return "Select a valid folder for this setting."


def _normalize_provider_hint_key(provider: str | None) -> str:
    """Normalize a provider name for provider-specific hints."""
    normalized = helpers.get_stripped_tts_platform(provider or "")
    return PROVIDER_HINT_ALIASES.get(normalized, normalized)


def get_provider_hint(
    field_key: str,
    provider: str | None,
) -> dict[str, str] | None:
    """Return provider-specific hint metadata for a field."""
    normalized_provider = _normalize_provider_hint_key(provider)
    if not normalized_provider:
        return None

    return PROVIDER_HINTS_BY_FIELD.get(field_key, {}).get(normalized_provider)


def _list_matching_chime_files(path: str, limit: int = 5) -> list[str]:
    """Return a few matching chime-like files from a folder."""
    current_dir = ensure_trailing_slash(path).rstrip("/") or "/"
    if not os.path.isdir(current_dir):
        return []

    files: list[str] = []
    with os.scandir(current_dir) as entries:
        for entry in entries:
            if not entry.is_file():
                continue
            if os.path.splitext(entry.name)[1].lower() not in CHIME_FILE_EXTENSIONS:
                continue
            files.append(entry.name)

    files.sort(key=str.lower)
    return files[:limit]


def validate_path_field(
    hass,
    config_entry: config_entries.ConfigEntry,
    field_key: str,
    path: str,
    values: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return live validation details for a single path field."""
    normalized = _normalize_string(path)
    normalized_with_slash = ensure_trailing_slash(normalized)
    current_values = {
        **get_settings_data(hass, config_entry),
        **(values or {}),
        field_key: normalized,
    }
    is_allowed = is_path_allowed_for_field(
        hass,
        config_entry,
        field_key,
        normalized_with_slash,
        current_values,
    )
    exists = bool(normalized) and os.path.isdir(normalized)

    if not normalized:
        message = FIELD_EMPTY_PATH_MESSAGES.get(field_key, "Enter a folder path.")
        tone = "muted" if message else ""
    elif field_key == CUSTOM_CHIMES_PATH_KEY and not os.path.isabs(normalized):
        message = "Enter an absolute folder path."
        tone = "error"
    elif is_allowed:
        message = "Folder path is valid for this setting."
        if not exists:
            message += " The folder does not exist yet."
        tone = "success"
    else:
        message = _path_validation_message(field_key, False)
        tone = "error"

    suggestion_paths: list[str] = []
    if (
        field_key in {TEMP_CHIMES_PATH_KEY, TEMP_PATH_KEY}
        and message == "Select a folder inside a configured media directory."
    ):
        root_path = get_root_path(hass)
        media_dirs = list((hass.config.media_dirs or {}).values())
        suggestion_paths = _existing_directory_roots([*media_dirs, f"{root_path}/media"])

    return {
        "field_key": field_key,
        "path": normalized,
        "valid": is_allowed,
        "exists": exists,
        "tone": tone,
        "message": message,
        "badges": _path_badges(hass, normalized_with_slash),
        "suggestion_paths": suggestion_paths,
        "can_use_anyway": bool(normalized) and not is_allowed,
    }


def get_browse_roots(
    hass,
    config_entry: config_entries.ConfigEntry,
    field_key: str,
    values: dict[str, Any] | None = None,
) -> list[str]:
    """Return allowed browse roots for a path field."""
    current_values = values or get_settings_data(hass, config_entry)
    configured_path = _normalize_string(current_values.get(field_key))
    root_path = get_root_path(hass)

    if field_key == CUSTOM_CHIMES_PATH_KEY:
        return _existing_directory_roots(
            [
                configured_path,
                "/config",
                "/media",
                "/share",
                "/tmp",
                "/",
            ]
        )

    if field_key in {TEMP_CHIMES_PATH_KEY, TEMP_PATH_KEY}:
        media_dirs = list((hass.config.media_dirs or {}).values())
        return _existing_directory_roots([configured_path, *media_dirs, "/media"])

    if field_key == WWW_PATH_KEY:
        allowlist_dirs = list(hass.config.allowlist_external_dirs or [])
        return _existing_directory_roots(
            [
                configured_path,
                f"{root_path}/config/www",
                f"{root_path}/media",
                *allowlist_dirs,
            ]
        )

    return []


def is_path_allowed_for_field(
    hass,
    config_entry: config_entries.ConfigEntry,
    field_key: str,
    path: str,
    values: dict[str, Any] | None = None,
) -> bool:
    """Return True when a browsed path is allowed for the target field."""
    normalized = ensure_trailing_slash(path)
    if not normalized:
        return False

    if field_key == CUSTOM_CHIMES_PATH_KEY:
        return os.path.isabs(normalized)

    for root in get_browse_roots(hass, config_entry, field_key, values):
        if _is_subdirectory(root.rstrip("/"), normalized.rstrip("/")):
            return True

    return False


def is_path_navigable_for_field(
    hass,
    config_entry: config_entries.ConfigEntry,
    field_key: str,
    path: str,
    values: dict[str, Any] | None = None,
) -> bool:
    """Return True when a path can be visited while browsing for a field."""
    normalized = ensure_trailing_slash(path)
    if not normalized:
        return False

    if field_key == CUSTOM_CHIMES_PATH_KEY:
        return os.path.isabs(normalized)

    normalized_path = normalized.rstrip("/") or "/"
    for root in get_browse_roots(hass, config_entry, field_key, values):
        normalized_root = root.rstrip("/") or "/"
        if _is_subdirectory(normalized_root, normalized_path) or _is_subdirectory(
            normalized_path, normalized_root
        ):
            return True

    return False


def build_directory_browser_payload(
    hass,
    config_entry: config_entries.ConfigEntry,
    field_key: str,
    path: str | None = None,
    *,
    values: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a directory listing payload for the custom panel."""
    if field_key not in PATH_BROWSABLE_FIELD_KEYS:
        raise ValueError("unsupported_field")

    current_values = values or get_settings_data(hass, config_entry)
    allowed_roots = get_browse_roots(hass, config_entry, field_key, current_values)
    requested_path = ensure_trailing_slash(path or _normalize_string(current_values.get(field_key)))
    current_path = requested_path

    if not current_path or not is_path_navigable_for_field(
        hass, config_entry, field_key, current_path, current_values
    ):
        current_path = ensure_trailing_slash("/")

    current_dir = current_path.rstrip("/") or "/"
    if not os.path.isdir(current_dir):
        raise FileNotFoundError(current_dir)

    directories: list[dict[str, str]] = []
    with os.scandir(current_dir) as entries:
        for entry in entries:
            if not entry.is_dir():
                continue
            entry_path = ensure_trailing_slash(entry.path)
            if not is_path_navigable_for_field(
                hass, config_entry, field_key, entry_path, current_values
            ):
                continue
            directories.append(
                {
                    "name": entry.name,
                    "path": entry_path,
                    "badges": _path_badges(hass, entry_path),
                }
            )

    directories.sort(key=lambda item: item["name"].lower())

    parent_dir = os.path.dirname(current_dir.rstrip("/")) or "/"
    parent_path = ensure_trailing_slash(parent_dir)
    if parent_path == current_path or not is_path_navigable_for_field(
        hass, config_entry, field_key, parent_path, current_values
    ):
        parent_path = None

    field = SETTINGS_FIELD_MAP[field_key]
    current_path_allowed = is_path_allowed_for_field(
        hass, config_entry, field_key, current_path, current_values
    )
    current_preview_files = (
        _list_matching_chime_files(current_path)
        if field_key == CUSTOM_CHIMES_PATH_KEY
        else []
    )
    return {
        "field_key": field_key,
        "title": field.label,
        "current_path": current_path,
        "parent_path": parent_path,
        "current_path_allowed": current_path_allowed,
        "current_path_validation_message": _path_validation_message(
            field_key, current_path_allowed
        ),
        "current_path_badges": _path_badges(hass, current_path),
        "preview_files": current_preview_files,
        "roots": [
            {
                "name": root.rstrip("/").split("/")[-1] or "/",
                "path": root,
                "badges": _path_badges(hass, root),
            }
            for root in allowed_roots
        ],
        "directories": directories,
    }


def validate_settings(
    hass,
    config_entry: config_entries.ConfigEntry,
    user_input: dict[str, Any],
    *,
    allow_invalid_paths: set[str] | None = None,
) -> ValidationResult:
    """Validate submitted settings and normalize values for storage."""
    current_data = get_settings_data(hass, config_entry)
    normalized: dict[str, Any] = {}
    errors: dict[str, str] = {}
    allow_invalid_paths = allow_invalid_paths or set()

    try:
        normalized[QUEUE_TIMEOUT_KEY] = _normalize_int(
            user_input.get(QUEUE_TIMEOUT_KEY),
            current_data[QUEUE_TIMEOUT_KEY],
            required=True,
        )
        if normalized[QUEUE_TIMEOUT_KEY] < 0:
            errors["base"] = "timeout"
            errors[QUEUE_TIMEOUT_KEY] = "timeout_sub"
    except (TypeError, ValueError):
        errors["base"] = "timeout"
        errors[QUEUE_TIMEOUT_KEY] = "timeout_sub"
        normalized[QUEUE_TIMEOUT_KEY] = current_data[QUEUE_TIMEOUT_KEY]

    try:
        normalized[TTS_TIMEOUT_KEY] = _normalize_int(
            user_input.get(TTS_TIMEOUT_KEY),
            current_data[TTS_TIMEOUT_KEY],
            required=True,
        )
        if normalized[TTS_TIMEOUT_KEY] < -1:
            errors["base"] = "timeout"
            errors[TTS_TIMEOUT_KEY] = "timeout_sub"
    except (TypeError, ValueError):
        errors["base"] = "timeout"
        errors[TTS_TIMEOUT_KEY] = "timeout_sub"
        normalized[TTS_TIMEOUT_KEY] = current_data[TTS_TIMEOUT_KEY]

    for field_key in (OFFSET_KEY, CROSSFADE_KEY, FADE_TRANSITION_KEY):
        try:
            normalized[field_key] = _normalize_int(
                user_input.get(field_key),
                current_data[field_key],
                required=True,
            )
        except (TypeError, ValueError):
            normalized[field_key] = current_data[field_key]
            errors[field_key] = "invalid_number"

    try:
        normalized[REMOVE_TEMP_FILE_DELAY_KEY] = _normalize_int(
            user_input.get(REMOVE_TEMP_FILE_DELAY_KEY),
            "",
            required=False,
        )
    except (TypeError, ValueError):
        normalized[REMOVE_TEMP_FILE_DELAY_KEY] = current_data[
            REMOVE_TEMP_FILE_DELAY_KEY
        ]
        errors[REMOVE_TEMP_FILE_DELAY_KEY] = "invalid_number"

    if normalized[CROSSFADE_KEY] < 0:
        errors[CROSSFADE_KEY] = "invalid_number"
    if normalized[FADE_TRANSITION_KEY] < 0:
        errors[FADE_TRANSITION_KEY] = "invalid_number"
    if (
        normalized[REMOVE_TEMP_FILE_DELAY_KEY] != ""
        and normalized[REMOVE_TEMP_FILE_DELAY_KEY] < 0
    ):
        errors[REMOVE_TEMP_FILE_DELAY_KEY] = "invalid_number"

    for field_key in (
        DEFAULT_LANGUAGE_KEY,
        DEFAULT_VOICE_KEY,
        DEFAULT_TLD_KEY,
        CUSTOM_CHIMES_PATH_KEY,
        TEMP_CHIMES_PATH_KEY,
        TEMP_PATH_KEY,
        WWW_PATH_KEY,
    ):
        normalized[field_key] = _normalize_string(user_input.get(field_key))

    normalized[ADD_COVER_ART_KEY] = _normalize_bool(user_input.get(ADD_COVER_ART_KEY))

    installed_tts_platforms = get_tts_platforms(hass)
    for field_key in (TTS_PLATFORM_KEY, FALLBACK_TTS_PLATFORM_KEY):
        try:
            normalized[field_key] = _normalize_tts_platform(
                _normalize_string(user_input.get(field_key)),
                installed_tts_platforms,
            )
        except LookupError as error:
            normalized[field_key] = _normalize_string(user_input.get(field_key))
            errors[field_key] = str(error)

    temp_folder_in_media_dir = False
    media_dirs_dict = hass.config.media_dirs or {}
    for media_dir in media_dirs_dict.values():
        if _is_subdirectory(media_dir, normalized[TEMP_PATH_KEY]):
            temp_folder_in_media_dir = True
            break
    if not temp_folder_in_media_dir and TEMP_PATH_KEY not in allow_invalid_paths:
        errors[TEMP_PATH_KEY] = TEMP_PATH_KEY

    external_folder_in_external_dirs = False
    external_dirs = hass.config.allowlist_external_dirs or {}
    for external_dir in external_dirs:
        if _is_subdirectory(external_dir, normalized[WWW_PATH_KEY]):
            external_folder_in_external_dirs = True
            break

    root_path = get_root_path(hass)
    if not external_folder_in_external_dirs:
        www_path = normalized[WWW_PATH_KEY]
        if not (
            www_path.startswith(f"{root_path}/media/")
            or www_path.startswith(f"{root_path}/config/www/")
        ):
            if WWW_PATH_KEY not in allow_invalid_paths:
                errors[WWW_PATH_KEY] = WWW_PATH_KEY

    restart_required = _normalize_string(
        normalized[CUSTOM_CHIMES_PATH_KEY]
    ) != _normalize_string(config_entry.options.get(CUSTOM_CHIMES_PATH_KEY))

    return ValidationResult(
        data=normalized,
        errors=errors,
        restart_required=restart_required,
    )


def build_panel_payload(
    hass,
    config_entry: config_entries.ConfigEntry,
    *,
    values: dict[str, Any] | None = None,
    notify_profiles: list[dict[str, Any]] | None = None,
    notify_profile_errors: list[dict[str, str]] | None = None,
    errors: dict[str, str] | None = None,
    message: str | None = None,
    message_type: str | None = None,
    restart_required: bool = False,
) -> dict[str, Any]:
    """Build the payload used by the custom panel."""
    values = values or get_settings_data(hass, config_entry)
    loaded_notify_profiles, notify_profiles_load_error = load_notify_profiles(hass)
    if notify_profiles is None:
        notify_profiles = loaded_notify_profiles
    tts_platforms = get_tts_platforms(hass)
    chime_options = get_notify_chime_options()
    field_options = {
        TTS_PLATFORM_KEY: [{"value": "", "label": "Not set"}]
        + [{"value": option, "label": option} for option in tts_platforms],
        FALLBACK_TTS_PLATFORM_KEY: [{"value": "", "label": "Not set"}]
        + [{"value": option, "label": option} for option in tts_platforms],
        DEFAULT_TLD_KEY: TLD_OPTIONS,
    }
    default_provider = _normalize_string(values.get(TTS_PLATFORM_KEY))
    fallback_provider = _normalize_string(values.get(FALLBACK_TTS_PLATFORM_KEY))

    return {
        "version": VERSION,
        "icon_url": f"/api/{DOMAIN}/icon.svg?v={VERSION.lstrip('v') or VERSION}",
        "documentation_url": CONFIGURATION_DOCS_BASE_URL,
        "logs_url": f"/config/logs?filter={DOMAIN}",
        "fallback_note": "The standard Configure dialog still works and remains available as a fallback.",
        "restart_note": "Changing the custom chimes folder or its contents requires a Home Assistant restart.",
        "message": message,
        "message_type": message_type,
        "restart_required": restart_required,
        "restart_required_field_keys": sorted(RESTART_REQUIRED_FIELD_KEYS),
        "errors": errors or {},
        "values": values,
        "notify_profiles": notify_profiles,
        "notify_profile_errors": notify_profile_errors or [],
        "notify_profiles_load_error": notify_profiles_load_error,
        "log_events": get_panel_log_events(hass),
        "sections": [
            {
                "key": section["key"],
                "title": section["title"],
                "description": section["description"],
                "fields": [
                    {
                        "key": field.key,
                        "label": field.label,
                        "description": field.description,
                        "docs_url": FIELD_DOCUMENTATION_URLS.get(field.key),
                        "icon_url": f"/api/{DOMAIN}/option_icons/{field.key}.svg",
                        "type": field.field_type,
                        "required": field.required,
                        "allow_custom_value": field.allow_custom_value,
                        "min": field.min_value,
                        "step": field.step,
                        "wide": field.wide,
                        "advanced": field.advanced,
                        "empty_default_hint": FIELD_EMPTY_DEFAULT_HINTS.get(field.key),
                        "placeholder": FIELD_PLACEHOLDERS.get(field.key),
                        "provider_hint": get_provider_hint(
                            field.key,
                            fallback_provider
                            if field.key == FALLBACK_TTS_PLATFORM_KEY
                            else default_provider,
                        ),
                        "provider_hints": PROVIDER_HINTS_BY_FIELD.get(field.key, {}),
                        "can_browse": field.key in PATH_BROWSABLE_FIELD_KEYS,
                        "path_validation": (
                            validate_path_field(
                                hass,
                                config_entry,
                                field.key,
                                _normalize_string(values.get(field.key)),
                                values,
                            )
                            if field.key in PATH_BROWSABLE_FIELD_KEYS
                            else None
                        ),
                        "options": field_options.get(field.key, []),
                    }
                    for field in (
                        SETTINGS_FIELD_MAP[field_key] for field_key in section["fields"]
                    )
                ],
            }
            for section in SETTINGS_SECTIONS
        ]
        + [
            {
                "key": "notify_profiles",
                "kind": "notify_profiles",
                "title": "Notification Profiles",
                "description": "Create and manage notify services for Chime TTS to easily send Chime TTS notifications in automations and scripts. Saving changes requires a Home Assistant restart.",
                "docs_url": NOTIFY_DOCS_URL,
                "profile_fields": [
                    {
                        **field,
                        "docs_url": NOTIFY_FIELD_DOCUMENTATION_URLS.get(
                            field["key"], NOTIFY_DOCS_URL
                        ),
                        "options": (
                            [{"value": "", "label": "Not set"}]
                            + [{"value": option, "label": option} for option in tts_platforms]
                            if field["key"] == "tts_platform"
                            else (
                                TLD_OPTIONS
                                if field["key"] == "tld"
                                else (
                                    chime_options
                                    if field["key"] in {"chime_path", "end_chime_path"}
                                    else []
                                )
                            )
                        ),
                    }
                    for field in NOTIFY_PROFILE_SCHEMA_FIELDS
                ],
            },
            {
                "key": "logs",
                "kind": "logs",
                "title": "Logs",
                "description": "Review Chime TTS events captured during this Home Assistant session, including actions, generated media, and raw log output.",
                "docs_url": CONFIGURATION_DOCS_BASE_URL,
            },
        ],
        "notify_profile_template": dict(NOTIFY_PROFILE_DEFAULTS),
        "notify_chime_options": chime_options,
    }
