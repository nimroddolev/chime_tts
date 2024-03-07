"""Constants for chime_tts."""
from logging import Logger, getLogger

import os
import json

LOGGER: Logger = getLogger(__package__)

DOMAIN = "chime_tts"
NAME = "Chime TTS"
DESCRIPTION = "A custom Home Assistant integration to play audio with text-to-speech (TTS) messages"

# Current version number from manifest.json
integration_dir = os.path.dirname(__file__)
manifest_path = os.path.join(integration_dir, "manifest.json")
if os.path.isfile(manifest_path):
    with open(manifest_path) as manifest_file:
        manifest_data = json.load(manifest_file)
    VERSION = manifest_data.get("version")
else:
    VERSION = None

SERVICE_SAY = "say"
SERVICE_SAY_URL = "say_url"
SERVICE_CLEAR_CACHE = "clear_cache"
DEFAULT_DELAY_MS = 450
FADE_TRANSITION_S = 1.0
FADE_TRANSITION_STEPS = 4
DATA_STORAGE_KEY = "chime_tts_integration_data"
AUDIO_PATH_KEY = "audio_path" # <-- Deprecated
LOCAL_PATH_KEY = "local_path"
PUBLIC_PATH_KEY = "public_path"
AUDIO_DURATION_KEY = "audio_duration"

ALEXA_MEDIA_PLAYER_PLATFORM = "alexa_media"
SPOTIFY_PLATFORM = "spotify"

ROOT_PATH_KEY = "root_path_key"
MEDIA_FOLDER_PATH = "/local/"
PUBLIC_FOLDER_PATH = "/config/www/"
DEFAULT_TEMP_CHIMES_PATH_KEY = "default_temp_chimes_path"
TEMP_CHIMES_PATH_KEY = "temp_chimes_path"
TEMP_CHIMES_PATH_DEFAULT = "/media/sounds/temp/chime_tts/chimes/"
DEFAULT_TEMP_PATH_KEY = "default_temp_path"
TEMP_PATH_KEY = "temp_path"
TEMP_PATH_DEFAULT = "/media/sounds/temp/chime_tts/"
DEFAULT_WWW_PATH_KEY = "default_www_path"
WWW_PATH_KEY = "www_path"
WWW_PATH_DEFAULT = "/www/chime_tts/"
MEDIA_DIR_KEY = "media_dir"
MEDIA_DIR_DEFAULT = "local"

MP3_PRESET_PATH = "custom_components/chime_tts/mp3s/"
MP3_PRESET_PATH_PLACEHOLDER = "mp3_path_placeholder-"  # DEPRECATED
MP3_PRESETS = [
    "ba_dum_tss",
    "bells",
    "bells_2",
    "bright",
    "chirp",
    "choir",
    "chord",
    "classical",
    "crickets",
    "ding_dong",
    "drumroll",
    "dun_dun_dun",
    "error",
    "fanfare",
    "glockenspiel",
    "hail",
    "marimba",
    "mario_coin",
    "microphone_tap",
    "tada",
    "toast",
    "twenty_four",
    "sad_trombone",
    "soft",
    "whistle",
]
MP3_PRESET_CUSTOM_PREFIX = "custom_chime_path_"
MP3_PRESET_CUSTOM_KEY = "custom_paths"
QUEUE = "QUEUE"
QUEUE_STATUS_KEY = "QUEUE_STATUS"
QUEUE_RUNNING = "QUEUE_RUNNING"
QUEUE_IDLE = "QUEUE_IDLE"
QUEUE_CURRENT_ID_KEY = "QUEUE_CURRENT_ID"
QUEUE_LAST_ID = "QUEUE_LAST_ID"
QUEUE_TIMEOUT_KEY = "queue_timeout"
QUEUE_TIMEOUT_DEFAULT = 60

# FFmpeg Arguments
FFMPEG_ARGS_ALEXA = "-y -ac 2 -codec:a libmp3lame -b:a 48k -ar 24000 -write_xing 0"
FFMPEG_ARGS_VOLUME = '-filter:a volume=X'

# TTS Platforms
AMAZON_POLLY = "amazon_polly"
BAIDU = "baidu"
ELEVENLABS_TTS = "tts.elevenlabs_tts"
GOOGLE_CLOUD = "google_cloud"
GOOGLE_TRANSLATE = "google_translate"
IBM_WATSON_TTS = "watson_tts"
MARYTTS = "MaryTTS"
MICROSOFT_TTS = "microsoft"
MICROSOFT_EDGE_TTS = "edge_tts"
NABU_CASA_CLOUD_TTS = "cloud"
NABU_CASA_CLOUD_TTS_OLD = "cloud_say"
OPENAI_TTS = "openai_tts"
PICOTTS = "picotts"
PIPER = "tts.piper"
VOICE_RSS = "voicerss"
YANDEX_TTS = "yandextts"
