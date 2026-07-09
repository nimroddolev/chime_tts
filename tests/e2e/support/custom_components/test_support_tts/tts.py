"""Deterministic local TTS provider for live E2E coverage."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from homeassistant.components.tts import Provider, TtsAudioType
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType


SUPPORT_LANGUAGES = ["en", "en-US", "fr"]
SUPPORT_OPTIONS = ["voice", "tld"]


async def async_get_engine(
    hass: HomeAssistant,
    config: ConfigType,
    discovery_info: DiscoveryInfoType | None = None,
) -> TestSupportProvider:
    """Return the local E2E TTS provider."""
    del config, discovery_info
    return TestSupportProvider(hass)


class TestSupportProvider(Provider):
    """Simple provider that records request metadata and returns local audio."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Store hass and static metadata."""
        self.hass = hass
        self.name = "test_support_tts"

    @property
    def default_language(self) -> str:
        """Return the default language."""
        return "en"

    @property
    def supported_languages(self) -> list[str]:
        """Return supported languages."""
        return SUPPORT_LANGUAGES

    @property
    def supported_options(self) -> list[str]:
        """Return supported options."""
        return SUPPORT_OPTIONS

    def get_tts_audio(
        self, message: str, language: str, options: dict[str, Any]
    ) -> TtsAudioType:
        """Record the request and return bundled MP3 bytes."""
        config_dir = Path(self.hass.config.config_dir)
        record_path = config_dir / "test_support_tts_last_request.json"
        record_path.write_text(
            json.dumps(
                {
                    "message": message,
                    "language": language,
                    "options": options,
                }
            ),
            encoding="utf-8",
        )

        mp3_path = config_dir / "custom_components" / "chime_tts" / "mp3s" / "bells.mp3"
        return "mp3", mp3_path.read_bytes()
