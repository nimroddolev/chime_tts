"""Audio helper functions for Chime TTS."""

import logging
import time
import tempfile
import os
import hashlib
import subprocess
import shutil
from io import BytesIO
import re
import yaml
import requests
from pydub import AudioSegment
from homeassistant.core import HomeAssistant, State
from homeassistant.const import CONF_ENTITY_ID, SERVICE_TURN_ON
from homeassistant.components.media_player.const import (
    ATTR_MEDIA_VOLUME_LEVEL,
    ATTR_MEDIA_ANNOUNCE,
    ATTR_GROUP_MEMBERS
)
from .const import (
    DEFAULT_DELAY_MS,
    ALEXA_FFMPEG_ARGS,
    MP3_PRESET_PATH,
    MP3_PRESETS,
    MP3_PRESET_PATH_PLACEHOLDER,  # DEPRECATED
    MP3_PRESET_CUSTOM_PREFIX,
    MP3_PRESET_CUSTOM_KEY,
    TEMP_CHIMES_PATH_KEY,
    AUDIO_PATH_KEY,
    AUDIO_DURATION_KEY
)
_LOGGER = logging.getLogger(__name__)

class ChimeTTSHelper:
    """Helper functions for Chime TTS."""

    def parse_options_yaml(self, data):
        """Parse TTS service options YAML into dict object."""
        options = {}
        try:
            options_string = data.get("options", "")
            options = yaml.safe_load(options_string)
            if options is None:
                options = {}
        except yaml.YAMLError as error:
            _LOGGER.error("Error parsing options YAML: %s", error)
            return {}

        for key in ["tld", "gender"]:
            if key not in options:
                value = data.get(key, None)
                if value is not None:
                    options[key] = value

        if len(options) > 0:
            _LOGGER.debug("----- TTS-Specific Params -----")
            for key, value in options.items():
                _LOGGER.debug(" * %s = %s", key, str(value))

        return options

    async def async_parse_params(self, data, hass: HomeAssistant):
        """Parse TTS service parameters."""
        entity_ids = self.parse_entity_ids(data, hass)
        chime_path =str(data.get("chime_path", ""))
        end_chime_path = str(data.get("end_chime_path", ""))
        offset = float(data.get("delay", data.get("offset", DEFAULT_DELAY_MS)))
        final_delay = float(data.get("final_delay", 0))
        message = str(data.get("message", ""))
        tts_platform = str(data.get("tts_platform", ""))
        tts_playback_speed = float(data.get("tts_playback_speed", 100))
        volume_level = float(data.get(ATTR_MEDIA_VOLUME_LEVEL, -1))
        media_players_array = await self.async_initialize_media_players(
            hass, entity_ids, volume_level
        )
        join_players = data.get("join_players", False)
        unjoin_players = data.get("unjoin_players", False)
        language = data.get("language", None)
        cache = data.get("cache", False)
        announce = data.get("announce", False)

        # FFmpeg arguments
        ffmpeg_args = data.get("audio_conversion", None)
        if ffmpeg_args is not None:
            if data.get("audio_conversion", None).lower() == "alexa":
                ffmpeg_args = ALEXA_FFMPEG_ARGS
            else:
                if data.get("audio_conversion", None).lower() == "custom":
                    ffmpeg_args = None
                else:
                    data.get("audio_conversion", None)

        params = {
            "entity_ids": entity_ids,
            "hass": hass,
            "chime_path": chime_path,
            "end_chime_path": end_chime_path,
            "cache": cache,
            "offset": offset,
            "final_delay": final_delay,
            "media_players_array": media_players_array,
            "message": message,
            "language": language,
            "tts_platform": tts_platform,
            "tts_playback_speed": tts_playback_speed,
            "announce": announce,
            "volume_level": volume_level,
            "join_players": join_players,
            "unjoin_players": unjoin_players,
            "ffmpeg_args": ffmpeg_args,
        }

        _LOGGER.debug("----- General Parameters -----")
        for key, value in params.items():
            if value is not None and value != "" and key not in ["hass", "media_players_array"]:
                _LOGGER.debug(" * %s = %s", key, str(value))

        return params


    def parse_entity_ids(self, data, hass):
        """Parse media_player entity_ids into list object."""
        entity_ids = data.get(CONF_ENTITY_ID, [])
        if isinstance(entity_ids, str):
            entity_ids = entity_ids.split(",")

        # Find all media_player entities associated with device/s specified
        device_ids = data.get("device_id", [])
        if isinstance(device_ids, str):
            device_ids = device_ids.split(",")
        entity_registry = hass.data["entity_registry"]
        for device_id in device_ids:
            matching_entity_ids = [
                entity.entity_id
                for entity in entity_registry.entities.values()
                if entity.device_id == device_id
                and entity.entity_id.startswith("media_player.")
            ]
            entity_ids.extend(matching_entity_ids)
        entity_ids = list(set(entity_ids))
        return entity_ids

    def parse_message(self, message_string):
        """Parse the message string/YAML object into segments dictionary."""
        message_string = str(message_string)
        segments = []
        if len(message_string) == 0 or message_string == "None":
            return []

        if (message_string.find("'type':") > -1 or message_string.find('"type":') > -1):

            # Convert message string to YAML object
            message_yaml = None
            try:
                message_yaml = yaml.safe_load(message_string)
            except yaml.YAMLError as exc:
                if hasattr(exc, 'problem_mark'):
                    _LOGGER.error("Message YAML parsing error at line %s, column %s: %s",
                                  str(exc.problem_mark.line + 1),
                                  str(exc.problem_mark.column + 1),
                                  str(exc))
                else:
                    _LOGGER.error("Message YAML error: %s", str(exc))
            except Exception as error:
                _LOGGER.error("An unexpected error occurred while parsing message YAML: %s",
                              str(error))

            # Verify objects in YAML are valid chime/tts/delay segements
            if isinstance(message_yaml, list):
                is_valid = True
                for elem in message_yaml:
                    if isinstance(elem, dict):
                        if "type" not in elem:
                            is_valid = False
                    else:
                        is_valid = False
                if is_valid is True:
                    segments = message_yaml

        # Add message string as TTS segment
        if len(segments) == 0:
            segments.append({
                'type': 'tts',
                'message': message_string
            })

        # Make all segment keys lowercase
        final_segments = []
        ignore_string = ""
        for i, segment_n in enumerate(segments):
            segment = {}
            for key, value in segment_n.items():
                if isinstance(value, dict):
                    for key_n, value_n in value.items():
                        value[key_n.lower()] = value_n
                segment[key.lower()] = value
            final_segments.append(segment)
            ignore_string += str(i)

        return final_segments

    def get_supported_feature(self, entity: State, feature: str):
        """Whether a feature is supported by the media_player device."""
        if entity is None or entity.attributes is None:
            return False
        supported_features = entity.attributes.get("supported_features", 0)

        if feature is ATTR_MEDIA_VOLUME_LEVEL:
            return bool(supported_features & 2)

        if feature is ATTR_MEDIA_ANNOUNCE:
            # Announce support detection feature not yet supporting in HA
            # return bool(supported_features & 128)
            return True

        if feature is ATTR_GROUP_MEMBERS:
            return bool(supported_features & 524288)

        return False


    def sleep(self, duration_s: float):
        """Make a synchronous time.sleep call lasting duration_s seconds."""
        return time.sleep(duration_s)


    def validate_path(self, hass: HomeAssistant, p_filepath: str = ""):
        """Return a valid file path string."""
        ret_value = None
        if p_filepath is None:
            return ret_value

        filepaths = [p_filepath]

        # Test for docker/virtual instances filepath
        root_path = hass.config.path("")
        absolute_path = (root_path + p_filepath).replace("/config", "").replace("//", "/")
        if p_filepath is not absolute_path:
            filepaths.append(absolute_path)

        # Test each filepath
        for filepath in filepaths:
            if os.path.exists(filepath) is True:
                ret_value = filepath
            if ret_value is None:
                _LOGGER.debug("File not found at path: %s", filepath)

        return ret_value

    async def async_get_chime_path(self, chime_path, cache, data, hass: HomeAssistant):
        """Retrieve preset chime path if selected."""

        custom_chime_paths_dict = data[MP3_PRESET_CUSTOM_KEY]
        temp_chimes_path = data[TEMP_CHIMES_PATH_KEY]

        # Remove prefix (prefix deprecated in v0.9.1)
        chime_path = chime_path.replace(MP3_PRESET_PATH_PLACEHOLDER, "")

        # Preset chime mp3 path?
        if chime_path in MP3_PRESETS:
            return MP3_PRESET_PATH + chime_path + ".mp3"

        # Custom chime mp3 path?
        if chime_path.startswith(MP3_PRESET_CUSTOM_PREFIX):
            chime_path = custom_chime_paths_dict[chime_path]
            if chime_path == "":
                _LOGGER.warning(
                    "MP3 file path missing for custom chime path `Custom #%s`",
                    chime_path.replace(MP3_PRESET_CUSTOM_PREFIX, ""),
                )

        # External URL?
        if chime_path.startswith("http://") or chime_path.startswith("https://"):
            # Use cached version?
            if cache is True:
                local_file = self.get_downloaded_chime_path(folder=temp_chimes_path, url=chime_path)
                if local_file is not None:
                    return local_file
                _LOGGER.debug(" - Chime does not exist in cache")

            # Download from URL
            audio_dict = await self.async_download_file(hass, chime_path, temp_chimes_path)
            if audio_dict is not None:
                _LOGGER.debug(" - Chime downloaded successfully")
                # # Store audio data in cache
                # file_hash = self.get_hash_for_string(chime_path)
                # data[DATA_STORAGE_KEY][file_hash] = audio_dict
                # store = storage.Store(hass, 1, DATA_STORAGE_KEY)
                # await store.async_save(data[DATA_STORAGE_KEY])
                return audio_dict[AUDIO_PATH_KEY]

            _LOGGER.warning(" - Unable to downloaded chime %s", chime_path)
            return None

        chime_path = self.validate_path(hass, chime_path)
        return chime_path

    def ffmpeg_convert_from_audio_segment(self,
                                          audio_segment: AudioSegment,
                                          ffmpeg_args: str,
                                          folder: str):
        """Convert pydub AudioSegment with FFmpeg and provided arguments."""
        # Save to temp file
        temp_filename = "temp_segment.mp3"
        temp_audio_file = self.save_audio_to_folder(audio=audio_segment,
                                                    folder=folder,
                                                    file_name=temp_filename)
        if temp_audio_file is None:
            _LOGGER.warning("ffmpeg_convert_from_audio_segment - Unable to store audio segment")
            return audio_segment

        # Convert with FFmpeg
        converted_audio_file = self.ffmpeg_convert_from_file(temp_audio_file, ffmpeg_args)
        if converted_audio_file is None or converted_audio_file is False or len(converted_audio_file) < 5:
            _LOGGER.warning("ffmpeg_convert_from_audio_segment - Unable convert audio segment")
            return audio_segment

        # Load new AudioSegment from converted file
        try:
            converted_audio_segment = AudioSegment.from_file(converted_audio_file)
        except Exception as error:
            _LOGGER.warning("ffmpeg_convert_from_audio_segment - Unable to load converted audio segment %s", error)
            return audio_segment

        # Delete temp file & converted file
        if os.path.exists(temp_audio_file):
            try:
                os.remove(temp_audio_file)
            except Exception as error:
                _LOGGER.warning("ffmpeg_convert_from_audio_segment - Unable to delete temp files: %s", error)
        if os.path.exists(converted_audio_file):
            try:
                os.remove(converted_audio_file)
            except Exception as error:
                _LOGGER.warning("ffmpeg_convert_from_audio_segment - Unable to delete temp files: %s", error)

        if converted_audio_segment is not None:
            return converted_audio_segment

        return audio_segment


    def ffmpeg_convert_from_file(self, file_path: str, ffmpeg_args: str):
        """Convert audio file with FFmpeg and provided arguments."""
        try:
            ffmpeg_cmd = [
                'ffmpeg',
                '-i', file_path,
                *ffmpeg_args.split()
            ]

            # Save to a specific file type (arguement option -f)
            try:
                # Use the file type specific by the -f option (eg: -f wav)
                index = ffmpeg_cmd.index('-f')
                file_extension = ffmpeg_cmd[index+1]
                converted_file_path = file_path.replace(".mp3", f".{file_extension}")
            except Exception:
                # Use the default file type of mp3
                converted_file_path = file_path.replace(".mp3", "_converted.mp3")
            ffmpeg_cmd.append(converted_file_path)

            # Overwrite output file if it already exists
            ffmpeg_cmd.append('-y')

            # Convert the audil file
            ffmpeg_cmd_string = " ".join(ffmpeg_cmd)
            ffmpeg_process = subprocess.Popen(ffmpeg_cmd,
                                              stdin=subprocess.PIPE,
                                              stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE)
            converted_file, error_output = ffmpeg_process.communicate()

            if ffmpeg_process.returncode != 0:
                error_message = error_output.decode('utf-8')
                _LOGGER.error("%s, %s, output=%s, stderr=%s",
                               str(ffmpeg_process.returncode),
                               ' '.join(ffmpeg_cmd),
                               converted_file_path,
                               str(error_message))
                return False

            # Replace original with converted file
            if converted_file_path == file_path.replace(".mp3", "_converted.mp3"):
                try:
                    shutil.move(converted_file_path, file_path)
                    return file_path
                except Exception as error:
                    _LOGGER.error("Error renaming file %s to %s. Error: %s. FFmpeg options: %s",
                                   file_path, converted_file_path, error, ffmpeg_cmd_string)
                    return False

            return converted_file_path

        except subprocess.CalledProcessError as error:
            _LOGGER.error("FFmpeg subproces error: %s FFmpeg options: %s",
                           error, ffmpeg_cmd_string)

        except Exception as error:
            _LOGGER.error("FFmpeg unexpected error: %s FFmpeg options: %s",
                           error, ffmpeg_cmd_string)

        return file_path

    def get_downloaded_chime_path(self, folder: str, url: str):
        """Local file path string for chime URL in local folder."""
        return folder + ("" if folder.endswith("/") else "/") + re.sub(r'[\/:*?"<>|]', '_', url.replace("https://", "").replace("http://", ""))

    def save_audio_to_folder(self, audio, folder, file_name: str = None):
        """Save audio to local folder."""

        # Create folder if it doesn't already exist
        if os.path.exists(folder) is False:
            _LOGGER.debug("  - Creating audio folder: %s", folder)
            try:
                os.makedirs(folder)
            except OSError as error:
                _LOGGER.warning(
                    "  - An error occurred while creating the folder '%s': %s",
                    folder, error)
                return None
            except Exception as error:
                _LOGGER.warning(
                    "  - An error occurred while creating the folder '%s': %s",
                    folder, error)
                return None

        # Save to file
        if file_name is None:
            try:
                with tempfile.NamedTemporaryFile(
                    prefix=folder, suffix=".mp3"
                ) as temp_obj:
                    audio_full_path = temp_obj.name
                audio.export(audio_full_path, format="mp3")
                _LOGGER.debug(" - File saved successfully")
            except Exception as error:
                _LOGGER.warning(
                    "An error occurred when creating the temp mp3 file: %s", error
                )
                return None
        else:
            try:
                # Make file name safe
                audio_full_path = self.get_downloaded_chime_path(url=file_name, folder=folder)
                audio.export(audio_full_path, format="mp3")
            except Exception as error:
                _LOGGER.warning(
                    "An error occurred when creating the mp3 file: %s", error
                )
                return None

        _LOGGER.debug(" - File saved to path: %s", audio_full_path)
        return audio_full_path

    def combine_audio(self,
                      audio_1: AudioSegment,
                      audio_2: AudioSegment,
                      offset: int = 0):
        """Combine two AudioSegment object with either a delay (if >0) or overlay (if <0)."""
        if audio_1 is None:
            return audio_2
        if audio_2 is None:
            return audio_1
        ret_val = audio_1 + audio_2

        # Overlay / delay
        if offset < 0:
            _LOGGER.debug("Performing overlay of %sms", str(offset))
            ret_val = self.overlay(audio_1, audio_2, offset)
        elif offset > 0:
            _LOGGER.debug("Performing delay of %sms", str(offset))
            ret_val = audio_1 + (AudioSegment.silent(duration=offset) + audio_2)
        else:
            _LOGGER.debug("Combining audio files with no delay or overlay")

        return ret_val


    def overlay(self, audio_1: AudioSegment, audio_2: AudioSegment, overlay: int = 0):
        """Overlay two audio segments."""
        overlay = abs(overlay)
        overlap_point = len(audio_1) - overlay
        overlap_point = max(0, overlap_point)

        crossover_audio = audio_1.overlay(audio_2, position=overlap_point)
        if len(audio_2) > overlay:
            crossover_audio += audio_2[overlay:]
        return crossover_audio


    ##############################
    ### Media Player Functions ###
    ##############################

    def get_group_members_suppored(self, media_players_array):
        """Get the number of media player which support the join feature."""
        group_members_supported = 0
        for media_player_dict in media_players_array:
            if "group_member_support" in media_player_dict and media_player_dict["group_member_support"] is True:
                group_members_supported += 1
        return group_members_supported


    async def async_initialize_media_players(
            self,
            hass: HomeAssistant,
            entity_ids,
            volume_level: float
    ):
        """Initialize media player entities."""
        # Service call was from chime_tts.say_url, so media_players are irrelevant
        if len(entity_ids) == 0:
            return False

        entity_found = False
        media_players_array = []
        for entity_id in entity_ids:
            # Validate media player entity_id
            entity = hass.states.get(entity_id)
            if entity is None:
                _LOGGER.warning('Media player entity: "%s" not found', entity_id)
                continue
            else:
                entity_found = True

            # Ensure media player is turned on
            if entity.state == "off":
                _LOGGER.info(
                    'Media player entity "%s" is turned off. Turning on...', entity_id
                )
                await hass.services.async_call(
                    "media_player", SERVICE_TURN_ON, {CONF_ENTITY_ID: entity_id}, True
                )

            # Store media player's current volume level
            should_change_volume = False
            initial_volume_level = -1
            if volume_level >= 0:
                initial_volume_level = float(
                    entity.attributes.get(ATTR_MEDIA_VOLUME_LEVEL, -1)
                )
                if float(initial_volume_level) == float(volume_level / 100):
                    _LOGGER.debug(
                        "%s's volume_level is already %s", entity_id, str(volume_level)
                    )
                else:
                    should_change_volume = True

            # Group members supported?
            group_member_support = self.get_supported_feature(entity, ATTR_GROUP_MEMBERS)

            media_players_array.append(
                {
                    "entity_id": entity_id,
                    "should_change_volume": should_change_volume,
                    "initial_volume_level": initial_volume_level,
                    "group_members_supported": group_member_support,
                }
            )
        if entity_found is False:
            _LOGGER.error("No valid media player found")
            return False
        return media_players_array

    async def async_download_file(self, hass: HomeAssistant, url, folder):
        """Download a file and save locally."""
        try:
            _LOGGER.debug("Downloading chime at URL: %s", url)
            response = await hass.async_add_executor_job(requests.get, url)
            response.raise_for_status() # Raise an HTTPError for bad responses (4xx and 5xx status codes)
        except requests.exceptions.HTTPError as errh:
            _LOGGER.warning(" - HTTP Error: %s", str(errh))
            return None
        except requests.exceptions.ConnectionError as errc:
            _LOGGER.warning(" - Error Connecting: %s", str(errc))
            return None
        except requests.exceptions.Timeout as errt:
            _LOGGER.warning(" - Timeout Error: %s", str(errt))
            return None
        except requests.exceptions.RequestException as err:
            _LOGGER.warning(" - Request Exception: %s", str(err))
            return None
        except Exception as error:
            _LOGGER.warning(" - An unexpected error occurred: %s", str(error))
            return None

        if response is None:
            _LOGGER.warning(" - Received an invalid response")
            return None

        content_type = response.headers.get('Content-Type', '')
        if 'audio' in content_type:
            _LOGGER.debug(" - Audio downloaded successfully")
            file_name, file_extension = os.path.splitext(url)
            audio_content = AudioSegment.from_file(BytesIO(response.content),
                                                   format=file_extension.replace(".", ""))
            if audio_content is not None:
                audio_file_path = self.save_audio_to_folder(audio=audio_content,
                                                            folder=folder,
                                                            file_name=url)
                audio_duration = float(len(audio_content) / 1000)
                return {
                    AUDIO_PATH_KEY: audio_file_path,
                    AUDIO_DURATION_KEY: audio_duration
                }
        else:
            _LOGGER.warning(" - Unable to extract audio from URL with content-type '%s'",
                            str(content_type))
        return None

    def get_hash_for_string(self, string):
        """Generate a has for a given string."""
        hash_object = hashlib.sha256()
        hash_object.update(string.encode("utf-8"))
        hash_value = str(hash_object.hexdigest())
        return hash_value
