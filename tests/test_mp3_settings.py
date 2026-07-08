"""Tests for MP3 output settings and processing."""

from __future__ import annotations

import hashlib
import importlib
import inspect
import json
import subprocess
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from pydub import AudioSegment
from pydub.generators import Sine

from custom_components.chime_tts.const import AUDIO_DURATION_KEY
from custom_components.chime_tts.const import FFMPEG_ARGS_ALEXA
from custom_components.chime_tts.const import LOCAL_PATH_KEY
from custom_components.chime_tts.const import PUBLIC_PATH_KEY
from custom_components.chime_tts.const import TEMP_PATH_KEY
from custom_components.chime_tts.const import WWW_PATH_KEY
from custom_components.chime_tts.helpers.filesystem import FilesystemHelper
from custom_components.chime_tts.helpers import helpers as helpers_module
from custom_components.chime_tts.helpers.helpers import ChimeTTSHelper
from homeassistant.components.media_player.const import ATTR_MEDIA_CONTENT_ID
from pydub.generators import Square

integration_module = importlib.import_module("custom_components.chime_tts.__init__")

EXPECTED_PCM_MD5 = {
    "base": "fbb9c6e77875d2a4756796dde5dae858",
    "speed125": "27ab47cf8a4ec4ec9c06420e52216ccd",
    "pitch12": "6899ada5e1a53a3135ba7ccb8ab050b3",
    "alexa": "2c6ce06185e4b841a3c2e825191da9c6",
    "delay": "c53002b2dd22145acfb5f31e438fe469",
    "yaml_combo": "fc46c44180390c480f9029f872a11bab",
}


class FakeHass:
    """Small Home Assistant stand-in for unit tests."""

    def __init__(self) -> None:
        """Initialise the fake object."""
        self.config = SimpleNamespace(path=lambda *parts: f"/config/{'/'.join(parts)}")

    async def async_add_executor_job(self, func, *args):
        """Run executor jobs inline for tests."""
        return func(*args)


@pytest.fixture
def helper() -> ChimeTTSHelper:
    """Return a fresh helper instance."""
    return ChimeTTSHelper()


@pytest.fixture
def filesystem_helper() -> FilesystemHelper:
    """Return a filesystem helper instance."""
    return FilesystemHelper()


def generate_base_tone() -> AudioSegment:
    """Generate a deterministic source tone for artifact tests."""
    return Sine(440).to_audio_segment(duration=1000).set_frame_rate(44100).set_channels(1)


def probe_media_file(path: str) -> dict:
    """Return ffprobe JSON for a generated media file."""
    output = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", path],
        text=True,
    )
    return json.loads(output)


def test_parse_ffmpeg_args_supports_named_presets(helper: ChimeTTSHelper) -> None:
    """Named audio conversion presets should map to FFmpeg args."""
    assert helper.parse_ffmpeg_args("Alexa") == "-y -ac 2 -codec:a libmp3lame -b:a 48k -ar 24000 -write_xing 0"
    assert helper.parse_ffmpeg_args("Volume 125%") == "-filter:a volume=1.25"
    assert helper.parse_ffmpeg_args("Custom") is None


