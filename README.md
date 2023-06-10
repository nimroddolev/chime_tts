# Chime TTS

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
![version](https://img.shields.io/github/v/release/nimroddolev/chime_tts)
[![Community Forum][forum-shield]][forum]

Chime TTS is a custom integration for Home Assistant that combines audio files with Text-to-Speech (TTS) audio locally, creating seamless playback without any lag or timing issues caused by cloud TTS processing and networking delays - perfect for playing a notification sound with a TTS notification.

[Discussion on Home Assistant Community Forum](https://community.home-assistant.io/t/chime-tts-play-audio-before-after-tts-audio-lag-free/578430)


# Features

Chime TTS offers the following enhancements for TTS audio playback:

* **No lag or timing issues:** Cloud TTS processing and network delays are eliminated, ensuring precise timing between audio files.

* **Customizable audio cues:** Play preset audio options or your own custom files before and/or after the TTS message, creating a single file with seamless playback.

* **Flexible TTS platform selection:** Chime TTS supports [TTS platform integrations in Home Assistant](https://www.home-assistant.io/integrations/#text-to-speech).

* **Easy service invocation:** The Chime TTS service can be used in automations, scripts, and other Home Assistant components.

* **Set media player notification volume:** Set the volume of the media player for the notification, and restore it back once completed.

* **Configurable delay:** Set a custom delay period between audio files and TTS audio.


# Quick start

## Installation

It is recommended to use the [HACS Home Assistant Community Store](https://hacs.xyz/) to install Chime TTS:
1. Once HACS is installed, click on `HACS` -> select `Integrations` -> ⋮ -> `Custom repositories`.
2. Enter `https://github.com/nimroddolev/chime_tts` as the `Repository` -> select "Integration" from the `Category` menu -> select `ADD`.
3. Select `EXPLORE & DOWNLOAD REPOSITORIES` -> search for *Chime TTS* -> Select it -> Select `Download` to install.
4. Restart Home Assistant

## Adding the integration

Chime TTS uses Home Assistant's [tts_get_url](https://www.home-assistant.io/integrations/tts/#post-apitts_get_url) API in order to generate and locate TTS audio files. Use of the API requires a long-lived token.
1. Navigate to your profile (found at the bottom of Home Assistant's left-hand-side navigation bar).
2. Make sure `Advanced Mode` is enabled
3. Scroll to the bottom and select `CREATE TOKEN` under the 'Long-Lived Access Tokens' section.
4. Enter a name (eg: *Chime TTS*) and copy the token string
5. Go to Home Assistant's `Settings` -> `Devices and Services` -> `Add Integration`, and type: *Chime TTS* (if it does not appear empty your browser cache and reload the page).
6. Paste in your token and click `Submit`.

# Configuration

The following service options are all optional:
| Option                 | Parameter            | Description                                                                                                                                                          | Default |
| ---------------------- | -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| Chime Path             | ```chime_path```     | The audio file to be played **before** the TTS message. You can use either a preset option or a local file path.                                                     | Bells   |
| End Chime Path         | ```end_chime_path``` | The audio file to be played **after** the TTS message. You can use either a preset option or a local file path.                                                      | None    |
| Delay                  | ```delay```          | Delay (ms) between chime audio and the TTS message                                                                                                                   | 450ms   |
| Message                | ```message```        | The text to be converted into TTS audio                                                                                                                              | None    |
| TTS Platform           | ```tts_platform```   | TTS platform to be used to create TTS audio. **Note:** the [TTS platforms](https://www.home-assistant.io/integrations/#text-to-speech) must be installed separately. | None    |
| Media Player Entity Id | ```media_player```   | The entity_id for the media player to play the audio                                                                                                                 | None    |
| Volume Level           | ```volume_level```   | The volume level (between 0.0 - 1.0) to play the audio. The original value will be restored after playback.                                                          | 1       |


# Calling Service from Home Assistant

## From the UI

<picture>
<source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/nimroddolev/chime_tts/main/images/call_service_from_ui-dark.png">
<source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/nimroddolev/chime_tts/main/images/call_service_from_ui-light.png">
<img alt="Screenshot of the parameters for the Chime TTS service in the UI" src="https://raw.githubusercontent.com/nimroddolev/chime_tts/main/images/call_service_from_ui-light">
</picture>

## From YAML
<picture>
<source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/nimroddolev/chime_tts/main/images/call_service_from_yaml-dark.png">
<source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/nimroddolev/chime_tts/main/images/call_service_from_yaml-light.png">
<img alt="Screenshot of the parameters for the Chime TTS service in YAML" src=https://raw.githubusercontent.com/nimroddolev/chime_tts/main/images/call_service_from_yaml-light.png">
</picture>


# Show your support 👍

<a href="https://www.buymeacoffee.com/nimroddolev" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 40px !important;width: 140px !important;" ></a>

[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=popout
[forum]: https://community.home-assistant.io/t/chime-tts-play-audio-before-after-tts-audio-lag-free/578430