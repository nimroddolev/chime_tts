#!/usr/bin/env python3

import argparse
import asyncio
import json
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse, urlunparse

import aiohttp


class BrowserModHarness:
    def __init__(
        self,
        hass_url: str,
        client_id: str,
        refresh_token: str,
        browser_id: str,
        artifact_dir: Path,
    ) -> None:
        self.hass_url = hass_url.rstrip("/")
        self.client_id = client_id
        self.refresh_token = refresh_token
        self.browser_id = browser_id
        self.artifact_dir = artifact_dir
        self.session: aiohttp.ClientSession | None = None
        self.ws: aiohttp.ClientWebSocketResponse | None = None
        self.command_id = 10
        self.connect_subscription_id: int | None = None
        self.player_state = {
            "volume": 1.0,
            "muted": False,
            "src": "",
            "state": "off",
            "media_duration": None,
            "media_position": 0,
            "extra": {
                "title": "Browser Mod Harness",
                "audioInteractionRequired": False,
                "videoInteractionRequired": False,
            },
        }

    async def run(self) -> None:
        timeout = aiohttp.ClientTimeout(total=None, sock_connect=30, sock_read=None)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            self.session = session
            access_token = await self._refresh_access_token()
            await self._connect_websocket(access_token)
            await self._register_browser()
            await self._connect_browser()
            await self._send_full_update()
            await self._event_loop()

    async def _refresh_access_token(self) -> str:
        assert self.session is not None
        token_url = f"{self.hass_url}/auth/token"
        data = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "refresh_token": self.refresh_token,
        }
        async with self.session.post(token_url, data=data) as response:
            response.raise_for_status()
            payload = await response.json()
        return payload["access_token"]

    async def _connect_websocket(self, access_token: str) -> None:
        assert self.session is not None
        ws_url = self.hass_url.replace("http://", "ws://").replace("https://", "wss://")
        ws_url = f"{ws_url}/api/websocket"
        self.ws = await self.session.ws_connect(ws_url, heartbeat=30)

        auth_required = await self.ws.receive_json()
        if auth_required.get("type") != "auth_required":
            raise RuntimeError(f"Unexpected websocket banner: {auth_required}")

        await self.ws.send_json({"type": "auth", "access_token": access_token})
        auth_ok = await self.ws.receive_json()
        if auth_ok.get("type") != "auth_ok":
            raise RuntimeError(f"Websocket auth failed: {auth_ok}")

        await self.ws.send_json(
            {
                "id": 1,
                "type": "supported_features",
                "features": {"coalesce_messages": 1},
            }
        )
        await self.ws.receive_json()

    async def _register_browser(self) -> None:
        await self._send_command(
            {
                "type": "browser_mod/register",
                "browserID": self.browser_id,
                "data": {
                    "registered": True,
                    "meta": "browser_mod_harness",
                    "settings": {
                        "fullInteraction": True,
                    },
                },
            }
        )

    async def _connect_browser(self) -> None:
        connect_id = await self._send_command(
            {
                "type": "browser_mod/connect",
                "browserID": self.browser_id,
            }
        )
        self.connect_subscription_id = connect_id

    async def _send_command(self, payload: dict) -> int:
        assert self.ws is not None
        self.command_id += 1
        message = {"id": self.command_id, **payload}
        await self.ws.send_json(message)
        return self.command_id

    async def _send_update(self, data: dict) -> None:
        await self._send_command(
            {
                "type": "browser_mod/update",
                "browserID": self.browser_id,
                "data": data,
            }
        )

    async def _send_full_update(self) -> None:
        await self._send_update(
            {
                "browser": {
                    "browserID": self.browser_id,
                    "path": "/browser-mod-harness",
                    "visibility": "visible",
                    "userAgent": "Codex Browser Mod Harness",
                    "currentUser": "admin",
                    "fullyKiosk": False,
                    "width": 1280,
                    "height": 720,
                },
                "player": self.player_state,
            }
        )

    async def _event_loop(self) -> None:
        assert self.ws is not None
        async for msg in self.ws:
            if msg.type != aiohttp.WSMsgType.TEXT:
                if msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                    break
                continue
            payload = json.loads(msg.data)
            messages = payload if isinstance(payload, list) else [payload]
            for message in messages:
                if (
                    isinstance(message, dict)
                    and message.get("type") == "event"
                    and message.get("id") == self.connect_subscription_id
                ):
                    await self._handle_browser_event(message["event"])

    async def _handle_browser_event(self, event: dict) -> None:
        command = event.get("command")
        if not command:
            return

        if command == "player-play":
            await self._handle_player_play(event)
            return

        if command == "player-pause":
            self.player_state["state"] = "paused"
        elif command == "player-stop":
            self.player_state["state"] = "stopped"
            self.player_state["src"] = ""
        elif command == "player-set-volume":
            self.player_state["volume"] = event.get("volume_level", self.player_state["volume"])
        elif command == "player-mute":
            mute = event.get("mute")
            self.player_state["muted"] = (not self.player_state["muted"]) if mute is None else bool(mute)
        elif command == "player-seek":
            self.player_state["media_position"] = event.get("position", 0)
        elif command == "player-turn-off":
            self.player_state["state"] = "off"
            self.player_state["src"] = ""
        elif command == "player-turn-on":
            if self.player_state["src"]:
                self.player_state["state"] = "paused"

        await self._send_update({"player": self.player_state})

    async def _handle_player_play(self, event: dict) -> None:
        media_url = event.get("media_content_id") or self.player_state["src"]
        media_type = event.get("media_type") or self.player_state["extra"].get("media_content_type")
        extra = event.get("extra") or {}

        if media_url:
            self.player_state["src"] = media_url
        self.player_state["state"] = "playing" if media_url else "off"
        self.player_state["media_position"] = 0
        self.player_state["extra"] = {
            **self.player_state["extra"],
            **extra,
            "media_content_id": media_url,
            "media_content_type": media_type,
            "audioInteractionRequired": False,
            "videoInteractionRequired": False,
        }

        await self._capture_media(media_url, media_type)
        await self._send_update({"player": self.player_state})

    async def _capture_media(self, media_url: str | None, media_type: str | None) -> None:
        if not media_url:
            return

        self.artifact_dir.mkdir(parents=True, exist_ok=True)
        index_path = self.artifact_dir / "last_play.json"
        payload = {
            "browser_id": self.browser_id,
            "media_url": media_url,
            "media_type": media_type,
        }

        try:
            absolute_url = self._resolve_media_url(media_url)
            assert self.session is not None
            async with self.session.get(absolute_url) as response:
                payload["status"] = response.status
                payload["content_type"] = response.headers.get("Content-Type")
                if response.ok:
                    suffix = self._guess_suffix(media_type, payload["content_type"])
                    media_path = self.artifact_dir / f"last_play{suffix}"
                    media_path.write_bytes(await response.read())
                    payload["saved_to"] = str(media_path)
                else:
                    payload["error"] = await response.text()
        except Exception as err:  # pragma: no cover - harness best-effort capture
            payload["exception"] = str(err)

        index_path.write_text(json.dumps(payload, indent=2))

    @staticmethod
    def _guess_suffix(media_type: str | None, content_type: str | None) -> str:
        source = (content_type or media_type or "").lower()
        if "mpeg" in source or "mp3" in source:
            return ".mp3"
        if "wav" in source:
            return ".wav"
        if "ogg" in source:
            return ".ogg"
        if "mp4" in source:
            return ".mp4"
        return ".bin"

    def _resolve_media_url(self, media_url: str) -> str:
        absolute_url = urljoin(f"{self.hass_url}/", media_url.lstrip("/"))
        parsed_media = urlparse(absolute_url)
        parsed_hass = urlparse(self.hass_url)
        if parsed_media.netloc and parsed_media.netloc != parsed_hass.netloc:
            absolute_url = urlunparse(parsed_media._replace(netloc=parsed_hass.netloc))
        return absolute_url


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Register a fake Browser Mod client for HA testing.")
    parser.add_argument("--hass-url", required=True)
    parser.add_argument("--client-id", required=True)
    parser.add_argument("--refresh-token", required=True)
    parser.add_argument("--browser-id", required=True)
    parser.add_argument("--artifact-dir", required=True)
    return parser.parse_args()


async def async_main() -> int:
    args = parse_args()
    harness = BrowserModHarness(
        hass_url=args.hass_url,
        client_id=args.client_id,
        refresh_token=args.refresh_token,
        browser_id=args.browser_id,
        artifact_dir=Path(args.artifact_dir),
    )
    await harness.run()
    return 0


def main() -> int:
    try:
        return asyncio.run(async_main())
    except KeyboardInterrupt:
        return 130
    except Exception as err:
        print(f"browser_mod_harness failed: {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