@pytest.mark.asyncio
async def test_async_parse_params_supports_deprecated_aliases_and_flags(helper: ChimeTTSHelper) -> None:
    """Parameter parsing should preserve deprecated aliases and exposed flags."""
    hass = FakeHass()

    class FakeMediaPlayerHelper:
        """Minimal media player helper for parameter parsing tests."""

        def parse_entity_ids(self, data, hass):
            """Return parsed entity ids."""
            del hass
            return data["entity_id"]

        async def async_initialize_media_players(
            self,
            hass,
            entity_ids,
            volume_level,
            join_players,
            unjoin_players,
            announce,
            fade_audio,
        ):
            """Return a non-empty media-player list so parsing can continue."""
            del hass, entity_ids, volume_level, join_players, unjoin_players, announce, fade_audio
            return ["media_player.kitchen"]

    params = await helper.async_parse_params(
        hass=hass,
        data={
            "entity_id": ["media_player.kitchen"],
            "chime_path": "bells",
            "end_chime_path": "tada",
            "delay": 125,
            "crossfade": 25,
            "final_delay": 300,
            "message": "hello",
            "tts_platform": "google_translate",
            "tts_playback_speed": 135,
            "tts_pitch": 4,
            "volume_level": 0.4,
            "join_players": True,
            "unjoin_players": True,
            "language": "en",
            "cache": True,
            "announce": True,
            "fade_audio": True,
            "audio_conversion": "Volume 125%",
        },
        is_say_url=False,
        media_player_helper=FakeMediaPlayerHelper(),
    )

    assert params is not None
    assert params["entity_ids"] == ["media_player.kitchen"]
    assert params["chime_path"] == "bells"
    assert params["end_chime_path"] == "tada"
    assert params["offset"] == 125.0
    assert params["crossfade"] == 25
    assert params["final_delay"] == 300.0
    assert params["tts_speed"] == 135.0
    assert params["tts_pitch"] == 4
    assert params["volume_level"] == 0.4
    assert params["join_players"] is True
    assert params["unjoin_players"] is True
    assert params["cache"] is True
    assert params["announce"] is True
    assert params["fade_audio"] is True
    assert params["ffmpeg_args"] == "-filter:a volume=1.25"


@pytest.mark.asyncio
async def test_async_parse_params_returns_none_without_media_players(helper: ChimeTTSHelper) -> None:
    """Non-say_url calls should fail fast when no valid media players were resolved."""
    hass = FakeHass()

    class EmptyMediaPlayerHelper:
        """Media player helper that resolves no players."""

        def parse_entity_ids(self, data, hass):
            """Return an empty entity list."""
            del data, hass
            return []

        async def async_initialize_media_players(self, *args, **kwargs):
            """Return no media players."""
            del args, kwargs
            return []

    params = await helper.async_parse_params(
        hass=hass,
        data={"message": "hello"},
        is_say_url=False,
        media_player_helper=EmptyMediaPlayerHelper(),
    )

    assert params is None


def test_parse_options_yaml_applies_defaults_only_for_matching_platform(helper: ChimeTTSHelper) -> None:
    """Default language, voice, and TLD should only apply when the selected platform matches."""
    defaults = {
        "tts_platform_key": "google_translate",
        "default_language_key": "en-US",
        "default_voice_key": "Jenny",
        "default_tld_key": "co.uk",
    }

    options = helper.parse_options_yaml({"options": "", "tts_platform": "google_translate"}, defaults)
    assert options == {"language": "en-US", "voice": "Jenny", "tld": "co.uk"}

    non_default_options = helper.parse_options_yaml({"options": "", "tts_platform": "cloud"}, defaults)
    assert non_default_options == {}


def test_parse_options_yaml_merges_yaml_and_exposed_fields(helper: ChimeTTSHelper) -> None:
    """Explicit voice and tld fields should merge into parsed YAML options."""
    options = helper.parse_options_yaml(
        {
            "options": "language: fr-FR",
            "voice": "Brigitte",
            "tld": "fr",
        },
        {},
    )

    assert options == {"language": "fr-FR", "voice": "Brigitte", "tld": "fr"}


def test_parse_message_returns_plain_tts_segment_for_plain_text(helper: ChimeTTSHelper) -> None:
    """Plain text input should become a single TTS segment."""
    assert helper.parse_message("Hello world") == [{"type": "tts", "message": "Hello world"}]


def test_parse_message_normalizes_short_format_repeat_and_aliases(helper: ChimeTTSHelper) -> None:
    """Short YAML format should be expanded into normalized segment dictionaries."""
    message = """
- chime: bells
  repeat: 2
- tts: "Hello there"
  speed: 125
  pitch: -2
- delay: 500
"""

    segments = helper.parse_message(message)

    assert segments == [
        {"type": "chime", "path": "bells", "repeat": 2},
        {"type": "chime", "path": "bells", "repeat": 2},
        {"type": "tts", "message": "Hello there", "tts_speed": 125, "tts_pitch": -2},
        {"type": "delay", "length": 500},
    ]


