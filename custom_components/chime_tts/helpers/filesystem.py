"""Filesystem helper functions for Chime TTS."""

import logging
import secrets
import os
import hashlib
import shutil
from io import BytesIO
import re
import asyncio
from asyncio import create_subprocess_exec
from asyncio.subprocess import PIPE
from concurrent.futures import ThreadPoolExecutor
from pydub import AudioSegment
import requests

from homeassistant.helpers.network import get_url
from homeassistant.core import HomeAssistant
from ..const import (
    MP3_PRESET_PATH,
    DEFAULT_CHIME_OPTIONS,
    MP3_PRESET_PATH_PLACEHOLDER,  # DEPRECATED
    MP3_PRESET_CUSTOM_PREFIX,
    MP3_PRESET_CUSTOM_KEY,
    CUSTOM_CHIMES_PATH_KEY,
    TEMP_CHIMES_PATH_KEY,
    LOCAL_PATH_KEY,
    AUDIO_DURATION_KEY,
)
from .media_player_helper import MediaPlayerHelper
media_player_helper = MediaPlayerHelper()

_LOGGER = logging.getLogger(__name__)
_AUDIO_EXTENSIONS = ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.aiff', '.aif', '.ape']

class FilesystemHelper:
    """Filesystem helper functions for Chime TTS."""

    def filepath_exists_locally(self, hass: HomeAssistant, filepath):
        """Test whether a local filepath or extenral URL exists locally."""
        local_path = self.get_local_path(hass, filepath)
        return local_path and os.path.isfile(local_path)

    def path_exists(self, path):
        """Test whether filepath/folderpath exists."""
        if not path or len(path) == 0:
            return False
        if os.path.exists(path):
            return True
        # Check if folder path not found due to incorrect letter case
        parent_directory = os.path.dirname(path) or "."
        target_name = os.path.basename(path).lower()
        if not target_name or len(target_name) == 0:
            return False
        # List of all items in parent directory
        try:
            dir_contents = os.listdir(parent_directory)
        except FileNotFoundError:
            return False
        except PermissionError:
            _LOGGER.warning(f"Error: No permission to access '{parent_directory}'.")
            return False

        # Case-insensitive search for folder/file
        for item in dir_contents:
            if item.lower() == target_name:
                full_path = os.path.join(parent_directory, item)
                if os.path.isdir(full_path):
                    return True
                elif os.path.isfile(full_path):
                    return True
        return False

    async def async_validate_path(self, hass: HomeAssistant, p_filepath: str = ""):
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
            if await hass.async_add_executor_job(self.path_exists, filepath) is True:
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

    async def async_get_chime_path(self, chime_path: str, cache, data: dict, hass: HomeAssistant):
        """Retrieve preset chime path if selected."""

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
                if await hass.async_add_executor_job(self.path_exists, final_chime_path):
                    _LOGGER.debug("Local path to chime: %s", final_chime_path)
                    return final_chime_path

        # Custom chime from chimes folder?
        custom_chimes_folder_options = await self.async_get_chime_options_from_path(data.get(CUSTOM_CHIMES_PATH_KEY, ""))
        for option_dict in custom_chimes_folder_options:
            p_chime_name = str(option_dict.get("label", "")).lower()
            p_chime_path = option_dict.get("value")
            chime_path_clean = chime_path.lower()
            for ext in _AUDIO_EXTENSIONS:
                chime_path_clean = chime_path_clean.replace(ext, "")
            if (p_chime_name and p_chime_path and chime_path_clean == p_chime_name):
                return option_dict.get("value")

        # Custom chime mp3 path? DEPRECATED since v1.1.0
        if chime_path.startswith(MP3_PRESET_CUSTOM_PREFIX):
            custom_chime_paths_dict = data.get(MP3_PRESET_CUSTOM_KEY, {})
            index = chime_path.replace(MP3_PRESET_CUSTOM_PREFIX, "")
            chime_path = custom_chime_paths_dict.get(chime_path, "")
            if chime_path == "":
                _LOGGER.warning("MP3 file path missing for custom chime path `Custom #%s`", str(index))
                return None
            elif await hass.async_add_executor_job(self.path_exists, chime_path):
                return chime_path
            else:
                _LOGGER.debug("Custom chime not found at path: %s", chime_path)
                return None

        # External URL?
        if chime_path.startswith("http://") or chime_path.startswith("https://"):
            temp_chimes_path = data.get(TEMP_CHIMES_PATH_KEY, "")
            # Use cached version?
            if cache is True:
                local_file = self.get_downloaded_chime_path(folder=temp_chimes_path, url=chime_path)
                if local_file is not None and await hass.async_add_executor_job(self.path_exists, local_file):
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

        chime_path = await self.async_validate_path(hass, chime_path)
        return chime_path

    def get_downloaded_chime_path(self, folder: str, url: str):
        """Local file path string for chime URL in local folder."""
        return folder + ("" if folder.endswith("/") else "/") + re.sub(r'[\/:*?"<>|]', '_', url.replace("https://", "").replace("http://", ""))

    async def async_save_audio_to_folder(self, hass: HomeAssistant, audio: AudioSegment, folder, file_name: str = None):
        """Save audio to local folder."""

        folder_exists = await self.async_create_folder(hass, folder)
        if folder_exists is False:
            _LOGGER.warning("Unable to create folder: %s", folder)
            return None

        # Save to file
        if file_name is None:
            try:
                # Generate a secure & unique file name
                secure_name = f"{secrets.token_hex(16)}.mp3"
                audio_full_path = os.path.join(folder, secure_name)

                # Ensure the directory exists
                os.makedirs(folder, exist_ok=True)

                # Export the audio to the secure file path
                await self.async_export_audio(audio, audio_full_path)
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
                    if await hass.async_add_executor_job(self.path_exists, audio_full_path):
                        os.remove(audio_full_path)
                    await self.async_export_audio(audio, audio_full_path)
            except Exception as error:
                _LOGGER.warning(
                    "An error occurred when creating the mp3 file: %s", error
                )
                return None

        if await hass.async_add_executor_job(self.path_exists, audio_full_path):
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
                audio_file_path = await self.async_save_audio_to_folder(hass=hass,
                                                                        audio=audio_content,
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

    async def async_create_folder(self, hass: HomeAssistant, folder):
        """Create folder if it doesn't already exist."""
        if await hass.async_add_executor_job(self.path_exists, folder) is False:
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

    async def async_copy_file(self, hass: HomeAssistant, source_file: str, destination_folder: str):
        """Copy a file to a folder."""
        if not destination_folder:
            _LOGGER.warning("Unable to copy file: No destination folder path provided")
            return None
        if await self.async_create_folder(hass, destination_folder):
            try:
                copied_file_path = shutil.copy(source_file, destination_folder)
                return copied_file_path
            except FileNotFoundError:
                _LOGGER.warning("Unable to copy file: Source file %s not found.", source_file)
            except PermissionError:
                _LOGGER.warning("Unable to copy file: Permission denied. Check if you have sufficient permissions.")
            except Exception as e:
                if str(e).find("are the same file") != -1:
                    return source_file
                _LOGGER.warning("Unable to copy file: An error occurred: %s", str(e))
        return None

    async def async_file_exists_in_directory(self, file_path, directory):
        """Determine whether a file path exists within a given directory asynchronously."""
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(
                pool,
                self._file_exists_in_directory,
                file_path,
                directory)

    def _file_exists_in_directory(self, file_path, directory):
        """Determine whether a file path exists within a given directory."""
        for root, _, files in os.walk(directory):
            for filename in files:
                if os.path.join(root, filename).lower() == file_path.lower():
                    return True
        return False

    def get_external_address(self, hass: HomeAssistant):
        """External address of the Home Assistant instance."""
        instance_url = hass.config.external_url
        if instance_url is None:
            instance_url = str(get_url(hass, prefer_external=True))
        if instance_url and instance_url.endswith("/"):
            instance_url = instance_url[:-1]
        return instance_url

    async def async_get_external_url(self, hass: HomeAssistant, file_path: str):
        """Convert file system path of public file to external URL."""
        if file_path is None:
            return None

        # File is already external URL
        if file_path.lower().startswith(self.get_external_address(hass).lower()):
            return file_path

        # Return local path if file not in www folder
        public_dir = hass.config.path('www')
        if public_dir is None:
            _LOGGER.warning("Unable to locate public 'www' folder. Please check that the folder: /config/www exists.")
            return None

        if await self.async_file_exists_in_directory(file_path, public_dir) is False:
            return None

        instance_url = self.get_external_address(hass)

        return (
            (instance_url + "/" + file_path)
            .replace("/config", "")
            .replace("www/", "local/")
            .replace(instance_url + "//", instance_url + "/")
        )


    async def async_is_audio_alexa_compatible(self, hass: HomeAssistant, file_path: str) -> bool:
        """Determine whether a given audio file is Alexa Media Player compatible.

        Args:
            hass: HomeAssistant object
            file_path: Path to the audio file to check

        Returns:
            bool: True if file meets Alexa compatibility requirements, False otherwise

        """
        try:
            # Validate file path
            file_path = self.get_local_path(hass=hass, file_path=file_path)
            if not (os.path.isfile(file_path) and await hass.async_add_executor_job(self.path_exists, file_path)):
                _LOGGER.debug("Unable to convert audio. File not found: %s", file_path)
                return False

            try:
                # Create and run async subprocess
                process = await create_subprocess_exec(
                    'ffmpeg', '-i', file_path,
                    stdout=PIPE,
                    stderr=PIPE
                )

                try:
                    # Wait for the process to complete with timeout
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(),
                        timeout=30.0  # 30 second timeout
                    )

                    # Convert bytes to string and combine outputs for checking
                    try:
                        output = (stderr.decode('utf-8', errors='replace').lower() if stderr else '') + \
                                (stdout.decode('utf-8', errors='replace').lower() if stdout else '')

                        # More robust pattern matching
                        requirements = [
                            'mp3' in output,
                            any(rate in output for rate in ['24000 hz', '24khz', '24000hz']),
                            any(ch in output for ch in ['stereo', '2 channels', '2ch']),
                            any(rate in output for rate in ['48 kb/s', '48k', '48000']),
                            'xing' not in output  # Check for absence of Xing header
                        ]

                        # File failed Alexa Media Player compatibility test
                        if not all(requirements):
                            _LOGGER.debug("File is not Alexa Media Player compatibile: %s", file_path)
                            return False

                        return True

                    except UnicodeDecodeError as decode_error:
                        _LOGGER.error("Failed to decode FFmpeg output: %s", decode_error)
                        return False

                except asyncio.TimeoutError:
                    _LOGGER.error("FFmpeg process timed out while analyzing: %s", file_path)
                    # Ensure we clean up the process
                    try:
                        process.kill()
                        await process.wait()
                    except ProcessLookupError:
                        pass
                    return False

            except FileNotFoundError:
                _LOGGER.error("FFmpeg executable not found. Please ensure FFmpeg is installed")
                return False
            except PermissionError:
                _LOGGER.error("Permission denied when trying to execute FFmpeg")
                return False
            except asyncio.CancelledError:
                _LOGGER.debug("Audio analysis cancelled for: %s", file_path)
                raise  # Re-raise CancelledError to properly handle task cancellation
            except Exception as subprocess_error:
                _LOGGER.error("Subprocess error during FFmpeg execution: %s", subprocess_error)
                return False

        except OSError as os_error:
            _LOGGER.error("OS error while processing file %s: %s", file_path, os_error)
            return False
        except Exception as general_error:
            _LOGGER.error("Unexpected error while checking audio compatibility: %s", general_error)
            return False


    def delete_file(self, hass: HomeAssistant, file_path) -> None:
        """Delete local / public-facing file in filesystem."""
        if file_path is None:
            return

        # Convert external URL to local filepath
        instance_url = self.get_external_address(hass)
        if f"{file_path}".startswith(instance_url):
            file_path = (
                file_path
                .replace(f"{instance_url}/", "")
                .replace(f"{instance_url}", "")
                .replace("local/", "/config/www/")
                .replace("//", "/")
            )

        # If file exists, delete it
        if self.path_exists(file_path):
            _LOGGER.debug("Deleting file %s", file_path)
            os.remove(file_path)
        else:
            _LOGGER.warning("No file at path %s - unable to delete", file_path)

    def get_local_path(self, hass: HomeAssistant, file_path: str = ""):
        """Convert external URL to local public path."""
        file_path = f"{file_path}"
        if not file_path:
            _LOGGER.debug("get_local_path(): No file_path provided")
            return None
        if file_path.startswith("/"):
            return file_path

        instance_url = self.get_external_address(hass)
        if not instance_url:
            _LOGGER.error("Failed to determine the instance URL.")
            return file_path

        instance_url = f"{instance_url}"
        if instance_url.endswith("/"):
            instance_url = instance_url[:-1]
        public_dir = hass.config.path('www')

        local_file_path = file_path.replace(instance_url, public_dir).replace('/www/local/', '/www/')
        if self.path_exists(local_file_path) and os.path.isfile(local_file_path):
            if local_file_path != file_path:
                _LOGGER.debug("Local file path for external URL is '%s'", local_file_path)
            return local_file_path
        return None

    def get_hash_for_string(self, string):
        """Generate a has for a given string."""
        hash_object = hashlib.sha256()
        hash_object.update(string.encode("utf-8"))
        hash_value = str(hash_object.hexdigest())
        return hash_value

    def make_folder_path_safe(self, path):
        """Validate folder path."""
        if not path:
            return ""
        if not f"{path}".startswith("/"):
            path = f"/{path}"
        if not f"{path}".endswith("/"):
            path = f"{path}/"
        path = path.replace("//", "/").strip()
        return path

    ### Offloading to asyncio.to_thread ####

    async def async_export_audio(self, audio: AudioSegment, audio_full_path: str):
        """Save AudioSegment to a filepath."""
        await asyncio.to_thread(audio.export, audio_full_path, format="mp3")

    async def async_load_audio(self, file_path: str):
        """Load AudioSegment from a filepath."""
        return await asyncio.to_thread(AudioSegment.from_file, file_path)

    async def async_get_chime_options_from_path(self, directory):
        """Walk through a directory of chime audio files and return a formatted dictionary."""
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(
                pool,
                self._get_chime_options_from_path,
                directory)

    def _get_chime_options_from_path(self, directory):
        """Walk through a directory of chime audio files and return a formatted dictionary."""
        chime_options = []

        if directory and self.path_exists(directory):
            for dirpath, _, filenames in os.walk(directory):
                for filename in filenames:
                    # Construct the absolute file path
                    file_path = os.path.join(dirpath, filename)
                    absolute_file_path = os.path.abspath(file_path)

                    # Separte the file extension from the label
                    label = os.path.splitext(filename)[0]
                    ext = os.path.splitext(filename)[1]
                    if ext in _AUDIO_EXTENSIONS:
                        # Append the dictionary to the list
                        chime_options.append({"label": label, "value": absolute_file_path})
        return chime_options
