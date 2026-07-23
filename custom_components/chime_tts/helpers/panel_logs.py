"""Panel log storage and capture helpers for the Chime TTS sidebar."""

from __future__ import annotations

from collections import deque
from collections import Counter
from collections.abc import Mapping
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import UTC, datetime
import logging
import re
import uuid

import yaml

from ..const import DOMAIN

PANEL_LOG_STORE_KEY = f"{DOMAIN}_panel_log_store"
PANEL_LOG_HANDLER_KEY = f"{DOMAIN}_panel_log_handler"
MAX_PANEL_LOG_EVENTS = 100
MAX_RAW_LOG_LINES = 200
MAX_BACKFILL_LOG_LINES = 20000
RELATED_LOG_WINDOW_MS = 1000
LOGGER_NAMESPACE = f"custom_components.{DOMAIN}"
PANEL_LOGGER = logging.getLogger(LOGGER_NAMESPACE)
NOTIFY_EVENT_TITLE = "Notification profile call"
BACKFILLED_EVENT_KEY = "_backfilled_event_key"
BACKFILLED_EVENT_TIME_KEY = "_backfilled_event_time_key"
LOG_LINE_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d+)?)\s+"
    r"(?P<level>[A-Z]+)\s+\([^)]+\)\s+\[(?P<logger>[^\]]+)\]\s+"
    r"(?P<message>.*)$"
)
ISO_LOG_LINE_PATTERN = re.compile(
    r"^\[(?P<timestamp>[^\]]+)\]\s+"
    r"(?P<level>[A-Z]+)\s+"
    r"(?P<logger>[^:]+):\s+"
    r"(?P<message>.*)$"
)


def _utc_now() -> str:
    """Return the current UTC timestamp as an ISO string."""
    return datetime.now(UTC).isoformat()


def _normalize_service_data(value):
    """Recursively normalize service data into JSON-safe primitives."""
    if isinstance(value, Mapping):
        return {str(key): _normalize_service_data(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_normalize_service_data(item) for item in value]
    return value


def _append_event(store: "PanelLogStore", event: dict) -> None:
    """Insert the latest event at the top of the bounded event list."""
    store.events.insert(0, event)
    if len(store.events) <= MAX_PANEL_LOG_EVENTS:
        return

    kept_events = store.events[:MAX_PANEL_LOG_EVENTS]
    if not any(item.get("type") == "integration_initiation" for item in kept_events):
        preserved_init_event = next(
            (
                item
                for item in store.events[MAX_PANEL_LOG_EVENTS:]
                if item.get("type") == "integration_initiation"
            ),
            None,
        )
        if preserved_init_event is not None:
            kept_events[-1] = preserved_init_event

    store.events = kept_events


def _notify_panel_log_subscribers(store: "PanelLogStore", event: dict) -> None:
    """Push a new completed panel log event to active websocket subscribers."""
    if not store.subscribers:
        return

    payload = deepcopy(event)
    for subscriber in list(store.subscribers):
        try:
            subscriber(payload)
        except Exception:
            PANEL_LOGGER.exception("Unable to notify a panel log subscriber")


def _local_tzinfo():
    """Return the host local timezone."""
    return datetime.now().astimezone().tzinfo


def _to_utc_timestamp(value: str | None) -> datetime | None:
    """Normalize a timestamp string into an aware UTC datetime."""
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=_local_tzinfo())
    return parsed.astimezone(UTC)


def _timepoint_key(value: str | None) -> str:
    """Return a normalized UTC millisecond timepoint key."""
    parsed = _to_utc_timestamp(value)
    if parsed is None:
        return str(value or "")
    return parsed.isoformat(timespec="milliseconds")


def _log_key(log_entry: Mapping) -> tuple[str, str, str]:
    """Return the normalized identity for a raw log line."""
    return (
        _timepoint_key(log_entry.get("timestamp")),
        str(log_entry.get("logger", "")),
        str(log_entry.get("message", "")),
    )


