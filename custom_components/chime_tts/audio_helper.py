"""Audio helper functions for Chime TTS"""

import subprocess
import shutil
import logging

_LOGGER = logging.getLogger(__name__)


class ChimeTTSFAudioHelper():
    """Audio helper functions for Chime TTS"""

    def ffmpeg_convert_from_file(file_path, ffmpeg_args):
        """Convert audio stream with FFmpeg and provided arguments."""
        try:
            converted_file_path = file_path.replace(".mp3", "_converted.mp3")
            ffmpeg_cmd = [
                'ffmpeg',
                '-i', file_path,
                *ffmpeg_args.split(),
                converted_file_path
            ]
            ffmpeg_process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            converted_file, error_output = ffmpeg_process.communicate()

            if ffmpeg_process.returncode != 0:
                error_message = error_output.decode('utf-8')
                raise subprocess.CalledProcessError(ffmpeg_process.returncode, ' '.join(ffmpeg_cmd), output=converted_file_path, stderr=error_message)

            # Replace original file
            try:
                shutil.move(converted_file_path, file_path)
            except Exception as error:
                _LOGGER.debug("Error replacing file %s with %s: %s", file_path, converted_file_path, error)

            return converted_file_path

        except subprocess.CalledProcessError as error:
            _LOGGER.error("Error during FFmpeg conversion subprocess: %s", error)

        except Exception as error:
            _LOGGER.error("Unexpected error during FFmpeg conversion: %s", error)

        return file_path

