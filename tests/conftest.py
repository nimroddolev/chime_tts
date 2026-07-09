"""Shared fixtures for chime_tts tests."""

from __future__ import annotations

from contextlib import suppress
import sys
import types
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    import custom_components  # type: ignore[import-not-found]
except ImportError:
    custom_components = types.ModuleType("custom_components")
    custom_components.__path__ = []
    sys.modules["custom_components"] = custom_components

OURS = str(ROOT / "custom_components")
if OURS not in custom_components.__path__:
    custom_components.__path__.append(OURS)


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(request: pytest.FixtureRequest):
    """Load chime_tts as a custom integration when the HA pytest plugin exists."""
    with suppress(pytest.FixtureLookupError):
        request.getfixturevalue("enable_custom_integrations")
    yield


@pytest.fixture
def integration_root() -> Path:
    """Return the absolute path to the chime_tts integration package."""
    return ROOT / "custom_components" / "chime_tts"
