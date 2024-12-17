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

SERVICE_CLEAR_CACHE = "clear_cache"
SERVICE_REPLAY = "replay"
SERVICE_SAY = "say"
SERVICE_SAY_URL = "say_url"

OFFSET_KEY = "offset"
DEFAULT_OFFSET_MS = 450
CROSSFADE_KEY = "crossfade"

DATA_STORAGE_KEY = "chime_tts_integration_data"
AUDIO_PATH_KEY = "audio_path" # <-- Deprecated
LOCAL_PATH_KEY = "local_path"
PUBLIC_PATH_KEY = "public_path"
AUDIO_DURATION_KEY = "audio_duration"

FADE_TRANSITION_KEY = "fade_transition_key"
DEFAULT_FADE_TRANSITION_MS = 500
REMOVE_TEMP_FILE_DELAY_KEY = "remove_temp_file_delay"
TRANSITION_STEP_MS = 150
ADD_COVER_ART_KEY = "add_cover_art"

ALEXA_MEDIA_PLAYER_PLATFORM = "alexa_media"
SONOS_PLATFORM = "sonos"
SPOTIFY_PLATFORM = "spotify"

ROOT_PATH_KEY = "root_path_key"
MEDIA_FOLDER_PATH = "/local/"
PUBLIC_FOLDER_PATH = "/config/www/"
CUSTOM_CHIMES_PATH_KEY = "custom_chimes_path"
DEFAULT_TEMP_CHIMES_PATH_KEY = "default_temp_chimes_path"
TEMP_CHIMES_PATH_KEY = "temp_chimes_path"
TEMP_CHIMES_PATH_DEFAULT = "/media/sounds/temp/chime_tts/chimes/"
DEFAULT_TEMP_PATH_KEY = "default_temp_path"
TEMP_PATH_KEY = "temp_path"
TEMP_PATH_DEFAULT = "/media/sounds/temp/chime_tts/"
DEFAULT_WWW_PATH_KEY = "default_www_path"
WWW_PATH_KEY = "www_path"
WWW_PATH_DEFAULT = "/config/www/chime_tts/"

MP3_PRESET_PATH = "custom_components/chime_tts/mp3s/"
MP3_PRESET_PATH_PLACEHOLDER = "mp3_path_placeholder-"  # DEPRECATED
DEFAULT_CHIME_OPTIONS = [
    {"label": "Ba-Dum Tss!", "value": "ba_dum_tss"},
    {"label": "Bells", "value": "bells"},
    {"label": "Bells 2", "value": "bells_2"},
    {"label": "Bright", "value": "bright"},
    {"label": "Chirp", "value": "chirp"},
    {"label": "Choir", "value": "choir"},
    {"label": "Chord", "value": "chord"},
    {"label": "Classical", "value": "classical"},
    {"label": "Crickets", "value": "crickets"},
    {"label": "Ding Dong", "value": "ding_dong"},
    {"label": "Drum Roll", "value": "drumroll"},
    {"label": "Dun dun DUUUN!", "value": "dun_dun_dun"},
    {"label": "Error", "value": "error"},
    {"label": "Fanfare", "value": "fanfare"},
    {"label": "Glockenspiel", "value": "glockenspiel"},
    {"label": "Hail", "value": "hail"},
    {"label": "Knock", "value": "knock"},
    {"label": "Marimba", "value": "marimba"},
    {"label": "Mario Coin", "value": "mario_coin"},
    {"label": "Microphone Tap", "value": "microphone_tap"},
    {"label": "Ta-da!", "value": "tada"},
    {"label": "Toast", "value": "toast"},
    {"label": "Twenty Four", "value": "twenty_four"},
    {"label": "Sad Trombone", "value": "sad_trombone"},
    {"label": "Soft", "value": "soft"},
    {"label": "Whistle", "value": "whistle"}
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
TTS_TIMEOUT_KEY = "tts_timeout"
TTS_TIMEOUT_DEFAULT = 30
MAX_CONCURRENT_TASKS = 10
MAX_TIMEOUT = 600
QUEUE_PROCESSOR_SLEEP_TIME = 0.2

TTS_PLATFORM_KEY = "tts_platform_key"
FALLBACK_TTS_PLATFORM_KEY = "fallback_tts_platform_key"
DEFAULT_LANGUAGE_KEY = "default_language_key"
DEFAULT_VOICE_KEY = "default_voice_key"
DEFAULT_TLD_KEY = "default_tld_key"

# FFmpeg Arguments
FFMPEG_ARGS_ALEXA = "-y -ac 2 -codec:a libmp3lame -b:a 48k -ar 24000 -write_xing 0"
FFMPEG_ARGS_VOLUME = '-filter:a volume=X'

# TTS Platforms
AMAZON_POLLY = "amazon_polly"
BAIDU = "baidu"
ELEVENLABS = "tts.elevenlabs"
GOOGLE_CLOUD = "tts.google_cloud"
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

QUOTE_CHAR_SUBSTITUTE = "🁢"
