"""Audio helper functions for Chime TTS."""

import logging
import time
import os
import subprocess
import shutil
import yaml
from homeassistant.core import HomeAssistant, State
from homeassistant.const import CONF_ENTITY_ID
from homeassistant.components.media_player.const import (
    ATTR_MEDIA_VOLUME_LEVEL,
    ATTR_MEDIA_ANNOUNCE,
    ATTR_GROUP_MEMBERS
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
        return options


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
        if len(message_string) > 0:
            try:
                message_yaml = yaml.safe_load(message_string)
            except yaml.YAMLError as exc:
                if hasattr(exc, 'problem_mark'):
                    # Handle parsing errors with line and column information
                    _LOGGER.error("Message YAML parsing error at line %s, column {exc.problem_mark.column + 1}: %s",
                                  str(exc.problem_mark.line + 1), str(exc))
                else:
                    # Handle other YAML-related errors
                    _LOGGER.error("Message YAML error: %s", str(exc))
            except Exception as error:
                _LOGGER.error("An unexpected error occurred while parsing message YAML: %s", str(error))
                # Handle other unexpected exceptions
            if isinstance(message_yaml, list):
                segments = message_yaml
            elif isinstance(message_yaml, str):
                segments.append({
                    'type': 'tts',
                    'message': message_string
                })
            else:
                _LOGGER.error("Error parsing message parameter")
                return []

        # Make all keys lowercase
        final_segments = []
        ignore_string = ""
        for i, segment_n in enumerate(segments):
            segment = {}
            for key, value in segment_n.items():
                key_lower = key.lower()
                segment[key_lower] = value
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


    def get_file_path(self, hass: HomeAssistant, p_filepath: str = ""):
        """Return a valid file path string."""
        ret_value = None

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

    def ffmpeg_convert_from_file(self, file_path, ffmpeg_args):
        """Convert audio stream with FFmpeg and provided arguments."""
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
