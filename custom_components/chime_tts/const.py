"""Constants for chime_tts."""
from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "chime_tts"
NAME = "Chime TTS"
DESCRIPTION = "A custom Home Assistant integration to play an audio file before and/or after text-to-speech (TTS) messages"
VERSION = "0.0.1"

SERVICE_SAY = "say"
HTTP_BEARER_AUTHENTICATION = "HTTP_BEARER_AUTHENTICATION"
