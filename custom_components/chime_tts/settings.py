"""Shared settings metadata and validation for Chime TTS."""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
import json
import os
from pathlib import Path
import shutil
from typing import Any
from urllib.parse import quote

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
    DEFAULT_POST_SCRIPT_KEY,
    DEFAULT_PRE_SCRIPT_KEY,
    DEFAULT_SCRIPTS_SHARED_KEY,
    DEFAULT_PRE_SCRIPT_SHARED_KEY,
    DEFAULT_POST_SCRIPT_SHARED_KEY,
    DEFAULT_PRE_SCRIPT_SAY_URL_KEY,
    DEFAULT_POST_SCRIPT_SAY_URL_KEY,
    DEFAULT_CHIME_OFFSETS,
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
    CHIME_SETS_KEY,
    CHIME_OFFSETS_KEY,
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
from .chime_sets import (
    normalize_sets,
    selector_options,
)

helpers = ChimeTTSHelper()

_INTEGRATION_ROOT = Path(__file__).resolve().parent
_FOOTER_LOGO_PATH = _INTEGRATION_ROOT / "panel" / "chime_tts.svg"
_OPTION_ICONS_PATH = _INTEGRATION_ROOT / "panel" / "images" / "option_icons"


def _footer_logo_url() -> str:
    """Return the cache-busted footer logo URL."""
    fallback_version = VERSION.lstrip("v") or VERSION
    try:
        asset_version = str(_FOOTER_LOGO_PATH.stat().st_mtime_ns)
    except OSError:
        asset_version = fallback_version
    return f"/api/{DOMAIN}/footer_logo.svg?v={asset_version}"


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

# Keep this aligned with Home Assistant's google_translate.SUPPORT_TLD list.
GOOGLE_TRANSLATE_TLDS = """
ad ae al am as at az ba be bf bg bi
bj bs bt by ca cat cd cf cg ch ci cl
cm cn co.ao co.bw co.ck co.cr co.id co.il co.in co.jp co.ke co.kr
co.ls co.ma co.mz co.nz co.th co.tz co.ug co.uk co.uz co.ve co.vi co.za
co.zm co.zw com com.af com.ag com.ai com.ar com.au com.bd com.bh com.bn com.bo
com.br com.bz com.co com.cu com.cy com.do com.ec com.eg com.et com.fj com.gh com.gi
com.gt com.hk com.jm com.kh com.kw com.lb com.ly com.mm com.mt com.mx com.my com.na
com.ng com.ni com.np com.om com.pa com.pe com.pg com.ph com.pk com.pr com.py com.qa
com.sa com.sb com.sg com.sl com.sv com.tj com.tr com.tw com.ua com.uy com.vc com.vn
cv cz de dj dk dm dz ee es fi fm fr
ga ge gg gl gm gr gy hn hr ht hu ie
im iq is it je jo kg ki kz la li lk
lt lu lv md me mg mk ml mn ms mu mv
mw ne nl no nr nu pl pn ps pt ro rs
ru rw sc se sh si sk sm sn so sr st
td tg tl tm tn to tt vg vu ws
""".split()

GOOGLE_TRANSLATE_TLD_NAMES = {
    "ad": "Andorra", "ae": "United Arab Emirates", "al": "Albania", "am": "Armenia", "as": "American Samoa", "at": "Austria", "az": "Azerbaijan", "ba": "Bosnia and Herzegovina", "be": "Belgium", "bf": "Burkina Faso", "bg": "Bulgaria", "bi": "Burundi", "bj": "Benin", "bs": "Bahamas", "bt": "Bhutan", "by": "Belarus", "ca": "Canada", "cat": "Catalan", "cd": "Democratic Republic of the Congo", "cf": "Central African Republic", "cg": "Republic of the Congo", "ch": "Switzerland", "ci": "Côte d’Ivoire", "cl": "Chile", "cm": "Cameroon", "cn": "China",
    "co.ao": "Angola", "co.bw": "Botswana", "co.ck": "Cook Islands", "co.cr": "Costa Rica", "co.id": "Indonesia", "co.il": "Israel", "co.in": "India", "co.jp": "Japan", "co.ke": "Kenya", "co.kr": "South Korea", "co.ls": "Lesotho", "co.ma": "Morocco", "co.mz": "Mozambique", "co.nz": "New Zealand", "co.th": "Thailand", "co.tz": "Tanzania", "co.ug": "Uganda", "co.uk": "United Kingdom", "co.uz": "Uzbekistan", "co.ve": "Venezuela", "co.vi": "U.S. Virgin Islands", "co.za": "South Africa", "co.zm": "Zambia", "co.zw": "Zimbabwe",
    "com": "Global", "com.af": "Afghanistan", "com.ag": "Antigua and Barbuda", "com.ai": "Anguilla", "com.ar": "Argentina", "com.au": "Australia", "com.bd": "Bangladesh", "com.bh": "Bahrain", "com.bn": "Brunei", "com.bo": "Bolivia", "com.br": "Brazil", "com.bz": "Belize", "com.co": "Colombia", "com.cu": "Cuba", "com.cy": "Cyprus", "com.do": "Dominican Republic", "com.ec": "Ecuador", "com.eg": "Egypt", "com.et": "Ethiopia", "com.fj": "Fiji", "com.gh": "Ghana", "com.gi": "Gibraltar", "com.gt": "Guatemala", "com.hk": "Hong Kong", "com.jm": "Jamaica", "com.kh": "Cambodia", "com.kw": "Kuwait", "com.lb": "Lebanon", "com.ly": "Libya", "com.mm": "Myanmar", "com.mt": "Malta", "com.mx": "Mexico", "com.my": "Malaysia", "com.na": "Namibia", "com.ng": "Nigeria", "com.ni": "Nicaragua", "com.np": "Nepal", "com.om": "Oman", "com.pa": "Panama", "com.pe": "Peru", "com.pg": "Papua New Guinea", "com.ph": "Philippines", "com.pk": "Pakistan", "com.pr": "Puerto Rico", "com.py": "Paraguay", "com.qa": "Qatar", "com.sa": "Saudi Arabia", "com.sb": "Solomon Islands", "com.sg": "Singapore", "com.sl": "Sierra Leone", "com.sv": "El Salvador", "com.tj": "Tajikistan", "com.tr": "Türkiye", "com.tw": "Taiwan", "com.ua": "Ukraine", "com.uy": "Uruguay", "com.vc": "Saint Vincent and the Grenadines", "com.vn": "Vietnam",
    "cv": "Cape Verde", "cz": "Czech Republic", "de": "Germany", "dj": "Djibouti", "dk": "Denmark", "dm": "Dominica", "dz": "Algeria", "ee": "Estonia", "es": "Spain", "fi": "Finland", "fm": "Micronesia", "fr": "France", "ga": "Gabon", "ge": "Georgia", "gg": "Guernsey", "gl": "Greenland", "gm": "Gambia", "gr": "Greece", "gy": "Guyana", "hn": "Honduras", "hr": "Croatia", "ht": "Haiti", "hu": "Hungary", "ie": "Ireland", "im": "Isle of Man", "iq": "Iraq", "is": "Iceland", "it": "Italy", "je": "Jersey", "jo": "Jordan", "kg": "Kyrgyzstan", "ki": "Kiribati", "kz": "Kazakhstan", "la": "Laos", "li": "Liechtenstein", "lk": "Sri Lanka", "lt": "Lithuania", "lu": "Luxembourg", "lv": "Latvia", "md": "Moldova", "me": "Montenegro", "mg": "Madagascar", "mk": "North Macedonia", "ml": "Mali", "mn": "Mongolia", "ms": "Montserrat", "mu": "Mauritius", "mv": "Maldives", "mw": "Malawi", "ne": "Niger", "nl": "Netherlands", "no": "Norway", "nr": "Nauru", "nu": "Niue", "pl": "Poland", "pn": "Pitcairn", "ps": "Palestine", "pt": "Portugal", "ro": "Romania", "rs": "Serbia", "ru": "Russia", "rw": "Rwanda", "sc": "Seychelles", "se": "Sweden", "sh": "Saint Helena", "si": "Slovenia", "sk": "Slovakia", "sm": "San Marino", "sn": "Senegal", "so": "Somalia", "sr": "Suriname", "st": "São Tomé and Príncipe", "td": "Chad", "tg": "Togo", "tl": "Timor-Leste", "tm": "Turkmenistan", "tn": "Tunisia", "to": "Tonga", "tt": "Trinidad and Tobago", "vg": "British Virgin Islands", "vu": "Vanuatu", "ws": "Samoa",
}

