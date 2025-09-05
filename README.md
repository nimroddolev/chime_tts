![Chime TTS](https://raw.githubusercontent.com/nimroddolev/chime_tts/main/icon.png)

[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg)](https://github.com/hacs/integration)
![version](https://img.shields.io/github/v/release/nimroddolev/chime_tts)
[![Community Forum][forum-shield]][forum]
<a href="https://www.buymeacoffee.com/nimroddolev"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" height="0px"></a>

Chime TTS is a custom Home Assistant integration that eliminates the audio lag between playing a chime/notification sound effect before a TTS audio notification.

#### If you find Chime TTS useful, consider showing your support: <a href="https://www.buymeacoffee.com/nimroddolev" target="_blank"><img src="https://i.ibb.co/D1sqFY8/buy-me-a-coffee.png" alt="Buy Me A Coffee"></a>


- [What is Chime TTS?](https://nimroddolev.github.io/chime_tts/docs/getting-started#what-is-chime-tts)
- [Features](https://nimroddolev.github.io/chime_tts/docs/getting-started#features)
- [Quick Start](https://nimroddolev.github.io/chime_tts/docs/getting-started#quick-start)
- [How Do I Use It?](https://nimroddolev.github.io/chime_tts/docs/getting-started#how-do-i-use-it)
- [Support & Discussion](https://nimroddolev.github.io/chime_tts/docs/getting-started#support-and-discussion)

---

## What is Chime TTS?

Chime TTS is a custom Home Assistant integration that locally combines TTS audio and sound effects into seamless audio for playback in a single action call, eliminating the lag. Chime TTS includes a [suite of options](https://nimroddolev.github.io/chime_tts/docs/getting-started#features) to further customize the audio.

### The Problem:

<source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/nimroddolev/chime_tts/main/images/wiki/home/no_chime_tts-dark.png">
<source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/nimroddolev/chime_tts/main/images/wiki/home/no_chime_tts-light.png">
<img alt="Latency is introduced between the notification chime and the TTS audio" src="https://raw.githubusercontent.com/nimroddolev/chime_tts/main/images/wiki/home/no_chime_tts-dark.png">

Adding a notification chime before Text-To-Speech (TTS) audio messages requires two separate action calls, which introduces lag due to networking latency of cloud TTS platforms, audio processing, and delays before media_player playback begins.

### The Solution:

<source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/nimroddolev/chime_tts/main/images/wiki/home/wuth_chime_tts-dark.png">
<source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/nimroddolev/chime_tts/main/images/wiki/home/with_chime_tts-light.png">
<img alt="Chime TTS removes the latency between the notification chime and the TTS audio" src="https://raw.githubusercontent.com/nimroddolev/chime_tts/main/images/wiki/home/with_chime_tts-dark.png">

**Chime TTS** addresses this issue by combining the audio files into _a single file_ locally on your Home Assistant device. This combined file is then played through your speakers in one seamless event, eliminating any lag.

***

##  Features

Chime TTS offers various features that enhance TTS audio playback experience:

- **No lag or timing issues:** Precise timing between audio files without cloud TTS delays.
- **Customizable audio cues:** Play preset or custom audio before and after TTS messages.
- **Flexible TTS platform selection:** Supports various [TTS platform integrations](https://www.home-assistant.io/integrations/#text-to-speech).
-  **Easy action invocation:** Use the [`chime_tts.say`](https://nimroddolev.github.io/chime_tts/docs/documentation/actions/say-action/) and [`chime_tts.say_url`](https://nimroddolev.github.io/chime_tts/docs/documentation/actions/say_url-action/) actions in automations and scripts.
-  **Set media player  volume:** Notifications can be played at a defined volume and restored after playback.
- **Restore previous audio:** Chime TTS supports pausing and resuming currently playing audio beyond the media player platforms supported by Home Assistant *(eg: HomePods)*.
-  **Mix and match TTS platforms:** Combine TTS audio using multiple TTS platforms within the same audio announcement.
- **Configurable TTS speed:** Set the TTS audio speed anywhere from 1-500%.
- **Configurable TTS pitch:** Set the pitch for TTS audio, allowing for more customization.
- **Support for FFmpeg arguments:** Apply FFmpeg jobs to the generated audio, or specific jobs to specific chimes and TTS audio segments.
-  **Configurable delay:** Set custom delays between chimes & TTS audio.
-  **Configurable overlay:** Set custom overlay durations between chimes & TTS audio.
-  **Caching:** Cache audio for faster playback.
-  **Speaker Groups:** Group speakers for simultaneous playback *(on supported platforms)*.

***

## Quick Start

Follow these easy steps to get started with Chime TTS:

1. [Installation](https://nimroddolev.github.io/chime_tts/docs/quick-start/installing-chime-tts) - Quickly install Chime TTS via HACS or manually.
2. [Add the Integration](https://nimroddolev.github.io/chime_tts/docs/quick-start/adding-the-integration) - Add Chime TTS to your Home Assistant instance.

***

## How Do I Use It?

### Actions

Chime TTS adds 4 new actions to your Home Assistant instance: `chime_tts.say`, `chime_tts.say_url`, `chime_tts.replay` and `chime_tts.clear_cache`. Discover how you can use these actions and the features they offer:

- [`chime_tts.say`](https://nimroddolev.github.io/chime_tts/docs/documentation/actions/say-action/): Play audio and TTS messages with various settings.
- [`chime_tts.say_url`](https://nimroddolev.github.io/chime_tts/docs/documentation/actions/say_url-action/): Generates a publicly accessible URL to the MP3 file generated by `chime_tts.say`.
- [`chime_tts.replay`](https://nimroddolev.github.io/chime_tts/docs/documentation/actions/replay-action): Repeats the previous action call made to `chime_tts.say`.
- [`chime_tts.clear_cache`](https://nimroddolev.github.io/chime_tts/docs/documentation/actions/clear_cache-action): Clear generated audio cache.

### Notify Entities
Chime TTS adds a [notify platform](https://www.home-assistant.io/integrations/notify/): "[chime_tts](https://nimroddolev.github.io/chime_tts/docs/documentation/notify)", which allows you to create fully customised notify entries for use in your automations and scripts.

***

## Configuration & Documentation

For configuration, examples and documentation check out [the official Chime TTS site](https://nimroddolev.github.io/chime_tts).

## Support and Discussion

For questions, suggestions, and community discussion about Chime TTS, visit our [Community Forum](https://community.home-assistant.io/t/chime-tts-play-audio-before-after-tts-audio-lag-free/578430).

***

[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=popout
[forum]: https://community.home-assistant.io/t/chime-tts-play-audio-before-after-tts-audio-lag-free/578430