def test_parse_message_falls_back_to_tts_for_invalid_yaml_segments(helper: ChimeTTSHelper) -> None:
    """Invalid YAML segment lists should be treated as plain TTS text."""
    message = """
- something_else: bells
- totally: invalid
"""

    segments = helper.parse_message(message)

    assert segments == [{"type": "tts", "message": message}]


def test_parse_message_removes_niqqud(helper: ChimeTTSHelper) -> None:
    """Hebrew niqqud should be stripped before creating the TTS segment."""
    segments = helper.parse_message("שָׁלוֹם")

    assert segments == [{"type": "tts", "message": "שלום"}]


def test_add_atempo_values_supports_sub_half_values(helper: ChimeTTSHelper) -> None:
    """Very slow playback requires chained atempo filters."""
    assert helper.add_atempo_values_to_ffmpeg_args_string(0.25) == "-af atempo=0.5,atempo=0.5"


@pytest.mark.asyncio
async def test_change_speed_builds_expected_ffmpeg_args(helper: ChimeTTSHelper) -> None:
    """Speed changes should translate to the expected FFmpeg filter chain."""
    audio = object()
    hass = FakeHass()
    helper.async_ffmpeg_convert_from_audio_segment = AsyncMock(return_value="converted")

    result = await helper.async_change_speed_of_audiosegment(hass, audio, speed=25, temp_folder="/tmp")

    assert result == "converted"
    helper.async_ffmpeg_convert_from_audio_segment.assert_awaited_once_with(
        hass=hass,
        audio_segment=audio,
        ffmpeg_args="-af atempo=0.5,atempo=0.5",
        folder="/tmp",
    )


@pytest.mark.asyncio
async def test_change_pitch_builds_expected_ffmpeg_args(helper: ChimeTTSHelper) -> None:
    """Pitch shifts should preserve tempo by pairing asetrate with atempo."""
    audio = SimpleNamespace(frame_rate=44100)
    hass = FakeHass()
    helper.async_ffmpeg_convert_from_audio_segment = AsyncMock(return_value="converted")

    result = await helper.async_change_pitch_of_audiosegment(hass, audio, pitch=12, temp_folder="/tmp")

    assert result == "converted"
    helper.async_ffmpeg_convert_from_audio_segment.assert_awaited_once_with(
        hass=hass,
        audio_segment=audio,
        ffmpeg_args="-af asetrate=44100*2.0,atempo=0.5",
        folder="/tmp",
    )


def test_combine_audio_applies_positive_offset(helper: ChimeTTSHelper) -> None:
    """Positive offset should add silence between segments."""
    audio_1 = AudioSegment.silent(duration=1000)
    audio_2 = AudioSegment.silent(duration=500)

    combined = helper.combine_audio(audio_1, audio_2, offset=200)

    assert len(combined) == 1700


def test_combine_audio_applies_crossfade(helper: ChimeTTSHelper) -> None:
    """Crossfade should reduce the total duration by the overlap amount."""
    audio_1 = AudioSegment.silent(duration=1000)
    audio_2 = AudioSegment.silent(duration=500)

    combined = helper.combine_audio(audio_1, audio_2, crossfade=800)

    assert len(combined) == 1000


def test_combine_audio_applies_overlay(helper: ChimeTTSHelper) -> None:
    """Negative offset should overlap audio segments."""
    audio_1 = AudioSegment.silent(duration=1000)
    audio_2 = AudioSegment.silent(duration=500)

    combined = helper.combine_audio(audio_1, audio_2, offset=-250)

    assert len(combined) == 1250


@pytest.mark.asyncio
async def test_ffmpeg_convert_skips_alexa_compatible_files(monkeypatch: pytest.MonkeyPatch, helper: ChimeTTSHelper) -> None:
    """Alexa-compatible MP3s should not be converted again."""
    hass = FakeHass()
    popen = AsyncMock()

    monkeypatch.setattr(
        helpers_module.filesystem_helper,
        "async_get_local_path",
        AsyncMock(return_value="/tmp/source.mp3"),
    )
    monkeypatch.setattr(helpers_module.os.path, "isfile", lambda path: True)
    monkeypatch.setattr(helpers_module.filesystem_helper, "path_exists", lambda path: True)
    monkeypatch.setattr(helpers_module.filesystem_helper, "async_is_audio_alexa_compatible", AsyncMock(return_value=True))
    monkeypatch.setattr(helpers_module.subprocess, "Popen", popen)

    result = await helper.async_ffmpeg_convert_from_file(hass, "media.mp3", FFMPEG_ARGS_ALEXA)

    assert result == "media.mp3"
    popen.assert_not_called()


