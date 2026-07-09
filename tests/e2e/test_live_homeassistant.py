"""Live end-to-end tests against real Home Assistant containers."""

from __future__ import annotations

import asyncio
import base64
from contextlib import suppress
from dataclasses import dataclass
from datetime import UTC, datetime
import hashlib
import hmac
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
from typing import Any
from urllib.parse import urlencode, urljoin, urlparse, urlunparse
from urllib.request import Request, urlopen

import aiohttp
import pytest
import pytest_asyncio
import yaml


pytestmark = pytest.mark.e2e

ROOT = Path(__file__).resolve().parents[2]
COMPOSE_FILE = ROOT / "docker-compose.homeassistant.yml"
SOURCE_INTEGRATION_DIR = ROOT / "custom_components" / "chime_tts"
SUPPORT_COMPONENTS_DIR = ROOT / "tests" / "e2e" / "support" / "custom_components"
CLIENT_ID = "http://localhost"
AUTH_USER_ID = "01KX2E2EAUTHUSER000000000001"
AUTH_TOKEN_ID = "01KX2E2EAUTHTOKEN0000000001"
AUTH_TOKEN_VALUE = (
    "codex-e2e-refresh-token-"
    "4f4c5f6385a447f0a92e83bf53fca5f90886a8e9f7f24f5ca87d8f6fb6f0b320"
)
AUTH_JWT_KEY = (
    "9e5f86fe46564d7e96b0c05b35f7c79541ca3ec903f3e36b6d524c57f1b9532f"
    "47165e4a8d4d4f9a8a6c390130f3ecf9b82117a3c53fdc0809c3a4e67b4f7c90"
)

E2E_CONFIGURATION = """\
# Dedicated Home Assistant runtime config for Chime TTS end-to-end tests.
default_config:

api:

logger:
  default: info
  logs:
    custom_components.chime_tts: debug

homeassistant:
  media_dirs:
    local: /media
  allowlist_external_dirs:
    - /media
    - /config/www

media_source:

ffmpeg:
  ffmpeg_bin: /usr/bin/ffmpeg

media_player:
  - platform: test_support_player

tts:
  - platform: test_support_tts
  - platform: google_translate
    service_name: google_say
"""


@dataclass(frozen=True)
class RuntimeTarget:
    """Container-specific runtime locations and connection details."""

    name: str
    service_name: str
    hass_url: str
    runtime_root: Path
    image: str

    @property
    def config_dir(self) -> Path:
        return self.runtime_root / "config"

    @property
    def media_dir(self) -> Path:
        return self.runtime_root / "media"

    @property
    def integration_dir(self) -> Path:
        return self.runtime_root / "integration" / "chime_tts"

    @property
    def public_dir(self) -> Path:
        return self.config_dir / "www" / "chime_tts"

    @property
    def temp_dir(self) -> Path:
        return self.media_dir / "sounds" / "temp" / "chime_tts"

    @property
    def test_support_tts_record_path(self) -> Path:
        return self.config_dir / "test_support_tts_last_request.json"


TARGETS = (
    RuntimeTarget(
        name="stable",
        service_name="homeassistant-stable",
        hass_url="http://127.0.0.1:8123",
        runtime_root=ROOT / ".ha" / "stable",
        image="ghcr.io/home-assistant/home-assistant:stable",
    ),
    RuntimeTarget(
        name="dev",
        service_name="homeassistant-dev",
        hass_url="http://127.0.0.1:18123",
        runtime_root=ROOT / ".ha" / "dev",
        image="ghcr.io/home-assistant/home-assistant:dev",
    ),
)


def _http_request(
    method: str,
    url: str,
    *,
    token: str | None = None,
    json_body: dict[str, Any] | None = None,
    form_body: dict[str, str] | None = None,
    timeout: float = 30.0,
) -> tuple[int, Any]:
    """Issue an HTTP request and decode any JSON response."""
    headers = {"Accept": "application/json"}
    data: bytes | None = None
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if json_body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(json_body).encode("utf-8")
    elif form_body is not None:
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        data = urlencode(form_body).encode("utf-8")

    request = Request(url, data=data, headers=headers, method=method)
    with urlopen(request, timeout=timeout) as response:
        raw = response.read()
        if not raw:
            return response.status, None
        try:
            return response.status, json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return response.status, raw


