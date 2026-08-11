"""Additional unit tests for TTS request preparation and audio processing."""

from __future__ import annotations

import importlib
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from pydub import AudioSegment

from custom_components.chime_tts.const import FALLBACK_TTS_PLATFORM_KEY
from custom_components.chime_tts.const import GOOGLE_CLOUD
from custom_components.chime_tts.const import IBM_WATSON_TTS
from custom_components.chime_tts.const import TTS_PLATFORM_KEY
from custom_components.chime_tts.helpers.tts_audio_helper import TTSAudioHelper


def test_engine_candidates_and_language_adjustments(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Entity and legacy engines plus provider-specific option rules are normalized."""
    helper = TTSAudioHelper()
    hass = SimpleNamespace(
        data={"tts_manager": SimpleNamespace(providers={"google": object()})}
    )
    assert helper._engine_candidates(hass, "tts.google") == ["tts.google", "google"]
    assert helper._engine_candidates(hass, "google") == ["google", "tts.google"]
    assert helper._engine_candidates(SimpleNamespace(data={}), "other") == ["tts.other"]

    options = {"language": "en-US", "voice": "voice"}
    assert helper._adjust_language_and_voice(GOOGLE_CLOUD, None, options) == "en-US"
    assert "language" not in options
    watson_options: dict[str, str] = {}
    assert (
        helper._adjust_language_and_voice(IBM_WATSON_TTS, "en-US", watson_options)
        is None
    )
    assert watson_options["voice"] == "en-US"

    module = importlib.import_module(
        "custom_components.chime_tts.helpers.tts_audio_helper"
    )
    monkeypatch.setattr(module.helpers, "get_tts_platform", lambda **kwargs: "google")
    helper._data = {TTS_PLATFORM_KEY: "google", FALLBACK_TTS_PLATFORM_KEY: "fallback"}
    assert helper._prepare_tts_request(hass, "", "", None, {}) == (None, None, None)
    assert helper._prepare_tts_request(hass, "", "hello", "en", {}) == (
        "google",
        {},
        "en",
    )


@pytest.mark.asyncio
async def test_generate_process_extract_and_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Generated IDs are retrieved, decoded, and retried through configured fallback."""
    helper = TTSAudioHelper()
    helper._data = {TTS_PLATFORM_KEY: "primary", FALLBACK_TTS_PLATFORM_KEY: "fallback"}
    hass = SimpleNamespace(
        data={"tts_manager": SimpleNamespace(providers={"primary": object()})}
    )
    module = importlib.import_module(
        "custom_components.chime_tts.helpers.tts_audio_helper"
    )
    monkeypatch.setattr(
        module.tts.media_source,
        "generate_media_source_id",
        lambda **kwargs: "media-source://tts/test",
    )
    assert await helper._generate_tts_audio(
        hass, "primary", "hello", None, False, {}
    ) == ("media-source://tts/test", None)

    monkeypatch.setattr(
        module.tts,
        "async_get_media_source_audio",
        AsyncMock(return_value=("mp3", b"bytes")),
    )
    monkeypatch.setattr(
        module.filesystem_helper,
        "async_load_audio",
        AsyncMock(return_value=AudioSegment.silent(duration=1)),
    )
    audio = await helper._process_audio_data(
        hass, "media-source://tts/test", None, datetime.now()
    )
    assert len(audio) == 1
    assert await helper._process_audio_data(hass, None, None, datetime.now()) is None

    retry = AsyncMock(return_value="fallback-audio")
    monkeypatch.setattr(helper, "async_request_tts_audio", retry)
    assert (
        await helper._retry_with_fallback(hass, "primary", "hi", "en", False, {})
        == "fallback-audio"
    )
    assert (
        await helper._retry_with_fallback(hass, "fallback", "hi", "en", False, {})
        is None
    )


@pytest.mark.asyncio
async def test_request_timeout_and_generation_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Timeouts and provider failures produce a useful error and fallback result."""
    helper = TTSAudioHelper()
    helper._data = {TTS_PLATFORM_KEY: "primary", FALLBACK_TTS_PLATFORM_KEY: ""}
    hass = SimpleNamespace(data={})
    module = importlib.import_module(
        "custom_components.chime_tts.helpers.tts_audio_helper"
    )
    monkeypatch.setattr(module.helpers, "get_tts_platform", lambda **kwargs: "primary")
    monkeypatch.setattr(
        helper, "_async_generate_and_process_audio", AsyncMock(side_effect=TimeoutError)
    )
    assert (
        await helper.async_request_tts_audio(hass, "primary", "hello", "en", False, {})
        is None
    )
    assert "timed out" in helper.last_error_message

    monkeypatch.setattr(
        module.tts.media_source,
        "generate_media_source_id",
        lambda **kwargs: (_ for _ in ()).throw(ValueError("bad")),
    )
    assert await helper._generate_tts_audio(
        hass, "primary", "hello", None, False, {}
    ) == (None, None)
    assert "failed to generate" in helper.last_error_message


@pytest.mark.parametrize(
    ("tts_platform", "expected"),
    [
        ("google_translate", "סַפָּר"),
        ("tts.google_en_com", "סַפָּר"),
        ("tts.piper", "ספר"),
        ("tts.google_generative_ai", "ספר"),
    ],
)
def test_adapt_message_to_platform(tts_platform: str, expected: str) -> None:
    """Niqqud reaches platforms that pronounce it, and is stripped for the rest."""
    assert TTSAudioHelper()._adapt_message_to_platform("סַפָּר", tts_platform) == expected


def test_adapt_message_to_platform_keeps_maqaf_when_stripping() -> None:
    """Stripping niqqud must not remove the maqaf and join the two words."""
    assert TTSAudioHelper()._adapt_message_to_platform("כָּל־הָעוֹלָם", "tts.piper") == "כל־העולם"