@pytest.mark.asyncio
async def test_ffmpeg_convert_uses_requested_output_format(monkeypatch: pytest.MonkeyPatch, helper: ChimeTTSHelper) -> None:
    """Explicit output formats should be passed through to FFmpeg."""
    hass = FakeHass()
    commands: list[list[str]] = []

    class FakePopen:
        """Capture subprocess commands without running FFmpeg."""

        def __init__(self, command, stdin=None, stdout=None, stderr=None):
            """Store the command and emulate a successful process."""
            del stdin, stdout, stderr
            commands.append(command)
            self.returncode = 0

        def communicate(self):
            """Return an empty stderr payload."""
            return b"", b""

    monkeypatch.setattr(
        helpers_module.filesystem_helper,
        "async_get_local_path",
        AsyncMock(return_value="/tmp/source.mp3"),
    )
    monkeypatch.setattr(helpers_module.os.path, "isfile", lambda path: True)
    monkeypatch.setattr(helpers_module.filesystem_helper, "path_exists", lambda path: False)
    monkeypatch.setattr(helpers_module.subprocess, "Popen", FakePopen)

    result = await helper.async_ffmpeg_convert_from_file(hass, "media.mp3", "-f wav -ar 16000")

    assert result == "media.mp3"
    assert commands == [["ffmpeg", "-i", "/tmp/source.mp3", "-f", "wav", "-ar", "16000", "/tmp/source.wav"]]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("name", "transform", "expected_duration_ms", "expected_sample_rate", "expected_channels"),
    [
        ("base", lambda helper, hass, audio, folder: audio, 1000, "44100", 1),
        ("speed125", lambda helper, hass, audio, folder: helper.async_change_speed_of_audiosegment(hass, audio, 125, folder), 800, "44100", 1),
        ("pitch12", lambda helper, hass, audio, folder: helper.async_change_pitch_of_audiosegment(hass, audio, 12, folder), 974, "48000", 1),
        ("alexa", lambda helper, hass, audio, folder: helper.async_ffmpeg_convert_from_audio_segment(hass, audio, FFMPEG_ARGS_ALEXA, folder), 1056, "24000", 2),
        ("delay", lambda helper, hass, audio, folder: helper.combine_audio(audio, AudioSegment.silent(duration=200), offset=0), 1200, "44100", 1),
    ],
)
async def test_mp3_artifacts_have_expected_audio_fingerprint(
    helper: ChimeTTSHelper,
    filesystem_helper: FilesystemHelper,
    tmp_path,
    name: str,
    transform,
    expected_duration_ms: int,
    expected_sample_rate: str,
    expected_channels: int,
) -> None:
    """Generated MP3 artifacts should decode to stable, known audio output."""
    hass = FakeHass()
    source_audio = generate_base_tone()
    transformed = transform(helper, hass, source_audio, str(tmp_path))
    if inspect.isawaitable(transformed):
        transformed = await transformed

    artifact_path = await filesystem_helper.async_save_audio_to_folder(hass, transformed, str(tmp_path), f"{name}.mp3")

    assert artifact_path is not None

    decoded = await filesystem_helper.async_load_audio(artifact_path)
    normalized = decoded.set_channels(1).set_frame_rate(16000).set_sample_width(2)
    assert hashlib.md5(normalized.raw_data).hexdigest() == EXPECTED_PCM_MD5[name]
    assert len(decoded) == expected_duration_ms

    probe_data = probe_media_file(artifact_path)
    audio_stream = next(stream for stream in probe_data["streams"] if stream["codec_type"] == "audio")
    assert audio_stream["codec_name"] == "mp3"
    assert audio_stream["sample_rate"] == expected_sample_rate
    assert audio_stream["channels"] == expected_channels