@pytest.fixture(autouse=True)
def verify_cleanup() -> None:
    """Disable HA's in-process cleanup guard for Docker-backed E2E tests."""
    yield


class HomeAssistantE2EClient:
    """Minimal client for a live Home Assistant instance."""

    def __init__(self, target: RuntimeTarget) -> None:
        """Store the target runtime and later-created auth/config state."""
        self.target = target
        self.hass_url = target.hass_url.rstrip("/")
        self.access_token: str | None = None
        self.entry_id: str | None = None

    def reset_runtime(self) -> None:
        """Clear the runtime so onboarding starts fresh."""
        if self.target.runtime_root.exists():
            subprocess.run(
                [
                    "docker",
                    "run",
                    "--rm",
                    "-v",
                    f"{self.target.runtime_root}:/state",
                    self.target.image,
                    "sh",
                    "-c",
                    "find /state -mindepth 1 -maxdepth 1 -exec rm -rf {} +",
                ],
                check=True,
            )

        self.target.config_dir.mkdir(parents=True, exist_ok=True)
        self.target.media_dir.mkdir(parents=True, exist_ok=True)
        self.target.integration_dir.parent.mkdir(parents=True, exist_ok=True)
        (self.target.config_dir / "www").mkdir(parents=True, exist_ok=True)
        shutil.copytree(SOURCE_INTEGRATION_DIR, self.target.integration_dir)
        self.copy_support_components()
        self.target.config_dir.joinpath("configuration.yaml").write_text(
            E2E_CONFIGURATION,
            encoding="utf-8",
        )
        self.seed_auth_storage()

    def copy_support_components(self) -> None:
        """Install test-only custom components into the runtime config."""
        destination_root = self.target.config_dir / "custom_components"
        destination_root.mkdir(parents=True, exist_ok=True)
        for component_dir in SUPPORT_COMPONENTS_DIR.iterdir():
            shutil.copytree(component_dir, destination_root / component_dir.name)

    def seed_auth_storage(self) -> None:
        """Seed an owner user and refresh token so tests can authenticate directly."""
        storage_dir = self.target.config_dir / ".storage"
        storage_dir.mkdir(parents=True, exist_ok=True)
        auth_payload = {
            "version": 1,
            "minor_version": 1,
            "key": "auth",
            "data": {
                "users": [
                    {
                        "id": AUTH_USER_ID,
                        "group_ids": ["system-admin"],
                        "is_owner": True,
                        "is_active": True,
                        "name": "Codex E2E",
                        "system_generated": False,
                        "local_only": False,
                    },
                    {
                        "id": "f63b9274bbb24539b54c7254afe0ed32",
                        "group_ids": ["system-read-only"],
                        "is_owner": False,
                        "is_active": True,
                        "name": "Home Assistant Content",
                        "system_generated": True,
                        "local_only": False,
                    },
                ],
                "groups": [
                    {"id": "system-admin", "name": "Administrators"},
                    {"id": "system-users", "name": "Users"},
                    {"id": "system-read-only", "name": "Read Only"},
                ],
                "credentials": [],
                "refresh_tokens": [
                    {
                        "id": AUTH_TOKEN_ID,
                        "user_id": AUTH_USER_ID,
                        "client_id": CLIENT_ID,
                        "client_name": "Codex E2E",
                        "client_icon": None,
                        "token_type": "long_lived_access_token",
                        "created_at": _utc_now(),
                        "access_token_expiration": 31536000.0,
                        "token": AUTH_TOKEN_VALUE,
                        "jwt_key": AUTH_JWT_KEY,
                        "last_used_at": None,
                        "last_used_ip": None,
                        "expire_at": None,
                        "credential_id": None,
                        "version": "codex-e2e",
                    }
                ],
            },
        }
        storage_dir.joinpath("auth").write_text(
            json.dumps(auth_payload),
            encoding="utf-8",
        )

    def docker_compose(self, *args: str, check: bool = True) -> None:
        """Run docker compose for the target service."""
        subprocess.run(
            ["docker", "compose", "-f", str(COMPOSE_FILE), *args],
            cwd=ROOT,
            check=check,
        )

    def stop(self) -> None:
        """Stop the target Home Assistant container."""
        self.docker_compose("stop", self.target.service_name, check=False)

    def start(self) -> None:
        """Start the target Home Assistant container."""
        self.docker_compose("up", "-d", self.target.service_name)

    def restart(self) -> None:
        """Restart the target Home Assistant container."""
        self.docker_compose("restart", self.target.service_name)

    def wait_for_api(self, timeout: float = 180.0) -> None:
        """Wait until the Home Assistant API is available."""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            with suppress(Exception):
                status, _payload = _http_request(
                    "GET",
                    f"{self.hass_url}/manifest.json",
                    timeout=5.0,
                )
                if status == 200:
                    return
            time.sleep(2)
        raise RuntimeError(
            f"Home Assistant {self.target.name} did not finish booting in time"
        )

    def issue_access_token(self) -> None:
        """Issue a JWT access token that matches the seeded refresh token."""
        self.access_token = _encode_access_token(
            refresh_token_id=AUTH_TOKEN_ID,
            jwt_key=AUTH_JWT_KEY,
            expires_in=31536000,
        )

    def install_chime_tts_entry(self) -> None:
        """Create the Chime TTS config entry through Home Assistant's real API."""
        assert self.access_token is not None
        _status, payload = _http_request(
            "POST",
            f"{self.hass_url}/api/config/config_entries/flow",
            token=self.access_token,
            json_body={"handler": "chime_tts"},
        )
        self.entry_id = self._finish_flow(payload)

    def wait_for_entry_loaded(self, timeout: float = 90.0) -> None:
        """Wait until the Chime TTS config entry reports a loaded state."""
        assert self.access_token is not None
        assert self.entry_id is not None
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            with suppress(Exception):
                status, payload = _http_request(
                    "GET",
                    f"{self.hass_url}/api/config/config_entries/entry",
                    token=self.access_token,
                    timeout=10.0,
                )
                if status == 200:
                    for entry in payload:
                        if (
                            entry.get("entry_id") == self.entry_id
                            and entry.get("state") == "loaded"
                        ):
                            return
            time.sleep(2)
        raise RuntimeError(
            f"Timed out waiting for the Chime TTS config entry to load on {self.target.name}"
        )

    def _finish_flow(self, payload: dict[str, Any]) -> str:
        """Resolve a config flow response into a created entry id."""
        flow_type = payload.get("type")
        if flow_type == "create_entry":
            return payload["result"]["entry_id"]
        if flow_type != "form":
            raise RuntimeError(f"Unexpected config flow response: {payload}")

        _status, next_payload = _http_request(
            "POST",
            f"{self.hass_url}/api/config/config_entries/flow/{payload['flow_id']}",
            token=self.access_token,
            json_body={},
        )
        if next_payload.get("type") != "create_entry":
            raise RuntimeError(f"Unexpected config flow step response: {next_payload}")
        return next_payload["result"]["entry_id"]

    async def bootstrap(self) -> None:
        """Start a fresh container and prepare the integration."""
        self.stop()
        self.reset_runtime()
        self.start()
        self.wait_for_api()
        self.issue_access_token()
        self.install_chime_tts_entry()
        self.wait_for_entry_loaded()
        await self.wait_for_panel()

    async def wait_for_panel(self, timeout: float = 60.0) -> None:
        """Wait until the custom panel websocket commands are registered."""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                payload = await self.ws_command({"type": "chime_tts/get_settings"})
                if payload.get("sections"):
                    return
            except Exception:
                await asyncio.sleep(2)
                continue
        raise RuntimeError(
            f"Timed out waiting for the Chime TTS panel websocket API on {self.target.name}"
        )

    async def ws_command(self, payload: dict[str, Any]) -> Any:
        """Send one websocket command and return its result payload."""
        assert self.access_token is not None
        ws_url = self.hass_url.replace("http://", "ws://").replace("https://", "wss://")
        ws_url = f"{ws_url}/api/websocket"
        timeout = aiohttp.ClientTimeout(total=60, sock_connect=30, sock_read=60)
        async with (
            aiohttp.ClientSession(timeout=timeout) as session,
            session.ws_connect(ws_url, heartbeat=30) as ws,
        ):
            auth_required = await ws.receive_json()
            assert auth_required["type"] == "auth_required"
            await ws.send_json({"type": "auth", "access_token": self.access_token})
            auth_ok = await ws.receive_json()
            assert auth_ok["type"] == "auth_ok"
            await ws.send_json({"id": 1, **payload})
            message = await ws.receive_json()
            assert message["id"] == 1
            if not message.get("success", False):
                raise AssertionError(message)
            return message["result"]

    def get_state(self, entity_id: str) -> dict[str, Any]:
        """Fetch one entity state through the Home Assistant REST API."""
        assert self.access_token is not None
        status, payload = _http_request(
            "GET",
            f"{self.hass_url}/api/states/{entity_id}",
            token=self.access_token,
            timeout=10.0,
        )
        if status != 200:
            raise RuntimeError(f"Unable to fetch state for {entity_id}: {status} {payload}")
        return payload

    def get_test_support_tts_request(self) -> dict[str, Any]:
        """Read the last request captured by the local E2E TTS provider."""
        return json.loads(self.target.test_support_tts_record_path.read_text(encoding="utf-8"))

    async def wait_for_test_support_tts_request(
        self, timeout: float = 15.0
    ) -> dict[str, Any]:
        """Poll until the support TTS provider records a request."""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            with suppress(FileNotFoundError, json.JSONDecodeError):
                return self.get_test_support_tts_request()
            await asyncio.sleep(0.5)
        raise RuntimeError(
            f"Timed out waiting for the support TTS request record on {self.target.name}"
        )

    async def wait_for_state_attr(
        self,
        entity_id: str,
        attr_name: str,
        predicate: callable,
        timeout: float = 30.0,
    ) -> dict[str, Any]:
        """Poll one entity attribute until it matches the expected condition."""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            state = self.get_state(entity_id)
            if predicate(state["attributes"].get(attr_name)):
                return state
            await asyncio.sleep(1)
        raise RuntimeError(
            f"Timed out waiting for {entity_id} attribute {attr_name!r} on {self.target.name}"
        )

    def resolve_hass_url(self, url: str) -> str:
        """Map a returned Home Assistant URL back to the local runtime."""
        absolute_url = urljoin(f"{self.hass_url}/", url.lstrip("/"))
        parsed_url = urlparse(absolute_url)
        parsed_hass = urlparse(self.hass_url)
        if parsed_url.netloc and parsed_url.netloc != parsed_hass.netloc:
            absolute_url = urlunparse(parsed_url._replace(netloc=parsed_hass.netloc))
        return absolute_url


