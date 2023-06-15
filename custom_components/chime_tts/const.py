"""Constants for chime_tts."""
from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "chime_tts"
NAME = "Chime TTS"
DESCRIPTION = "A custom Home Assistant integration to play audio with text-to-speech (TTS) messages"
VERSION = "0.0.1"

SERVICE_SAY = "say"
PAUSE_DURATION_MS = 450
DATA_STORAGE_KEY = "chime_tts_integration_data"
TTS_API = "/api/tts_get_url"
HTTP_BEARER_AUTHENTICATION = "HTTP_BEARER_AUTHENTICATION"
TIMEOUT = 10