TLD_OPTIONS = [{"value": "", "label": "Provider default"}] + [
    {"value": tld, "label": f"{tld} — {GOOGLE_TRANSLATE_TLD_NAMES[tld]}"}
    for tld in GOOGLE_TRANSLATE_TLDS
]

PATH_BROWSABLE_FIELD_KEYS = {
    CUSTOM_CHIMES_PATH_KEY,
    TEMP_CHIMES_PATH_KEY,
    TEMP_PATH_KEY,
    WWW_PATH_KEY,
}
RESTART_REQUIRED_FIELD_KEYS: set[str] = set()
CHIME_FILE_EXTENSIONS = {
    ".aac",
    ".aif",
    ".aiff",
    ".ape",
    ".flac",
    ".m4a",
    ".mp3",
    ".ogg",
    ".oga",
    ".wav",
    ".wma",
}
FIELD_EMPTY_DEFAULT_HINTS = {
}

FIELD_PLACEHOLDERS = {
    DEFAULT_LANGUAGE_KEY: "Blank means the selected provider chooses the language.",
    DEFAULT_VOICE_KEY: "Blank means the selected provider chooses the voice.",
    DEFAULT_TLD_KEY: "Blank means Google Translate uses its default dialect.",
    DEFAULT_PRE_SCRIPT_KEY: "Enter script.name, or YAML with script and data fields.",
    DEFAULT_POST_SCRIPT_KEY: "Enter script.name, or YAML with script and data fields.",
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
KNOWN_TTS_PROVIDER_ALIASES = {
    AMAZON_POLLY.lower(): AMAZON_POLLY,
    "amazonpolly": AMAZON_POLLY,
    BAIDU.lower(): BAIDU,
    "baidu": BAIDU,
    ELEVENLABS.lower(): ELEVENLABS,
    "elevenlabs": ELEVENLABS,
    GOOGLE_CLOUD.lower(): GOOGLE_CLOUD,
    "googlecloud": GOOGLE_CLOUD,
    GOOGLE_TRANSLATE.lower(): GOOGLE_TRANSLATE,
    "googletranslate": GOOGLE_TRANSLATE,
    IBM_WATSON_TTS.lower(): IBM_WATSON_TTS,
    "ibmwatson": IBM_WATSON_TTS,
    "watsontts": IBM_WATSON_TTS,
    MARYTTS.lower(): MARYTTS,
    "marytts": MARYTTS,
    MICROSOFT_TTS.lower(): MICROSOFT_TTS,
    "microsofttts": MICROSOFT_TTS,
    MICROSOFT_EDGE_TTS.lower(): MICROSOFT_EDGE_TTS,
    "microsoftedgetts": MICROSOFT_EDGE_TTS,
    "edgetts": MICROSOFT_EDGE_TTS,
    NABU_CASA_CLOUD_TTS.lower(): NABU_CASA_CLOUD_TTS,
    NABU_CASA_CLOUD_TTS_OLD.lower(): NABU_CASA_CLOUD_TTS,
    "nabucasa": NABU_CASA_CLOUD_TTS,
    "nabucasacloud": NABU_CASA_CLOUD_TTS,
    "nabucasacloudtts": NABU_CASA_CLOUD_TTS,
    "cloudsay": NABU_CASA_CLOUD_TTS,
    OPENAI_TTS.lower(): OPENAI_TTS,
    "openaitts": OPENAI_TTS,
    PICOTTS.lower(): PICOTTS,
    "picotts": PICOTTS,
    PIPER.lower(): PIPER,
    "piper": PIPER,
    VOICE_RSS.lower(): VOICE_RSS,
    "voicerss": VOICE_RSS,
    YANDEX_TTS.lower(): YANDEX_TTS,
    "yandex": YANDEX_TTS,
    "yandextts": YANDEX_TTS,
}

CONFIGURATION_DOCS_BASE_URL = (
    "https://nimroddolev.github.io/chime_tts/docs/documentation/configuration/"
)
NOTIFY_DOCS_URL = (
    "https://nimroddolev.github.io/chime_tts/docs/documentation/notify/"
)
CHIME_SETS_DOCS_URL = (
    "https://nimroddolev.github.io/chime_tts/docs/documentation/chime-sets/"
)
CHIMES_DOCS_URL = "https://nimroddolev.github.io/chime_tts/docs/documentation/chimes/"
SAY_ACTION_PARAMS_DOCS_URL = (
    "https://nimroddolev.github.io/chime_tts/docs/documentation/actions/say-action/parameters/"
)
PROJECT_HOME_URL = "https://nimroddolev.github.io/chime_tts"
QUICK_START_URL = "https://nimroddolev.github.io/chime_tts/docs/quick-start/installing-chime-tts"
SUPPORT_DISCUSSION_URL = (
    "https://community.home-assistant.io/t/chime-tts-play-audio-before-after-tts-audio-lag-free/578430"
)
BUY_ME_A_COFFEE_URL = "https://www.buymeacoffee.com/nimroddolev"
ISSUE_TRACKER_URL = "https://github.com/nimroddolev/chime_tts/issues"

ABOUT_ITEMS: tuple[dict[str, Any], ...] = (
    {
        "key": "documentation",
        "title": "Documentation",
        "description": "Read the official documentation for setup, configuration, actions, and examples.",
        "url": PROJECT_HOME_URL,
        "link_label": "Open Docs",
    },
    {
        "key": "bugs",
        "title": "Report Bugs",
        "description": "Found a bug or regression? Open an issue with reproduction steps and logs.",
        "url": ISSUE_TRACKER_URL,
        "link_label": "Open Issue Tracker",
    },
    {
        "key": "feature_requests",
        "title": "Feature Requests",
        "description": "Share improvement ideas and requested features through the GitHub issue tracker.",
        "url": ISSUE_TRACKER_URL,
        "link_label": "Request a Feature",
    },
    {
        "key": "support",
        "title": "Support & Discussion",
        "description": "Ask questions, share use cases, and get help from the Home Assistant community.",
        "url": SUPPORT_DISCUSSION_URL,
        "link_label": "Open Community Thread",
    },
    {
        "key": "coffee",
        "title": "Buy Me a Coffee",
        "description": "If Chime TTS has been useful, you can support ongoing maintenance and development.",
        "url": BUY_ME_A_COFFEE_URL,
        "link_label": "Support the Project",
    },
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
        "key": "pre_script",
        "label": "Pre-playback script",
        "type": "textarea",
        "description": "Runs before playback. Supports script.name or YAML with script and data fields.",
        "placeholder": "eg: script.mute_tv",
    },
    {
        "key": "post_script",
        "label": "Post-playback script",
        "type": "textarea",
        "description": "Runs after playback. Supports script.name or YAML with script and data fields.",
        "placeholder": "eg script.unmute_tv",
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
    "pre_script",
    "post_script",
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
    "pre_script": "",
    "post_script": "",
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
    DEFAULT_PRE_SCRIPT_KEY: f"{SAY_ACTION_PARAMS_DOCS_URL}#pre_script",
    DEFAULT_POST_SCRIPT_KEY: f"{SAY_ACTION_PARAMS_DOCS_URL}#post_script",
    DEFAULT_PRE_SCRIPT_SAY_URL_KEY: f"{SAY_ACTION_PARAMS_DOCS_URL}#pre_script",
    DEFAULT_POST_SCRIPT_SAY_URL_KEY: f"{SAY_ACTION_PARAMS_DOCS_URL}#post_script",
    FALLBACK_TTS_PLATFORM_KEY: f"{CONFIGURATION_DOCS_BASE_URL}#fallback-tts-platform",
    OFFSET_KEY: f"{CONFIGURATION_DOCS_BASE_URL}#default-offset",
    CROSSFADE_KEY: (
        "https://nimroddolev.github.io/chime_tts/docs/documentation/"
        "configuration/playback-options/#default-crossfade"
    ),
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
    "pre_script": f"{SAY_ACTION_PARAMS_DOCS_URL}#pre_script",
    "post_script": f"{SAY_ACTION_PARAMS_DOCS_URL}#post_script",
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
        description="Used when no TTS platform was specified",
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
    ),
    SettingsField(
        key=DEFAULT_VOICE_KEY,
        label="Default voice",
        description="Applied with the default TTS platform when supported.",
        field_type="text",
        section="voice",
    ),
    SettingsField(
        key=DEFAULT_TLD_KEY,
        label="Default dialect",
        description="Google Translate TTS dialect fallback.",
        field_type="select",
        section="voice",
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
        key=DEFAULT_PRE_SCRIPT_KEY,
        label="Default pre-playback script",
        description="Runs before playback when an action does not specify pre_script. Supports script.name or YAML with script and data fields.",
        field_type="textarea",
        section="general",
    ),
    SettingsField(
        key=DEFAULT_POST_SCRIPT_KEY,
        label="Default post-playback script",
        description="Runs after playback when an action does not specify post_script. Supports script.name or YAML with script and data fields.",
        field_type="textarea",
        section="general",
    ),
    SettingsField(
        key=DEFAULT_PRE_SCRIPT_SHARED_KEY,
        label="Use for both chime_tts.say & chime_tts.say_url actions",
        description="",
        field_type="boolean",
        section="general",
    ),
    SettingsField(
        key=DEFAULT_POST_SCRIPT_SHARED_KEY,
        label="Use for both chime_tts.say & chime_tts.say_url actions",
        description="",
        field_type="boolean",
        section="general",
    ),
    SettingsField(
        key=DEFAULT_PRE_SCRIPT_SAY_URL_KEY,
        label="Default pre-playback script for chime_tts.say_url",
        description="Runs before chime_tts.say_url generates audio.",
        field_type="textarea",
        section="general",
    ),
    SettingsField(
        key=DEFAULT_POST_SCRIPT_SAY_URL_KEY,
        label="Default post-playback script for chime_tts.say_url",
        description="Runs after chime_tts.say_url generates audio.",
        field_type="textarea",
        section="general",
    ),
    SettingsField(
        key="chime_path",
        label="Start chime",
        description="Optional chime to play before generated speech.",
        field_type="select",
        section="playback",
    ),
    SettingsField(
        key="end_chime_path",
        label="End chime",
        description="Optional chime to play after generated speech.",
        field_type="select",
        section="playback",
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
        description="Folder containing your own chime audio files.",
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
    ),
    SettingsField(
        key=TEMP_PATH_KEY,
        label="Temporary audio folder",
        description="Must stay inside a configured media directory.",
        field_type="text",
        section="audio_folders",
        required=True,
        wide=True,
    ),
    SettingsField(
        key=WWW_PATH_KEY,
        label="say_url output folder",
        description="Must stay inside an allowlisted external directory, /media, or /config/www.",
        field_type="text",
        section="audio_folders",
        required=True,
        wide=True,
    ),
)

