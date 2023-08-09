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

* **Easy service invocation:** The Chime TTS 'say' service can be used in automations, scripts, and other Home Assistant components, and supports queuing multiple service calls.

* **Set media player notification volume:** Set the volume of the media player for the notification, and restore it back once playback ends.

* **Configurable TTS playback speed:** Set the desired playback speed of the TTS audio, anywhere from 100% - 200%.

* **Configurable delay:** Set a custom delay period between audio files and TTS audio.

* **Caching:** Audio created by Chime TTS can be cached for faster playback in future service calls.


# Quick start

## 1. Installation

### Via HACS (Recommended)

It is recommended to use the [HACS Home Assistant Community Store](https://hacs.xyz/) to install Chime TTS.

Either:

1. Once HACS is installed, add the Chime TTS repository to HACS: <a href="https://my.home-assistant.io/redirect/hacs_repository/?owner=nimroddolev&repository=chime_tts&category=integration" title="Chime TTS HACS repository"><div class="badge"><img loading="lazy" src="https://my.home-assistant.io/badges/hacs_repository.svg"></div></a></div>
2. Click `ADD` and then `DOWNLOAD`
3. Restart Home Assistant.

or

1. Once HACS is installed, click on `HACS` -> select `Integrations` -> ⋮ -> `Custom repositories`.
2. Enter `https://github.com/nimroddolev/chime_tts` as the `Repository` -> select "Integration" from the `Category` menu -> select `ADD`.
3. Select `EXPLORE & DOWNLOAD REPOSITORIES` -> search for *Chime TTS* -> Select it -> Select `Download` to install.
4. Restart Home Assistant.

### Manual Installation
1. Using your file browser of choice open the directory for your HA configuration (where you find configuration.yaml).
2. Create a ```custom_components``` directory if it does not already exist.
3. Add a subdirectory inside ```custom_components``` named ```chime_tts```.
4. Download all the files from the ```custom_components/chime_tts/``` directory in this repository.
5. Place them into the new ```custom_components/chime_tts``` directory you created.
6. Restart Home Assistant.

## 2. Adding the integration

Chime TTS uses Home Assistant's [tts_get_url](https://www.home-assistant.io/integrations/tts/#post-apitts_get_url) API to generate and locate TTS audio files. The API requires a long-lived token.
1. Navigate to your profile (found at the bottom of Home Assistant's left-hand-side navigation bar).
2. Make sure `Advanced Mode` is enabled
3. Scroll to the bottom and select `CREATE TOKEN` under the 'Long-Lived Access Tokens' section.
4. Enter a name (eg: *Chime TTS*) and copy the token string.
5. Navigate to: `Settings` -> `Devices and Services` -> `Add Integration`, and then type: *Chime TTS* (if it does not appear empty your browser cache and reload the page).
6. Paste in your token and then click `Submit`.

# Services

## chime_tts.say

The `chime_tts.say` service can play to multiple `media_player` targets and supports the following parameters:

| Name                   | YAML Key             | Required? | Description                                                                                                                                                          | Default |
| ---------------------- | -------------------- | --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| Chime Path             | `chime_path`         |           | Either an audio preset or a local audio file path to be played **before** the TTS message.                                                                           | None    |
| End Chime Path         | `end_chime_path`     |           | Either an audio preset or a local audio file path to be played **after** the TTS message.                                                                            | None    |
| Delay                  | `delay`              |           | Delay (ms) between chime audio and the TTS message                                                                                                                   | 450ms   |
| Final Delay            | `final_delay`        |           | Final delay (ms) added after playback (useful for queued calls)                                                                                                                    | 0ms   |
| Message                | `message`            | Required  | The text to be converted into TTS audio                                                                                                                              | None    |
| TTS Platform           | `tts_platform`       | Required  | TTS platform to be used to create TTS audio. **Note:** the [TTS platforms](https://www.home-assistant.io/integrations/#text-to-speech) must be installed separately. | None    |
| TTS Playback Speed     | `tts_playback_speed` |           | The desired playback speed for the TTS audio, anywhere from 100% - 200%                                                                                              | 100     |
| Volume Level           | `volume_level`       |           | The volume level (between 0.0 - 1.0) to play the audio. The original value will be restored after playback.                                                          | 1       |
| Cache                  | `cache`              |           | Save generated audio to the cache for reuse in future service calls.                                                                                                 | False   |

### Additional parameters (not supported by all TTS platforms)
| Name     | Parameter  | Required? | Description                | Supported TTS Platforms                                                                                                                       | Default |
| -------- | ---------- | --------- | -------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| Language | `language` |           | The speech language to use | [Google Translate](https://www.home-assistant.io/integrations/google_translate/), [Nabu Casa Cloud TTS](https://www.nabucasa.com/config/tts/) | None    |
| TLD      | `tld`      |           | The dialect domain         | [Google Translate](https://www.home-assistant.io/integrations/google_translate/)                                                              | None    |
| Gender   | `gender`   |           | Use a male or female voice | [Nabu Casa Cloud TTS](https://www.nabucasa.com/config/tts/)                                                                                   | None    |

### From the UI

<picture>
<source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/nimroddolev/chime_tts/main/images/call_service_from_ui-dark.png?v=4">
<source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/nimroddolev/chime_tts/main/images/call_service_from_ui-light.png?v=4">
<img alt="Screenshot of the parameters for the Chime TTS say service in the UI" src="https://raw.githubusercontent.com/nimroddolev/chime_tts/main/images/call_service_from_ui-light?v=4">
</picture>

### From YAML

```
service: chime_tts.say
data:
  message: The washing's done!
  tts_platform: google_translate
  cache: true
  language: en
  tld: com.au
  chime_path: custom_components/chime_tts/mp3s/tada.mp3
  tts_playback_speed: 120
  volume_level: 0.7
  announce: true
target:
  entity_id:
    - media_player.homepod_mini
```

## chime_tts.clear_cache

The `chime_tts.clear_cache` service removes all genenrated audio cache files & referennces to cached TTS audio.

### From the UI


<picture>
<source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/nimroddolev/chime_tts/main/images/call_service_clear_cache_from_ui-dark.png">
<source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/nimroddolev/chime_tts/main/images/call_service_clear_cache_from_ui-light.png">
<img alt="Screenshot of the parameters for the Chime TTS clear cache service in the UI" src="https://raw.githubusercontent.com/nimroddolev/chime_tts/main/images/call_service_clear_cache_from_ui-light.pnng">
</picture>

### From YAML

```
service: chime_tts.clear_cache
```

# Show your support 👍

<a href="https://www.buymeacoffee.com/nimroddolev" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 40px !important;width: 140px !important;" ></a>

[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=popout
[forum]: https://community.home-assistant.io/t/chime-tts-play-audio-before-after-tts-audio-lag-free/578430
