"""Tests for deterministic filesystem helper behaviour."""

from __future__ import annotations

import importlib
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from custom_components.chime_tts.helpers.filesystem import FilesystemHelper


class Hass:
    """Minimal Home Assistant facade for filesystem helper tests."""

    def __init__(self, root: Path) -> None:
        """Expose config paths and execute executor work inline."""
        self.root = root
        self.config = SimpleNamespace(
            external_url="http://ha.local/",
            path=lambda *parts: str(root.joinpath(*parts)),
        )

    async def async_add_executor_job(self, func, *args):
        """Run executor jobs synchronously in the test process."""
        return func(*args)


def test_path_helpers_and_chime_discovery(tmp_path: Path) -> None:
    """Path resolution is case tolerant and custom audio choices are discovered."""
    helper = FilesystemHelper()
    folder = tmp_path / "Chimes"
    folder.mkdir()
    audio = folder / "Bell.mp3"
    audio.write_bytes(b"audio")
    (folder / "readme.txt").write_text("not audio")

    assert helper.path_exists(str(audio)) is True
    assert helper.path_exists(str(folder / "bell.mp3")) is True
    assert helper.path_exists("") is False
    assert helper.path_to_parent_folder("definitely-missing") is None
    assert (
        helper.get_downloaded_chime_path("/tmp", "https://host/a:b.mp3")
        == "/tmp/host_a_b.mp3"
    )
    assert helper.make_folder_path_safe("folder") == "/folder/"
    assert helper.make_folder_path_safe("/folder/") == "/folder/"
    assert helper.make_folder_path_safe("") == ""
    assert len(helper.get_hash_for_string("same")) == 64
    assert helper._get_chime_options_from_path(str(folder)) == [
        {"label": "Bell", "value": str(audio)}
    ]
    fingerprint = helper._get_chime_directory_fingerprint(str(folder))
    assert fingerprint[0][0] == "Bell.mp3"


@pytest.mark.asyncio
async def test_async_path_url_and_file_operations(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Async wrappers create, copy, validate, expose, and delete local files."""
    helper = FilesystemHelper()
    hass = Hass(tmp_path)
    source = tmp_path / "source.mp3"
    source.write_bytes(b"audio")
    target_dir = tmp_path / "target"
    public_dir = tmp_path / "www"
    public_dir.mkdir()
    public_file = public_dir / "sound.mp3"
    public_file.write_bytes(b"audio")

    assert await helper.async_validate_path(hass, str(source)) == str(source)
    assert await helper.async_create_folder(hass, str(target_dir)) is True
    assert await helper.async_copy_file(hass, str(source), str(target_dir)) == str(
        target_dir / "source.mp3"
    )
    assert await helper.async_copy_file(hass, str(source), "") is None
    assert (
        await helper.async_file_exists_in_directory(str(public_file), str(public_dir))
        is True
    )
    assert await helper.async_get_external_url(hass, str(public_file)) == (
        f"http://ha.local/{public_file}".replace("www/", "local/").replace(
            "http://ha.local//", "http://ha.local/"
        )
    )
    assert helper.get_local_path(hass, str(source)) == str(source)
    assert await helper.async_get_local_path(hass, str(source)) == str(source)
    assert helper.filepath_exists_locally(hass, str(source)) is True
    helper.delete_file(hass, str(source))
    assert source.exists() is False

    monkeypatch.setattr(helper, "async_load_audio", AsyncMock(return_value=None))
    response = SimpleNamespace(
        headers={"Content-Type": "audio/mpeg"},
        content=b"x",
        raise_for_status=lambda: None,
    )
    module = importlib.import_module("custom_components.chime_tts.helpers.filesystem")
    monkeypatch.setattr(module.requests, "get", lambda url: response)
    assert (
        await helper.async_download_file(
            hass, "https://example.com/sound.mp3", str(target_dir)
        )
        is None
    )


@pytest.mark.asyncio
async def test_chime_path_resolution_for_custom_url_and_set(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Custom chimes, URL cache, and Random Chime Sets resolve without recursion."""
    helper = FilesystemHelper()
    hass = Hass(tmp_path)
    custom = tmp_path / "tone.mp3"
    custom.write_bytes(b"audio")
    monkeypatch.setattr(
        helper,
        "async_get_chime_options_from_path",
        AsyncMock(return_value=[{"label": "Tone", "value": str(custom)}]),
    )
    data = {"custom_chimes_path": str(tmp_path)}
    assert await helper.async_get_chime_path("tone.wav", False, data, hass) == str(
        custom
    )

    cached = tmp_path / "cached.mp3"
    cached.write_bytes(b"audio")
    monkeypatch.setattr(
        helper, "get_downloaded_chime_path", lambda **kwargs: str(cached)
    )
    assert await helper.async_get_chime_path(
        "https://example.com/a.mp3", True, data, hass
    ) == str(cached)

    set_data = {
        "chime_sets": [{"id": "set", "name": "Set", "chimes": ["tone"]}],
        "custom_chimes_path": str(tmp_path),
    }
    assert await helper.async_get_chime_path_with_offset(
        "Set", False, set_data, hass
    ) == (str(custom), None)
