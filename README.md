# Chime TTS

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
![version](https://img.shields.io/github/v/release/nimroddolev/chime_tts)
[![Community Forum][forum-shield]][forum]

<img src="https://raw.githubusercontent.com/nimroddolev/chime_tts/main/icon.png" width=80>

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

* **Speaker Groups:** Supported speakers can be grouped together for simultaneous playback.


# Quick start

## Step 1. Installation

### Via HACS (Recommended)

1. Make sure [HACS](https://hacs.xyz/) is installed.
2. Add the Chime TTS repository to HACS: <a href="https://my.home-assistant.io/redirect/hacs_repository/?owner=nimroddolev&repository=chime_tts&category=integration" title="Chime TTS HACS repository"><div class="badge"><img loading="lazy" src="https://my.home-assistant.io/badges/hacs_repository.svg"></div></a>
3. Click `ADD` and then `DOWNLOAD`
4. Restart Home Assistant.

Or:

### Manual Installation

1. Using your file browser of choice open the directory for your HA configuration (where you find configuration.yaml).
2. Create a ```custom_components``` directory if it does not already exist.
3. Add a subdirectory inside ```custom_components``` named ```chime_tts```.
4. Download all the files from the ```custom_components/chime_tts/``` directory in this repository.
5. Place them into the new ```custom_components/chime_tts``` directory you created.
6. Restart Home Assistant.

## Step 2. Add the integration

Click this button <a href="https://my.home-assistant.io/redirect/config_flow_start/?domain=chime_tts" rel="nofollow"><img src="https://camo.githubusercontent.com/637fd24a458765d763a6dced4b312c503f54397bdd9b683584ef8054f305cd7f/68747470733a2f2f6d792e686f6d652d617373697374616e742e696f2f6261646765732f636f6e6669675f666c6f775f73746172742e737667" alt="Open your Home Assistant instance and start setting up a new integration." data-canonical-src="https://my.home-assistant.io/badges/config_flow_start.svg" style="max-width: 100%;"></a> to add the interation.

# Services

## chime_tts.say

The `chime_tts.say` service can play to multiple `media_player` targets and supports the following parameters:

| Name                   | YAML Key             | Required? | Description                                                                                                                                                          | Default |
| ---------------------- | -------------------- | --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| Chime Path             | `chime_path`         |           | Either an audio preset or a local audio file path to be played **before** the TTS message.                                                                           | None    |
| End Chime Path         | `end_chime_path`     |           | Either an audio preset or a local audio file path to be played **after** the TTS message.                                                                            | None    |
| Delay                  | `delay`              |           | Delay (ms) between chime audio and the TTS message.                                                                                                                  | 450ms   |
| Final Delay            | `final_delay`        |           | Final delay (ms) added after playback (useful for queued calls).                                                                                                                   | 0ms   |
| Message                | `message`            | Required  | The text to be converted into TTS audio.                                                                                                                             | None    |
| TTS Platform           | `tts_platform`       | Required  | TTS platform to be used to create TTS audio. **Note:** the [TTS platforms](https://www.home-assistant.io/integrations/#text-to-speech) must be installed separately. | None    |
| TTS Playback Speed     | `tts_playback_speed` |           | The desired playback speed for the TTS audio, anywhere from 100% - 200%.                                                                                             | 100     |
| Volume Level           | `volume_level`       |           | The volume level (between 0.0 - 1.0) to play the audio. The original value will be restored after playback.                                                          | 1.0     |
| Join Players           | `join_players`       |           | Play the audio simultaneously on media_players (that support speaker groups).                                                                          | False   |
| Cache                  | `cache`              |           | Save generated audio to the cache for reuse in future service calls.                                                                                                 | False   |
| Announce               | `announce`           |           | Stops current media during the announcement and then resume (on supported devices).                                                                                                | False   |

#### Additional parameters (not supported by all TTS platforms)
| Name     | Parameter  | Required? | Description                | Supported TTS Platforms                                                                                                                       | Default |
| -------- | ---------- | --------- | -------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| Language | `language` |           | The speech language to use | [Google Translate](https://www.home-assistant.io/integrations/google_translate/), [Nabu Casa Cloud TTS](https://www.nabucasa.com/config/tts/) | None    |
| TLD      | `tld`      |           | The dialect domain         | [Google Translate](https://www.home-assistant.io/integrations/google_translate/)                                                              | None    |
| Gender   | `gender`   |           | Use a male or female voice | [Nabu Casa Cloud TTS](https://www.nabucasa.com/config/tts/)                                                                                   | None    |


### Example

```
service: chime_tts.say
data:
  chime_path: custom_components/chime_tts/mp3s/tada.mp3
  message: The washing's done!
  tts_platform: google_translate
  tts_playback_speed: 120
  volume_level: 0.7
  cache: true
  announce: true
  language: en
  tld: com.au
target:
  entity_id:
    - media_player.homepod_mini
    - media_player.kitchen
```

## chime_tts.clear_cache

The `chime_tts.clear_cache` service removes all genenrated audio cache files & referennces to cached TTS audio.

```
service: chime_tts.clear_cache
```

# Show your support 👍

<a href="https://www.buymeacoffee.com/nimroddolev" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 40px !important;width: 140px !important;" ></a>

[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=popout
[forum]: https://community.home-assistant.io/t/chime-tts-play-audio-before-after-tts-audio-lag-free/578430
