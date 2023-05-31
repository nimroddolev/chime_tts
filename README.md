# Chime TTS
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
![version](https://img.shields.io/github/v/release/nimroddolev/chime_tts)

Have you ever missed the start of a TTS messages from Home Assistant because you didn't realize it had already started playing?

Chime TTS adds a Home Assistant service to locally add audio **before** and/or **after** your TTS audio into a single file, allowing you to hear them seamlessly without any delay in between.

## Quick start

1. Go to the "Integrations" section on HACS, click "Explore and download repositories", search for "Chime TTS", select it and then click "Download".
2. Restart Home Assistant
3. Create a new "Long-Lived Token" (used to retrieve TTS audio files from your Home Assistant instance - [see below](https://github.com/nimroddolev/chime_tts#why-do-i-need-to-enter-a-long-lived-token)):
   - Navigate to your profile (the bottom item in the left side-menu)
   - Scroll to the bottom and select 'CREATE TOKEN' under the 'Long-Lived Access Tokens' section.
   - Enter a name (eg: Chime TTS) and copy the token text (you'll only have access to it once)
4. Go to Settings -> Devices and Services -> Add Integration, and type: Chime TTS. If integration not found, try to empty your browser cache and reload page.
5. Paste in yout token string from step 3 and click Submit
6. To use Chiem TTS, go to Developer Tools -> Services, type `chime` and select  `Chime TTS: say`.
7. Enter your selections and then press the Call Service button to hear your message!

Refer to the [Configuration section](https://github.com/nimroddolev/chime_tts#configuration) for further fine-tuning.

## TTS Platforms
This integration supports [TTS platform integrations in Home Assistant](https://www.home-assistant.io/integrations/#text-to-speech) which need to be configured independently, as Chime TTS itself does not generate TTS audio.

## Why do I need to enter a long-lived token?

Chime TTS uses the [tts_get_url](https://www.home-assistant.io/integrations/tts/#post-apitts_get_url) Home Assistant API (to generate TTS audio files and locate the filepath) which requires a long-lived token.

## Configuration
The service options below are all optional:
Parameter | Description | Default
------------ | ------------- | -------------
Chime Path | The preset option or full local path to the audio file to be played **before** the TTS message. | Bells
End Chime Path | The preset option or full local path to the audio file to be played **after** the TTS message. | None
Message | The text to be converted into speach by a TTS platform | None
TTS Platform | The name of the TTS platform to use to create TTS audio. **Note:** you need to configure one or more [TTS platforms](https://www.home-assistant.io/integrations/#text-to-speech) in order to select them from the list.| None
Media Player Entity Id | The entity_id for the media player to play the audio | None
Volume Level | A value between 0 - 1 to set the media player to before playing the audio | 1

## Calling Service from Home Assistant

### From the UI
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github.com/nimroddolev/chime_tts/images/call_service_from_ui-dark.png">
  <source media="(prefers-color-scheme: light)" srcset="https://github.com/nimroddolev/chime_tts/images/call_service_from_ui-light.png">
  <img alt="Screenshot of the parameters for the Chime TTS service in the UI" src="https://github.com/nimroddolev/chime_tts/images/call_service_from_ui-light.png">
</picture>

### From YAML
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github.com/nimroddolev/chime_tts/images/call_service_from_yaml-dark.png">
  <source media="(prefers-color-scheme: light)" srcset="https://github.com/nimroddolev/chime_tts/images/call_service_from_yaml-light.png">
  <img alt="Sreenshot of the parameters for the Chime TTS service in YAML" src="https://github.com/nimroddolev/chime_tts/images/call_service_from_yaml-light.png">
</picture>