@pytest_asyncio.fixture(params=TARGETS, ids=lambda target: target.name)
async def e2e_client(request: pytest.FixtureRequest) -> HomeAssistantE2EClient:
    """Start each Home Assistant runtime for live e2e tests."""
    if os.environ.get("CHIME_TTS_E2E") != "1":
        pytest.skip("Set CHIME_TTS_E2E=1 to run live Home Assistant end-to-end tests.")
    request.getfixturevalue("socket_enabled")

    client = HomeAssistantE2EClient(request.param)
    await client.bootstrap()
    try:
        yield client
    finally:
        client.stop()


def _utc_now() -> str:
    """Return an ISO-8601 UTC timestamp."""
    return datetime.now(UTC).isoformat()


def _b64url(data: bytes) -> str:
    """Encode bytes using URL-safe base64 without padding."""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _encode_access_token(refresh_token_id: str, jwt_key: str, expires_in: int) -> str:
    """Build a Home Assistant-compatible HS256 JWT access token."""
    now = int(time.time())
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "iss": refresh_token_id,
        "iat": now,
        "exp": now + expires_in,
    }
    signing_input = ".".join(
        [
            _b64url(json.dumps(header, separators=(",", ":")).encode("utf-8")),
            _b64url(json.dumps(payload, separators=(",", ":")).encode("utf-8")),
        ]
    )
    signature = hmac.new(
        jwt_key.encode("utf-8"),
        signing_input.encode("ascii"),
        hashlib.sha256,
    ).digest()
    return f"{signing_input}.{_b64url(signature)}"


