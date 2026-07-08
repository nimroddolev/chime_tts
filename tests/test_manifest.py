"""Manifest and HACS metadata checks.

These run without the Home Assistant test harness, so they stay green on any
interpreter and catch the kind of metadata drift hassfest rejects in CI.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "custom_components" / "chime_tts" / "manifest.json"
HACS = ROOT / "hacs.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def test_manifest_is_valid_json():
    assert MANIFEST.is_file()
    _load(MANIFEST)


def test_manifest_required_keys():
    manifest = _load(MANIFEST)
    for key in ("domain", "name", "version", "documentation", "issue_tracker"):
        assert manifest.get(key), f"manifest missing {key}"
    assert manifest["domain"] == "chime_tts"


def test_manifest_requirements_present():
    manifest = _load(MANIFEST)
    reqs = manifest.get("requirements", [])
    assert "pydub" in reqs
    assert "aiofiles" in reqs


def test_hacs_metadata():
    hacs = _load(HACS)
    assert hacs.get("name")
    assert hacs.get("homeassistant"), "hacs.json must declare a minimum HA version"