@pytest.mark.asyncio
async def test_mp3_artifact_can_embed_cover_art(filesystem_helper: FilesystemHelper, helper: ChimeTTSHelper, tmp_path) -> None:
    """Adding cover art should create an attached picture stream without changing audio content."""
    hass = FakeHass()
    base_audio = generate_base_tone()
    source_path = await filesystem_helper.async_save_audio_to_folder(hass, base_audio, str(tmp_path), "cover_source.mp3")
    cover_art_path = f"{helpers_module.filesystem_helper.path_to_parent_folder('custom_components')}/chime_tts/cover_art.jpg"

    output_path = await helper.async_ffmpeg_convert_from_file(
        hass,
        source_path,
        f"-i {cover_art_path} -c copy -map 0 -map 1",
    )

    assert output_path == source_path

    probe_data = probe_media_file(output_path)
    audio_stream = next(stream for stream in probe_data["streams"] if stream["codec_type"] == "audio")
    image_stream = next(stream for stream in probe_data["streams"] if stream["codec_type"] == "video")
    normalized = (await filesystem_helper.async_load_audio(output_path)).set_channels(1).set_frame_rate(16000).set_sample_width(2)

    assert hashlib.md5(normalized.raw_data).hexdigest() == EXPECTED_PCM_MD5["base"]
    assert audio_stream["codec_name"] == "mp3"
    assert image_stream["codec_name"] == "mjpeg"
    assert image_stream["disposition"]["attached_pic"] == 1


@pytest.mark.asyncio
async def test_async_verify_cached_audio_deletes_missing_cache_entry(monkeypatch: pytest.MonkeyPatch) -> None:
    """Missing cached files should evict the stored cache entry."""
    hass = FakeHass()
    delete_data = AsyncMock()

    monkeypatch.setattr(
        integration_module,
        "async_get_cached_audio_data",
        AsyncMock(
            return_value={
                LOCAL_PATH_KEY: "/tmp/missing-local.mp3",
                PUBLIC_PATH_KEY: "/media/missing-public.mp3",
                AUDIO_DURATION_KEY: 1.0,
            }
        ),
    )
    monkeypatch.setattr(integration_module, "async_delete_data", delete_data)
    monkeypatch.setattr(integration_module.filesystem_helper, "path_exists", lambda path: False)
    monkeypatch.setattr(
        integration_module.filesystem_helper,
        "get_local_path",
        lambda hass, file_path: "/config/www/missing-public.mp3",
    )

    result = await integration_module.async_verify_cached_audio(
        hass=hass,
        filepath_hash="deadbeef",
        params={},
        options={},
        is_local=True,
        is_public=True,
        ffmpeg_args="",
    )

    assert result is None
    delete_data.assert_awaited_once_with(hass=hass, key="deadbeef")


@pytest.mark.asyncio
async def test_async_verify_cached_audio_recovers_missing_local_copy(monkeypatch: pytest.MonkeyPatch) -> None:
    """A cached public file should be copied back into the local temp folder when needed."""
    hass = FakeHass()
    add_to_cache = AsyncMock()
    path_exists_results = iter([False, True, True, True])

    integration_module._data[TEMP_PATH_KEY] = "/tmp/chime-local"

    monkeypatch.setattr(
        integration_module,
        "async_get_cached_audio_data",
        AsyncMock(
            return_value={
                LOCAL_PATH_KEY: None,
                PUBLIC_PATH_KEY: "/media/public.mp3",
                AUDIO_DURATION_KEY: 1.5,
            }
        ),
    )
    monkeypatch.setattr(integration_module, "async_add_audio_file_to_cache", add_to_cache)
    monkeypatch.setattr(
        integration_module.filesystem_helper,
        "path_exists",
        lambda path: next(path_exists_results),
    )
    monkeypatch.setattr(
        integration_module.filesystem_helper,
        "get_local_path",
        lambda hass, file_path: "/config/www/public.mp3",
    )
    monkeypatch.setattr(
        integration_module.filesystem_helper,
        "async_copy_file",
        AsyncMock(return_value="/tmp/chime-local/public.mp3"),
    )
    monkeypatch.setattr(
        integration_module.filesystem_helper,
        "async_get_external_url",
        AsyncMock(return_value="https://example.test/local/public.mp3"),
    )
    monkeypatch.setattr(
        integration_module.media_player_helper,
        "get_media_content_id",
        lambda hass, file_path: f"media:{file_path}",
    )

    result = await integration_module.async_verify_cached_audio(
        hass=hass,
        filepath_hash="recover-local",
        params={"message": "hello"},
        options={},
        is_local=True,
        is_public=True,
        ffmpeg_args="",
    )

    assert result == {
        LOCAL_PATH_KEY: "/tmp/chime-local/public.mp3",
        PUBLIC_PATH_KEY: "https://example.test/local/public.mp3",
        AUDIO_DURATION_KEY: 1.5,
        ATTR_MEDIA_CONTENT_ID: "media:/tmp/chime-local/public.mp3",
    }
    add_to_cache.assert_awaited_once_with(
        hass,
        "/tmp/chime-local/public.mp3",
        1.5,
        {"message": "hello"},
        {},
    )


