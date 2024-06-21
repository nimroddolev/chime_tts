"""Filesystem helper functions for Chime TTS."""

import logging
import tempfile
import os
import hashlib
import shutil
from io import BytesIO
import re
import requests
import asyncio
from pydub import AudioSegment
from homeassistant.helpers.network import get_url
from homeassistant.core import HomeAssistant
from ..const import (
    MP3_PRESET_PATH,
    DEFAULT_CHIME_OPTIONS,
    MP3_PRESET_PATH_PLACEHOLDER,  # DEPRECATED
    MP3_PRESET_CUSTOM_PREFIX,
    MP3_PRESET_CUSTOM_KEY,
    TEMP_CHIMES_PATH_KEY,
    LOCAL_PATH_KEY,
    AUDIO_DURATION_KEY,
)
from .media_player_helper import MediaPlayerHelper
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

    def path_to_parent_folder(self, folder):
        """Absolute path to a parent folder."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        count = 0
        while os.path.basename(current_dir) != folder and count < 100:
            parent_dir = os.path.dirname(current_dir)
            if parent_dir == current_dir:
                _LOGGER.warning("%s folder not found", folder)
                return None
            current_dir = parent_dir
            count = count + 1
        return current_dir

    async def async_get_chime_path(self, chime_path, cache, data: dict, hass: HomeAssistant):
        """Retrieve preset chime path if selected."""
        custom_chime_paths_dict = data.get(MP3_PRESET_CUSTOM_KEY, {})
        temp_chimes_path = data.get(TEMP_CHIMES_PATH_KEY, "")
        # Remove prefix (prefix deprecated in v0.9.1)
        chime_path = chime_path.replace(MP3_PRESET_PATH_PLACEHOLDER, "")

        # Preset chime mp3 path?
        for option in DEFAULT_CHIME_OPTIONS:
            if option.get("value") == chime_path:
                # Validate MP3 preset path before use
                mp3_path = MP3_PRESET_PATH
                absolute_custom_comopnents_dir = self.path_to_parent_folder('custom_components')
                if absolute_custom_comopnents_dir:
                    mp3_path = MP3_PRESET_PATH.replace("custom_components", absolute_custom_comopnents_dir)
                final_chime_path = mp3_path + chime_path + ".mp3"
                if os.path.exists(final_chime_path):
                    _LOGGER.debug("Local path to chime: %s", final_chime_path)
                    return final_chime_path

        # Custom chime mp3 path?
        if chime_path.startswith(MP3_PRESET_CUSTOM_PREFIX):
            index = chime_path.replace(MP3_PRESET_CUSTOM_PREFIX, "")
            chime_path = custom_chime_paths_dict.get(chime_path, "")
            if chime_path == "":
                _LOGGER.warning("MP3 file path missing for custom chime path `Custom #%s`", str(index))
                return None
            elif os.path.exists(chime_path):
                return chime_path
            else:
                _LOGGER.debug("Custom chime not found at path: %s", chime_path)
                return None

        # External URL?
        if chime_path.startswith("http://") or chime_path.startswith("https://"):
            # Use cached version?
            if cache is True:
                local_file = self.get_downloaded_chime_path(folder=temp_chimes_path, url=chime_path)
                if local_file is not None and os.path.exists(local_file):
                    _LOGGER.debug("Chime found in cache")
                    return local_file
                _LOGGER.debug("External chime not found in cache")

            # Download from URL
            audio_dict = await self.async_download_file(hass, chime_path, temp_chimes_path)
            if audio_dict is not None:
                _LOGGER.debug("Chime downloaded successfully")
                file_hash = self.get_hash_for_string(chime_path)
                return {
                    "audio_dict": audio_dict,
                    "file_hash": file_hash
                }

            _LOGGER.warning("Unable to downloaded chime from URL: %s", chime_path)
            return None

        chime_path = self.validate_path(hass, chime_path)
        return chime_path

    def get_downloaded_chime_path(self, folder: str, url: str):
        """Local file path string for chime URL in local folder."""
        return folder + ("" if folder.endswith("/") else "/") + re.sub(r'[\/:*?"<>|]', '_', url.replace("https://", "").replace("http://", ""))

    async def async_save_audio_to_folder(self, audio: AudioSegment, folder, file_name: str = None):
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
                await self.export_audio(audio, audio_full_path)
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
                    await self.export_audio(audio, audio_full_path)
            except Exception as error:
                _LOGGER.warning(
                    "An error occurred when creating the mp3 file: %s", error
                )
                return None

        if os.path.exists(audio_full_path):
            _LOGGER.debug("File saved to path: %s", audio_full_path)
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
            _LOGGER.warning("HTTP Error: %s", str(errh))
            return None
        except requests.exceptions.ConnectionError as errc:
            _LOGGER.warning("Error Connecting: %s", str(errc))
            return None
        except requests.exceptions.Timeout as errt:
            _LOGGER.warning("Timeout Error: %s", str(errt))
            return None
        except requests.exceptions.RequestException as err:
            _LOGGER.warning("Request Exception: %s", str(err))
            return None
        except Exception as error:
            _LOGGER.warning("An unexpected error occurred: %s", str(error))
            return None

        if response is None:
            _LOGGER.warning("Received an invalid response")
            return None

        content_type = response.headers.get('Content-Type', '')
        if 'audio' in content_type:
            _LOGGER.debug("Audio downloaded successfully")
            _, file_extension = os.path.splitext(url)
            try:
                audio_content = await self.async_load_audio(
                    BytesIO(response.content))#,
                    #format=file_extension.replace(".", ""))
            except Exception as error:
                _LOGGER.warning("Error when loading audio from downloaded file: %s", str(error))
                return None
            if audio_content is not None:
                audio_file_path = await self.async_save_audio_to_folder(audio=audio_content,
                                                            folder=folder,
                                                            file_name=url)
                audio_duration = float(len(audio_content) / 1000)
                return {
                    LOCAL_PATH_KEY: audio_file_path,
                    AUDIO_DURATION_KEY: audio_duration
                }
            else:
                _LOGGER.warning("Downloaded file did not contain audio: %s", url)
        else:
            _LOGGER.warning("Unable to extract audio from URL with content-type '%s'",
                            str(content_type))
        return None

    def create_folder(self, folder):
        """Create folder if it doesn't already exist."""
        if os.path.exists(folder) is False:
            _LOGGER.debug("Creating audio folder: %s", folder)
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

    def get_external_url(self, hass: HomeAssistant, file_path):
        """Convert local public path to external URL or local path to media-source."""
        if file_path is None:
            return None

        # Return local path if file not in www folder
        public_dir = hass.config.path('www')
        if public_dir is None:
            _LOGGER.warning("Unable to locate public 'www' folder. Please check that the folder: /config/www exists.")
            return None

        if self.file_exists_in_directory(file_path, public_dir) is False:
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

    def get_local_path(self, hass: HomeAssistant, file_path):
        """Convert external URL to local public path."""
        instance_url = hass.config.external_url
        if instance_url is None:
            instance_url = str(get_url(hass))
        public_dir = hass.config.path('www')
        return file_path.replace(instance_url, public_dir).replace('/www/local/', '/www/')

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

    def make_folder_path_safe(self, path):
        """Validate folder path."""
        if not path:
            return None
        if not f"{path}".startswith("/"):
            path = f"/{path}"
        if not f"{path}".endswith("/"):
            path = f"{path}/"
        path = path.replace("//", "/")
        return path

    ### Offloading to asyncio.to_thread ####

    async def export_audio(self, audio: AudioSegment, audio_full_path: str):
        """Save AudioSegment to a filepath."""
        await asyncio.to_thread(audio.export, audio_full_path, format="mp3")

    async def async_load_audio(self, file_path: str):
        """Load AudioSegment from a filepath."""
        return await asyncio.to_thread(AudioSegment.from_file, file_path)

    def get_chime_options_from_path(self, directory):
        """Walk through a directory of chime audio files and return a formatted dictionary."""
        chime_options = []
        audio_extensions = ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.aiff', '.aif', '.ape']

        if directory and os.path.exists(directory):
            for dirpath, _, filenames in os.walk(directory):
                for filename in filenames:
                    # Construct the absolute file path
                    file_path = os.path.join(dirpath, filename)
                    absolute_file_path = os.path.abspath(file_path)

                    # Separte the file extension from the label
                    label = os.path.splitext(filename)[0]
                    ext = os.path.splitext(filename)[1]
                    if ext in audio_extensions:
                        # Append the dictionary to the list
                        chime_options.append({"label": label, "value": absolute_file_path})
        return chime_options
