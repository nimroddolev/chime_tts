"use strict";(self.webpackChunkchime_tts=self.webpackChunkchime_tts||[]).push([[6992],{5558:t=>{t.exports=JSON.parse('{"version":{"pluginId":"default","version":"current","label":"Next","banner":null,"badge":false,"noIndex":false,"className":"docs-version-current","isLast":true,"docsSidebars":{"tutorialSidebar":[{"type":"link","label":"Chime TTS","href":"/chime_tts/docs/getting-started","docId":"getting-started","unlisted":false},{"type":"category","label":"Quick Start","collapsible":true,"collapsed":true,"items":[{"type":"link","label":"1. Installation","href":"/chime_tts/docs/quick-start/installing-chime-tts","docId":"quick-start/installing-chime-tts","unlisted":false},{"type":"link","label":"2. Adding the Integration","href":"/chime_tts/docs/quick-start/adding-the-integration","docId":"quick-start/adding-the-integration","unlisted":false},{"type":"link","label":"3. Additional Requirements","href":"/chime_tts/docs/quick-start/additional-requirements","docId":"quick-start/additional-requirements","unlisted":false}],"href":"/chime_tts/docs/quick-start/"},{"type":"category","label":"Documentation","collapsible":true,"collapsed":true,"items":[{"type":"link","label":"Configuration","href":"/chime_tts/docs/documentation/configuration","docId":"documentation/configuration","unlisted":false},{"type":"category","label":"Actions","collapsible":true,"collapsed":true,"items":[{"type":"category","label":"1. Say Action","collapsible":true,"collapsed":true,"items":[{"type":"link","label":"Parameters","href":"/chime_tts/docs/documentation/actions/say-action/parameters","docId":"documentation/actions/say-action/parameters","unlisted":false},{"type":"link","label":"Examples","href":"/chime_tts/docs/documentation/actions/say-action/examples","docId":"documentation/actions/say-action/examples","unlisted":false}],"href":"/chime_tts/docs/documentation/actions/say-action/"},{"type":"category","label":"2. Say URL Action","collapsible":true,"collapsed":true,"items":[{"type":"link","label":"Parameters","href":"/chime_tts/docs/documentation/actions/say_url-action/parameters","docId":"documentation/actions/say_url-action/parameters","unlisted":false},{"type":"link","label":"Examples","href":"/chime_tts/docs/documentation/actions/say_url-action/examples","docId":"documentation/actions/say_url-action/examples","unlisted":false}],"href":"/chime_tts/docs/documentation/actions/say_url-action/"},{"type":"link","label":"3. Replay Action","href":"/chime_tts/docs/documentation/actions/replay-action","docId":"documentation/actions/replay-action","unlisted":false},{"type":"link","label":"4. Clear Cache Action","href":"/chime_tts/docs/documentation/actions/clear_cache-action","docId":"documentation/actions/clear_cache-action","unlisted":false}],"href":"/chime_tts/docs/documentation/actions/"},{"type":"category","label":"Notify","collapsible":true,"collapsed":true,"items":[{"type":"link","label":"1. Adding Notify Entires","href":"/chime_tts/docs/documentation/notify/adding","docId":"documentation/notify/adding","unlisted":false},{"type":"link","label":"2. Sending Notifications","href":"/chime_tts/docs/documentation/notify/sending","docId":"documentation/notify/sending","unlisted":false}],"href":"/chime_tts/docs/documentation/notify/"}],"href":"/chime_tts/docs/documentation/"},{"type":"link","label":"Support","href":"/chime_tts/docs/support","docId":"support","unlisted":false}]},"docs":{"documentation/actions/clear_cache-action":{"id":"documentation/actions/clear_cache-action","title":"4. Clear Cache Action","description":"The chimetts.clearcache action can be used to remove cached audio files from the chimetts.say and chimetts.sayurl actions as well as Home Assistant\'s TTS cache.","sidebar":"tutorialSidebar"},"documentation/actions/index":{"id":"documentation/actions/index","title":"1. Actions","description":"Chime TTS adds 4 actions for you to use in Home Assistant:","sidebar":"tutorialSidebar"},"documentation/actions/replay-action":{"id":"documentation/actions/replay-action","title":"3. Replay Action","description":"The chimetts.replay action calls the chimetts.say action with the exact same set of parameter values used in the previous chime_tts.say action call.","sidebar":"tutorialSidebar"},"documentation/actions/say_url-action/examples":{"id":"documentation/actions/say_url-action/examples","title":"Examples","description":"The chimetts.sayurl action passess all arguments to the chimetts.say action (with the exception of all audio playback parameters such (as mediaplayer targets and other playback-related parameters, as there is no audio playback).","sidebar":"tutorialSidebar"},"documentation/actions/say_url-action/index":{"id":"documentation/actions/say_url-action/index","title":"2. Say URL Action","description":"The chimetts.sayurl action generates an audio file with the chimetts.say action and returns either a publicly accessible URL or a media content id to the generated file.","sidebar":"tutorialSidebar"},"documentation/actions/say_url-action/parameters":{"id":"documentation/actions/say_url-action/parameters","title":"Parameters","description":"The chimetts.sayurl action accepts the exact same parameters as the chimetts.say action (with the exception of all audio playback parameters such as mediaplayer targets and other playback-related parameters, as there is no audio playback).","sidebar":"tutorialSidebar"},"documentation/actions/say-action/examples":{"id":"documentation/actions/say-action/examples","title":"Examples","description":"The following YAML examples cover additional features provided by the chime_tts.say action:","sidebar":"tutorialSidebar"},"documentation/actions/say-action/index":{"id":"documentation/actions/say-action/index","title":"1. Say Action","description":"The chimetts.say action joins together audio files (*\\"chimes\\"*) and TTS audio as a new MP3 file, locally, for playback on mediaplayer target/s.","sidebar":"tutorialSidebar"},"documentation/actions/say-action/parameters":{"id":"documentation/actions/say-action/parameters","title":"Parameters","description":"The chime_tts.say action has standard parameters used by all TTS platforms, and additional parameters used by specific TTS platforms.","sidebar":"tutorialSidebar"},"documentation/configuration":{"id":"documentation/configuration","title":"Configuration","description":"You can configure the following options for the chimetts.say and chimetts.sayurl actions through the integration\'s configuration page:","sidebar":"tutorialSidebar"},"documentation/index":{"id":"documentation/index","title":"1. Documentation","description":"\u2699\ufe0f Configuration","sidebar":"tutorialSidebar"},"documentation/notify/adding":{"id":"documentation/notify/adding","title":"1. Adding Notify Entires","description":"1. Open your Home Assistant configuration.yaml file.","sidebar":"tutorialSidebar"},"documentation/notify/index":{"id":"documentation/notify/index","title":"Notify","description":"You can add Chime TTS notify entries to your configuration.yaml file, each with specific parameter values.","sidebar":"tutorialSidebar"},"documentation/notify/sending":{"id":"documentation/notify/sending","title":"2. Sending Notifications","description":"See the below example for how to send Chime TTS notifications:","sidebar":"tutorialSidebar"},"getting-started":{"id":"getting-started","title":"Chime TTS","description":"If you find Chime TTS useful, please consider showing your support:","sidebar":"tutorialSidebar"},"quick-start/adding-the-integration":{"id":"quick-start/adding-the-integration","title":"2. Adding the Integration","description":"1. Click this button:","sidebar":"tutorialSidebar"},"quick-start/additional-requirements":{"id":"quick-start/additional-requirements","title":"3. Additional Requirements","description":"Additional Requirements","sidebar":"tutorialSidebar"},"quick-start/installing-chime-tts":{"id":"quick-start/installing-chime-tts","title":"1. Installation","description":"Adding the Chime TTS Integration","sidebar":"tutorialSidebar"},"quick-start/quick-start":{"id":"quick-start/quick-start","title":"Quick Start","description":"Here\'s how to get started with Chime TTS audio notifications in three simple steps:","sidebar":"tutorialSidebar"},"support":{"id":"support","title":"Support","description":"1. Chime TTS GitHub Issues Page","sidebar":"tutorialSidebar"}}}}')}}]);