@pytest.mark.asyncio
async def test_async_verify_cached_audio_recovers_missing_public_copy(monkeypatch: pytest.MonkeyPatch) -> None:
    """A cached local file should be copied into the public folder when `say_url` needs it."""
    hass = FakeHass()
    add_to_cache = AsyncMock()
    path_exists_results = iter([True, False, True])

    integration_module._data[WWW_PATH_KEY] = "/config/www/chime_tts"

    monkeypatch.setattr(
        integration_module,
        "async_get_cached_audio_data",
        AsyncMock(
            return_value={
                LOCAL_PATH_KEY: "/media/local.mp3",
                PUBLIC_PATH_KEY: None,
                AUDIO_DURATION_KEY: 2.0,
            }
        ),
    )
    monkeypatch.setattr(integration_module, "async_add_audio_file_to_cache", add_to_cache)
    monkeypatch.setattr(
        integration_module.filesystem_helper,
        "path_exists",
        lambda path: next(path_exists_results),
    )
    monkeypatch.setattr(
        integration_module.filesystem_helper,
        "get_local_path",
        lambda hass, file_path: "",
    )
    monkeypatch.setattr(
        integration_module.filesystem_helper,
        "async_copy_file",
        AsyncMock(return_value="/config/www/chime_tts/local.mp3"),
    )
    monkeypatch.setattr(
        integration_module.filesystem_helper,
        "async_get_external_url",
        AsyncMock(return_value="https://example.test/public/local.mp3"),
    )
    monkeypatch.setattr(
        integration_module.media_player_helper,
        "get_media_content_id",
        lambda hass, file_path: f"media:{file_path}",
    )

    result = await integration_module.async_verify_cached_audio(
        hass=hass,
        filepath_hash="recover-public",
        params={},
        options={"cache": True},
        is_local=False,
        is_public=True,
        ffmpeg_args="",
    )

    assert result == {
        LOCAL_PATH_KEY: "/media/local.mp3",
        PUBLIC_PATH_KEY: "https://example.test/public/local.mp3",
        AUDIO_DURATION_KEY: 2.0,
        ATTR_MEDIA_CONTENT_ID: "media:/media/local.mp3",
    }
    add_to_cache.assert_awaited_once_with(
        hass,
        "/config/www/chime_tts/local.mp3",
        2.0,
        {},
        {"cache": True},
    )