@pytest.mark.asyncio
async def test_panel_settings_round_trip(e2e_client: HomeAssistantE2EClient) -> None:
    """The live panel websocket should expose and persist settings."""
    payload = await e2e_client.ws_command({"type": "chime_tts/get_settings"})

    assert payload["documentation_url"].endswith("/configuration/")
    assert any(section["key"] == "paths" for section in payload["sections"])

    updated_values = dict(payload["values"])
    updated_values["queue_timeout"] = int(updated_values["queue_timeout"]) + 5

    saved = await e2e_client.ws_command(
        {"type": "chime_tts/save_settings", "values": updated_values}
    )

    assert saved["message_type"] == "success"
    assert saved["values"]["queue_timeout"] == updated_values["queue_timeout"]

    refreshed = await e2e_client.ws_command({"type": "chime_tts/get_settings"})
    assert refreshed["values"]["queue_timeout"] == updated_values["queue_timeout"]


@pytest.mark.asyncio
async def test_panel_notify_profiles_round_trip(
    e2e_client: HomeAssistantE2EClient,
) -> None:
    """The live panel websocket should load and persist Chime TTS notify profiles."""
    e2e_client.target.config_dir.joinpath("configuration.yaml").write_text(
        E2E_CONFIGURATION
        + "\nnotify:\n"
        + "  - platform: file\n"
        + "    name: archive\n"
        + "  - platform: chime_tts\n"
        + "    name: arrival\n"
        + "    entity_id:\n"
        + "      - media_player.test_speaker\n"
        + "      - media_player.group_speaker\n"
        + "    crossfade: 125\n",
        encoding="utf-8",
    )

    payload = await e2e_client.ws_command({"type": "chime_tts/get_settings"})
    notify_section = next(
        section for section in payload["sections"] if section["key"] == "notify_profiles"
    )
    notify_profile_fields = {
        field["key"]: field for field in notify_section["profile_fields"]
    }
    assert payload["notify_profiles"][0]["name"] == "arrival"
    assert payload["notify_profiles"][0]["entity_id"] == (
        "media_player.test_speaker, media_player.group_speaker"
    )
    assert notify_profile_fields["tts_platform"]["docs_url"].endswith(
        "/documentation/configuration/#default-tts-platform"
    )
    assert notify_profile_fields["crossfade"]["docs_url"].endswith(
        "/documentation/actions/say-action/parameters/#crossfade"
    )
    assert notify_profile_fields["announce"]["docs_url"].endswith(
        "/documentation/actions/say-action/parameters/#announce"
    )

    saved = await e2e_client.ws_command(
        {
            "type": "chime_tts/save_settings",
            "values": dict(payload["values"]),
            "notify_profiles": [
                {
                    "name": "arrival",
                    "entity_id": "media_player.test_speaker, media_player.group_speaker",
                    "crossfade": 200,
                    "volume_level": 0.5,
                    "announce": True,
                    "options": "voice: Jenny",
                }
            ],
        }
    )

    assert saved["message_type"] == "success"
    assert saved["restart_required"] is True

    saved_yaml = yaml.safe_load(
        e2e_client.target.config_dir.joinpath("configuration.yaml").read_text(
            encoding="utf-8"
        )
    )
    assert saved_yaml["notify"][0] == {"platform": "file", "name": "archive"}
    assert saved_yaml["notify"][1] == {
        "platform": "chime_tts",
        "name": "arrival",
        "entity_id": ["media_player.test_speaker", "media_player.group_speaker"],
        "crossfade": 200,
        "volume_level": 0.5,
        "options": {"voice": "Jenny"},
        "announce": True,
    }


