"""Filesystem helper functions for Chime TTS."""

import logging
import tempfile
import os
import hashlib
import shutil
from io import BytesIO
import re
import requests
from pydub import AudioSegment
from homeassistant.helpers.network import get_url
from homeassistant.core import HomeAssistant
from ..const import (
    MP3_PRESET_PATH,
    MP3_PRESETS,
    MP3_PRESET_PATH_PLACEHOLDER,  # DEPRECATED
    MP3_PRESET_CUSTOM_PREFIX,
    MP3_PRESET_CUSTOM_KEY,
    TEMP_CHIMES_PATH_KEY,
    LOCAL_PATH_KEY,
    AUDIO_DURATION_KEY,
)
from .media_player import MediaPlayerHelper
media_player_helper = MediaPlayerHelper()

_LOGGER = logging.getLogger(__name__)

class FilesystemHelper:
    """Filesystem helper functions for Chime TTS."""

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
                file_hash = self.get_hash_for_string(chime_path)
                return {
                    "audio_dict": audio_dict,
                    "file_hash": file_hash
                }

            _LOGGER.warning(" Unable to downloaded chime %s", chime_path)
            return None

        chime_path = self.validate_path(hass, chime_path)
        return chime_path

    def get_downloaded_chime_path(self, folder: str, url: str):
        """Local file path string for chime URL in local folder."""
        return folder + ("" if folder.endswith("/") else "/") + re.sub(r'[\/:*?"<>|]', '_', url.replace("https://", "").replace("http://", ""))

    def save_audio_to_folder(self, audio, folder, file_name: str = None):
        """Save audio to local folder."""

        folder_exists = self.create_folder(folder)
        if folder_exists is False:
            _LOGGER.warning("Unable to create folder: %s", folder)
            return None

        # Save to file
        if file_name is None:
            try:
                with tempfile.NamedTemporaryFile(
                    prefix=folder, suffix=".mp3"
                ) as temp_obj:
                    audio_full_path = temp_obj.name
                audio.export(audio_full_path, format="mp3")
            except Exception as error:
                _LOGGER.warning(
                    "An error occurred when creating the temp mp3 file: %s", error
                )
                return None
        else:
            try:
                # Make file name safe
                audio_full_path = self.get_downloaded_chime_path(url=file_name, folder=folder)
                if audio_full_path and isinstance(audio_full_path, str):
                    if os.path.exists(audio_full_path):
                        os.remove(audio_full_path)
                    audio.export(audio_full_path, format="mp3")
            except Exception as error:
                _LOGGER.warning(
                    "An error occurred when creating the mp3 file: %s", error
                )
                return None

        if os.path.exists(audio_full_path):
            _LOGGER.debug(" - File saved to path: %s", audio_full_path)
        else:
            _LOGGER.error("Saved file inaccessible, something went wrong. Path = %s", audio_full_path)

        return audio_full_path

    async def async_download_file(self, hass: HomeAssistant, url, folder):
        """Download a file and save locally."""
        try:
            _LOGGER.debug("Downloading chime at URL: %s", url)
            response = await hass.async_add_executor_job(requests.get, url)
            response.raise_for_status() # Raise an HTTPError for bad responses (4xx and 5xx status codes)
        except requests.exceptions.HTTPError as errh:
            _LOGGER.warning(" HTTP Error: %s", str(errh))
            return None
        except requests.exceptions.ConnectionError as errc:
            _LOGGER.warning(" Error Connecting: %s", str(errc))
            return None
        except requests.exceptions.Timeout as errt:
            _LOGGER.warning(" Timeout Error: %s", str(errt))
            return None
        except requests.exceptions.RequestException as err:
            _LOGGER.warning(" Request Exception: %s", str(err))
            return None
        except Exception as error:
            _LOGGER.warning(" An unexpected error occurred: %s", str(error))
            return None

        if response is None:
            _LOGGER.warning(" Received an invalid response")
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
                    LOCAL_PATH_KEY: audio_file_path,
                    AUDIO_DURATION_KEY: audio_duration
                }
        else:
            _LOGGER.warning(" Unable to extract audio from URL with content-type '%s'",
                            str(content_type))
        return None

    def create_folder(self, folder):
        """Create folder if it doesn't already exist."""
        if os.path.exists(folder) is False:
            _LOGGER.debug("  - Creating audio folder: %s", folder)
            try:
                os.makedirs(folder)
                return True
            except OSError as error:
                _LOGGER.warning(
                    "An OSError occurred while creating the folder '%s': %s",
                    folder, error)
            except Exception as error:
                _LOGGER.warning(
                    "An error occurred while creating the folder '%s': %s",
                    folder, error)
            return False
        return True

    def copy_file(self, source_file, destination_folder):
        """Copy a file to a folder."""
        if self.create_folder(destination_folder):
            try:
                copied_file_path = shutil.copy(source_file, destination_folder)
                return copied_file_path
            except FileNotFoundError:
                _LOGGER.warning("Unable to copy file: Source file not found.")
            except PermissionError:
                _LOGGER.warning("Unable to copy file: Permission denied. Check if you have sufficient permissions.")
            except Exception as e:
                if str(e).find("are the same file") != -1:
                    return source_file
                _LOGGER.warning(f"Unable to copy file: An error occurred: {e}")
        return None

    def file_exists_in_directory(self, file_path, directory):
        """Determine whether a file path exists within a given directory."""
        for root, _, files in os.walk(directory):
            for filename in files:
                if os.path.join(root, filename) == file_path:
                    return True
        return False

    def create_url_path(self, hass: HomeAssistant, file_path):
        """Convert public path to external URL or local path to media-source."""
        if file_path is None:
            return None

        # Return local path if file not in www folder
        public_dir = hass.config.path('www')
        if public_dir is None:
            _LOGGER.warning("Unable to locate public 'www' folder. Please check that the folder: /config/www exists.")
            return None

        if self.file_exists_in_directory(file_path, public_dir) is False:
            _LOGGER.warning(f"Unable to create public URL - File: '{file_path}' is outside the public folder.")
            return None

        instance_url = hass.config.external_url
        if instance_url is None:
            instance_url = str(get_url(hass))

        return (
            (instance_url + "/" + file_path)
            .replace(instance_url + "//", instance_url + "/")
            .replace("/config", "")
            .replace("www/", "local/")
        )

    def delete_file(self, file_path):
        """Safely delete a file."""
        if os.path.exists(file_path):
            os.remove(file_path)

    def get_hash_for_string(self, string):
        """Generate a has for a given string."""
        hash_object = hashlib.sha256()
        hash_object.update(string.encode("utf-8"))
        hash_value = str(hash_object.hexdigest())
        return hash_value
