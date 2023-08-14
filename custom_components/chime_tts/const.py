"""Constants for chime_tts."""
from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "chime_tts"
NAME = "Chime TTS"
DESCRIPTION = "A custom Home Assistant integration to play audio with text-to-speech (TTS) messages"

SERVICE_SAY = "say"
SERVICE_CLEAR_CACHE = "clear_cache"
PAUSE_DURATION_MS = 450
DATA_STORAGE_KEY = "chime_tts_integration_data"
AUDIO_PATH_KEY = "audio_path"
AUDIO_DURATION_KEY = "audio_duration"
BLANK_MP3_PATH = "custom_components/chime_tts/mp3s/_blank.mp3"
TEMP_PATH = "/media/sounds/temp/chime_tts/"
QUEUE_STATUS = "QUEUE_STATUS"
QUEUE_RUNNING = "QUEUE_RUNNING"
QUEUE_IDLE = "QUEUE_IDLE"
QUEUE_CURRENT_ID = "QUEUE_CURRENT_ID"
QUEUE_LAST_ID = "QUEUE_LAST_ID"
QUEUE_TIMEOUT_S = 7.5

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
PIPER = "tts.piper"
VOICE_RSS = "voicerss"
YANDEX_TTS = "yandextts"