@pytest.mark.asyncio
async def test_async_verify_cached_audio_skips_non_alexa_reconversion(monkeypatch: pytest.MonkeyPatch) -> None:
    """Cached audio should not be reconverted when the cache key already encodes the conversion."""
    hass = FakeHass()
    ffmpeg_convert = AsyncMock()

    monkeypatch.setattr(
        integration_module,
        "async_get_cached_audio_data",
        AsyncMock(
            return_value={
                LOCAL_PATH_KEY: "/media/local.mp3",
                PUBLIC_PATH_KEY: "/media/public.mp3",
                AUDIO_DURATION_KEY: 1.0,
            }
        ),
    )
    monkeypatch.setattr(integration_module.filesystem_helper, "path_exists", lambda path: True)
    monkeypatch.setattr(
        integration_module.filesystem_helper,
        "async_get_local_path",
        AsyncMock(return_value="/config/www/public.mp3"),
    )
    monkeypatch.setattr(
        integration_module.filesystem_helper,
        "async_get_external_url",
        AsyncMock(return_value="https://example.test/public.mp3"),
    )
    monkeypatch.setattr(
        integration_module.media_player_helper,
        "get_media_content_id",
        lambda hass, file_path: "media:cached",
    )
    monkeypatch.setattr(integration_module.helpers, "async_ffmpeg_convert_from_file", ffmpeg_convert)

    result = await integration_module.async_verify_cached_audio(
        hass=hass,
        filepath_hash="convert",
        params={},
        options={},
        is_local=True,
        is_public=True,
        ffmpeg_args="-af volume=1.25",
    )

    assert result[ATTR_MEDIA_CONTENT_ID] == "media:cached"
    assert result[PUBLIC_PATH_KEY] == "https://example.test/public.mp3"
    assert ffmpeg_convert.await_args_list == []


@pytest.mark.asyncio
async def test_async_prepare_media_returns_say_url_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    """`say_url` should return the generated public URL and metadata without playback work."""
    monkeypatch.setattr(
        integration_module,
        "async_get_playback_audio_path",
        AsyncMock(
            return_value={
                LOCAL_PATH_KEY: "/media/chime.mp3",
                PUBLIC_PATH_KEY: "https://example.test/chime.mp3",
                ATTR_MEDIA_CONTENT_ID: "media:chime",
                AUDIO_DURATION_KEY: 3.25,
            }
        ),
    )

    result = await integration_module.async_prepare_media(
        hass=FakeHass(),
        params={"cache": True},
        options={},
        media_players_array=[],
        is_say_url=True,
        start_time=datetime.now(),
    )

    assert result == {
        "url": "https://example.test/chime.mp3",
        ATTR_MEDIA_CONTENT_ID: "media:chime",
        "duration": 3.25,
        "success": True,
    }


@pytest.mark.asyncio
async def test_yaml_combo_artifact_has_expected_audio_fingerprint(
    filesystem_helper: FilesystemHelper,
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A mixed YAML sequence should render to a stable combined audio artifact."""
    hass = FakeHass()
    integration_module._data[TEMP_PATH_KEY] = str(tmp_path)

    async def fake_get_audio_from_path(
        hass,
        filepath,
        cache=False,
        offset=0,
        crossfade=0,
        audio_conversion="",
        audio=None,
    ):
        del hass, cache, audio_conversion
        if filepath == "intro":
            segment = Square(220).to_audio_segment(duration=120).set_frame_rate(44100).set_channels(1)
        elif filepath == "outro":
            segment = Square(660).to_audio_segment(duration=90).set_frame_rate(44100).set_channels(1)
        else:
            raise AssertionError(f"Unexpected chime path: {filepath}")
        return integration_module.helpers.combine_audio(audio, segment, offset, crossfade)

    monkeypatch.setattr(integration_module, "async_get_audio_from_path", fake_get_audio_from_path)
    monkeypatch.setattr(
        integration_module.tts_audio_helper,
        "async_request_tts_audio",
        AsyncMock(return_value=Sine(440).to_audio_segment(duration=300).set_frame_rate(44100).set_channels(1)),
    )

    output = await integration_module.async_process_segments(
        hass=hass,
        message="""
- chime: intro
  repeat: 2
- delay: 150
- tts: "Hello there"
  speed: 125
  pitch: -3
- chime: outro
  offset: -50
""",
        output_audio=None,
        params={
            "tts_platform": "google_translate",
            "language": "en",
            "cache": False,
            "tts_speed": 100,
            "tts_pitch": 0,
            "offset": 0,
            "crossfade": 0,
        },
        options={},
    )

    artifact_path = await filesystem_helper.async_save_audio_to_folder(
        hass, output, str(tmp_path), "yaml_combo.mp3"
    )
    decoded = await filesystem_helper.async_load_audio(artifact_path)
    normalized = decoded.set_channels(1).set_frame_rate(16000).set_sample_width(2)

    assert hashlib.md5(normalized.raw_data).hexdigest() == EXPECTED_PCM_MD5["yaml_combo"]
    assert len(decoded) == 673
