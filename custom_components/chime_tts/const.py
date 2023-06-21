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

# TTS Platforms
AMAZON_POLLY = "amazon_polly"
BAIDU = "baidu"
GOOGLE_CLOUD = "google_cloud"
GOOGLE_TRANSLATE = "google_translate"
IBM_WATSON_TTS = "watson_tts"
MARYTTS = "MaryTTS"
MICROSOFT_TTS = "microsoft"
NABU_CASA = "cloud_say"
PICOTTS = "picotts"
VOICE_RSS = "voicerss"
YANDEX_TTS = "yandextts"
