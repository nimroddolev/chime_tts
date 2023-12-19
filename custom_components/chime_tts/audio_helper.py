"""Audio helper functions for Chime TTS."""

import subprocess
import shutil
import logging

_LOGGER = logging.getLogger(__name__)


class ChimeTTSFAudioHelper:
    """Audio helper functions for Chime TTS."""

    def ffmpeg_convert_from_file(file_path, ffmpeg_args):
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


            ffmpeg_process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            converted_file, error_output = ffmpeg_process.communicate()

            if ffmpeg_process.returncode != 0:
                error_message = error_output.decode('utf-8')
                _LOGGER.error(f"{ffmpeg_process.returncode}, {' '.join(ffmpeg_cmd)}, output={converted_file_path}, stderr={error_message}")
                return False
                raise subprocess.CalledProcessError(ffmpeg_process.returncode, ' '.join(ffmpeg_cmd), output=converted_file_path, stderr=error_message)

            # Replace original with converted file
            if (converted_file_path == file_path.replace(".mp3", "_converted.mp3")):
                try:
                    shutil.move(converted_file_path, file_path)
                    return file_path
                except Exception as error:
                    _LOGGER.error("Error renaming file %s to %s. Error: %s. FFmpeg options: %s", file_path, converted_file_path, error, ffmpeg_cmd_string)
                    return False
                except Exception as error:
                    _LOGGER.warning("Error deleting original audio file %s. Error: %s. FFmpeg options: %s", file_path, error, ffmpeg_cmd_string)

            return converted_file_path

        except subprocess.CalledProcessError as error:
            _LOGGER.error("Error during FFmpeg conversion subprocess: %s FFmpeg options: %s", error, ffmpeg_cmd_string)

        except Exception as error:
            _LOGGER.error("Unexpected error during FFmpeg conversion: %s FFmpeg options: %s", error, ffmpeg_cmd_string)

        return file_path