SETTINGS_FIELD_MAP = {field.key: field for field in SETTINGS_FIELDS}

SETTINGS_SECTIONS = (
    {
        "key": "paths",
        "title": "Folder Paths",
        "description": "Folder paths for custom and downloaded chime audio files.",
        "fields": [
            CUSTOM_CHIMES_PATH_KEY,
            TEMP_CHIMES_PATH_KEY,
        ],
    },
    {
        "key": "voice",
        "title": "TTS Defaults & Fallback",
        "description": "Preferred TTS providers and their default language, voice, and dialect settings.",
        "fields": [
            TTS_PLATFORM_KEY,
            FALLBACK_TTS_PLATFORM_KEY,
            DEFAULT_LANGUAGE_KEY,
            DEFAULT_VOICE_KEY,
            DEFAULT_TLD_KEY,
        ],
    },
    {
        "key": "playback",
        "title": "Playback Options",
        "description": "Audio timing and cleanup defaults for generated announcements.",
        "fields": [
            "chime_path",
            "end_chime_path",
            OFFSET_KEY,
            CROSSFADE_KEY,
            FADE_TRANSITION_KEY,
            REMOVE_TEMP_FILE_DELAY_KEY,
            ADD_COVER_ART_KEY,
        ],
    },
    {
        "key": "audio_folders",
        "title": "Audio Files Folders",
        "description": "Folder paths for temporary and say_url generated audio files.",
        "fields": [
            TEMP_PATH_KEY,
            WWW_PATH_KEY,
        ],
    },
    {
        "key": "general",
        "title": "Action & Script Options",
        "description": "Core timeout behavior and default playback scripts used across the integration.",
        "fields": [
            QUEUE_TIMEOUT_KEY,
            TTS_TIMEOUT_KEY,
            DEFAULT_PRE_SCRIPT_KEY,
            DEFAULT_POST_SCRIPT_KEY,
            DEFAULT_PRE_SCRIPT_SHARED_KEY,
            DEFAULT_POST_SCRIPT_SHARED_KEY,
            DEFAULT_PRE_SCRIPT_SAY_URL_KEY,
            DEFAULT_POST_SCRIPT_SAY_URL_KEY,
        ],
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


def get_available_tts_platforms(hass) -> list[str]:
    """Return currently loaded TTS entity ids."""
    return sorted(helpers.get_installed_tts_platforms(hass))


def get_initial_tts_platforms(hass) -> list[str]:
    """Return the startup TTS platform baseline for this HA session."""
    domain_data = hass.data.get(DOMAIN, {}) if hass else {}
    initial_platforms = domain_data.get("_initial_tts_platforms", [])
    return sorted(str(platform) for platform in initial_platforms if str(platform))


def has_initial_tts_platform_baseline(hass) -> bool:
    """Return whether this HA boot has finished capturing its TTS baseline."""
    domain_data = hass.data.get(DOMAIN, {}) if hass else {}
    return "_initial_tts_platforms" in domain_data


def _normalize_tts_provider_identity(provider: str) -> str:
    """Normalize TTS provider names and entity ids to a comparable identity."""
    normalized = _normalize_string(provider).lower()
    if not normalized:
        return ""

    collapsed = "".join(character for character in normalized if character.isalnum())

    def _match_alias_prefix(candidate: str) -> str:
        """Return a canonical alias when a suffixed entity id starts with one."""
        collapsed_candidate = "".join(character for character in candidate if character.isalnum())
        for alias, canonical in KNOWN_TTS_PROVIDER_ALIASES.items():
            if candidate.startswith(f"{alias}_"):
                return canonical.lower()

            collapsed_alias = "".join(character for character in alias if character.isalnum())
            if not collapsed_alias:
                continue
            if candidate.startswith(f"{collapsed_alias}_"):
                return canonical.lower()
            if collapsed_candidate.startswith(collapsed_alias):
                return canonical.lower()

        return ""

    if normalized in KNOWN_TTS_PROVIDER_ALIASES:
        return KNOWN_TTS_PROVIDER_ALIASES[normalized].lower()
    if collapsed in KNOWN_TTS_PROVIDER_ALIASES:
        return KNOWN_TTS_PROVIDER_ALIASES[collapsed].lower()
    if normalized.startswith("tts."):
        suffix = normalized[4:]
        if suffix in KNOWN_TTS_PROVIDER_ALIASES:
            return KNOWN_TTS_PROVIDER_ALIASES[suffix].lower()
        collapsed_suffix = "".join(character for character in suffix if character.isalnum())
        if collapsed_suffix in KNOWN_TTS_PROVIDER_ALIASES:
            return KNOWN_TTS_PROVIDER_ALIASES[collapsed_suffix].lower()
        prefix_match = _match_alias_prefix(suffix)
        if prefix_match:
            return prefix_match

    stripped = _normalize_string(helpers.get_stripped_tts_platform(normalized)).lower()
    if stripped in KNOWN_TTS_PROVIDER_ALIASES:
        return KNOWN_TTS_PROVIDER_ALIASES[stripped].lower()
    stripped_collapsed = "".join(character for character in stripped if character.isalnum())
    if stripped_collapsed in KNOWN_TTS_PROVIDER_ALIASES:
        return KNOWN_TTS_PROVIDER_ALIASES[stripped_collapsed].lower()
    prefix_match = _match_alias_prefix(stripped)
    if prefix_match:
        return prefix_match
    prefix_match = _match_alias_prefix(stripped_collapsed)
    if prefix_match:
        return prefix_match
    return ""


def _format_tts_provider_display_name(candidate: str) -> str:
    """Return the provider string that should be shown in panel alerts."""
    return _normalize_string(candidate)


def _get_configured_tts_provider_candidates(hass) -> list[dict[str, str]]:
    """Return configured TTS providers with comparison ids and display names."""
    configured: list[dict[str, str]] = []
    seen_identities: set[str] = set()
    for entry in hass.config_entries.async_entries():
        raw_candidates = [
            str(getattr(entry, "title", "") or ""),
            str(getattr(entry, "name", "") or ""),
            str(entry.domain or ""),
        ]
        provider_identity = next(
            (
                normalized
                for normalized in (
                    _normalize_tts_provider_identity(candidate)
                    for candidate in raw_candidates
                )
                if normalized
            ),
            "",
        )
        if not provider_identity or provider_identity in seen_identities:
            continue

        display_name = next(
            (
                _format_tts_provider_display_name(candidate)
                for candidate in raw_candidates
                if _normalize_string(candidate)
            ),
            provider_identity,
        )
        configured.append(
            {
                "identity": provider_identity,
                "display_name": display_name,
            }
        )
        seen_identities.add(provider_identity)
    return configured


def _get_filesystem_tts_provider_candidates(hass) -> list[str]:
    """Return TTS provider integrations detected from custom_components on disk."""
    custom_components_path = Path(hass.config.path("custom_components"))
    if not custom_components_path.exists() or not custom_components_path.is_dir():
        return []

    detected: list[str] = []
    for entry in custom_components_path.iterdir():
        if not entry.is_dir():
            continue

        domain = entry.name
        manifest_path = entry / "manifest.json"
        if manifest_path.exists():
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                domain = str(manifest.get("domain") or domain)
            except (OSError, ValueError, TypeError):
                domain = entry.name

        provider = _normalize_tts_provider_identity(domain)
        if provider and provider not in detected:
            detected.append(provider)

    return detected


def _build_panel_alerts(hass) -> tuple[list[dict[str, Any]], str | None]:
    """Build startup alerts related to TTS provider availability."""
    # Do not interpret the small startup window before the post-start snapshot
    # as an empty provider list or as a list of newly installed providers.
    if not has_initial_tts_platform_baseline(hass):
        return [], None

    available_platforms = get_available_tts_platforms(hass)
    initial_platforms = get_initial_tts_platforms(hass)
    initial_provider_identities = {
        _normalize_tts_provider_identity(provider)
        for provider in initial_platforms
        if provider
    }
    newly_added_providers = [
        provider
        for provider in available_platforms
        if (
            normalized_provider := _normalize_tts_provider_identity(provider)
        )
        and normalized_provider not in initial_provider_identities
    ]

    alerts: list[dict[str, Any]] = []
    panel_tone: str | None = None

    if not available_platforms:
        alerts.append(
            {
                "tone": "error",
                "title": "No TTS providers detected",
                "message": "At least 1 TTS provider must be installed before Chime TTS can be used.",
                "action": {
                    "kind": "link",
                    "label": "Add TTS Provider",
                    "href": "/config/integrations/dashboard",
                },
            }
        )
        panel_tone = "error"
    elif newly_added_providers:
        provider_count = len(newly_added_providers)
        if provider_count == 1:
            provider_list = newly_added_providers[0]
        elif provider_count > 1:
            provider_list = (
                "</strong>, <strong>".join(newly_added_providers[:-1])
                + "</strong> and <strong>"
                + newly_added_providers[-1]
            )
        alerts.append(
            {
                "tone": "warning",
                "title": "1 New TTS Provider Detected"
                if provider_count == 1
                else f"{provider_count} New TTS Providers Detected",
                "message": f"To use the new {provider_list} TTS {'provider' if provider_count == 1 else 'providers'}, Home Assistant must be restarted.",
                "message_html": f"To use the new <strong>{provider_list}</strong> TTS {'provider' if provider_count == 1 else 'providers'}, Home Assistant must be restarted.",
                "highlighted_terms": newly_added_providers,
                "action": {
                    "kind": "restart",
                    "label": "Restart",
                },
            }
        )
        panel_tone = "warning"

    return alerts, panel_tone


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
        DEFAULT_PRE_SCRIPT_KEY: "",
        DEFAULT_POST_SCRIPT_KEY: "",
        DEFAULT_SCRIPTS_SHARED_KEY: True,
        DEFAULT_PRE_SCRIPT_SHARED_KEY: True,
        DEFAULT_POST_SCRIPT_SHARED_KEY: True,
        DEFAULT_PRE_SCRIPT_SAY_URL_KEY: "",
        DEFAULT_POST_SCRIPT_SAY_URL_KEY: "",
        FALLBACK_TTS_PLATFORM_KEY: "",
        "chime_path": "",
        "end_chime_path": "",
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
        if key in {DEFAULT_PRE_SCRIPT_SHARED_KEY, DEFAULT_POST_SCRIPT_SHARED_KEY}:
            if DEFAULT_SCRIPTS_SHARED_KEY in source:
                return source[DEFAULT_SCRIPTS_SHARED_KEY]

    return _field_default_value(key, hass)


def get_settings_data(
    hass,
    config_entry: config_entries.ConfigEntry,
    user_input: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Get current settings data."""
    values = {
        field.key: _get_entry_value(config_entry, field.key, hass, user_input)
        for field in SETTINGS_FIELDS
    }
    source = (
        user_input
        if user_input is not None and (CHIME_SETS_KEY in user_input or CHIME_OFFSETS_KEY in user_input)
        else config_entry.options
    )
    values[CHIME_SETS_KEY] = normalize_sets(source.get(CHIME_SETS_KEY))
    raw_offsets = source.get(CHIME_OFFSETS_KEY, {})
    if not isinstance(raw_offsets, dict):
        raw_offsets = {}
    values[CHIME_OFFSETS_KEY] = {
        **DEFAULT_CHIME_OFFSETS,
        **{
            str(key): int(value) for key, value in raw_offsets.items()
            if str(key) and isinstance(value, int | float | str) and str(value).lstrip("-").isdigit()
        },
    }
    return values


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
        raise TypeError("configuration.yaml must contain a mapping at the root level.")

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
        raise TypeError("services.yaml must contain a mapping at the root level.")
    return loaded


def get_loaded_chime_tts_platforms() -> list[str]:
    """Return the TTS provider options currently loaded into Chime TTS services."""
    try:
        services_yaml = _load_services_yaml()
        options = (
            services_yaml.get("say", {})
            .get("fields", {})
            .get("tts_platform", {})
            .get("selector", {})
            .get("select", {})
            .get("options", [])
        )
    except (OSError, ValueError, yaml.YAMLError):
        options = []

    loaded_platforms: list[str] = []
    for option in options:
        if not isinstance(option, dict):
            continue
        value = _normalize_string(option.get("value"))
        normalized = _normalize_tts_provider_identity(value)
        if normalized and normalized not in loaded_platforms:
            loaded_platforms.append(normalized)
    return loaded_platforms


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


def _with_chime_sets(
    chime_options: list[dict[str, str]], values: dict[str, Any]
) -> list[dict[str, str]]:
    """Append current Random Chime Sets without waiting for services.yaml reload."""
    options = [dict(option) for option in chime_options]
    known_values = {str(option.get("value", "")) for option in options}
    options.extend(
        option
        for option in selector_options(values)
        if option["value"] not in known_values
    )
    return options


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
    if isinstance(value, list | tuple):
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

    def _to_yaml_safe(item: Any) -> Any:
        if isinstance(item, Mapping):
            return {str(key): _to_yaml_safe(val) for key, val in item.items()}
        if isinstance(item, list):
            return [_to_yaml_safe(entry) for entry in item]
        if isinstance(item, tuple):
            return [_to_yaml_safe(entry) for entry in item]
        if isinstance(item, str):
            return str(item)
        if isinstance(item, bool):
            return bool(item)
        if isinstance(item, int):
            return int(item)
        if isinstance(item, float):
            return float(item)
        return item

    dumped = yaml.safe_dump(
        _to_yaml_safe(value),
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
        "pre_script",
        "post_script",
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


def _build_panel_sections(
    hass,
    config_entry: config_entries.ConfigEntry,
    values: dict[str, Any],
    *,
    field_options: dict[str, list[dict[str, Any]]],
    tts_platforms: list[str],
    chime_options: list[dict[str, Any]],
    default_provider: str,
    fallback_provider: str,
    include_path_validations: bool,
    icon_versioned: bool,
) -> list[dict[str, Any]]:
    """Build the shared panel sections payload used by both panel builders."""
    integration_version = VERSION.lstrip("v") or VERSION

    def icon_name(field_key: str) -> str:
        """Return the concise SVG filename for a configuration field."""
        if field_key.startswith("default_"):
            field_key = field_key.removeprefix("default_")
        return field_key.removesuffix("_key")

    def icon_url(field_key: str) -> str:
        """Return a versioned URL that also changes when the SVG asset changes."""
        filename = f"{icon_name(field_key)}.svg"
        url = f"/api/{DOMAIN}/images/option_icons/{filename}"
        if not icon_versioned:
            return url
        try:
            asset_version = _OPTION_ICONS_PATH.joinpath(filename).stat().st_mtime_ns
        except OSError:
            asset_version = integration_version
        return f"{url}?v={integration_version}&asset={asset_version}"

    def build_section(section: dict[str, Any]) -> dict[str, Any]:
        """Build a configuration section with its field metadata."""
        return {
            "key": section["key"],
            "title": section["title"],
            "description": section["description"],
            "fields": [
                {
                    "key": field.key,
                    "label": field.label,
                    "description": field.description,
                    "docs_url": FIELD_DOCUMENTATION_URLS.get(field.key),
                    "icon_url": icon_url(field.key),
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
                        fallback_provider if field.key == FALLBACK_TTS_PLATFORM_KEY else default_provider,
                    ),
                    "provider_hints": PROVIDER_HINTS_BY_FIELD.get(field.key, {}),
                    "can_browse": field.key in PATH_BROWSABLE_FIELD_KEYS,
                    "path_validation": (
                        validate_path_field(hass, config_entry, field.key, _normalize_string(values.get(field.key)), values)
                        if include_path_validations and field.key in PATH_BROWSABLE_FIELD_KEYS
                        else None
                    ),
                    "options": field_options.get(field.key, []),
                }
                for field in (SETTINGS_FIELD_MAP[field_key] for field_key in section["fields"])
            ],
        }

    paths_section = next(section for section in SETTINGS_SECTIONS if section["key"] == "paths")
    sections = [
        {
            "key": "chimes",
            "kind": "chimes",
            "title": "Chimes",
            "description": "Manage your custom chime folder and fine-tune the offset for each chime.",
            "docs_url": CHIMES_DOCS_URL,
            "folder_section": build_section(paths_section),
            "available_chimes": [
                option for option in chime_options
                if option.get("value") and not str(option.get("label", "")).startswith("🎲 ")
            ],
        },
        {
            "key": CHIME_SETS_KEY,
            "kind": "chime_sets",
            "title": "Chime Sets",
            "description": "Create your own custom chime sets that Chime TTS will randomly choose from each time.",
            "docs_url": CHIME_SETS_DOCS_URL,
            "sets": normalize_sets(values.get(CHIME_SETS_KEY)),
            "available_chimes": [
                option
                for option in chime_options
                if option.get("value") and not str(option.get("label", "")).startswith("🎲 ")
            ],
        },
    ] + [
        build_section(section)
        for section in SETTINGS_SECTIONS
        if section["key"] != "paths"
    ]

    sections.extend(
        [
            {
                "key": "notify_profiles",
                "kind": "notify_profiles",
                "title_key": "section.notify_profiles_title",
                "description_key": "section.notify_profiles_description",
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
                "title_key": "section.logs_title",
                "description_key": "section.logs_description",
                "docs_url": CONFIGURATION_DOCS_BASE_URL,
            },
            {
                "key": "about",
                "kind": "about",
                "title_key": "section.about_title",
                "description_key": "section.about_description",
                "docs_url": PROJECT_HOME_URL,
                "version": VERSION,
                "footer_logo_url": _footer_logo_url(),
                "about_items": [dict(item) for item in ABOUT_ITEMS],
            },
        ]
    )

    return sections


async def async_build_panel_payload(
    hass,
    config_entry: config_entries.ConfigEntry,
    **kwargs: Any,
) -> dict[str, Any]:
    """Build the panel payload without blocking the event loop."""
    values = kwargs.get("values") or get_settings_data(hass, config_entry)
    include_log_events = kwargs.get("include_log_events", True)
    include_notify_profiles = kwargs.get("include_notify_profiles", True)
    include_path_validations = kwargs.get("include_path_validations", True)
    notify_profiles = kwargs.get("notify_profiles")
    notify_profile_errors = kwargs.get("notify_profile_errors")
    errors = kwargs.get("errors")
    message = kwargs.get("message")
    message_type = kwargs.get("message_type")
    restart_required = kwargs.get("restart_required", False)

    async_jobs = [async_get_notify_chime_options(hass)]
    if include_notify_profiles:
        async_jobs.insert(0, async_load_notify_profiles(hass))
    if include_log_events:
        async_jobs.append(async_get_panel_log_events(hass))

    async_results = await asyncio.gather(*async_jobs)
    result_index = 0
    if include_notify_profiles:
        loaded_notify_profiles, notify_profiles_load_error = async_results[result_index]
        result_index += 1
    else:
        loaded_notify_profiles, notify_profiles_load_error = [], None

    chime_options = async_results[result_index]
    result_index += 1
    chime_options = _with_chime_sets(chime_options, values)
    log_events = async_results[result_index] if include_log_events else []

    if notify_profiles is None:
        notify_profiles = loaded_notify_profiles if include_notify_profiles else []

    tts_platforms = get_available_tts_platforms(hass)
    alerts, panel_tone = _build_panel_alerts(hass)
    field_options = {
        "chime_path": chime_options,
        "end_chime_path": chime_options,
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
        "footer_logo_url": _footer_logo_url(),
        "documentation_url": CONFIGURATION_DOCS_BASE_URL,
        "logs_url": f"/config/logs?filter={DOMAIN}",
        "alerts": alerts,
        "panel_tone": panel_tone,
        "restart_alert_note": "Home Assistant needs to restart before newly installed TTS providers appear in Chime TTS.",
        "fallback_note": "The standard Configure dialog still works and remains available as a fallback.",
        "restart_note": "Adding or removing Chime Sets requires a Home Assistant restart.",
        "message": message,
        "message_type": message_type,
        "restart_required": restart_required,
        "restart_required_field_keys": sorted(RESTART_REQUIRED_FIELD_KEYS),
        "errors": errors or {},
        "values": values,
        "notify_profiles": notify_profiles,
        "notify_profiles_hydrated": include_notify_profiles,
        "notify_profile_errors": notify_profile_errors or [],
        "notify_profiles_load_error": notify_profiles_load_error,
        "log_events": log_events,
        "sections": _build_panel_sections(
            hass,
            config_entry,
            values,
            field_options=field_options,
            tts_platforms=tts_platforms,
            chime_options=chime_options,
            default_provider=default_provider,
            fallback_provider=fallback_provider,
            include_path_validations=include_path_validations,
            icon_versioned=True,
        ),
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
    chime_options = _with_chime_sets(get_notify_chime_options(), data)
    chime_selector_options = [
        selector.SelectOptionDict(
            value=option["value"],
            label=option["label"] or option["value"] or "Not set",
        )
        for option in chime_options
    ]

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
                DEFAULT_PRE_SCRIPT_KEY,
                description={"suggested_value": data[DEFAULT_PRE_SCRIPT_KEY]},
            ): str,
            vol.Optional(
                DEFAULT_POST_SCRIPT_KEY,
                description={"suggested_value": data[DEFAULT_POST_SCRIPT_KEY]},
            ): str,
            vol.Optional(
                DEFAULT_PRE_SCRIPT_SHARED_KEY,
                default=data[DEFAULT_PRE_SCRIPT_SHARED_KEY],
            ): bool,
            vol.Optional(
                DEFAULT_POST_SCRIPT_SHARED_KEY,
                default=data[DEFAULT_POST_SCRIPT_SHARED_KEY],
            ): bool,
            vol.Optional(
                DEFAULT_PRE_SCRIPT_SAY_URL_KEY,
                description={"suggested_value": data[DEFAULT_PRE_SCRIPT_SAY_URL_KEY]},
            ): str,
            vol.Optional(
                DEFAULT_POST_SCRIPT_SAY_URL_KEY,
                description={"suggested_value": data[DEFAULT_POST_SCRIPT_SAY_URL_KEY]},
            ): str,
            vol.Optional(
                "chime_path",
                default=data["chime_path"],
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=chime_selector_options,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                    custom_value=False,
                )
            ),
            vol.Optional(
                "end_chime_path",
                default=data["end_chime_path"],
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=chime_selector_options,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                    custom_value=False,
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
    """Normalize a selected TTS platform back to a live TTS entity id."""
    if not platform:
        return ""

    if not installed_tts_platforms:
        raise LookupError("tts_platform_none")

    selected_platform = helpers._match_tts_platform(platform, installed_tts_platforms)
    if selected_platform is None:
        selected_platform = helpers._match_google_fallback(platform, installed_tts_platforms)
    if selected_platform is None:
        raise LookupError("tts_platform_select")

    return selected_platform


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


def _is_browser_audio_file_name(file_name: str) -> bool:
    """Return whether a file name has a supported audio extension."""
    return os.path.splitext(file_name or "")[1].lower() in CHIME_FILE_EXTENSIONS


def _browser_audio_preview_url(field_key: str, path: str) -> str:
    """Return an authenticated browser-audio preview URL."""
    return f"/api/{DOMAIN}/browser/audio?field_key={quote(field_key)}&path={quote(path)}"


def _list_matching_chime_files(path: str) -> list[str]:
    """Return matching chime-like files from a folder."""
    current_dir = ensure_trailing_slash(path).rstrip("/") or "/"
    if not os.path.isdir(current_dir):
        return []

    files: list[str] = []
    with os.scandir(current_dir) as entries:
        for entry in entries:
            if not entry.is_file():
                continue
            if not _is_browser_audio_file_name(entry.name):
                continue
            files.append(entry.name)

    files.sort(key=str.lower)
    return files


def _format_browser_entry_size(size: int | None) -> str:
    """Return a human-friendly byte count."""
    if size in (None, "", 0):
        return "0 B" if size == 0 else ""

    units = ["B", "KB", "MB", "GB", "TB"]
    numeric = float(size)
    unit_index = 0
    while numeric >= 1024 and unit_index < len(units) - 1:
        numeric /= 1024
        unit_index += 1
    if unit_index == 0:
        return f"{int(numeric)} {units[unit_index]}"
    return f"{numeric:.1f} {units[unit_index]}"


def _browser_relative_label(path: str, root: str) -> str:
    """Return the path relative to a browser root."""
    normalized_path = ensure_trailing_slash(path).rstrip("/") or "/"
    normalized_root = ensure_trailing_slash(root).rstrip("/") or "/"
    if normalized_root == "/":
        return normalized_path
    if normalized_path == normalized_root:
        return "/"
    if normalized_path.startswith(f"{normalized_root}/"):
        return normalized_path[len(normalized_root) :] or "/"
    return normalized_path


def _browser_breadcrumbs(path: str) -> list[dict[str, str]]:
    """Return breadcrumb segments for a path."""
    normalized = ensure_trailing_slash(path).rstrip("/") or "/"
    if normalized == "/":
        return [{"label": "/", "path": "/"}]

    breadcrumbs = [{"label": "/", "path": "/"}]
    parts = normalized.split("/")[1:]
    current = ""
    for part in parts:
        current += f"/{part}"
        breadcrumbs.append({"label": part, "path": ensure_trailing_slash(current)})
    return breadcrumbs


def _browser_entry_payload(
    hass,
    field_key: str,
    entry: os.DirEntry[str],
) -> dict[str, Any]:
    """Serialize a filesystem entry for browser UI consumption."""
    stat_result = entry.stat(follow_symlinks=False)
    is_dir = entry.is_dir(follow_symlinks=False)
    entry_path = ensure_trailing_slash(entry.path) if is_dir else str(entry.path)
    is_audio = not is_dir and _is_browser_audio_file_name(entry.name)
    try:
        modified_at = datetime.fromtimestamp(stat_result.st_mtime).isoformat()
    except Exception:
        modified_at = ""

    return {
        "name": entry.name,
        "path": entry_path,
        "is_dir": is_dir,
        "kind": "folder" if is_dir else "file",
        "size": stat_result.st_size if not is_dir else None,
        "size_label": "" if is_dir else _format_browser_entry_size(stat_result.st_size),
        "modified_at": modified_at,
        "badges": _path_badges(hass, entry_path) if is_dir else [],
        "extension": "" if is_dir else os.path.splitext(entry.name)[1].lower(),
        "is_audio": is_audio,
        "audio_preview_url": (
            _browser_audio_preview_url(field_key, entry_path) if is_audio else ""
        ),
    }


def _normalize_browser_target_path(
    hass,
    config_entry: config_entries.ConfigEntry,
    field_key: str,
    path: str | None,
    values: dict[str, Any] | None = None,
    *,
    require_exists: bool = True,
    require_navigable: bool = True,
) -> str:
    """Normalize and validate a browser target path."""
    current_values = values or get_settings_data(hass, config_entry)
    candidate = ensure_trailing_slash(path or _normalize_string(current_values.get(field_key)))

    if not candidate:
        candidate = ensure_trailing_slash("/")

    if require_navigable and not is_path_navigable_for_field(
        hass, config_entry, field_key, candidate, current_values
    ):
        raise PermissionError(candidate)

    normalized_path = candidate.rstrip("/") or "/"
    if require_exists and not os.path.exists(normalized_path):
        raise FileNotFoundError(normalized_path)

    return candidate if os.path.isdir(normalized_path) else normalized_path


def _find_existing_browser_ancestor(
    hass,
    config_entry: config_entries.ConfigEntry,
    field_key: str,
    path: str | None,
    values: dict[str, Any] | None = None,
) -> str | None:
    """Return the closest existing browsable ancestor for a requested path."""
    current_values = values or get_settings_data(hass, config_entry)
    candidate = ensure_trailing_slash(path or _normalize_string(current_values.get(field_key)))
    if not candidate:
        candidate = ensure_trailing_slash("/")

    seen: set[str] = set()
    while candidate and candidate not in seen:
        seen.add(candidate)
        normalized_path = candidate.rstrip("/") or "/"
        if os.path.isdir(normalized_path) and is_path_navigable_for_field(
            hass, config_entry, field_key, candidate, current_values
        ):
            return candidate
        parent_path = ensure_trailing_slash(os.path.dirname(normalized_path) or "/")
        if parent_path == candidate:
            break
        candidate = parent_path

    for root in get_browse_roots(hass, config_entry, field_key, current_values):
        normalized_root = ensure_trailing_slash(root)
        if os.path.isdir(normalized_root.rstrip("/") or "/"):
            return normalized_root

    if is_path_navigable_for_field(hass, config_entry, field_key, "/", current_values):
        return "/"
    return None


def _is_path_within_browser_roots(
    hass,
    config_entry: config_entries.ConfigEntry,
    field_key: str,
    path: str,
    values: dict[str, Any] | None = None,
) -> bool:
    """Return whether a filesystem path stays inside the allowed browser roots."""
    normalized_path = str(path or "").rstrip("/") or "/"
    if field_key == CUSTOM_CHIMES_PATH_KEY:
        return os.path.isabs(normalized_path)

    resolved_path = os.path.realpath(normalized_path)
    for root in get_browse_roots(hass, config_entry, field_key, values):
        if _is_subdirectory(os.path.realpath(root.rstrip("/")), resolved_path):
            return True
    return False


def resolve_browser_audio_file_path(
    hass,
    config_entry: config_entries.ConfigEntry,
    field_key: str,
    path: str,
    values: dict[str, Any] | None = None,
) -> str:
    """Resolve and validate a browser audio file path."""
    if field_key not in PATH_BROWSABLE_FIELD_KEYS:
        raise ValueError("unsupported_field")

    normalized_path = str(path or "").strip()
    if not normalized_path:
        raise ValueError("missing_path")
    if not _is_browser_audio_file_name(normalized_path):
        raise ValueError("unsupported_file_type")
    if not os.path.isabs(normalized_path):
        raise PermissionError(normalized_path)
    if not _is_path_within_browser_roots(
        hass, config_entry, field_key, normalized_path, values
    ):
        raise PermissionError(normalized_path)
    if not os.path.isfile(normalized_path):
        raise FileNotFoundError(normalized_path)

    return normalized_path


def _safe_browser_child_path(parent_path: str, child_name: str) -> str:
    """Return a safe child path within a browser directory."""
    sanitized_name = str(child_name or "").strip()
    if not sanitized_name or sanitized_name in {".", ".."}:
        raise ValueError("invalid_name")
    if "/" in sanitized_name or "\\" in sanitized_name:
        raise ValueError("invalid_name")
    return os.path.join(parent_path.rstrip("/") or "/", sanitized_name)


def _browser_upload_relative_parts(filename: str) -> list[str]:
    """Return sanitized relative path components for an upload."""
    return [
        part
        for part in str(filename or "").replace("\\", "/").split("/")
        if part and part not in {".", ".."}
    ]


def resolve_browser_upload_target_path(
    hass,
    config_entry: config_entries.ConfigEntry,
    field_key: str,
    destination_path: str,
    filename: str,
    *,
    values: dict[str, Any] | None = None,
) -> tuple[str, str]:
    """Return the final upload path and display-relative path."""
    current_values = values or get_settings_data(hass, config_entry)
    target_dir = _normalize_browser_target_path(
        hass,
        config_entry,
        field_key,
        destination_path,
        current_values,
    ).rstrip("/") or "/"

    relative_parts = _browser_upload_relative_parts(filename)
    if not relative_parts:
        raise ValueError("invalid_name")

    target_path = target_dir
    for part in relative_parts[:-1]:
        target_path = _safe_browser_child_path(target_path, part)

    final_path = _safe_browser_child_path(target_path, relative_parts[-1])
    if not _is_path_within_browser_roots(
        hass, config_entry, field_key, final_path, current_values
    ):
        raise PermissionError(final_path)
    return final_path, "/".join(relative_parts)


def inspect_browser_upload_conflicts(
    hass,
    config_entry: config_entries.ConfigEntry,
    field_key: str,
    destination_path: str,
    filenames: list[str],
    *,
    values: dict[str, Any] | None = None,
) -> list[dict[str, str]]:
    """Return uploads that would overwrite existing files."""
    conflicts: list[dict[str, str]] = []
    for filename in filenames:
        final_path, relative_path = resolve_browser_upload_target_path(
            hass,
            config_entry,
            field_key,
            destination_path,
            filename,
            values=values,
        )
        if os.path.isfile(final_path):
            conflicts.append(
                {
                    "filename": filename,
                    "relative_path": relative_path,
                    "existing_path": final_path,
                }
            )
    return conflicts


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
        **(values if values is not None else get_settings_data(hass, config_entry)),
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
    requested_dir = current_path.rstrip("/") or "/"
    requested_path_exists = bool(current_path) and os.path.isdir(requested_dir)
    requested_path_missing = bool(current_path) and not requested_path_exists

    if not current_path or not is_path_navigable_for_field(
        hass, config_entry, field_key, current_path, current_values
    ):
        current_path = ensure_trailing_slash("/")

    current_dir = current_path.rstrip("/") or "/"
    if not os.path.isdir(current_dir):
        fallback_path = _find_existing_browser_ancestor(
            hass,
            config_entry,
            field_key,
            requested_path,
            current_values,
        )
        if not fallback_path:
            raise FileNotFoundError(current_dir)
        current_path = ensure_trailing_slash(fallback_path)
        current_dir = current_path.rstrip("/") or "/"

    selected_path_notice = ""
    if requested_path_missing:
        selected_path_notice = (
            "The selected folder does not exist. Showing the closest existing folder instead."
        )

    entries_payload: list[dict[str, Any]] = []
    with os.scandir(current_dir) as entries:
        for entry in entries:
            is_dir = entry.is_dir(follow_symlinks=False)
            entry_path = ensure_trailing_slash(entry.path) if is_dir else str(entry.path)
            if is_dir and not is_path_navigable_for_field(
                hass, config_entry, field_key, entry_path, current_values
            ):
                continue
            if not is_dir and not _is_browser_audio_file_name(entry.name):
                continue
            entries_payload.append(_browser_entry_payload(hass, field_key, entry))

    entries_payload.sort(
        key=lambda item: (0 if item["is_dir"] else 1, item["name"].lower())
    )
    directories = [item for item in entries_payload if item["is_dir"]]
    files = [item for item in entries_payload if not item["is_dir"]]

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
        "requested_path": requested_path,
        "requested_path_exists": requested_path_exists,
        "requested_path_missing": requested_path_missing,
        "selected_path_notice": selected_path_notice,
        "current_path": current_path,
        "parent_path": parent_path,
        "breadcrumbs": _browser_breadcrumbs(current_path),
        "current_path_allowed": current_path_allowed,
        "current_path_validation_message": _path_validation_message(
            field_key, current_path_allowed
        ),
        "current_path_badges": _path_badges(hass, current_path),
        "preview_files": current_preview_files,
        "items": entries_payload,
        "directories": directories,
        "files": files,
        "roots": [
            {
                "name": root.rstrip("/").split("/")[-1] or "/",
                "path": root,
                "badges": _path_badges(hass, root),
                "relative_label": _browser_relative_label(current_path, root),
            }
            for root in allowed_roots
        ],
        "capabilities": {
            "can_select": current_path_allowed,
            "can_create_folder": True,
            "can_upload": True,
            "can_rename": current_dir != "/",
            "can_delete": current_dir != "/",
        },
    }


def create_browser_directory(
    hass,
    config_entry: config_entries.ConfigEntry,
    field_key: str,
    parent_path: str,
    name: str,
    *,
    values: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a folder and return refreshed browser payload."""
    target_parent = _normalize_browser_target_path(
        hass,
        config_entry,
        field_key,
        parent_path,
        values,
    )
    if not _is_path_within_browser_roots(
        hass, config_entry, field_key, target_parent, values
    ):
        raise PermissionError(target_parent)
    target_path = _safe_browser_child_path(target_parent, name)
    if os.path.exists(target_path):
        raise FileExistsError(target_path)
    os.makedirs(target_path, exist_ok=False)
    return build_directory_browser_payload(
        hass,
        config_entry,
        field_key,
        target_parent,
        values=values,
    )


def rename_browser_entry(
    hass,
    config_entry: config_entries.ConfigEntry,
    field_key: str,
    path: str,
    new_name: str,
    *,
    values: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Rename a file or folder and return refreshed browser payload."""
    current_values = values or get_settings_data(hass, config_entry)
    normalized_path = _normalize_browser_target_path(
        hass,
        config_entry,
        field_key,
        path,
        current_values,
        require_exists=True,
        require_navigable=os.path.isdir(str(path or "").rstrip("/")),
    )
    source_path = normalized_path.rstrip("/") or "/"
    if source_path == "/":
        raise ValueError("cannot_rename_root")
    if not _is_path_within_browser_roots(
        hass,
        config_entry,
        field_key,
        source_path,
        current_values,
    ):
        raise PermissionError(source_path)
    parent_path = os.path.dirname(source_path) or "/"
    target_path = _safe_browser_child_path(parent_path, new_name)
    if not _is_path_within_browser_roots(
        hass,
        config_entry,
        field_key,
        target_path,
        current_values,
    ):
        raise PermissionError(target_path)
    if os.path.exists(target_path):
        raise FileExistsError(target_path)
    os.rename(source_path, target_path)
    return build_directory_browser_payload(
        hass,
        config_entry,
        field_key,
        ensure_trailing_slash(parent_path),
        values=current_values,
    )


def delete_browser_entry(
    hass,
    config_entry: config_entries.ConfigEntry,
    field_key: str,
    path: str,
    *,
    values: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Delete a file or folder and return refreshed browser payload."""
    current_values = values or get_settings_data(hass, config_entry)
    normalized_path = _normalize_browser_target_path(
        hass,
        config_entry,
        field_key,
        path,
        current_values,
        require_exists=True,
        require_navigable=os.path.isdir(str(path or "").rstrip("/")),
    )
    source_path = normalized_path.rstrip("/") or "/"
    if source_path == "/":
        raise ValueError("cannot_delete_root")
    if not _is_path_within_browser_roots(
        hass,
        config_entry,
        field_key,
        source_path,
        current_values,
    ):
        raise PermissionError(source_path)
    parent_path = ensure_trailing_slash(os.path.dirname(source_path) or "/")
    if os.path.isdir(source_path):
        shutil.rmtree(source_path)
    else:
        os.remove(source_path)
    return build_directory_browser_payload(
        hass,
        config_entry,
        field_key,
        parent_path,
        values=current_values,
    )


def save_browser_upload(
    hass,
    config_entry: config_entries.ConfigEntry,
    field_key: str,
    destination_path: str,
    filename: str,
    content: bytes,
    *,
    values: dict[str, Any] | None = None,
) -> None:
    """Persist an uploaded file inside the allowed browser roots."""
    final_path, _relative_path = resolve_browser_upload_target_path(
        hass,
        config_entry,
        field_key,
        destination_path,
        filename,
        values=values,
    )
    os.makedirs(os.path.dirname(final_path), exist_ok=True)
    with open(final_path, "wb") as upload_file:
        upload_file.write(content)


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
        DEFAULT_PRE_SCRIPT_KEY,
        DEFAULT_POST_SCRIPT_KEY,
        DEFAULT_PRE_SCRIPT_SAY_URL_KEY,
        DEFAULT_POST_SCRIPT_SAY_URL_KEY,
        "chime_path",
        "end_chime_path",
        CUSTOM_CHIMES_PATH_KEY,
        TEMP_CHIMES_PATH_KEY,
        TEMP_PATH_KEY,
        WWW_PATH_KEY,
    ):
        normalized[field_key] = _normalize_string(user_input.get(field_key))

    submitted_sets = user_input.get(
       CHIME_SETS_KEY, current_data[CHIME_SETS_KEY]
    )
    normalized_sets = normalize_sets(submitted_sets)
    if submitted_sets not in (None, []) and len(normalized_sets) != len(submitted_sets):
        errors[CHIME_SETS_KEY] = "invalid_chime_sets"
    names = [chime_set["name"].casefold() for chime_set in normalized_sets]
    if len(names) != len(set(names)):
        errors[CHIME_SETS_KEY] = "duplicate_chime_set_name"
    normalized[CHIME_SETS_KEY] = normalized_sets
    submitted_offsets = user_input.get(CHIME_OFFSETS_KEY, current_data[CHIME_OFFSETS_KEY])
    if not isinstance(submitted_offsets, dict):
        submitted_offsets = {}
        errors[CHIME_OFFSETS_KEY] = "invalid_chime_offsets"
    normalized_offsets = {
        str(key): int(value) for key, value in (submitted_offsets or {}).items()
        if str(key) and str(value).lstrip("-").isdigit()
    }
    # Store only deviations from the shipped tuning. This preserves a user's
    # choices across restarts and upgrades while allowing future defaults to
    # apply to chimes they have not customized.
    normalized[CHIME_OFFSETS_KEY] = {
        key: value
        for key, value in normalized_offsets.items()
        if DEFAULT_CHIME_OFFSETS.get(key) != value
    }

    normalized[ADD_COVER_ART_KEY] = _normalize_bool(user_input.get(ADD_COVER_ART_KEY))
    _normalize_shared_script_settings(normalized, user_input, current_data)
    _clear_shared_action_script_values(normalized)

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

    saved_set_ids = {
        chime_set["id"]
        for chime_set in normalize_sets(current_data.get(CHIME_SETS_KEY))
    }
    submitted_set_ids = {chime_set["id"] for chime_set in normalized_sets}
    chime_sets_restart_required = saved_set_ids != submitted_set_ids
    restart_required = chime_sets_restart_required

    return ValidationResult(
        data=normalized,
        errors=errors,
        restart_required=restart_required,
    )


def _clear_shared_action_script_values(values: dict[str, Any]) -> None:
    """Erase action-specific defaults whenever the shared mode is selected."""
    values[DEFAULT_PRE_SCRIPT_SAY_URL_KEY] *= not values[DEFAULT_PRE_SCRIPT_SHARED_KEY]
    values[DEFAULT_POST_SCRIPT_SAY_URL_KEY] *= not values[DEFAULT_POST_SCRIPT_SHARED_KEY]


def _normalize_shared_script_settings(
    normalized: dict[str, Any],
    user_input: dict[str, Any],
    current_data: dict[str, Any],
) -> None:
    """Normalize the independent pre- and post-script sharing controls."""
    for field_key in (DEFAULT_PRE_SCRIPT_SHARED_KEY, DEFAULT_POST_SCRIPT_SHARED_KEY):
        normalized[field_key] = _normalize_bool(
            user_input.get(field_key, current_data[field_key])
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
    tts_platforms = get_available_tts_platforms(hass)
    alerts, panel_tone = _build_panel_alerts(hass)
    chime_options = _with_chime_sets(get_notify_chime_options(), values)
    field_options = {
        "chime_path": chime_options,
        "end_chime_path": chime_options,
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
        "footer_logo_url": _footer_logo_url(),
        "documentation_url": CONFIGURATION_DOCS_BASE_URL,
        "logs_url": f"/config/logs?filter={DOMAIN}",
        "alerts": alerts,
        "panel_tone": panel_tone,
        "restart_alert_note": "Home Assistant needs to restart before newly installed TTS providers appear in Chime TTS.",
        "fallback_note": "The standard Configure dialog still works and remains available as a fallback.",
        "restart_note": "Adding or removing Chime Sets requires a Home Assistant restart.",
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
        "sections": _build_panel_sections(
            hass,
            config_entry,
            values,
            field_options=field_options,
            tts_platforms=tts_platforms,
            chime_options=chime_options,
            default_provider=default_provider,
            fallback_provider=fallback_provider,
            include_path_validations=True,
            icon_versioned=True,
        ),
        "notify_profile_template": dict(NOTIFY_PROFILE_DEFAULTS),
        "notify_chime_options": chime_options,
    }
