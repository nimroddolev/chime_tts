"use strict";(self.webpackChunkchime_tts=self.webpackChunkchime_tts||[]).push([[6136],{1853:(e,s,r)=>{r.r(s),r.d(s,{assets:()=>h,contentTitle:()=>c,default:()=>x,frontMatter:()=>t,metadata:()=>l,toc:()=>o});var d=r(4848),n=r(8453),i=r(6025);const t={sidebar_position:2,title:"Parameters"},c="chime_tts.say Parameters",l={id:"documentation/services/say-service/parameters",title:"Parameters",description:"The chime_tts.say service has standard parameters used by all TTS platforms, and additional parameters used by specific TTS platforms.",source:"@site/docs/documentation/services/say-service/parameters.mdx",sourceDirName:"documentation/services/say-service",slug:"/documentation/services/say-service/parameters",permalink:"/chime_tts/docs/documentation/services/say-service/parameters",draft:!1,unlisted:!1,tags:[],version:"current",sidebarPosition:2,frontMatter:{sidebar_position:2,title:"Parameters"},sidebar:"tutorialSidebar",previous:{title:"1. Say Service",permalink:"/chime_tts/docs/documentation/services/say-service/"},next:{title:"Examples",permalink:"/chime_tts/docs/documentation/services/say-service/examples"}},h={},o=[{value:"Standard Parameters",id:"standard-parameters",level:2},{value:"<code>message</code>",id:"message",level:3},{value:"Basic Usage: Text",id:"basic-usage-text",level:4},{value:"Advanced Usage: &quot;Segment&quot; sequences",id:"advanced-usage-segment-sequences",level:4},{value:"<code>tts</code> Segment Type",id:"tts-segment-type",level:5},{value:"Overriding Parameters:",id:"overriding-parameters",level:5},{value:"<code>chime</code> Segment Type",id:"chime-segment-type",level:4},{value:"<code>delay</code> Segment Type",id:"delay-segment-type",level:4},{value:"<code>repeat</code>",id:"repeat",level:4},{value:"<code>tts_platform</code>",id:"tts_platform",level:3},{value:"<code>chime_path</code>",id:"chime_path",level:3},{value:"<code>end_chime_path</code>",id:"end_chime_path",level:3},{value:"<code>offset</code>",id:"offset",level:3},{value:"<code>final_delay</code>",id:"final_delay",level:3},{value:"<code>tts_speed</code>",id:"tts_speed",level:3},{value:"<code>tts_pitch</code>",id:"tts_pitch",level:3},{value:"<code>volume_level</code>",id:"volume_level",level:3},{value:"Basic Usage",id:"basic-usage",level:4},{value:"Advanced Usage",id:"advanced-usage",level:4},{value:"<code>join_players</code>",id:"join_players",level:3},{value:"<code>unjoin_players</code>",id:"unjoin_players",level:3},{value:"<code>cache</code>",id:"cache",level:3},{value:"<code>audio_conversion</code>",id:"audio_conversion",level:3},{value:"<code>announce</code>",id:"announce",level:3},{value:"<code>fade_audio</code>",id:"fade_audio",level:3},{value:"<code>options</code>",id:"options",level:3},{value:"Additional Parameters",id:"additional-parameters",level:2},{value:"<code>language</code>",id:"language",level:3},{value:"<code>tld</code>",id:"tld",level:3},{value:"<code>voice</code>",id:"voice",level:3}];function a(e){const s={a:"a",code:"code",em:"em",h1:"h1",h2:"h2",h3:"h3",h4:"h4",h5:"h5",hr:"hr",li:"li",p:"p",pre:"pre",strong:"strong",table:"table",tbody:"tbody",td:"td",th:"th",thead:"thead",tr:"tr",ul:"ul",...(0,n.R)(),...e.components};return(0,d.jsxs)(d.Fragment,{children:[(0,d.jsxs)(s.h1,{id:"chime_ttssay-parameters",children:[(0,d.jsx)(s.code,{children:"chime_tts.say"})," Parameters"]}),"\n",(0,d.jsxs)(s.p,{children:["The ",(0,d.jsx)(s.code,{children:"chime_tts.say"})," service has ",(0,d.jsx)(s.a,{href:"#standard-parameters",children:"standard parameters"})," used by all TTS platforms, and ",(0,d.jsx)(s.a,{href:"#additional-parameters",children:"additional parameters"})," used by specific TTS platforms."]}),"\n",(0,d.jsx)(s.hr,{}),"\n",(0,d.jsx)(s.h2,{id:"standard-parameters",children:"Standard Parameters"}),"\n",(0,d.jsx)(s.h3,{id:"message",children:(0,d.jsx)(s.code,{children:"message"})}),"\n",(0,d.jsx)(s.h4,{id:"basic-usage-text",children:"Basic Usage: Text"}),"\n",(0,d.jsxs)(s.p,{children:["The ",(0,d.jsx)(s.code,{children:"message"})," parameter defines the text that will be converted into TTS audio by the TTS platform ",(0,d.jsx)(s.em,{children:"(defined by the"})," ",(0,d.jsx)(s.a,{href:"#tts_platform",children:(0,d.jsx)(s.code,{children:"tts_platform"})})," ",(0,d.jsx)(s.em,{children:"parameter)"}),"."]}),"\n",(0,d.jsxs)(s.table,{children:[(0,d.jsx)(s.thead,{children:(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.th,{children:(0,d.jsx)(s.strong,{children:"Description:"})}),(0,d.jsx)(s.th,{children:"The text to be converted into TTS audio."})]})}),(0,d.jsxs)(s.tbody,{children:[(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Required:"})}),(0,d.jsx)(s.td,{children:"Yes"})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Example:"})}),(0,d.jsx)(s.td,{children:(0,d.jsx)(s.code,{children:"The washing's done!"})})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Default:"})}),(0,d.jsx)(s.td,{children:"None"})]})]})]}),"\n",(0,d.jsx)(s.h4,{id:"advanced-usage-segment-sequences",children:'Advanced Usage: "Segment" sequences'}),"\n",(0,d.jsxs)(s.p,{children:["The ",(0,d.jsx)(s.code,{children:"message"}),' parameter can also define a YAML sequence built from 3 different "segment" types: ',(0,d.jsx)(s.a,{href:"#tts-segment-type",children:(0,d.jsx)(s.code,{children:"tts"})}),", ",(0,d.jsx)(s.a,{href:"#chime-segment-type",children:(0,d.jsx)(s.code,{children:"chime"})})," and ",(0,d.jsx)(s.a,{href:"#delay-segment-type",children:(0,d.jsx)(s.code,{children:"delay"})}),". These segments can be used together to create any combination, for example:"]}),"\n",(0,d.jsx)("img",{src:(0,i.Ay)("/img/say/message_segments.png")}),"\n",(0,d.jsx)(s.pre,{children:(0,d.jsx)(s.code,{children:"service: chime_tts.say\ntarget:\n  entity_id: media_player.kitchen_speaker\ndata:\n  chime_path: chord\n  end_chime_path: tada\n  offset: 0\n  tts_platform: google_translate\n  language: en\n  message:\n    - tts: Greetings friend!\n      tts_platform: amazon_polly\n    - chime: bells_2\n    - tts: Hola amigo!\n      language: es\n      options:\n        tld: es\n      offset: 500\n    - delay: 1000\n    - tts: G'day mate!\n      cache: true\n      tts_speed: 115\n      options:\n        tld: com.au\n"})}),"\n",(0,d.jsx)("audio",{controls:!0,src:(0,i.Ay)("/audio/parameters/message_segments.mp3?v=1")}),"\n",(0,d.jsx)(s.hr,{}),"\n",(0,d.jsxs)(s.h5,{id:"tts-segment-type",children:[(0,d.jsx)(s.code,{children:"tts"})," Segment Type"]}),"\n",(0,d.jsxs)(s.p,{children:["The tts segment type supports the parameters: (",(0,d.jsx)(s.a,{href:"#options",children:(0,d.jsx)(s.code,{children:"options"})}),", ",(0,d.jsx)(s.a,{href:"#tts_platform",children:(0,d.jsx)(s.code,{children:"tts_platform"})}),", ",(0,d.jsx)(s.a,{href:"#tts_speed",children:(0,d.jsx)(s.code,{children:"tts_speed"})}),", ",(0,d.jsx)(s.a,{href:"#tts_pitch",children:(0,d.jsx)(s.code,{children:"tts_pitch"})}),", ",(0,d.jsx)(s.a,{href:"#language",children:(0,d.jsx)(s.code,{children:"language"})}),", ",(0,d.jsx)(s.a,{href:"#cache",children:(0,d.jsx)(s.code,{children:"cache"})}),"), ",(0,d.jsx)(s.a,{href:"#offset",children:(0,d.jsx)(s.code,{children:"offset"})}),", and ",(0,d.jsx)(s.a,{href:"#audio_conversion",children:(0,d.jsx)(s.code,{children:"audio_conversion"})})," which allow you to use different TTS providers, languages, voices, rates of speech, pitch and apply specific FFmpeg audio conversions on different TTS segments within the same message."]}),"\n",(0,d.jsx)(s.p,{children:"Example usage:"}),"\n",(0,d.jsx)(s.pre,{children:(0,d.jsx)(s.code,{children:"service: chime_tts.say\ntarget:\n  entity_id: media_player.kitchen_speaker\ndata:\n  chime_path: classical\n  end_chime_path: marimba\n  tts_platform: google_translate\n  cache: false\n  language: en\n  message:\n    - tts: May I please have your attention?\n      cache: true\n    - tts: It is officially time to move the washing to the dryer\n      offset: 3000\n      options:\n        tld: co.uk\n    - tts: V\xe1monos!\n      language: es\n      options:\n        tld: es\n      tts_speed: 115\n    - type: tts\n      message: Let's go!\n      tts_platform: amazon_polly\n"})}),"\n",(0,d.jsx)("audio",{controls:!0,src:(0,i.Ay)("/audio/parameters/tts_segments.mp3?v=1")}),"\n",(0,d.jsx)(s.p,{children:"In the above example:"}),"\n",(0,d.jsxs)(s.ul,{children:["\n",(0,d.jsx)(s.li,{children:"The 1st segment overrides the cache parameter, setting it to true for the segment."}),"\n",(0,d.jsx)(s.li,{children:"The 2nd segment adds a 3 second delay before the TTS message and overrides the domain, setting it to the UK."}),"\n",(0,d.jsx)(s.li,{children:"The 3rd segment overrides the language, setting it to Spanish with the domain accent of Spain, and sets the speech rate to 115%."}),"\n",(0,d.jsx)(s.li,{children:"The 4th segment overrides the TTS platform, setting it to Amazon Polly."}),"\n"]}),"\n",(0,d.jsx)(s.h5,{id:"overriding-parameters",children:"Overriding Parameters:"}),"\n",(0,d.jsxs)(s.p,{children:['When a parameter is defined in a TTS segment, it overrides the corresponding "parent" parameter in the main set of parameters, if defined.\nWhen including the ',(0,d.jsx)(s.code,{children:"options"})," parameter in a TTS segment, the included parameters will overwrite any corresponding options in the main ",(0,d.jsx)(s.code,{children:"options"}),' parameter. Any parameters not overwritten in the "parent" ',(0,d.jsx)(s.code,{children:"options"})," parameter will be applied as defined."]}),"\n",(0,d.jsx)(s.hr,{}),"\n",(0,d.jsxs)(s.h4,{id:"chime-segment-type",children:[(0,d.jsx)(s.code,{children:"chime"})," Segment Type"]}),"\n",(0,d.jsxs)(s.p,{children:["The chime segment allows you to insert chimes anywhere in your messages, *(not just at the start (via ",(0,d.jsx)(s.em,{children:(0,d.jsx)(s.a,{href:"#chime_path",children:(0,d.jsx)(s.code,{children:"chime_path"})})}),") or end (via ",(0,d.jsx)(s.em,{children:(0,d.jsx)(s.a,{href:"#end_chime_path",children:(0,d.jsx)(s.code,{children:"end_chime_path"})})}),"), and supports the ",(0,d.jsx)(s.a,{href:"#offset",children:(0,d.jsx)(s.code,{children:"offset"})})," and ",(0,d.jsx)(s.a,{href:"#audio_conversion",children:(0,d.jsx)(s.code,{children:"audio_conversion"})})," parameters."]}),"\n",(0,d.jsxs)(s.p,{children:["The chime value can be any value supported by the ",(0,d.jsx)(s.a,{href:"#chime_path",children:(0,d.jsx)(s.code,{children:"chime_path"})}),"/",(0,d.jsx)(s.a,{href:"#end_chime_path",children:(0,d.jsx)(s.code,{children:"end_chime_path"})})," parameters (see ",(0,d.jsx)(s.a,{href:"./#selecting-chimes",children:"selecting chimes"}),")."]}),"\n",(0,d.jsx)(s.pre,{children:(0,d.jsx)(s.code,{children:"service: chime_tts.say\ntarget:\n  entity_id: media_player.kitchen_speaker\ndata:\n  chime_path: toast\n  end_chime_path: tada\n  tts_platform: google_translate\n  message:\n    - tts: And the winner is, drumroll please\n    - chime: drumroll\n      offset: 500\n    - tts: You!\n      offset: 0\n    - chime: /config/media/sounds/my_chimes/hooray.mp3\n    - tts: You get to move the washing to the dryer!\n"})}),"\n",(0,d.jsx)("audio",{controls:!0,src:(0,i.Ay)("/audio/parameters/chime_segments.mp3?v=1")}),"\n",(0,d.jsx)(s.hr,{}),"\n",(0,d.jsxs)(s.h4,{id:"delay-segment-type",children:[(0,d.jsx)(s.code,{children:"delay"})," Segment Type"]}),"\n",(0,d.jsxs)(s.p,{children:["The delay segment allows you to add additional delays into the message. This might be useful for repeating a message, ",(0,d.jsx)(s.em,{children:"or pausing for dramatic effect"})," \ud83c\udfad"]}),"\n",(0,d.jsx)(s.pre,{children:(0,d.jsx)(s.code,{children:"service: chime_tts.say\ntarget:\n  entity_id: media_player.kitchen_speaker\ndata:\n  tts_platform: google_translate\n  message:\n    - tts: Hey, do you hear that? Just listen.\n    - delay: 1000\n    - tts: Yep, sounds like clothes waiting to be moved to the dryer\n"})}),"\n",(0,d.jsx)("audio",{controls:!0,src:(0,i.Ay)("/audio/parameters/delay_segments.mp3?v=1")}),"\n",(0,d.jsx)(s.hr,{}),"\n",(0,d.jsx)(s.h4,{id:"repeat",children:(0,d.jsx)(s.code,{children:"repeat"})}),"\n",(0,d.jsxs)(s.p,{children:["All message segment types can include a ",(0,d.jsx)(s.code,{children:"repeat"})," parameter to specify the number of times to repeat the segment."]}),"\n",(0,d.jsx)(s.pre,{children:(0,d.jsx)(s.code,{children:"service: chime_tts.say\ntarget:\n  entity_id: media_player.macbook_air\ndata:\n  tts_platform: google_translate\n  message:\n    - chime: https://www.zapsplat.com/wp-content/uploads/2015/sound-effects-three/household_clock_cuckoo_strike_001.mp3\n      repeat: 3\n      offset: -800\n    - tts: It's 3 o'clock\n"})}),"\n",(0,d.jsx)("audio",{controls:!0,src:(0,i.Ay)("/audio/parameters/repeat.mp3?v=1")}),"\n",(0,d.jsx)(s.hr,{}),"\n",(0,d.jsx)(s.h3,{id:"tts_platform",children:(0,d.jsx)(s.code,{children:"tts_platform"})}),"\n",(0,d.jsxs)(s.p,{children:["Chime TTS works with ",(0,d.jsx)(s.a,{href:"https://www.home-assistant.io/integrations/#text-to-speech",children:"TTS Platform integrations"}),", but you need to add them to your Home Assistant instance yourself beforehand."]}),"\n",(0,d.jsxs)(s.table,{children:[(0,d.jsx)(s.thead,{children:(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.th,{children:(0,d.jsx)(s.strong,{children:"Description:"})}),(0,d.jsx)(s.th,{children:"TTS platform to be used to create TTS audio."})]})}),(0,d.jsxs)(s.tbody,{children:[(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Required:"})}),(0,d.jsx)(s.td,{children:"Yes"})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Example:"})}),(0,d.jsx)(s.td,{children:(0,d.jsx)(s.code,{children:"amazon_polly"})})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Default:"})}),(0,d.jsx)(s.td,{children:"None"})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsxs)(s.strong,{children:["Possible Values:",(0,d.jsx)("sup",{children:"*"})]})}),(0,d.jsxs)(s.td,{children:[(0,d.jsx)(s.code,{children:"amazon_polly"})," (Amazon Polly)",(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"baidu"})," (Baidu)",(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"tts.eleven_labs_tts"})," (ElevenLabs TTS)",(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"edge_tts"})," (Microsoft Edge TTS)",(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"google_cloud"})," (Google Cloud)",(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"google_translate"})," (Google Translate)",(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"openai_tts"})," (OpenAI TTS)",(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"watson_tts"})," (IBM Watson TTS)",(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"marytts"})," (MaryTTS)",(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"microsoft"})," (Microsoft Text-To-Speech)",(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"cloud"})," (Nabu Casa Cloud TTS)",(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"picotts"})," (Picto TTS)",(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"tts.piper"})," (Piper)",(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"voicerss"})," (VoiceRSS)",(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"yandextts"})," (Yandex TTS)"]})]})]})]}),"\n",(0,d.jsxs)(s.p,{children:[(0,d.jsx)("sup",{children:"*"}),"To use a TTS platform not included in the list, simply set the custom TTS platform's service as the ",(0,d.jsx)(s.code,{children:"tts_platform"})," parameter value."]}),"\n",(0,d.jsx)(s.hr,{}),"\n",(0,d.jsx)(s.h3,{id:"chime_path",children:(0,d.jsx)(s.code,{children:"chime_path"})}),"\n",(0,d.jsxs)(s.table,{children:[(0,d.jsx)(s.thead,{children:(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.th,{children:(0,d.jsx)(s.strong,{children:"Description:"})}),(0,d.jsxs)(s.th,{children:["The file path for the audio to insert ",(0,d.jsx)(s.strong,{children:"before"})," the TTS audio"]})]})}),(0,d.jsxs)(s.tbody,{children:[(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Required:"})}),(0,d.jsx)(s.td,{children:"No"})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Example 1:"})}),(0,d.jsxs)(s.td,{children:["One of the Chime TTS presets:",(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"ba_dum_tss"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"bells"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"bells_2"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"bright"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"chirp"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"choir"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"chord"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"classical"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"crickets"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"ding_dong"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"drumroll"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"dun_dun_dun"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"error"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"fanfare"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"glockenspiel"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"hail"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"knock"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"marimba"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"mario_coin"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"microphone_tap"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"tada"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"toast"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"twenty_four"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"sad_trombone"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"soft"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"whistle"})]})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Example 2:"})}),(0,d.jsxs)(s.td,{children:["One of your own custom chimes : ",(0,d.jsx)(s.code,{children:"My Custom Chime"}),(0,d.jsx)("br",{}),"(",(0,d.jsxs)(s.em,{children:["see ",(0,d.jsx)(s.a,{href:"./#custom-chimes-folder",children:"Custom Chimes Folder"})]}),")"]})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Example 2:"})}),(0,d.jsxs)(s.td,{children:["A local file:",(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"/media/sounds/notification.mp3"})]})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Example 3:"})}),(0,d.jsxs)(s.td,{children:["A file from a remote URL:",(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"https://www.website.com/sounds/notification.ogg"})]})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Default:"})}),(0,d.jsx)(s.td,{children:"None"})]})]})]}),"\n",(0,d.jsx)(s.hr,{}),"\n",(0,d.jsx)(s.h3,{id:"end_chime_path",children:(0,d.jsx)(s.code,{children:"end_chime_path"})}),"\n",(0,d.jsxs)(s.table,{children:[(0,d.jsx)(s.thead,{children:(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.th,{children:(0,d.jsx)(s.strong,{children:"Description:"})}),(0,d.jsxs)(s.th,{children:["The file path for the audio to insert ",(0,d.jsx)(s.strong,{children:"after"})," the TTS audio"]})]})}),(0,d.jsxs)(s.tbody,{children:[(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Required:"})}),(0,d.jsx)(s.td,{children:"No"})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Example 1:"})}),(0,d.jsxs)(s.td,{children:["One of the Chime TTS presets:",(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"ba_dum_tss"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"bells"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"bells_2"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"bright"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"chirp"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"choir"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"chord"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"classical"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"crickets"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"ding_dong"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"drumroll"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"dun_dun_dun"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"error"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"fanfare"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"glockenspiel"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"hail"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"knock"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"marimba"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"mario_coin"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"microphone_tap"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"tada"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"toast"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"twenty_four"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"sad_trombone"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"soft"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"whistle"})]})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Example 2:"})}),(0,d.jsxs)(s.td,{children:["One of your own custom chimes : ",(0,d.jsx)(s.code,{children:"My Custom Chime"}),(0,d.jsx)("br",{}),"(",(0,d.jsxs)(s.em,{children:["see ",(0,d.jsx)(s.a,{href:"./#custom-chimes-folder",children:"Custom Chimes Folder"})]}),")"]})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Example 2:"})}),(0,d.jsxs)(s.td,{children:["A local file:",(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"/media/sounds/notification.mp3"})]})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Example 3:"})}),(0,d.jsxs)(s.td,{children:["A file from a remote URL:",(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"https://www.website.com/sounds/notification.ogg"})]})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Default:"})}),(0,d.jsx)(s.td,{children:"None"})]})]})]}),"\n",(0,d.jsx)(s.hr,{}),"\n",(0,d.jsx)(s.h3,{id:"offset",children:(0,d.jsx)(s.code,{children:"offset"})}),"\n",(0,d.jsxs)(s.table,{children:[(0,d.jsx)(s.thead,{children:(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.th,{children:(0,d.jsx)(s.strong,{children:"Description:"})}),(0,d.jsx)(s.th,{children:"Adds a delay between audio segments when value > 0, or overlays audio segments when value < 0."})]})}),(0,d.jsxs)(s.tbody,{children:[(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Required:"})}),(0,d.jsx)(s.td,{children:"No"})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Example 1:"})}),(0,d.jsxs)(s.td,{children:[(0,d.jsx)(s.code,{children:"500"})," (Adds a 1 second delay between chimes & TTS audio)"]})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Example 2:"})}),(0,d.jsxs)(s.td,{children:[(0,d.jsx)(s.code,{children:"-500"})," (Moves the audio 1 second earlier, overlaying it with the previous chime/TTS audio)"]})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Default:"})}),(0,d.jsx)(s.td,{children:(0,d.jsx)(s.code,{children:"450"})})]})]})]}),"\n",(0,d.jsx)(s.p,{children:"When using a value greater than 0, a delay is added between audio components:"}),"\n",(0,d.jsx)("img",{src:(0,i.Ay)("/img/say/offset_positive.gif")}),"\n",(0,d.jsx)(s.p,{children:"When using a negative value the audio components are overlaid:"}),"\n",(0,d.jsx)("img",{src:(0,i.Ay)("/img/say/offset_negative.gif")}),"\n",(0,d.jsx)(s.hr,{}),"\n",(0,d.jsx)(s.h3,{id:"final_delay",children:(0,d.jsx)(s.code,{children:"final_delay"})}),"\n",(0,d.jsxs)(s.table,{children:[(0,d.jsx)(s.thead,{children:(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.th,{children:(0,d.jsx)(s.strong,{children:"Description:"})}),(0,d.jsx)(s.th,{children:"The delay (in milliseconds) to insert after the chimes and the TTS audio"})]})}),(0,d.jsxs)(s.tbody,{children:[(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Required:"})}),(0,d.jsx)(s.td,{children:"No"})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Example:"})}),(0,d.jsx)(s.td,{children:(0,d.jsx)(s.code,{children:"200"})})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Default:"})}),(0,d.jsx)(s.td,{children:(0,d.jsx)(s.code,{children:"0"})})]})]})]}),"\n",(0,d.jsx)(s.hr,{}),"\n",(0,d.jsx)(s.h3,{id:"tts_speed",children:(0,d.jsx)(s.code,{children:"tts_speed"})}),"\n",(0,d.jsxs)(s.table,{children:[(0,d.jsx)(s.thead,{children:(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.th,{children:(0,d.jsx)(s.strong,{children:"Description:"})}),(0,d.jsx)(s.th,{children:"The speed for the TTS audio, between from 1% - 500%"})]})}),(0,d.jsxs)(s.tbody,{children:[(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Required:"})}),(0,d.jsx)(s.td,{children:"No"})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Example:"})}),(0,d.jsx)(s.td,{children:(0,d.jsx)(s.code,{children:"150"})})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Default:"})}),(0,d.jsx)(s.td,{children:(0,d.jsx)(s.code,{children:"100"})})]})]})]}),"\n",(0,d.jsx)(s.hr,{}),"\n",(0,d.jsx)(s.h3,{id:"tts_pitch",children:(0,d.jsx)(s.code,{children:"tts_pitch"})}),"\n",(0,d.jsxs)(s.table,{children:[(0,d.jsx)(s.thead,{children:(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.th,{children:(0,d.jsx)(s.strong,{children:"Description:"})}),(0,d.jsx)(s.th,{children:"The pitch of the TTS audio, in semitones (positive values to increase the pitch and negative values to lower it)"})]})}),(0,d.jsxs)(s.tbody,{children:[(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Required:"})}),(0,d.jsx)(s.td,{children:"No"})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Example:"})}),(0,d.jsx)(s.td,{children:(0,d.jsx)(s.code,{children:"2"})})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Default:"})}),(0,d.jsx)(s.td,{children:(0,d.jsx)(s.code,{children:"0"})})]})]})]}),"\n",(0,d.jsx)(s.hr,{}),"\n",(0,d.jsx)(s.h3,{id:"volume_level",children:(0,d.jsx)(s.code,{children:"volume_level"})}),"\n",(0,d.jsxs)(s.p,{children:["The ",(0,d.jsx)(s.code,{children:"volume_level"})," parameter can be used to set the volume of the media_player/s included in the service call to a specific volume for the Chime TTS announcement, and return the volume level back to the original value once completed."]}),"\n",(0,d.jsx)(s.h4,{id:"basic-usage",children:"Basic Usage"}),"\n",(0,d.jsxs)(s.p,{children:["When the ",(0,d.jsx)(s.code,{children:"volume_level"})," parameter is defined as a float value, it will be applied to ",(0,d.jsx)(s.strong,{children:"all media_player entities"})," included in the service call."]}),"\n",(0,d.jsxs)(s.table,{children:[(0,d.jsx)(s.thead,{children:(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.th,{children:(0,d.jsx)(s.strong,{children:"Description:"})}),(0,d.jsx)(s.th,{children:"The volume level (between 0.0 - 1.0) to play the audio."})]})}),(0,d.jsxs)(s.tbody,{children:[(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Required:"})}),(0,d.jsx)(s.td,{children:"No"})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Example:"})}),(0,d.jsx)(s.td,{children:(0,d.jsx)(s.code,{children:"0.75"})})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Default:"})}),(0,d.jsx)(s.td,{children:(0,d.jsx)(s.code,{children:"1.0"})})]})]})]}),"\n",(0,d.jsx)(s.h4,{id:"advanced-usage",children:"Advanced Usage"}),"\n",(0,d.jsxs)(s.p,{children:["To set the volume level for each individual media_player, you can set the ",(0,d.jsx)(s.code,{children:"volume_level"})," as a dictioary value, allowing you to ",(0,d.jsx)(s.strong,{children:"set a specific volume_level for each media_player entity"})," included in the service call."]}),"\n",(0,d.jsx)(s.p,{children:"Example:"}),"\n",(0,d.jsx)(s.pre,{children:(0,d.jsx)(s.code,{children:"volume_level:\n  - media_player.kitchen: 1.00\n  - media_player.bedroom: 0.45\n  - media_player.living_room: 0.75\n  - media_player.study: 0.5\n"})}),"\n",(0,d.jsx)(s.hr,{}),"\n",(0,d.jsx)(s.h3,{id:"join_players",children:(0,d.jsx)(s.code,{children:"join_players"})}),"\n",(0,d.jsxs)(s.table,{children:[(0,d.jsx)(s.thead,{children:(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.th,{children:(0,d.jsx)(s.strong,{children:"Description:"})}),(0,d.jsx)(s.th,{children:"Play the audio simultaneously on multiple media_player entities (that support speaker groups)."})]})}),(0,d.jsxs)(s.tbody,{children:[(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Required:"})}),(0,d.jsx)(s.td,{children:"No"})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Example:"})}),(0,d.jsx)(s.td,{children:(0,d.jsx)(s.code,{children:"true"})})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Default:"})}),(0,d.jsx)(s.td,{children:(0,d.jsx)(s.code,{children:"false"})})]})]})]}),"\n",(0,d.jsx)(s.hr,{}),"\n",(0,d.jsx)(s.h3,{id:"unjoin_players",children:(0,d.jsx)(s.code,{children:"unjoin_players"})}),"\n",(0,d.jsxs)(s.table,{children:[(0,d.jsx)(s.thead,{children:(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.th,{children:(0,d.jsx)(s.strong,{children:"Description:"})}),(0,d.jsx)(s.th,{children:"Unjoin the speakers after playback has completed."})]})}),(0,d.jsxs)(s.tbody,{children:[(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Required:"})}),(0,d.jsx)(s.td,{children:"No"})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Example:"})}),(0,d.jsx)(s.td,{children:(0,d.jsx)(s.code,{children:"true"})})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Default:"})}),(0,d.jsx)(s.td,{children:(0,d.jsx)(s.code,{children:"false"})})]})]})]}),"\n",(0,d.jsx)(s.hr,{}),"\n",(0,d.jsx)(s.h3,{id:"cache",children:(0,d.jsx)(s.code,{children:"cache"})}),"\n",(0,d.jsxs)(s.table,{children:[(0,d.jsx)(s.thead,{children:(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.th,{children:(0,d.jsx)(s.strong,{children:"Description:"})}),(0,d.jsx)(s.th,{children:"Save generated audio to the cache for reuse in future service calls."})]})}),(0,d.jsxs)(s.tbody,{children:[(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Required:"})}),(0,d.jsx)(s.td,{children:"No"})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Example:"})}),(0,d.jsx)(s.td,{children:(0,d.jsx)(s.code,{children:"true"})})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Default:"})}),(0,d.jsx)(s.td,{children:(0,d.jsx)(s.code,{children:"false"})})]})]})]}),"\n",(0,d.jsx)(s.hr,{}),"\n",(0,d.jsx)(s.h3,{id:"audio_conversion",children:(0,d.jsx)(s.code,{children:"audio_conversion"})}),"\n",(0,d.jsxs)(s.table,{children:[(0,d.jsx)(s.thead,{children:(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.th,{children:(0,d.jsx)(s.strong,{children:"Description:"})}),(0,d.jsx)(s.th,{children:"Convert the generated audio via FFmpeg to work with Alexa speakers, or convert with any FFmpeg arguments."})]})}),(0,d.jsxs)(s.tbody,{children:[(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Required:"})}),(0,d.jsx)(s.td,{children:"No"})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Example 1:"})}),(0,d.jsxs)(s.td,{children:[(0,d.jsx)(s.em,{children:"Convert the audio to play correctly on Alexa media_players:"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"Alexa"})]})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Example 2:"})}),(0,d.jsxs)(s.td,{children:[(0,d.jsx)(s.em,{children:'"Hard-code" the audio file\'s volume to be 200% of the original:'}),(0,d.jsx)("br",{})," ",(0,d.jsx)(s.code,{children:"Volume 200%"})]})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Example 3:"})}),(0,d.jsxs)(s.td,{children:[(0,d.jsx)(s.em,{children:"Any FFmpeg arguments, eg:"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"-y -ac 2 -codec:a libmp3lame -b:a 48k -ar 24000 -write_xing 0"})]})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Default:"})}),(0,d.jsx)(s.td,{children:"None"})]})]})]}),"\n",(0,d.jsx)(s.hr,{}),"\n",(0,d.jsx)(s.h3,{id:"announce",children:(0,d.jsx)(s.code,{children:"announce"})}),"\n",(0,d.jsx)(s.p,{children:(0,d.jsx)(s.em,{children:"The announce feature works natively for supported media_player platforms, and is simulated by Chime TTS for unsupported platforms (such as the Homepod)."})}),"\n",(0,d.jsxs)(s.table,{children:[(0,d.jsx)(s.thead,{children:(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.th,{children:(0,d.jsx)(s.strong,{children:"Description:"})}),(0,d.jsx)(s.th,{children:"Pauses any media currently playing on the media_player/s and resumes it after Chime TTS completes playback"})]})}),(0,d.jsxs)(s.tbody,{children:[(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Required:"})}),(0,d.jsx)(s.td,{children:"No"})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Example:"})}),(0,d.jsx)(s.td,{children:(0,d.jsx)(s.code,{children:"true"})})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Default:"})}),(0,d.jsx)(s.td,{children:(0,d.jsx)(s.code,{children:"false"})})]})]})]}),"\n",(0,d.jsx)(s.hr,{}),"\n",(0,d.jsx)(s.h3,{id:"fade_audio",children:(0,d.jsx)(s.code,{children:"fade_audio"})}),"\n",(0,d.jsxs)(s.table,{children:[(0,d.jsx)(s.thead,{children:(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.th,{children:(0,d.jsx)(s.strong,{children:"Description:"})}),(0,d.jsx)(s.th,{children:"Fades out and pauses any media currently playing on the media_player/s and resumes it after Chime TTS completes playback with fade in"})]})}),(0,d.jsxs)(s.tbody,{children:[(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Required:"})}),(0,d.jsx)(s.td,{children:"No"})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Example:"})}),(0,d.jsx)(s.td,{children:(0,d.jsx)(s.code,{children:"true"})})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Default:"})}),(0,d.jsx)(s.td,{children:(0,d.jsx)(s.code,{children:"false"})})]})]})]}),"\n",(0,d.jsx)(s.hr,{}),"\n",(0,d.jsx)(s.h3,{id:"options",children:(0,d.jsx)(s.code,{children:"options"})}),"\n",(0,d.jsxs)(s.table,{children:[(0,d.jsx)(s.thead,{children:(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.th,{children:(0,d.jsx)(s.strong,{children:"Description:"})}),(0,d.jsx)(s.th,{children:"YAML options field used by TTS services"})]})}),(0,d.jsxs)(s.tbody,{children:[(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Required:"})}),(0,d.jsx)(s.td,{children:"No"})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Example:"})}),(0,d.jsx)(s.td,{children:(0,d.jsx)(s.code,{children:"voice: Wendy"})})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Default:"})}),(0,d.jsx)(s.td,{children:"None"})]})]})]}),"\n",(0,d.jsx)(s.hr,{}),"\n",(0,d.jsx)(s.h2,{id:"additional-parameters",children:"Additional Parameters"}),"\n",(0,d.jsx)(s.p,{children:"The following parameters can be used with select TTS platforms, as outlined below:"}),"\n",(0,d.jsx)(s.hr,{}),"\n",(0,d.jsx)(s.h3,{id:"language",children:(0,d.jsx)(s.code,{children:"language"})}),"\n",(0,d.jsxs)(s.table,{children:[(0,d.jsx)(s.thead,{children:(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.th,{children:(0,d.jsx)(s.strong,{children:"Description:"})}),(0,d.jsxs)(s.th,{children:["The language to use for the TTS audio. This parameter is only supported by ",(0,d.jsx)(s.a,{href:"https://www.home-assistant.io/integrations/google_translate/",children:"Google Translate"})," and",(0,d.jsx)("br",{}),(0,d.jsx)(s.a,{href:"https://www.nabucasa.com/config/tts/",children:"Nabu Casa Cloud TTS"}),". This parameter should also be used to set ",(0,d.jsx)(s.a,{href:"https://www.home-assistant.io/integrations/watson_tts/",children:"IBM Watson TTS"}),"'s ",(0,d.jsx)(s.code,{children:"voice"})," value."]})]})}),(0,d.jsxs)(s.tbody,{children:[(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Required:"})}),(0,d.jsx)(s.td,{children:"No"})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Example:"})}),(0,d.jsx)(s.td,{children:(0,d.jsx)(s.code,{children:"en"})})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Default:"})}),(0,d.jsx)(s.td,{children:"None"})]})]})]}),"\n",(0,d.jsx)(s.hr,{}),"\n",(0,d.jsx)(s.h3,{id:"tld",children:(0,d.jsx)(s.code,{children:"tld"})}),"\n",(0,d.jsxs)(s.table,{children:[(0,d.jsx)(s.thead,{children:(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.th,{children:(0,d.jsx)(s.strong,{children:"Description:"})}),(0,d.jsxs)(s.th,{children:["The domain region to use for a specific dialect/accent. Refer to the documentation for ",(0,d.jsx)(s.a,{href:"https://www.home-assistant.io/integrations/google_translate/",children:"Google Translate"})]})]})}),(0,d.jsxs)(s.tbody,{children:[(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Required:"})}),(0,d.jsx)(s.td,{children:"No"})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Example:"})}),(0,d.jsx)(s.td,{children:(0,d.jsx)(s.code,{children:"com.au"})})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Default:"})}),(0,d.jsx)(s.td,{children:"None"})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Possible Values:"})}),(0,d.jsxs)(s.td,{children:[(0,d.jsx)(s.code,{children:"com"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"co.uk"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"com.au"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"ca"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"co.in"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"ie"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"co.za"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"fr"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"com.br"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"pt"}),(0,d.jsx)("br",{}),(0,d.jsx)(s.code,{children:"es"})]})]})]})]}),"\n",(0,d.jsx)(s.hr,{}),"\n",(0,d.jsx)(s.h3,{id:"voice",children:(0,d.jsx)(s.code,{children:"voice"})}),"\n",(0,d.jsxs)(s.table,{children:[(0,d.jsx)(s.thead,{children:(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.th,{children:(0,d.jsx)(s.strong,{children:"Description:"})}),(0,d.jsx)(s.th,{children:"Set the voice to use for TTS audio (on supported TTS platforms)"})]})}),(0,d.jsxs)(s.tbody,{children:[(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Required:"})}),(0,d.jsx)(s.td,{children:"No"})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Example:"})}),(0,d.jsx)(s.td,{children:(0,d.jsx)(s.code,{children:"TinaNeural"})})]}),(0,d.jsxs)(s.tr,{children:[(0,d.jsx)(s.td,{children:(0,d.jsx)(s.strong,{children:"Default:"})}),(0,d.jsx)(s.td,{children:"None"})]})]})]})]})}function x(e={}){const{wrapper:s}={...(0,n.R)(),...e.components};return s?(0,d.jsx)(s,{...e,children:(0,d.jsx)(a,{...e})}):a(e)}},8453:(e,s,r)=>{r.d(s,{R:()=>t,x:()=>c});var d=r(6540);const n={},i=d.createContext(n);function t(e){const s=d.useContext(i);return d.useMemo((function(){return"function"==typeof e?e(s):{...s,...e}}),[s,e])}function c(e){let s;return s=e.disableParentContext?"function"==typeof e.components?e.components(n):e.components||n:t(e.components),d.createElement(i.Provider,{value:s},e.children)}}}]);