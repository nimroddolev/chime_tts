"""Shared fixtures for chime_tts tests."""

import sys
from pathlib import Path

import pytest

# pytest-homeassistant-custom-component pins the `custom_components` namespace
# package to its own testing_config directory, which shadows this repo's
# integration. Merge our directory into that namespace so
# `custom_components.chime_tts` imports the code under test.
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import custom_components  # noqa: E402

_OURS = str(_ROOT / "custom_components")
if _OURS not in custom_components.__path__:
    custom_components.__path__.append(_OURS)

# pytest-homeassistant-custom-component ships the `hass`, `aioclient_mock`,
# and `enable_custom_integrations` fixtures, available once it is installed.


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Load chime_tts as a custom integration in every test."""
    yield


@pytest.fixture
def integration_root():
    """Return the absolute path to the chime_tts integration package."""
    from pathlib import Path

    return Path(__file__).resolve().parent.parent / "custom_components" / "chime_tts"
