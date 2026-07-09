"""Tests for cache lifecycle, queue management, playback dispatch, and TTS helpers."""

from __future__ import annotations

import asyncio
import importlib
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import ANY, AsyncMock

import pytest
from pydub import AudioSegment

from custom_components.chime_tts.const import ALEXA_MEDIA_PLAYER_PLATFORM
from custom_components.chime_tts.const import AUDIO_DURATION_KEY
from custom_components.chime_tts.const import AUDIO_PATH_KEY
from custom_components.chime_tts.const import FALLBACK_TTS_PLATFORM_KEY
from custom_components.chime_tts.const import GOOGLE_TRANSLATE
from custom_components.chime_tts.const import IBM_WATSON_TTS
from custom_components.chime_tts.const import LOCAL_PATH_KEY
from custom_components.chime_tts.const import MICROSOFT_TTS
from custom_components.chime_tts.const import NABU_CASA_CLOUD_TTS
from custom_components.chime_tts.const import PUBLIC_PATH_KEY
from custom_components.chime_tts.const import SONOS_PLATFORM
from custom_components.chime_tts.const import TEMP_CHIMES_PATH_KEY
from custom_components.chime_tts.const import TEMP_PATH_KEY
from custom_components.chime_tts.const import TTS_PLATFORM_KEY
from custom_components.chime_tts.const import TTS_TIMEOUT_KEY
from custom_components.chime_tts.helpers.tts_audio_helper import TTSAudioHelper
from custom_components.chime_tts.queue_manager import ChimeTTSQueueManager
from homeassistant.components.media_player.const import ATTR_MEDIA_ANNOUNCE
from homeassistant.components.media_player.const import ATTR_MEDIA_CONTENT_ID
from homeassistant.components.media_player.const import ATTR_MEDIA_CONTENT_TYPE
from homeassistant.components.media_player.const import MediaType
from homeassistant.const import CONF_ENTITY_ID

integration_module = importlib.import_module("custom_components.chime_tts.__init__")
tts_audio_module = importlib.import_module("custom_components.chime_tts.helpers.tts_audio_helper")


class FakeHass:
    """Small Home Assistant stand-in for broader unit tests."""

    def __init__(self) -> None:
        """Initialise fake Home Assistant properties used by the code under test."""
        self.config = SimpleNamespace(
            path=lambda *parts: f"/config/{'/'.join(parts)}",
            media_dirs={"media": "/media"},
        )

    async def async_add_executor_job(self, func, *args):
        """Run executor jobs inline for tests."""
        return func(*args)


class RecordingHass(FakeHass):
    """Fake Home Assistant that records executor sleep durations."""

    def __init__(self) -> None:
        """Initialise the recorder state."""
        super().__init__()
        self.sleep_calls: list[float] = []

    async def async_add_executor_job(self, func, *args):
        """Record sleep calls instead of blocking during tests."""
        if getattr(func, "__name__", "") == "sleep" and args:
            self.sleep_calls.append(args[0])
            return None
        return await super().async_add_executor_job(func, *args)


@pytest.mark.asyncio
async def test_async_get_cached_audio_data_migrates_string_path_and_backfills_duration(monkeypatch: pytest.MonkeyPatch) -> None:
    """Legacy string cache entries should become a public/local dict with computed duration."""
    monkeypatch.setattr(integration_module, "async_retrieve_data", AsyncMock(return_value="/config/www/chime_tts/legacy.mp3"))
    monkeypatch.setattr(integration_module.filesystem_helper, "async_file_exists_in_directory", AsyncMock(return_value=True))
    monkeypatch.setattr(integration_module.filesystem_helper, "path_exists", lambda path: True)
    monkeypatch.setattr(
        integration_module,
        "async_get_audio_from_path",
        AsyncMock(return_value=AudioSegment.silent(duration=1500)),
    )

    result = await integration_module.async_get_cached_audio_data(FakeHass(), "legacy")

    assert result == {
        LOCAL_PATH_KEY: None,
        PUBLIC_PATH_KEY: "/config/www/chime_tts/legacy.mp3",
        AUDIO_DURATION_KEY: 1.5,
    }