def _timestamps_within_window(
    first_value: str | None,
    second_value: str | None,
    *,
    window_ms: int = RELATED_LOG_WINDOW_MS,
) -> bool:
    """Return whether two timestamps are close enough to belong to one grouped event."""
    first_timestamp = _to_utc_timestamp(first_value)
    second_timestamp = _to_utc_timestamp(second_value)
    if first_timestamp is None or second_timestamp is None:
        return False
    return abs((first_timestamp - second_timestamp).total_seconds() * 1000) <= window_ms


def _is_initialization_related_log(log_entry: Mapping) -> bool:
    """Return whether a parsed log entry belongs to integration initialization."""
    logger = str(log_entry.get("logger", ""))
    message = str(log_entry.get("message", ""))
    logger_lower = logger.lower()
    message_lower = message.lower()

    if logger.startswith(LOGGER_NAMESPACE):
        return True

    if "chime_tts" in logger_lower or "chime_tts" in message_lower:
        return True

    return "chime tts" in message_lower


def _is_initialization_completion_log(message: str) -> bool:
    """Return whether a message marks the end of initialization logging."""
    return "Registered Chime TTS sidebar panel at /" in message


@dataclass(slots=True)
class PanelLogStore:
    """In-memory log storage for the current Home Assistant session."""

    events: list[dict] = field(default_factory=list)
    active_events: dict[str, dict] = field(default_factory=dict)
    imported_event_keys: set[str] = field(default_factory=set)
    backfill_loaded: bool = False
    backfill_loading: bool = False
    subscribers: set = field(default_factory=set)


