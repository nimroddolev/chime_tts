![Chime TTS](https://raw.githubusercontent.com/nimroddolev/chime_tts/main/icon.png)

[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg)](https://github.com/hacs/integration)
![version](https://img.shields.io/github/v/release/nimroddolev/chime_tts)
[![Community Forum][forum-shield]][forum]
[![Buy me a coffee](https://img.shields.io/badge/Buy%20me%20a%20coffee-FFDD00?logo=buymeacoffee&logoColor=black)](https://www.buymeacoffee.com/nimroddolev)

Chime TTS is a custom Home Assistant integration that combines TTS and audio files into one locally generated audio file, eliminating the gap caused by separate playback actions.

- [What is Chime TTS?](https://nimroddolev.github.io/chime_tts/docs/getting-started#what-is-chime-tts)
- [Features](https://nimroddolev.github.io/chime_tts/docs/getting-started#features)
- [Quick Start](https://nimroddolev.github.io/chime_tts/docs/quick-start/)
- [How Do I Use It?](https://nimroddolev.github.io/chime_tts/docs/getting-started#how-do-i-use-it)
- [Support & Discussion](https://nimroddolev.github.io/chime_tts/docs/getting-started#support-and-discussion)

---

## What is Chime TTS?

Chime TTS is a custom Home Assistant integration that locally combines TTS audio and sound effects into seamless audio for playback in a single action call. It can add chimes before, after, or between speech segments without playback lag.

### The Problem:

<source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/nimroddolev/chime_tts/main/images/wiki/home/no_chime_tts-dark.png">
<source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/nimroddolev/chime_tts/main/images/wiki/home/no_chime_tts-light.png">
<img alt="Latency is introduced between the notification chime and the TTS audio" src="https://raw.githubusercontent.com/nimroddolev/chime_tts/main/images/wiki/home/no_chime_tts-dark.png">

Adding a notification chime before Text-To-Speech (TTS) audio messages requires separate action calls, which can introduce lag from cloud TTS generation, audio processing, and media-player playback.

### The Solution:

<source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/nimroddolev/chime_tts/main/images/wiki/home/with_chime_tts-dark.png">
<source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/nimroddolev/chime_tts/main/images/wiki/home/with_chime_tts-light.png">
<img alt="Chime TTS removes the latency between the notification chime and the TTS audio" src="https://raw.githubusercontent.com/nimroddolev/chime_tts/main/images/wiki/home/with_chime_tts-dark.png">

**Chime TTS** combines the audio into a single file on your Home Assistant device, then plays that file as one seamless event.

***

## Features

Chime TTS offers features that enhance TTS audio playback:

- **No lag or timing issues:** Precise timing between audio files without separate playback actions.
- **Customizable audio cues:** Play preset, custom, downloaded, or remote audio before, after, or between TTS segments.
- **Chime Sets:** Create reusable groups of chimes and choose a member at random for each announcement.
- **Flexible TTS platform selection:** Works with any [TTS platform](https://www.home-assistant.io/integrations/#text-to-speech) configured in Home Assistant.
- **Easy action invocation:** Use [`chime_tts.say`](https://nimroddolev.github.io/chime_tts/docs/documentation/actions/say-action) and [`chime_tts.say_url`](https://nimroddolev.github.io/chime_tts/docs/documentation/actions/say_url-action) actions in automations and scripts.
- **Player controls:** Set media-player volume and restore currently playing audio where supported.
- **Metadata and artwork:** Forward media-player metadata and artwork to standard players with the `extra` action field.
- **Mix and match TTS platforms:** Use multiple TTS platforms in one announcement.
- **Audio controls:** Configure speed, pitch, offsets, crossfades, delays, repeats, caching, FFmpeg conversion, and speaker groups where supported.
- **Sidebar panel:** Manage defaults, chimes, Chime Sets, notification profiles, and logs from Home Assistant.

***

## Quick Start

Follow these steps to get started with Chime TTS:

1. [Installation](https://nimroddolev.github.io/chime_tts/docs/quick-start/installing-chime-tts) - Install Chime TTS through HACS or manually.
2. [Add the Integration](https://nimroddolev.github.io/chime_tts/docs/quick-start/adding-the-integration) - Add Chime TTS to Home Assistant and make your first announcement.
3. [Additional Requirements](https://nimroddolev.github.io/chime_tts/docs/quick-start/additional-requirements) - Configure a TTS platform and any player-specific requirements.

After installation, open **Chime TTS** from the Home Assistant sidebar to configure defaults and manage chimes. The panel is also available from the integration page’s **Settings** button.

***

## How Do I Use It?

### Actions

Chime TTS adds four actions to Home Assistant:

- [`chime_tts.say`](https://nimroddolev.github.io/chime_tts/docs/documentation/actions/say-action) generates and plays audio and TTS messages on one or more media players.
- [`chime_tts.say_url`](https://nimroddolev.github.io/chime_tts/docs/documentation/actions/say_url-action) generates an audio file and returns a public URL or media-source identifier without playing it.
- [`chime_tts.replay`](https://nimroddolev.github.io/chime_tts/docs/documentation/actions/replay-action) repeats the most recent Chime TTS playback request.
- [`chime_tts.clear_cache`](https://nimroddolev.github.io/chime_tts/docs/documentation/actions/clear_cache-action) removes generated audio from the cache.

### Notify Entities

Chime TTS adds a [notify platform](https://www.home-assistant.io/integrations/notify/): [`chime_tts`](https://nimroddolev.github.io/chime_tts/docs/documentation/notify). Create reusable notification profiles in the sidebar panel or define them in YAML for use in automations and scripts.

***

## Configuration & Documentation

For configuration, examples, and complete documentation, visit the [official Chime TTS site](https://nimroddolev.github.io/chime_tts).

- [Configuration](https://nimroddolev.github.io/chime_tts/docs/documentation/configuration)
- [Chimes and uploads](https://nimroddolev.github.io/chime_tts/docs/documentation/chimes)
- [Action parameters and examples](https://nimroddolev.github.io/chime_tts/docs/documentation/actions)
- [Notification profiles](https://nimroddolev.github.io/chime_tts/docs/documentation/notify)

## Support and Discussion

For questions, suggestions, and community discussion about Chime TTS, visit the [Community Forum](https://community.home-assistant.io/t/chime-tts-play-audio-before-after-tts-audio-lag-free/578430), or [report an issue](https://github.com/nimroddolev/chime_tts/issues).

***

[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=popout
[forum]: https://community.home-assistant.io/t/chime-tts-play-audio-before-after-tts-audio-lag-free/