@pytest.mark.asyncio
async def test_async_get_cached_audio_data_migrates_audio_path_dict(monkeypatch: pytest.MonkeyPatch) -> None:
    """Deprecated `audio_path` cache entries should be normalized to the modern keys."""
    monkeypatch.setattr(
        integration_module,
        "async_retrieve_data",
        AsyncMock(return_value={AUDIO_PATH_KEY: "/media/legacy.mp3", AUDIO_DURATION_KEY: 2.25}),
    )
    monkeypatch.setattr(integration_module.filesystem_helper, "async_file_exists_in_directory", AsyncMock(return_value=False))
    monkeypatch.setattr(integration_module.filesystem_helper, "path_exists", lambda path: True)

    result = await integration_module.async_get_cached_audio_data(FakeHass(), "legacy-dict")

    assert result == {
        LOCAL_PATH_KEY: "/media/legacy.mp3",
        PUBLIC_PATH_KEY: None,
        AUDIO_DURATION_KEY: 2.25,
    }


@pytest.mark.asyncio
async def test_async_get_cached_audio_data_removes_missing_entry(monkeypatch: pytest.MonkeyPatch) -> None:
    """Missing cache entries should trigger cache cleanup for old paths."""
    hass = FakeHass()
    remove_cached = AsyncMock()

    monkeypatch.setattr(integration_module, "async_retrieve_data", AsyncMock(return_value=None))
    monkeypatch.setattr(integration_module, "async_remove_cached_audio_data", remove_cached)

    result = await integration_module.async_get_cached_audio_data(hass, "missing")

    assert result is None
    remove_cached.assert_awaited_once_with(hass, "missing", True, True)


@pytest.mark.asyncio
async def test_async_remove_cached_audio_data_deletes_storage_when_paths_removed(monkeypatch: pytest.MonkeyPatch) -> None:
    """Cache metadata should be deleted once all referenced files are removed."""
    hass = FakeHass()
    delete_data = AsyncMock()
    delete_file_calls: list[str] = []

    integration_module._data[TEMP_CHIMES_PATH_KEY] = "/media/chimes"
    integration_module._data[TEMP_PATH_KEY] = "/media/temp"

    monkeypatch.setattr(
        integration_module,
        "async_retrieve_data",
        AsyncMock(
            return_value={
                LOCAL_PATH_KEY: "/media/temp/generated.mp3",
                PUBLIC_PATH_KEY: "/config/www/chime_tts/generated.mp3",
            }
        ),
    )
    monkeypatch.setattr(integration_module, "async_delete_data", delete_data)

    async def fake_exists_in_directory(path: str, directory: str | None) -> bool:
        return bool(directory and path.startswith(directory))

    monkeypatch.setattr(integration_module.filesystem_helper, "async_file_exists_in_directory", fake_exists_in_directory)
    monkeypatch.setattr(
        integration_module.filesystem_helper,
        "delete_file",
        lambda hass, path: delete_file_calls.append(path),
    )

    await integration_module.async_remove_cached_audio_data(
        hass,
        "cache-key",
        clear_temp_tts_cache=True,
        clear_www_tts_cache=True,
    )

    assert delete_file_calls == ["/media/temp/generated.mp3", "/config/www/chime_tts/generated.mp3"]
    delete_data.assert_awaited_once_with(hass, "cache-key")


@pytest.mark.asyncio
async def test_async_remove_cached_audio_data_keeps_storage_when_local_file_remains(monkeypatch: pytest.MonkeyPatch) -> None:
    """Cache metadata should stay when cleanup only removed the public copy."""
    hass = FakeHass()
    delete_data = AsyncMock()

    monkeypatch.setattr(
        integration_module,
        "async_retrieve_data",
        AsyncMock(
            return_value={
                LOCAL_PATH_KEY: "/elsewhere/keep.mp3",
                PUBLIC_PATH_KEY: "/config/www/chime_tts/remove.mp3",
            }
        ),
    )
    monkeypatch.setattr(integration_module, "async_delete_data", delete_data)
    monkeypatch.setattr(
        integration_module.filesystem_helper,
        "async_file_exists_in_directory",
        AsyncMock(return_value=False),
    )
    monkeypatch.setattr(integration_module.filesystem_helper, "delete_file", lambda hass, path: None)

    await integration_module.async_remove_cached_audio_data(
        hass,
        "cache-key",
        clear_www_tts_cache=True,
    )

    delete_data.assert_not_awaited()


