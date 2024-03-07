"""Audio helper functions for Chime TTS."""

import logging
import os
import subprocess
import shutil
import yaml
from pydub import AudioSegment
from homeassistant.core import HomeAssistant
from homeassistant.components.media_player.const import (
    ATTR_MEDIA_VOLUME_LEVEL,
)
from ..const import (
    DEFAULT_DELAY_MS,
    FFMPEG_ARGS_ALEXA,
    FFMPEG_ARGS_VOLUME
)
from .media_player import MediaPlayerHelper
from .filesystem import FilesystemHelper

media_player_helper = MediaPlayerHelper()
filesystem_helper = FilesystemHelper()

_LOGGER = logging.getLogger(__name__)

class ChimeTTSHelper:
    """Helper functions for Chime TTS."""

    async def async_parse_params(self, hass: HomeAssistant, data, is_say_url):
        """Parse TTS service parameters."""
        entity_ids = media_player_helper.parse_entity_ids(data, hass) if is_say_url is False else []
        chime_path =str(data.get("chime_path", ""))
        end_chime_path = str(data.get("end_chime_path", ""))
        offset = float(data.get("delay", data.get("offset", DEFAULT_DELAY_MS)))
        final_delay = float(data.get("final_delay", 0))
        message = str(data.get("message", ""))
        tts_platform = str(data.get("tts_platform", ""))
        tts_playback_speed = float(data.get("tts_playback_speed", 100))
        volume_level = float(data.get(ATTR_MEDIA_VOLUME_LEVEL, -1))
        media_players_array = await media_player_helper.async_initialize_media_players(
            hass, entity_ids, volume_level
        ) if is_say_url is False else []
        join_players = data.get("join_players", False)
        unjoin_players = data.get("unjoin_players", False)
        language = data.get("language", None)
        cache = data.get("cache", False)

        announce = data.get("announce", False)

        # FFmpeg arguments
        ffmpeg_args: str = self.parse_ffmpeg_args(data.get("audio_conversion", None))

        # Force "Alexa" conversion if any Alexa media_player entities included
        alexa_conversion_forced = False
        if ffmpeg_args is None and media_player_helper.get_alexa_media_player_count(hass, entity_ids) > 0:
            ffmpeg_args = FFMPEG_ARGS_ALEXA
            alexa_conversion_forced = True

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
                p_key = "audio_conversion" if key == "ffmpeg_args" else key
                _LOGGER.debug(" * %s = %s", p_key, str(value))

        if alexa_conversion_forced is True:
            _LOGGER.debug(" --- Audio will be converted to Alexa-friendly format as Alexa speaker/s detected ---")
        return params

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
        except Exception as error:
            _LOGGER.error("An unexpected error occurred while parsing options YAML: %s",
                          str(error))

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

        # Final adjustments
        final_segments = []
        for _, segment_n in enumerate(segments):
            segment = {}
            for key, value in segment_n.items():
                if isinstance(value, dict):
                    for key_n, value_n in value.items():
                        value[key_n.lower()] = value_n
                # Make all segment keys lowercase
                segment[key.lower()] = value
            # Dupliacte segments "repeat" times
            repeat = segment.get("repeat", 1)
            if isinstance(repeat, int):
                repeat = max(segment.get("repeat", 1), 1)
            else:
                repeat = 1
            for _ in range(repeat):
                final_segments.append(segment)

        return final_segments

    def parse_ffmpeg_args(self, ffmpeg_args_str: str):
        """Parse the FFmpeg argument string."""
        if ffmpeg_args_str is not None:
            if ffmpeg_args_str.lower() == "alexa":
                return FFMPEG_ARGS_ALEXA
            if (len(ffmpeg_args_str.split(" ")) == 2 and
                  ffmpeg_args_str.split(" ")[0].lower() == "volume"):
                try:
                    volume = float(ffmpeg_args_str.split(" ")[1].replace("%","")) / 100
                    return FFMPEG_ARGS_VOLUME.replace("X", str(volume))
                except ValueError:
                    _LOGGER.warning("Error parsing audio_conversion string")
            if ffmpeg_args_str.lower() == "custom":
                return None
        return ffmpeg_args_str


    def ffmpeg_convert_from_audio_segment(self,
                                          audio_segment: AudioSegment,
                                          ffmpeg_args: str,
                                          folder: str):
        """Convert pydub AudioSegment with FFmpeg and provided arguments."""
        # Save to temp file
        temp_filename = "temp_segment.mp3"
        temp_audio_file = filesystem_helper.save_audio_to_folder(audio=audio_segment,
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