@pytest.mark.asyncio
async def test_say_url_cache_and_clear_cache(
    e2e_client: HomeAssistantE2EClient,
) -> None:
    """The live integration should generate reusable audio and clear it again."""
    service_data = {
        "chime_path": "bells",
        "cache": True,
    }

    first = await e2e_client.ws_command(
        {
            "type": "call_service",
            "domain": "chime_tts",
            "service": "say_url",
            "service_data": service_data,
            "return_response": True,
        }
    )
    second = await e2e_client.ws_command(
        {
            "type": "call_service",
            "domain": "chime_tts",
            "service": "say_url",
            "service_data": service_data,
            "return_response": True,
        }
    )

    first_response = first["response"]
    second_response = second["response"]
    assert first_response["success"] is True
    assert first_response["url"]
    assert first_response["url"] == second_response["url"]

    audio_url = e2e_client.resolve_hass_url(first_response["url"])
    status, body = _http_request("GET", audio_url, timeout=30.0)
    assert status == 200
    assert isinstance(body, bytes | bytearray)
    assert len(body) > 100

    assert list(e2e_client.target.public_dir.rglob("*.mp3"))

    cleared = await e2e_client.ws_command(
        {
            "type": "call_service",
            "domain": "chime_tts",
            "service": "clear_cache",
            "service_data": {
                "clear_temp_tts_cache": True,
                "clear_www_tts_cache": True,
            },
        }
    )

    assert cleared["context"]["id"]

    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        if not list(e2e_client.target.public_dir.rglob("*.mp3")) and not list(
            e2e_client.target.temp_dir.rglob("*.mp3")
        ):
            break
        await asyncio.sleep(1)

    assert not list(e2e_client.target.public_dir.rglob("*.mp3"))
    assert not list(e2e_client.target.temp_dir.rglob("*.mp3"))


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("case_name", "service_data"),
    [
        ("start_chime", {"chime_path": "bells", "cache": False}),
        (
            "start_and_end_chime",
            {"chime_path": "bells", "end_chime_path": "tada", "cache": False},
        ),
        (
            "offset",
            {
                "chime_path": "bells",
                "end_chime_path": "tada",
                "offset": 250,
                "cache": False,
            },
        ),
        (
            "crossfade",
            {
                "chime_path": "bells",
                "end_chime_path": "tada",
                "crossfade": 150,
                "cache": False,
            },
        ),
    ],
    ids=lambda case: case,
)
async def test_say_url_parameter_variants(
    e2e_client: HomeAssistantE2EClient,
    case_name: str,
    service_data: dict[str, Any],
) -> None:
    """Live say_url calls should succeed across key local-audio parameter variants."""
    del case_name
    result = await e2e_client.ws_command(
        {
            "type": "call_service",
            "domain": "chime_tts",
            "service": "say_url",
            "service_data": service_data,
            "return_response": True,
        }
    )

    response = result["response"]
    assert response["success"] is True
    assert response["url"]
    assert response["duration"] > 0

    audio_url = e2e_client.resolve_hass_url(response["url"])
    status, body = _http_request("GET", audio_url, timeout=30.0)
    assert status == 200
    assert isinstance(body, bytes | bytearray)
    assert len(body) > 100


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("case_name", "service_data", "expected_language", "expected_options"),
    [
        (
            "message_only",
            {
                "message": "Message only test",
                "tts_platform": "test_support_tts",
                "cache": False,
            },
            "en",
            {},
        ),
        (
            "language_voice_tld",
            {
                "message": "Language and options test",
                "tts_platform": "test_support_tts",
                "language": "fr",
                "voice": "voice-fr",
                "tld": "ca",
                "cache": False,
            },
            "fr",
            {"voice": "voice-fr", "tld": "ca"},
        ),
        (
            "options_override",
            {
                "message": "Options override test",
                "tts_platform": "test_support_tts",
                "language": "en-US",
                "voice": "voice-base",
                "tld": "co.uk",
                "options": "voice: override-voice\ntld: com.au",
                "cache": False,
            },
            "en-US",
            {"voice": "override-voice", "tld": "com.au"},
        ),
    ],
    ids=lambda case: case,
)
async def test_say_url_message_parameter_variants(
    e2e_client: HomeAssistantE2EClient,
    case_name: str,
    service_data: dict[str, Any],
    expected_language: str,
    expected_options: dict[str, Any],
) -> None:
    """Live say_url message requests should pass message/language/options through to TTS."""
    del case_name
    result = await e2e_client.ws_command(
        {
            "type": "call_service",
            "domain": "chime_tts",
            "service": "say_url",
            "service_data": service_data,
            "return_response": True,
        }
    )

    response = result["response"]
    assert response["success"] is True
    assert response["url"]

    request = await e2e_client.wait_for_test_support_tts_request()
    assert request["message"] == service_data["message"]
    assert request["language"] == expected_language
    assert request["options"] == expected_options