def test_validate_audio_dict_requires_media_content_id_for_local_playback(monkeypatch: pytest.MonkeyPatch) -> None:
    """Local playback validation should fail when no media content id was produced."""
    monkeypatch.setattr(integration_module.filesystem_helper, "path_exists", lambda path: True)

    is_valid = integration_module.validate_audio_dict(
        hass=FakeHass(),
        is_local=True,
        is_public=False,
        audio_dict={
            LOCAL_PATH_KEY: "/media/test.mp3",
            PUBLIC_PATH_KEY: None,
            AUDIO_DURATION_KEY: 1.0,
            ATTR_MEDIA_CONTENT_ID: None,
        },
    )

    assert is_valid is False


def test_validate_audio_dict_accepts_localhost_public_url(monkeypatch: pytest.MonkeyPatch) -> None:
    """Public localhost URLs should be accepted even without a filesystem path."""
    monkeypatch.setattr(integration_module.filesystem_helper, "path_exists", lambda path: False)
    monkeypatch.setattr(
        integration_module.filesystem_helper,
        "get_local_path",
        lambda hass, file_path: "http://localhost:8123/local/chime_tts/test.mp3",
    )

    is_valid = integration_module.validate_audio_dict(
        hass=FakeHass(),
        is_local=False,
        is_public=True,
        audio_dict={
            LOCAL_PATH_KEY: None,
            PUBLIC_PATH_KEY: "http://localhost:8123/local/chime_tts/test.mp3",
            AUDIO_DURATION_KEY: 1.0,
            ATTR_MEDIA_CONTENT_ID: None,
        },
    )

    assert is_valid is True


def test_get_filename_hash_ignores_irrelevant_fields_and_tracks_relevant_changes() -> None:
    """Only relevant playback inputs should affect the cache key hash."""
    base_hash = integration_module.get_filename_hash_from_service_data(
        {"message": "Hello", "tts_platform": GOOGLE_TRANSLATE, "irrelevant": 1},
        {"voice": "Jenny", "another_unused": "x"},
    )
    same_hash = integration_module.get_filename_hash_from_service_data(
        {"message": "Hello", "tts_platform": GOOGLE_TRANSLATE, "something_else": True},
        {"voice": "Jenny"},
    )
    changed_hash = integration_module.get_filename_hash_from_service_data(
        {"message": "Hello", "tts_platform": GOOGLE_TRANSLATE, "tts_speed": 110},
        {"voice": "Jenny"},
    )

    assert base_hash == same_hash
    assert changed_hash != base_hash


@pytest.mark.asyncio
async def test_queue_manager_processes_successful_call() -> None:
    """Queued service calls should resolve their future with the coroutine result."""
    queue_manager = ChimeTTSQueueManager()
    future = asyncio.get_running_loop().create_future()

    async def return_value():
        return 42

    service_call = {
        "function": return_value,
        "args": (),
        "kwargs": {},
        "future": future,
    }
    queue_manager.queue.put_nowait(service_call)

    await queue_manager._process_service_call(service_call)

    assert future.result() == 42


@pytest.mark.asyncio
async def test_queue_manager_propagates_exceptions() -> None:
    """Queued failures should surface on the stored future."""
    queue_manager = ChimeTTSQueueManager()
    future = asyncio.get_running_loop().create_future()

    async def explode():
        raise ValueError("boom")

    service_call = {"function": explode, "args": (), "kwargs": {}, "future": future}
    queue_manager.queue.put_nowait(service_call)
    await queue_manager._process_service_call(
        service_call
    )

    assert isinstance(future.exception(), ValueError)