class ChimeTTSPanelLogHandler(logging.Handler):
    """Capture Chime TTS logger output for the custom panel."""

    def __init__(self, hass) -> None:
        """Initialize the handler."""
        super().__init__(level=logging.DEBUG)
        self._hass = hass

    def emit(self, record: logging.LogRecord) -> None:
        """Capture logger output into the panel store."""
        try:
            store = async_setup_panel_log_store(self._hass)
            if not self._should_capture(record, store):
                return

            log_entry = {
                "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(),
                "level": record.levelname.lower(),
                "logger": record.name,
                "message": record.getMessage(),
            }

            if store.active_events:
                for event in store.active_events.values():
                    raw_logs = event.setdefault("raw_logs", [])
                    raw_logs.append(log_entry)
                    if record.levelno >= logging.ERROR:
                        event["has_error"] = True
                        event["error_count"] = int(event.get("error_count", 0)) + 1
                    del raw_logs[:-MAX_RAW_LOG_LINES]
                return
        except Exception:
            self.handleError(record)

    @staticmethod
    def _should_capture(record: logging.LogRecord, store: PanelLogStore) -> bool:
        """Return True when the record belongs to Chime TTS."""
        if record.name == DOMAIN or record.name.startswith(LOGGER_NAMESPACE):
            return True

        related_timestamp = datetime.fromtimestamp(record.created, UTC).isoformat()
        related_entry = {
            "timestamp": related_timestamp,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for event in store.active_events.values():
            if event.get("title") != "Integration initialization":
                continue
            if not _is_initialization_related_log(related_entry):
                continue
            if _timestamps_within_window(
                event.get("started_at"),
                related_timestamp,
            ) or _timestamps_within_window(
                event.get("ended_at"),
                related_timestamp,
            ):
                return True

        return False


def async_setup_panel_log_store(hass) -> PanelLogStore:
    """Ensure the session log store and logger handler exist."""
    store = hass.data.get(PANEL_LOG_STORE_KEY)
    if store is None:
        store = PanelLogStore()
        hass.data[PANEL_LOG_STORE_KEY] = store

    if hass.data.get(PANEL_LOG_HANDLER_KEY) is None:
        handler = next(
            (
                existing
                for existing in PANEL_LOGGER.handlers
                if isinstance(existing, ChimeTTSPanelLogHandler)
            ),
            None,
        )
        if handler is None:
            handler = ChimeTTSPanelLogHandler(hass)
            PANEL_LOGGER.addHandler(handler)
        else:
            handler._hass = hass
        hass.data[PANEL_LOG_HANDLER_KEY] = handler

    return store


def _has_initialization_event(store: PanelLogStore) -> bool:
    """Return whether the store already contains an initialization row."""
    return any(event.get("type") == "integration_initiation" for event in store.events)


def _has_complete_initialization_event(store: PanelLogStore) -> bool:
    """Return whether the store contains a fully backfilled initialization row."""
    for event in store.events:
        if event.get("type") != "integration_initiation":
            continue
        raw_logs = event.get("raw_logs") or []
        if any(
            _is_initialization_completion_log(str(log.get("message", "")))
            for log in raw_logs
        ):
            return True
    return False


def get_panel_log_events(hass) -> list[dict]:
    """Return a deep-copied list of panel log events."""
    store = async_setup_panel_log_store(hass)
    _maybe_backfill_grouped_events_from_log_file(hass, store)
    return [deepcopy(event) for event in _dedupe_events(store.events)]


async def async_get_panel_log_events(hass) -> list[dict]:
    """Return panel log events and complete file backfill before responding."""
    store = async_setup_panel_log_store(hass)
    needs_backfill = (
        not store.backfill_loaded
        or not _has_initialization_event(store)
        or not _has_complete_initialization_event(store)
    )
    if needs_backfill:
        if store.backfill_loading:
            return [deepcopy(event) for event in _dedupe_events(store.events)]

        store.backfill_loading = True
        try:
            backfilled_events = await hass.async_add_executor_job(
                _load_backfilled_grouped_events_from_log_file,
                hass.config.path("home-assistant.log"),
            )
            _merge_backfilled_events(store, backfilled_events)
            store.backfill_loaded = True
        except Exception:
            PANEL_LOGGER.exception(
                "Unable to backfill panel log events from the Home Assistant log file"
            )
            store.backfill_loaded = True
        finally:
            store.backfill_loading = False
    return [deepcopy(event) for event in _dedupe_events(store.events)]


def subscribe_panel_log_events(hass, subscriber):
    """Subscribe to newly completed panel log events."""
    store = async_setup_panel_log_store(hass)
    store.subscribers.add(subscriber)

    def unsubscribe() -> None:
        store.subscribers.discard(subscriber)

    return unsubscribe


def _new_grouped_event(
    event_type: str,
    title: str,
    row_color: str,
    first_log: dict,
    *,
    summary: str = "",
    copy_yaml: str = "",
    can_repeat: bool = False,
) -> dict:
    """Create a grouped panel log event seeded with its first raw log line."""
    has_error = str(first_log.get("level", "")).lower() == "error"
    return {
        "id": f"log-{uuid.uuid4().hex}",
        "type": event_type,
        "title": title,
        "summary": summary,
        "started_at": first_log["timestamp"],
        "ended_at": first_log["timestamp"],
        "row_color": row_color,
        "has_error": has_error,
        "error_count": 1 if has_error else 0,
        "raw_logs": [first_log],
        "copy_yaml": copy_yaml,
        "can_repeat": can_repeat,
    }


def _row_color_for_service(service: str) -> str:
    """Return the panel row color for a service event."""
    if service in {"say", "say_url"}:
        return "action"
    if service == "replay":
        return "replay"
    if service == "clear_cache":
        return "clear"
    return "action"


def _append_grouped_log(current_event: dict, log_entry: dict) -> None:
    """Append a raw line into a grouped event and keep summary fields current."""
    current_event["raw_logs"].append(log_entry)
    current_event["ended_at"] = log_entry["timestamp"]
    if str(log_entry.get("level", "")).lower() == "error":
        current_event["has_error"] = True
        current_event["error_count"] = int(current_event.get("error_count", 0)) + 1
    del current_event["raw_logs"][:-MAX_RAW_LOG_LINES]


def _finalize_backfilled_event(store: PanelLogStore, event: dict | None) -> None:
    """Save a grouped backfilled event once, keyed by timestamp/title."""
    if event is None or not event.get("raw_logs"):
        return
    key = event.get(BACKFILLED_EVENT_KEY)
    if not key or key in store.imported_event_keys:
        return
    matching_event = _find_matching_event(store, event)
    if matching_event is not None:
        _merge_event_details(matching_event, event)
        store.imported_event_keys.add(key)
        return
    store.imported_event_keys.add(key)
    event.pop(BACKFILLED_EVENT_KEY, None)
    event.pop(BACKFILLED_EVENT_TIME_KEY, None)
    _append_event(store, event)


def _merge_backfilled_events(store: PanelLogStore, events: list[dict]) -> None:
    """Merge imported backfilled events into the live store."""
    for event in events:
        if not event or not event.get("raw_logs"):
            continue

        key = event.get(BACKFILLED_EVENT_KEY)
        if key:
            _finalize_backfilled_event(store, event)
            continue

        matching_event = _find_matching_event(
            store,
            {
                **event,
                BACKFILLED_EVENT_TIME_KEY: _timepoint_key(event.get("started_at")),
            },
        )
        if matching_event is not None:
            _merge_event_details(matching_event, event)
            continue

        _append_event(store, deepcopy(event))


def _parse_log_line(line: str) -> dict | None:
    """Parse a Home Assistant log line into structured fields."""
    stripped = line.strip()
    match = LOG_LINE_PATTERN.match(stripped) or ISO_LOG_LINE_PATTERN.match(stripped)
    if not match:
        return None
    return {
        "timestamp": match.group("timestamp"),
        "level": match.group("level").lower(),
        "logger": match.group("logger"),
        "message": match.group("message"),
    }


def _build_backfilled_event(log_entry: dict) -> dict | None:
    """Create a grouped event when a log line marks the start of one."""
    message = log_entry["message"]
    logger = log_entry["logger"]
    title = None
    event_type = "runtime_log"
    row_color = "action"
    copy_yaml = ""
    can_repeat = False

    if logger == "homeassistant.setup" and message == "Setting up chime_tts":
        title = "Integration initialization"
        event_type = "integration_initiation"
        row_color = "configuration"
    elif "Chime TTS Version " in message and " is set up" in message:
        title = "Integration initialization"
        event_type = "integration_initiation"
        row_color = "configuration"
    elif "Chime TTS Say Called." in message:
        title = f"Action call: {DOMAIN}.say"
        event_type = "action_call"
        row_color = _row_color_for_service("say")
        copy_yaml = "action: chime_tts.say"
    elif message == "Chime TTS Notify":
        title = NOTIFY_EVENT_TITLE
        event_type = "notification_call"
        row_color = "action"
    elif "Chime TTS Say URL Called." in message:
        title = f"Action call: {DOMAIN}.say_url"
        event_type = "action_call"
        row_color = _row_color_for_service("say_url")
        copy_yaml = "action: chime_tts.say_url"
    elif "Chime TTS Replay Called." in message:
        title = f"Action call: {DOMAIN}.replay"
        event_type = "action_call"
        row_color = _row_color_for_service("replay")
        copy_yaml = "action: chime_tts.replay"
    elif "Chime TTS Clear Cache Called" in message:
        title = f"Action call: {DOMAIN}.clear_cache"
        event_type = "action_call"
        row_color = _row_color_for_service("clear_cache")
        copy_yaml = "action: chime_tts.clear_cache"

    if not title:
        return None

    event = _new_grouped_event(
        event_type,
        title,
        row_color,
        log_entry,
        summary=log_entry["logger"],
        copy_yaml=copy_yaml,
        can_repeat=can_repeat,
    )
    event_time_key = _timepoint_key(log_entry["timestamp"])
    event[BACKFILLED_EVENT_KEY] = f"{event_time_key}|{title}"
    event[BACKFILLED_EVENT_TIME_KEY] = event_time_key
    return event


def _matches_existing_event(store: PanelLogStore, candidate: dict) -> bool:
    """Return whether a backfilled event already exists in the live store."""
    return _find_matching_event(store, candidate) is not None


def _find_matching_event(store: PanelLogStore, candidate: dict) -> dict | None:
    """Return an existing event with the same title and normalized start time."""
    candidate_title = candidate.get("title", "")
    candidate_time_key = candidate.get(BACKFILLED_EVENT_TIME_KEY, "")
    candidate_started_at = candidate.get("started_at")
    candidate_type = candidate.get("type")
    candidate_logs = candidate.get("raw_logs") or []
    candidate_log_keys = {_log_key(log_entry) for log_entry in candidate_logs}

    for existing in store.events:
        if existing.get("title", "") != candidate_title:
            continue
        if existing.get("type") == candidate_type == "integration_initiation":
            if _timestamps_within_window(
                existing.get("started_at"),
                candidate_started_at,
            ) or _timestamps_within_window(
                existing.get("ended_at"),
                candidate.get("ended_at"),
            ):
                return existing
            continue
        if _timepoint_key(existing.get("started_at")) == candidate_time_key:
            return existing
        if not candidate_log_keys:
            continue
        if not (
            _timestamps_within_window(
                existing.get("started_at"),
                candidate_started_at,
            )
            or _timestamps_within_window(
                existing.get("ended_at"),
                candidate.get("ended_at"),
            )
        ):
            continue
        existing_log_keys = {
            _log_key(log_entry)
            for log_entry in existing.get("raw_logs") or []
        }
        if candidate_log_keys & existing_log_keys:
            return existing
    return None


def _merge_event_details(existing: dict, incoming: dict) -> None:
    """Merge richer backfilled details into an existing event."""
    existing["started_at"] = incoming.get("started_at", existing.get("started_at"))
    existing["ended_at"] = incoming.get("ended_at", existing.get("ended_at"))
    existing["summary"] = incoming.get("summary") or existing.get("summary", "")
    existing["row_color"] = incoming.get("row_color", existing.get("row_color"))
    existing["has_error"] = bool(existing.get("has_error")) or bool(incoming.get("has_error"))
    existing["error_count"] = max(
        int(existing.get("error_count", 0)),
        int(incoming.get("error_count", 0)),
    )

    incoming_logs = list(incoming.get("raw_logs") or [])
    existing_logs = list(existing.get("raw_logs") or [])

    incoming_counts = Counter(_log_key(log_entry) for log_entry in incoming_logs)
    existing_counts = Counter(_log_key(log_entry) for log_entry in existing_logs)
    target_counts = {
        key: max(incoming_counts.get(key, 0), existing_counts.get(key, 0))
        for key in set(incoming_counts) | set(existing_counts)
    }

    combined_logs: list[dict] = []
    emitted_counts: Counter = Counter()
    for log_entry in [*incoming_logs, *existing_logs]:
        key = _log_key(log_entry)
        if emitted_counts[key] >= target_counts.get(key, 0):
            continue
        combined_logs.append(log_entry)
        emitted_counts[key] += 1

    combined_logs.sort(key=lambda entry: str(entry.get("timestamp", "")))
    existing["raw_logs"] = combined_logs[-MAX_RAW_LOG_LINES:]


def _find_active_parent_notification_event(
    store: PanelLogStore,
    event_id: str,
    event: dict,
) -> dict | None:
    """Return an active notification event that should absorb a nested say call."""
    if event.get("type") != "action_call":
        return None
    if event.get("title") != f"Action call: {DOMAIN}.say":
        return None

    for candidate_id, candidate in store.active_events.items():
        if candidate_id == event_id:
            continue
        if candidate.get("type") != "notification_call":
            continue
        if _timestamps_within_window(
            candidate.get("started_at"),
            event.get("started_at"),
            window_ms=5000,
        ) or _timestamps_within_window(
            candidate.get("ended_at"),
            event.get("ended_at"),
            window_ms=5000,
        ):
            return candidate
    return None


def _dedupe_events(events: list[dict]) -> list[dict]:
    """Remove duplicate rows using title + normalized start time."""
    deduped: list[dict] = []

    for event in events:
        existing_match = _find_matching_event(
            PanelLogStore(events=deduped),
            {
                **event,
                BACKFILLED_EVENT_TIME_KEY: _timepoint_key(event.get("started_at")),
            },
        )
        if existing_match is not None:
            if len(event.get("raw_logs") or []) > len(existing_match.get("raw_logs") or []):
                _merge_event_details(existing_match, event)
            continue
        deduped.append(event)

    return deduped


def _is_relevant_to_open_event(current_event: dict, log_entry: dict) -> bool:
    """Return whether a log line belongs to the currently grouped event."""
    logger = log_entry["logger"]
    message = log_entry["message"]
    title = current_event.get("title", "")

    if title == "Integration initialization":
        if logger.startswith(LOGGER_NAMESPACE):
            return True
        if _is_initialization_related_log(log_entry):
            return _timestamps_within_window(
                current_event.get("started_at"),
                log_entry.get("timestamp"),
            ) or _timestamps_within_window(
                current_event.get("ended_at"),
                log_entry.get("timestamp"),
            )
        return False

    if title == NOTIFY_EVENT_TITLE:
        return logger.startswith(LOGGER_NAMESPACE)

    if title.startswith(f"Action call: {DOMAIN}."):
        return logger.startswith(LOGGER_NAMESPACE)

    return False


def _is_event_complete(current_event: dict, log_entry: dict) -> bool:
    """Return whether a log line closes the currently grouped event."""
    title = current_event.get("title", "")
    message = log_entry["message"]

    if title == "Integration initialization":
        return _is_initialization_completion_log(message)
    if title == NOTIFY_EVENT_TITLE:
        return (
            "Chime TTS Say Completed" in message
            or "Error calling chime_tts.say service:" in message
            or "Service `chime_tts.say` error:" in message
        )
    if title == f"Action call: {DOMAIN}.say":
        return "Chime TTS Say Completed" in message or "Error calling chime_tts.say service:" in message
    if title == f"Action call: {DOMAIN}.say_url":
        return "Chime TTS Say URL Completed" in message or "Error calling chime_tts.say_url service:" in message
    if title == f"Action call: {DOMAIN}.replay":
        return "Error calling chime_tts.say service:" in message or "Chime TTS Say Completed" in message
    if title == f"Action call: {DOMAIN}.clear_cache":
        return "Chime TTS Clear Cache Completed" in message
    return False


def _prepend_same_timepoint_prefix(
    entries: list[dict],
    start_index: int,
    current_event: dict,
) -> None:
    """Attach prior log lines that share the event's start timepoint."""
    start_entry = entries[start_index]
    target_key = _timepoint_key(start_entry["timestamp"])
    prefix_entries: list[dict] = []
    index = start_index - 1
    while index >= 0:
        candidate = entries[index]
        if _timepoint_key(candidate["timestamp"]) != target_key:
            break
        if not _is_initialization_related_log(candidate):
            index -= 1
            continue
        prefix_entries.append(candidate)
        index -= 1

    for prefix in reversed(prefix_entries):
        current_event["raw_logs"].insert(0, prefix)
        current_event["started_at"] = prefix["timestamp"]


def _maybe_backfill_grouped_events_from_log_file(hass, store: PanelLogStore) -> None:
    """Import grouped panel events from Home Assistant's existing log file."""
    if store.backfill_loaded and _has_complete_initialization_event(store):
        return

    try:
        log_path = hass.config.path("home-assistant.log")
    except Exception:
        return

    _merge_backfilled_events(
        store,
        _load_backfilled_grouped_events_from_log_file(log_path),
    )
    store.backfill_loaded = True


def _load_backfilled_grouped_events_from_log_file(log_path: str | None) -> list[dict]:
    """Load grouped panel events from Home Assistant's log file."""
    if not log_path:
        return []

    try:
        with open(log_path, encoding="utf-8") as log_file:
            lines = list(deque(log_file, maxlen=MAX_BACKFILL_LOG_LINES))
    except OSError:
        return []

    entries = [entry for line in lines if (entry := _parse_log_line(line)) is not None]
    return _build_backfilled_grouped_events(entries)


def _build_backfilled_grouped_events(entries: list[dict]) -> list[dict]:
    """Build grouped backfilled events from parsed log entries."""
    temp_store = PanelLogStore()
    current_event: dict | None = None
    for index, log_entry in enumerate(entries):
        next_event = _build_backfilled_event(log_entry)
        if next_event is not None:
            if (
                current_event is not None
                and current_event.get("title") == NOTIFY_EVENT_TITLE
                and next_event.get("title") == f"Action call: {DOMAIN}.say"
            ):
                _append_grouped_log(current_event, log_entry)
                continue
            if (
                current_event is not None
                and current_event.get("title") == next_event.get("title")
                and _timepoint_key(current_event.get("started_at"))
                == _timepoint_key(next_event.get("started_at"))
            ):
                _append_grouped_log(current_event, log_entry)
                continue

            _finalize_backfilled_event(temp_store, current_event)
            current_event = next_event
            _prepend_same_timepoint_prefix(entries, index, current_event)
            continue

        if current_event is None or not _is_relevant_to_open_event(current_event, log_entry):
            continue

        _append_grouped_log(current_event, log_entry)
        if _is_event_complete(current_event, log_entry):
            _finalize_backfilled_event(temp_store, current_event)
            current_event = None

    _finalize_backfilled_event(temp_store, current_event)
    return temp_store.events


def build_action_event_details(domain: str, service: str, service_data: Mapping | None) -> dict:
    """Build reusable metadata for a replayable action event."""
    normalized_data = _normalize_service_data(dict(service_data or {}))
    payload = {
        "action": f"{domain}.{service}",
        "data": normalized_data,
    }
    summary = normalized_data.get("message") or normalized_data.get("entity_id") or service
    return {
        "summary": str(summary),
        "copy_yaml": yaml.safe_dump(payload, sort_keys=False, allow_unicode=False).strip(),
        "can_repeat": True,
        "repeat_service": service,
        "repeat_data": normalized_data,
        "row_color": _row_color_for_service(service),
    }


def build_notification_event_details(service: str, service_data: Mapping | None) -> dict:
    """Build reusable metadata for a notify profile log event."""
    normalized_data = _normalize_service_data(dict(service_data or {}))
    notify_payload = dict(normalized_data)
    notify_data = notify_payload.get("data", None)
    if notify_data is None:
        notify_payload.pop("data", None)
    elif not isinstance(notify_data, Mapping):
        notify_payload["data"] = {}
    payload = {
        "action": f"notify.{service}",
        "data": notify_payload,
    }
    summary = notify_payload.get("message") or service
    return {
        "summary": str(summary),
        "copy_yaml": yaml.safe_dump(payload, sort_keys=False, allow_unicode=False).strip(),
        "can_repeat": True,
        "repeat_service": service,
        "repeat_data": notify_payload,
        "row_color": "action",
    }


def start_panel_log_event(
    hass,
    event_type: str,
    title: str,
    *,
    row_color: str = "action",
    details: Mapping | None = None,
    summary: str | None = None,
) -> str:
    """Start a new structured panel log event."""
    store = async_setup_panel_log_store(hass)
    event_id = f"panel-{uuid.uuid4().hex}"
    detail_map = dict(details or {})
    event = {
        "id": event_id,
        "type": event_type,
        "title": title,
        "summary": summary or detail_map.get("summary") or "",
        "started_at": _utc_now(),
        "ended_at": None,
        "row_color": detail_map.get("row_color", row_color),
        "has_error": False,
        "error_count": 0,
        "raw_logs": [],
        "copy_yaml": detail_map.get("copy_yaml", ""),
        "can_repeat": bool(detail_map.get("can_repeat")),
        "_repeat_service": detail_map.get("repeat_service"),
        "_repeat_data": detail_map.get("repeat_data"),
    }
    store.active_events[event_id] = event
    return event_id


def finish_panel_log_event(hass, event_id: str) -> dict | None:
    """Finalize an active panel log event and add it to the session log list."""
    try:
        store = async_setup_panel_log_store(hass)
        event = store.active_events.pop(event_id, None)
        if event is None:
            return None

        if event.get("raw_logs"):
            first_log = event["raw_logs"][0]
            last_log = event["raw_logs"][-1]
            event["started_at"] = first_log.get("timestamp", event.get("started_at"))
            event["ended_at"] = last_log.get("timestamp", event.get("ended_at"))
        else:
            event["ended_at"] = _utc_now()

        parent_notification_event = _find_active_parent_notification_event(
            store,
            event_id,
            event,
        )
        if parent_notification_event is not None:
            _merge_event_details(parent_notification_event, event)
            return None

        _append_event(store, event)
        _notify_panel_log_subscribers(store, event)
        return deepcopy(event)
    except Exception:
        PANEL_LOGGER.exception("Unable to finalize panel log event %s", event_id)
        return None


def get_panel_log_event(hass, event_id: str) -> dict | None:
    """Return a specific panel log event by id."""
    store = async_setup_panel_log_store(hass)
    for event in store.events:
        if event.get("id") == event_id:
            return deepcopy(event)
    return None