@pytest.mark.asyncio
async def test_say_action_plays_media_on_target_player(
    e2e_client: HomeAssistantE2EClient,
) -> None:
    """The live say action should dispatch media_player.play_media to a target entity."""
    entity_id = "media_player.e2e_test_player"
    result = await e2e_client.ws_command(
        {
            "type": "call_service",
            "domain": "chime_tts",
            "service": "say",
            "service_data": {
                "entity_id": [entity_id],
                "chime_path": "bells",
                "volume_level": 0.42,
                "announce": True,
                "cache": False,
            },
        }
    )

    assert result["context"]["id"]

    state = await e2e_client.wait_for_state_attr(
        entity_id,
        "play_count",
        lambda value: value == 1,
    )
    attrs = state["attributes"]

    assert state["state"] == "idle"
    assert attrs["last_announce"] is True
    assert attrs["last_media_content_type"] == "music"
    assert attrs["last_media_content_id"].startswith("media-source://media_source/local/")
    assert attrs["play_count"] == 1
    assert 0.42 in attrs["volume_history"]
    assert abs(attrs["volume_level"] - 0.5) < 0.001


@pytest.mark.asyncio
async def test_say_action_message_uses_local_tts_provider(
    e2e_client: HomeAssistantE2EClient,
) -> None:
    """The live say action should request TTS audio and play it on the target player."""
    entity_id = "media_player.e2e_test_player"
    result = await e2e_client.ws_command(
        {
            "type": "call_service",
            "domain": "chime_tts",
            "service": "say",
            "service_data": {
                "entity_id": [entity_id],
                "message": "Say message live test",
                "tts_platform": "test_support_tts",
                "language": "fr",
                "voice": "say-voice",
                "cache": False,
            },
        }
    )

    assert result["context"]["id"]

    request = await e2e_client.wait_for_test_support_tts_request()
    assert request["message"] == "Say message live test"
    assert request["language"] == "fr"
    assert request["options"] == {"voice": "say-voice"}

    state = await e2e_client.wait_for_state_attr(
        entity_id,
        "play_count",
        lambda value: value == 1,
    )
    assert state["attributes"]["last_media_content_id"].startswith(
        "media-source://media_source/local/"
    )


@pytest.mark.asyncio
@pytest.mark.network
async def test_say_url_with_live_tts_message(
    e2e_client: HomeAssistantE2EClient,
) -> None:
    """An optional network-backed TTS pass can verify real message synthesis."""
    if os.environ.get("CHIME_TTS_E2E_NETWORK_TTS") != "1":
        pytest.skip("Set CHIME_TTS_E2E_NETWORK_TTS=1 to exercise a live TTS provider.")

    result = await e2e_client.ws_command(
        {
            "type": "call_service",
            "domain": "chime_tts",
            "service": "say_url",
            "service_data": {
                "message": "Chime TTS end to end test",
                "tts_platform": "google_translate",
                "cache": False,
            },
            "return_response": True,
        }
    )

    response = result["response"]
    assert response["success"] is True
    assert response["url"]