@pytest.mark.asyncio
async def test_queue_manager_times_out_long_running_calls() -> None:
    """Long-running queue items should fail with a timeout."""
    queue_manager = ChimeTTSQueueManager()
    queue_manager.timeout_s = 0.01
    future = asyncio.get_running_loop().create_future()

    async def too_slow():
        await asyncio.sleep(0.05)

    service_call = {"function": too_slow, "args": (), "kwargs": {}, "future": future}
    queue_manager.queue.put_nowait(service_call)
    await queue_manager._process_service_call(
        service_call
    )

    assert isinstance(future.exception(), TimeoutError)


@pytest.mark.asyncio
async def test_queue_manager_reset_queue_cancels_pending_futures(monkeypatch: pytest.MonkeyPatch) -> None:
    """Resetting the queue should cancel any pending queued futures and restart processing."""
    queue_manager = ChimeTTSQueueManager()
    restarted: list[bool] = []

    async def noop():
        return None

    future = queue_manager.add_to_queue(noop, 60)
    monkeypatch.setattr(queue_manager, "start_queue_processor", lambda: restarted.append(True))

    queue_manager.reset_queue()

    assert future.cancelled()
    assert restarted == [True]
    assert queue_manager.queue.empty()


@pytest.mark.asyncio
async def test_async_prepare_media_service_calls_groups_standard_players(monkeypatch: pytest.MonkeyPatch) -> None:
    """Standard media players should share one play_media service call."""
    helper = integration_module.media_player_helper

    helper.joined_entity_id = None
    monkeypatch.setattr(helper, "get_is_standard_media_player", lambda entity_id: entity_id.startswith("media_player.standard"))
    monkeypatch.setattr(helper, "get_media_players_of_platform", lambda entity_ids, platform: [])

    calls = await integration_module.async_prepare_media_service_calls(
        hass=FakeHass(),
        entity_ids=["media_player.standard_one", "media_player.standard_two"],
        service_data={
            CONF_ENTITY_ID: [],
            ATTR_MEDIA_ANNOUNCE: True,
            ATTR_MEDIA_CONTENT_TYPE: MediaType.MUSIC,
            ATTR_MEDIA_CONTENT_ID: "media-source://media_source/media/file.mp3",
        },
        audio_dict={PUBLIC_PATH_KEY: None},
    )

    assert calls == [
        {
            "domain": "media_player",
            "service": "play_media",
            "service_data": {
                CONF_ENTITY_ID: ["media_player.standard_one", "media_player.standard_two"],
                ATTR_MEDIA_ANNOUNCE: True,
                ATTR_MEDIA_CONTENT_TYPE: MediaType.MUSIC,
                ATTR_MEDIA_CONTENT_ID: "media-source://media_source/media/file.mp3",
            },
            "blocking": True,
            "result": True,
        }
    ]


@pytest.mark.asyncio
async def test_async_prepare_media_service_calls_splits_non_uniform_sonos(monkeypatch: pytest.MonkeyPatch) -> None:
    """Sonos players with different target volumes should each get their own play call."""
    helper = integration_module.media_player_helper

    helper.joined_entity_id = None
    monkeypatch.setattr(helper, "get_is_standard_media_player", lambda entity_id: False)
    monkeypatch.setattr(
        helper,
        "get_media_players_of_platform",
        lambda entity_ids, platform: entity_ids if platform == SONOS_PLATFORM else [],
    )
    monkeypatch.setattr(helper, "get_uniform_target_volume_level", lambda entity_ids: -1)
    monkeypatch.setattr(
        helper,
        "get_media_players_from_entity_ids",
        lambda entity_ids: [
            SimpleNamespace(entity_id="media_player.sonos_one", target_volume_level=0.25),
            SimpleNamespace(entity_id="media_player.sonos_two", target_volume_level=0.4),
        ],
    )

    calls = await integration_module.async_prepare_media_service_calls(
        hass=FakeHass(),
        entity_ids=["media_player.sonos_one", "media_player.sonos_two"],
        service_data={
            CONF_ENTITY_ID: [],
            ATTR_MEDIA_ANNOUNCE: False,
            ATTR_MEDIA_CONTENT_TYPE: MediaType.MUSIC,
            ATTR_MEDIA_CONTENT_ID: "media-source://media_source/media/file.mp3",
        },
        audio_dict={PUBLIC_PATH_KEY: None},
    )

    assert calls == [
        {
            "domain": "media_player",
            "service": "play_media",
            "service_data": {
                CONF_ENTITY_ID: "media_player.sonos_one",
                ATTR_MEDIA_ANNOUNCE: False,
                ATTR_MEDIA_CONTENT_TYPE: MediaType.MUSIC,
                ATTR_MEDIA_CONTENT_ID: "media-source://media_source/media/file.mp3",
                "extra": {"volume": 25},
            },
            "blocking": True,
            "result": True,
        },
        {
            "domain": "media_player",
            "service": "play_media",
            "service_data": {
                CONF_ENTITY_ID: "media_player.sonos_two",
                ATTR_MEDIA_ANNOUNCE: False,
                ATTR_MEDIA_CONTENT_TYPE: MediaType.MUSIC,
                ATTR_MEDIA_CONTENT_ID: "media-source://media_source/media/file.mp3",
                "extra": {"volume": 40},
            },
            "blocking": True,
            "result": True,
        },
    ]


@pytest.mark.asyncio
async def test_async_prepare_media_service_calls_converts_alexa_public_audio(monkeypatch: pytest.MonkeyPatch) -> None:
    """Alexa service calls should convert incompatible public audio and send a notify payload."""
    helper = integration_module.media_player_helper

    helper.joined_entity_id = None
    monkeypatch.setattr(helper, "get_is_standard_media_player", lambda entity_id: False)
    monkeypatch.setattr(
        helper,
        "get_media_players_of_platform",
        lambda entity_ids, platform: entity_ids if platform == ALEXA_MEDIA_PLAYER_PLATFORM else [],
    )
    monkeypatch.setattr(
        integration_module.filesystem_helper,
        "async_is_audio_alexa_compatible",
        AsyncMock(return_value=False),
    )
    monkeypatch.setattr(
        integration_module.helpers,
        "async_ffmpeg_convert_from_file",
        AsyncMock(return_value="https://example.test/alexa.mp3"),
    )

    calls = await integration_module.async_prepare_media_service_calls(
        hass=FakeHass(),
        entity_ids=["media_player.echo"],
        service_data={
            CONF_ENTITY_ID: [],
            ATTR_MEDIA_ANNOUNCE: True,
            ATTR_MEDIA_CONTENT_TYPE: MediaType.MUSIC,
            ATTR_MEDIA_CONTENT_ID: None,
        },
        audio_dict={PUBLIC_PATH_KEY: "https://example.test/source.mp3"},
    )

    assert calls == [
        {
            "domain": "notify",
            "service": "alexa_media",
            "service_data": {
                "message": "<audio src='https://example.test/alexa.mp3'/>",
                "data": {"type": "tts"},
                "target": ["media_player.echo"],
            },
            "result": False,
        }
    ]


def test_tts_audio_helper_prepare_request_rewrites_microsoft_voice_and_language(monkeypatch: pytest.MonkeyPatch) -> None:
    """Microsoft TTS should rewrite voice to `type` and normalize the language source."""
    helper = TTSAudioHelper()
    helper._data[TTS_PLATFORM_KEY] = GOOGLE_TRANSLATE
    helper._data[FALLBACK_TTS_PLATFORM_KEY] = "fallback"

    monkeypatch.setattr(tts_audio_module.helpers, "get_tts_platform", lambda **kwargs: MICROSOFT_TTS)

    platform, options, language = helper._prepare_tts_request(
        hass=FakeHass(),
        tts_platform=MICROSOFT_TTS,
        message="hello",
        language=None,
        options={"language": "en-US", "voice": "JennyNeural"},
    )

    assert platform == MICROSOFT_TTS
    assert options == {"type": "JennyNeural"}
    assert language == "en-US"


def test_tts_audio_helper_prepare_request_sets_watson_voice_from_language(monkeypatch: pytest.MonkeyPatch) -> None:
    """Watson TTS should move the requested language into the voice field when needed."""
    helper = TTSAudioHelper()
    helper._data[TTS_PLATFORM_KEY] = IBM_WATSON_TTS
    helper._data[FALLBACK_TTS_PLATFORM_KEY] = ""

    monkeypatch.setattr(tts_audio_module.helpers, "get_tts_platform", lambda **kwargs: IBM_WATSON_TTS)

    platform, options, language = helper._prepare_tts_request(
        hass=FakeHass(),
        tts_platform=IBM_WATSON_TTS,
        message="hello",
        language="en-US_AllisonV3Voice",
        options={},
    )

    assert platform == IBM_WATSON_TTS
    assert options == {"voice": "en-US_AllisonV3Voice"}
    assert language is None


def test_tts_audio_helper_adjusts_nabu_casa_language_from_voice() -> None:
    """Nabu Casa voice choices should backfill language when only the voice was provided."""
    helper = TTSAudioHelper()
    options = {"voice": "Jenny"}

    original_voices = dict(tts_audio_module.nabu_voices.TTS_VOICES)
    tts_audio_module.nabu_voices.TTS_VOICES = {"en-US": ["Jenny", "Guy"]}
    try:
        language = helper._adjust_language_and_voice(NABU_CASA_CLOUD_TTS, None, options)
    finally:
        tts_audio_module.nabu_voices.TTS_VOICES = original_voices

    assert language == "en-US"


@pytest.mark.asyncio
async def test_tts_audio_helper_generate_audio_retries_prefixed_engine(monkeypatch: pytest.MonkeyPatch) -> None:
    """TTS engines are normalized to the `tts.` entity-id form before generation."""
    helper = TTSAudioHelper()
    helper._data[TTS_TIMEOUT_KEY] = 1
    requested_engines: list[str] = []

    def fake_generate_media_source_id(**kwargs):
        requested_engines.append(kwargs["engine"])
        return "media-source://tts/google"

    monkeypatch.setattr(tts_audio_module.tts.media_source, "generate_media_source_id", fake_generate_media_source_id)

    media_source_id, audio_data = await helper._generate_tts_audio(
        hass=FakeHass(),
        tts_platform=GOOGLE_TRANSLATE,
        message="hello",
        language="en",
        cache=True,
        tts_options={},
    )

    assert requested_engines == [f"tts.{GOOGLE_TRANSLATE}"]
    assert media_source_id == "media-source://tts/google"
    assert audio_data is None


@pytest.mark.asyncio
async def test_tts_audio_helper_retry_with_fallback_calls_async_request(monkeypatch: pytest.MonkeyPatch) -> None:
    """Fallback retries should delegate back through `async_request_tts_audio`."""
    helper = TTSAudioHelper()
    helper._data[FALLBACK_TTS_PLATFORM_KEY] = "fallback_engine"
    request_tts = AsyncMock(return_value="audio")

    monkeypatch.setattr(helper, "async_request_tts_audio", request_tts)

    result = await helper._retry_with_fallback(
        hass=FakeHass(),
        tts_platform="primary_engine",
        message="hello",
        language="en",
        cache=True,
        options={"voice": "Jenny"},
    )

    assert result == "audio"
    request_tts.assert_awaited_once_with(
        hass=ANY,
        tts_platform="fallback_engine",
        message="hello",
        language="en",
        cache=True,
        options={"voice": "Jenny"},
        is_fallback=True,
    )


@pytest.mark.asyncio
async def test_tts_audio_helper_extract_audio_loads_segment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Extracting TTS audio should return the decoded audio segment."""
    helper = TTSAudioHelper()
    audio = AudioSegment.silent(duration=250)

    monkeypatch.setattr(tts_audio_module.filesystem_helper, "async_load_audio", AsyncMock(return_value=audio))

    result = await helper._extract_audio(("audio/mpeg", b"binary-audio"), start_time=datetime.now())

    assert result == audio
