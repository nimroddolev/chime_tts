"use strict";(self.webpackChunkchime_tts=self.webpackChunkchime_tts||[]).push([[925],{2816:(e,t,n)=>{n.r(t),n.d(t,{assets:()=>c,contentTitle:()=>r,default:()=>p,frontMatter:()=>d,metadata:()=>o,toc:()=>l});var s=n(4848),a=n(8453),i=n(6025);const d={sidebar_position:3,title:"Examples"},r="chime_tts.say Examples",o={id:"documentation/services/say-service/examples",title:"Examples",description:"The following YAML examples cover additional features provided by the chime_tts.say service:",source:"@site/docs/documentation/services/say-service/examples.mdx",sourceDirName:"documentation/services/say-service",slug:"/documentation/services/say-service/examples",permalink:"/chime_tts/docs/documentation/services/say-service/examples",draft:!1,unlisted:!1,tags:[],version:"current",sidebarPosition:3,frontMatter:{sidebar_position:3,title:"Examples"},sidebar:"tutorialSidebar",previous:{title:"Parameters",permalink:"/chime_tts/docs/documentation/services/say-service/parameters"},next:{title:"2. Say URL Service",permalink:"/chime_tts/docs/documentation/services/say_url-service/"}},c={},l=[{value:"Basic TTS Audio",id:"basic-tts-audio",level:2},{value:"Basic example",id:"basic-example",level:3},{value:"<code>chime_path</code>",id:"chime_path",level:3},{value:"<code>end_chime_path</code>",id:"end_chime_path",level:3},{value:"<code>chime_path</code> and <code>end_chime_path</code>",id:"chime_path-and-end_chime_path",level:3},{value:"More complex examples",id:"more-complex-examples",level:2},{value:"<code>tts_speed</code>",id:"tts_speed",level:3},{value:"Increase speed",id:"increase-speed",level:4},{value:"Decrease speed",id:"decrease-speed",level:4},{value:"<code>tts_pitch</code>",id:"tts_pitch",level:3},{value:"Raise pitch",id:"raise-pitch",level:4},{value:"Lower pitch",id:"lower-pitch",level:4},{value:"Musical Fun",id:"musical-fun",level:4},{value:"<code>offset</code>",id:"offset",level:3},{value:"Positive Offset (delay audio)",id:"positive-offset-delay-audio",level:4},{value:"Negative Offset (overlay audio)",id:"negative-offset-overlay-audio",level:4},{value:"<code>language</code> and <code>tld</code>",id:"language-and-tld",level:3},{value:"<code>join_players</code>",id:"join_players",level:3},{value:"Message Segments",id:"message-segments",level:2},{value:"<code>tts</code> Segment Type",id:"tts-segment-type",level:3},{value:"<code>chime</code> Segment Type",id:"chime-segment-type",level:3},{value:"<code>delay</code> Segment Type",id:"delay-segment-type",level:3},{value:"<code>repeat</code>",id:"repeat",level:3}];function h(e){const t={a:"a",code:"code",h1:"h1",h2:"h2",h3:"h3",h4:"h4",li:"li",p:"p",pre:"pre",ul:"ul",...(0,a.R)(),...e.components};return(0,s.jsxs)(s.Fragment,{children:[(0,s.jsxs)(t.h1,{id:"chime_ttssay-examples",children:[(0,s.jsx)(t.code,{children:"chime_tts.say"})," Examples"]}),"\n",(0,s.jsxs)(t.p,{children:["The following YAML examples cover additional features provided by the ",(0,s.jsxs)(t.a,{href:"./",children:[(0,s.jsx)(t.code,{children:"chime_tts.say"})," service"]}),":"]}),"\n",(0,s.jsx)(t.h2,{id:"basic-tts-audio",children:"Basic TTS Audio"}),"\n",(0,s.jsxs)(t.p,{children:["All service calls to ",(0,s.jsxs)(t.a,{href:"./",children:[(0,s.jsx)(t.code,{children:"chime_tts.say"})," service"]})," must include one or more ",(0,s.jsx)(t.code,{children:"media_player"})," entity targets, and a data object with the TTS ",(0,s.jsx)(t.a,{href:"./parameters#message",children:(0,s.jsx)(t.code,{children:"message"})})," and ",(0,s.jsx)(t.a,{href:"./parameters#tts_platform",children:(0,s.jsx)(t.code,{children:"tts_platform"})})," values."]}),"\n",(0,s.jsx)(t.h3,{id:"basic-example",children:"Basic example"}),"\n",(0,s.jsx)(t.pre,{children:(0,s.jsx)(t.code,{children:"service: chime_tts.say\ntarget:\n  entity_id:\n    - media_player.living_room\ndata:\n  tts_platform: google_translate\n  message: Hello world!\n"})}),"\n",(0,s.jsx)("audio",{controls:!0,src:(0,i.Ay)("/audio/examples/basic.mp3?v=1")}),"\n",(0,s.jsx)(t.h3,{id:"chime_path",children:(0,s.jsx)(t.code,{children:"chime_path"})}),"\n",(0,s.jsxs)(t.p,{children:["Use ",(0,s.jsx)(t.a,{href:"./parameters#chime_path",children:(0,s.jsx)(t.code,{children:"chime_path"})})," to play a chime before the TTS audio (using a 'Chime TTS' chime):"]}),"\n",(0,s.jsx)(t.pre,{children:(0,s.jsx)(t.code,{children:"service: chime_tts.say\ntarget:\n  entity_id:\n    - media_player.living_room\ndata:\n  tts_platform: google_translate\n  message: Hello world!\n  chime_path: tada\n"})}),"\n",(0,s.jsx)("audio",{controls:!0,src:(0,i.Ay)("/audio/examples/chime_path.mp3?v=1"),class:"audio"}),"\n",(0,s.jsx)(t.h3,{id:"end_chime_path",children:(0,s.jsx)(t.code,{children:"end_chime_path"})}),"\n",(0,s.jsxs)(t.p,{children:["Use ",(0,s.jsx)(t.a,{href:"./parameters#end_chime_path",children:(0,s.jsx)(t.code,{children:"end_chime_path"})})," to play a chime after the TTS audio (from your media folder)"]}),"\n",(0,s.jsx)(t.pre,{children:(0,s.jsx)(t.code,{children:"service: chime_tts.say\ntarget:\n  entity_id:\n    - media_player.living_room\ndata:\n  tts_platform: google_translate\n  message: Hello world!\n  end_chime_path: /media/sounds/doorbell.mp3\n"})}),"\n",(0,s.jsx)("audio",{controls:!0,src:(0,i.Ay)("/audio/examples/end_chime_path.mp3?v=1"),class:"audio"}),"\n",(0,s.jsxs)(t.h3,{id:"chime_path-and-end_chime_path",children:[(0,s.jsx)(t.code,{children:"chime_path"})," and ",(0,s.jsx)(t.code,{children:"end_chime_path"})]}),"\n",(0,s.jsxs)(t.p,{children:["Include both ",(0,s.jsx)(t.a,{href:"./parameters#chime_path",children:(0,s.jsx)(t.code,{children:"chime_path"})})," and ",(0,s.jsx)(t.a,{href:"./parameters#end_chime_path",children:(0,s.jsx)(t.code,{children:"end_chime_path"})})," to play a chime before and after TTS audio"]}),"\n",(0,s.jsx)(t.pre,{children:(0,s.jsx)(t.code,{children:"service: chime_tts.say\ntarget:\n  entity_id:\n    - media_player.living_room\ndata:\n  tts_platform: google_translate\n  message: Hello world!\n  chime_path: drumroll\n  end_chime_path: /media/sounds/doorbell.mp3\n"})}),"\n",(0,s.jsx)("audio",{controls:!0,src:(0,i.Ay)("/audio/examples/chime_path_end_chime_path.mp3?v=1")}),"\n",(0,s.jsx)(t.h2,{id:"more-complex-examples",children:"More complex examples"}),"\n",(0,s.jsx)(t.h3,{id:"tts_speed",children:(0,s.jsx)(t.code,{children:"tts_speed"})}),"\n",(0,s.jsxs)(t.p,{children:["Use the ",(0,s.jsx)(t.a,{href:"./parameters#tts_speed",children:(0,s.jsx)(t.code,{children:"tts_speed"})})," parameter to increase/decrease the TTS audio speed"]}),"\n",(0,s.jsx)(t.h4,{id:"increase-speed",children:"Increase speed"}),"\n",(0,s.jsx)(t.pre,{children:(0,s.jsx)(t.code,{children:"service: chime_tts.say\ntarget:\n  entity_id:\n    - media_player.kitchen\n    - media_player.dining_room\ndata:\n  chime_path: bells_2\n  message: The washing's done!\n  tts_platform: amazon_polly\n  tts_speed: 150\n"})}),"\n",(0,s.jsx)("audio",{controls:!0,src:(0,i.Ay)("/audio/examples/speed_increase.mp3?v=1")}),"\n",(0,s.jsx)(t.h4,{id:"decrease-speed",children:"Decrease speed"}),"\n",(0,s.jsx)(t.pre,{children:(0,s.jsx)(t.code,{children:"service: chime_tts.say\ntarget:\n  entity_id:\n    - media_player.kitchen\n    - media_player.dining_room\ndata:\n  chime_path: bells_2\n  message: The washing's done!\n  tts_platform: amazon_polly\n  tts_speed: 75\n"})}),"\n",(0,s.jsx)("audio",{controls:!0,src:(0,i.Ay)("/audio/examples/speed_decrease.mp3?v=1")}),"\n",(0,s.jsx)(t.h3,{id:"tts_pitch",children:(0,s.jsx)(t.code,{children:"tts_pitch"})}),"\n",(0,s.jsxs)(t.p,{children:["Use the ",(0,s.jsx)(t.a,{href:"./parameters#tts_pitch",children:(0,s.jsx)(t.code,{children:"tts_pitch"})})," parameter to raise/lower the pitch of the TTS audio"]}),"\n",(0,s.jsx)(t.h4,{id:"raise-pitch",children:"Raise pitch"}),"\n",(0,s.jsx)(t.pre,{children:(0,s.jsx)(t.code,{children:"service: chime_tts.say\ntarget:\n  entity_id:\n    - media_player.kitchen\n    - media_player.dining_room\ndata:\n  chime_path: chord\n  message: The washing's done!\n  tts_platform: amazon_polly\n  tts_pitch: 5\n"})}),"\n",(0,s.jsx)("audio",{controls:!0,src:(0,i.Ay)("/audio/examples/pitch_raise.mp3?v=1")}),"\n",(0,s.jsx)(t.h4,{id:"lower-pitch",children:"Lower pitch"}),"\n",(0,s.jsx)(t.pre,{children:(0,s.jsx)(t.code,{children:"service: chime_tts.say\ntarget:\n  entity_id:\n    - media_player.kitchen\n    - media_player.dining_room\ndata:\n  chime_path: chord\n  message: The washing's done!\n  tts_platform: amazon_polly\n  tts_pitch: -7\n"})}),"\n",(0,s.jsx)("audio",{controls:!0,src:(0,i.Ay)("/audio/examples/pitch_lower.mp3?v=1")}),"\n",(0,s.jsx)(t.h4,{id:"musical-fun",children:"Musical Fun"}),"\n",(0,s.jsx)(t.pre,{children:(0,s.jsx)(t.code,{children:"service: chime_tts.say\ntarget:\n  entity_id:\n    - media_player.kitchen\n    - media_player.dining_room\ndata:\n  tts_platform: google_translate\n  message:\n    - tts: Laah\n      pitch: -12\n      speed: 90\n    - tts: Laah\n      pitch: 0\n      speed: 125\n      offset: -400\n    - tts: Laah\n      pitch: 4\n      speed: 90\n      offset: -400\n    - tts: Laah\n      pitch: 7\n      speed: 125\n      offset: -400\n    - tts: Laah\n      pitch: -15\n      speed: 90\n      offset: -400\n    - tts: Laah\n      pitch: -3\n      speed: 125\n      offset: -400\n    - tts: Laah\n      pitch: 1\n      speed: 90\n      offset: -400\n    - tts: Laah\n      pitch: 4\n      speed: 125\n      offset: -400\n    - tts: Laah\n      pitch: -19\n      speed: 90\n      offset: -400\n    - tts: Laah\n      pitch: -7\n      speed: 125\n      offset: -400\n    - tts: Laah\n      pitch: -3\n      speed: 90\n      offset: -400\n    - tts: Laah\n      pitch: 0\n      speed: 125\n      offset: -400\n    - tts: Laah\n      pitch: -17\n      speed: 90\n      offset: -400\n    - tts: Laah\n      pitch: -5\n      speed: 125\n      offset: -400\n    - tts: Laah\n      pitch: -1\n      speed: 90\n      offset: -400\n    - tts: Laah\n      pitch: 2\n      speed: 125\n      offset: -400\n    - tts: Laah\n      pitch: 12\n      speed: 70\n      offset: -4916\n    - tts: Laah\n      pitch: 12\n      speed: 70\n      offset: -4340\n    - tts: Laah\n      pitch: 12\n      speed: 39.05\n      offset: -3950\n    - tts: Laah\n      pitch: 12\n      speed: 125\n      offset: -2300\n    - tts: Laah\n      pitch: 11\n      speed: 90\n      offset: -2150\n    - tts: Laah\n      pitch: 9\n      speed: 125\n      offset: -1800\n    - tts: Laah\n      pitch: 11\n      speed: 90\n      offset: -1600\n    - tts: Laah\n      pitch: 12\n      speed: 125\n      offset: -1200\n    - tts: Laah\n      pitch: 15\n      speed: 90\n      offset: -1000\n"})}),"\n",(0,s.jsx)("audio",{controls:!0,src:(0,i.Ay)("/audio/examples/musical_fun.mp3?v=1")}),"\n",(0,s.jsx)(t.h3,{id:"offset",children:(0,s.jsx)(t.code,{children:"offset"})}),"\n",(0,s.jsxs)(t.p,{children:["Use the ",(0,s.jsx)(t.a,{href:"./parameters#offset",children:(0,s.jsx)(t.code,{children:"offset"})})," parameter to shift the start of chime/TTS audio backward (to overlap) or forward (to add a delay)"]}),"\n",(0,s.jsx)(t.h4,{id:"positive-offset-delay-audio",children:"Positive Offset (delay audio)"}),"\n",(0,s.jsxs)(t.p,{children:["Using a positive ",(0,s.jsx)(t.a,{href:"./parameters#offset",children:(0,s.jsx)(t.code,{children:"offset"})})," value adds a delay between chimes and TTS audio."]}),"\n",(0,s.jsx)(t.pre,{children:(0,s.jsx)(t.code,{children:"service: chime_tts.say\ntarget:\n  entity_id:\n    - media_player.kitchen\n    - media_player.dining_room\ndata:\n  chime_path: drumroll\n  end_chime_path: tada\n  message: The suspense is killing me\n  tts_platform: google_translate\n  offset: 2000\n"})}),"\n",(0,s.jsx)("audio",{controls:!0,src:(0,i.Ay)("/audio/examples/offset_delay.mp3?v=1")}),"\n",(0,s.jsx)(t.h4,{id:"negative-offset-overlay-audio",children:"Negative Offset (overlay audio)"}),"\n",(0,s.jsxs)(t.p,{children:["Using a negative ",(0,s.jsx)(t.a,{href:"./parameters#offset",children:(0,s.jsx)(t.code,{children:"offset"})})," value overlays chimes and TTS audio on top of each other."]}),"\n",(0,s.jsx)(t.pre,{children:(0,s.jsx)(t.code,{children:"service: chime_tts.say\ntarget:\n  entity_id:\n    - media_player.kitchen\n    - media_player.dining_room\ndata:\n  chime_path: soft\n  message: It's time to go to work\n  tts_platform: google_translate\n  offset: -2100\n"})}),"\n",(0,s.jsx)("audio",{controls:!0,src:(0,i.Ay)("/audio/examples/offset_overlay.mp3?v=1")}),"\n",(0,s.jsxs)(t.h3,{id:"language-and-tld",children:[(0,s.jsx)(t.code,{children:"language"})," and ",(0,s.jsx)(t.code,{children:"tld"})]}),"\n",(0,s.jsxs)(t.p,{children:["You can use ",(0,s.jsx)(t.a,{href:"./parameters#language",children:(0,s.jsx)(t.code,{children:"language"})})," and ",(0,s.jsx)(t.a,{href:"./parameters#tld",children:(0,s.jsx)(t.code,{children:"tld"})})," to play TTS audio with a different language and/or accent on the ",(0,s.jsx)(t.a,{href:"https://www.home-assistant.io/integrations/google_translate/",children:"Google Translate"})," TTS platform"]}),"\n",(0,s.jsx)(t.pre,{children:(0,s.jsx)(t.code,{children:"service: chime_tts.say\ntarget:\n  entity_id:\n    - media_player.kitchen\n    - media_player.dining_room\ndata:\n  chime_path: tada\n  message: le lavage est fait!\n  tts_platform: google_translate\n  language: fr\n  tld: fr\n"})}),"\n",(0,s.jsx)("audio",{controls:!0,src:(0,i.Ay)("/audio/examples/language.mp3?v=1")}),"\n",(0,s.jsx)(t.h3,{id:"join_players",children:(0,s.jsx)(t.code,{children:"join_players"})}),"\n",(0,s.jsxs)(t.p,{children:["Use the ",(0,s.jsx)(t.a,{href:"./parameters#join_players",children:(0,s.jsx)(t.code,{children:"join_players"})})," parameter to hear the announcement across multiple speakers at the same time (only on supported speakers)"]}),"\n",(0,s.jsx)(t.pre,{children:(0,s.jsx)(t.code,{children:"service: chime_tts.say\ntarget:\n  entity_id:\n    - media_player.kitchen\n    - media_player.dining_room\n    - media_player.bedroom\ndata:\n  chime_path: tada\n  message: The washing's done!\n  tts_platform: amazon_polly\n  join_players: true\n  unjoin_players: true\n"})}),"\n",(0,s.jsx)("audio",{controls:!0,src:(0,i.Ay)("/audio/examples/join_players.mp3?v=1")}),"\n",(0,s.jsx)(t.h2,{id:"message-segments",children:"Message Segments"}),"\n",(0,s.jsxs)(t.p,{children:["The ",(0,s.jsx)(t.code,{children:"message"})," parameter can be used to specify multiple ",(0,s.jsx)(t.a,{href:"./parameters#advanced-usage-segment-sequences",children:(0,s.jsx)(t.code,{children:"message segments"})})," which can be used to construct complicated notifications of muliple chimes & TTS audio segments."]}),"\n",(0,s.jsxs)(t.h3,{id:"tts-segment-type",children:[(0,s.jsx)(t.code,{children:"tts"})," Segment Type"]}),"\n",(0,s.jsxs)(t.p,{children:["Review the ",(0,s.jsx)(t.a,{href:"./parameters#tts-segment-type",children:"tts segment type"})," documentation to learn more."]}),"\n",(0,s.jsx)(t.pre,{children:(0,s.jsx)(t.code,{children:"service: chime_tts.say\ntarget:\n  entity_id: media_player.kitchen_speaker\ndata:\n  chime_path: classical\n  end_chime_path: marimba\n  tts_platform: google_translate\n  cache: false\n  language: en\n  message:\n    - tts: May I please have your attention?\n      cache: true\n    - tts: It is officially time to move the washing to the dryer\n      offset: 3000\n      options:\n        tld: co.uk\n    - tts: V\xe1monos!\n      language: es\n      options:\n        tld: es\n      tts_speed: 115\n    - type: tts\n      message: Let's go!\n      tts_platform: amazon_polly\n"})}),"\n",(0,s.jsx)("audio",{controls:!0,src:(0,i.Ay)("/audio/examples/segments_tts.mp3?v=1")}),"\n",(0,s.jsx)(t.p,{children:"In the above example:"}),"\n",(0,s.jsxs)(t.ul,{children:["\n",(0,s.jsx)(t.li,{children:"The 1st segment overrides the cache parameter, setting it to true for the segment."}),"\n",(0,s.jsx)(t.li,{children:"The 2nd segment adds a 3 second delay before the TTS message and overrides the domain, setting it to the UK."}),"\n",(0,s.jsx)(t.li,{children:"The 3rd segment overrides the language, setting it to Spanish with the domain accent of Spain, and sets the speech rate to 115%."}),"\n",(0,s.jsx)(t.li,{children:"The 4th segment overrides the TTS platform, setting it to Amazon Polly."}),"\n"]}),"\n",(0,s.jsxs)(t.h3,{id:"chime-segment-type",children:[(0,s.jsx)(t.code,{children:"chime"})," Segment Type"]}),"\n",(0,s.jsxs)(t.p,{children:["Review the ",(0,s.jsx)(t.a,{href:"./parameters#chime-segment-type",children:"chime segment type"})," documentation to learn more."]}),"\n",(0,s.jsx)(t.pre,{children:(0,s.jsx)(t.code,{children:"service: chime_tts.say\ntarget:\n  entity_id: media_player.kitchen_speaker\ndata:\n  chime_path: toast\n  end_chime_path: tada\n  tts_platform: google_translate\n  message:\n    - tts: And the winner is, drumroll please\n    - chime: drumroll\n      offset: 500\n    - tts: You!\n      offset: 0\n    - chime: /config/media/sounds/my_chimes/hooray.mp3\n    - tts: You get to move the washing to the dryer!\n    - chime: dun_dun_dun\n    - tts: Sorry. You're the only one with arms.\n"})}),"\n",(0,s.jsx)("audio",{controls:!0,src:(0,i.Ay)("/audio/examples/segments_chime.mp3?v=1")}),"\n",(0,s.jsxs)(t.h3,{id:"delay-segment-type",children:[(0,s.jsx)(t.code,{children:"delay"})," Segment Type"]}),"\n",(0,s.jsxs)(t.p,{children:["Review the ",(0,s.jsx)(t.a,{href:"./parameters#delay-segment-type",children:"delay segment type"})," documentation to learn more."]}),"\n",(0,s.jsx)(t.pre,{children:(0,s.jsx)(t.code,{children:"service: chime_tts.say\ntarget:\n  entity_id: media_player.kitchen_speaker\ndata:\n  tts_platform: google_translate\n  message:\n    - tts: Hey, do you hear that? Just listen.\n    - delay: 1000\n    - tts: Yep, sounds like clothes waiting to be moved to the dryer\n"})}),"\n",(0,s.jsx)("audio",{controls:!0,src:(0,i.Ay)("/audio/examples/segments_delay.mp3?v=1")}),"\n",(0,s.jsx)(t.h3,{id:"repeat",children:(0,s.jsx)(t.code,{children:"repeat"})}),"\n",(0,s.jsxs)(t.p,{children:["All message segment types can include a ",(0,s.jsx)(t.code,{children:"repeat"})," parameter to specify the number of times to repeat the segment."]}),"\n",(0,s.jsx)(t.pre,{children:(0,s.jsx)(t.code,{children:"service: chime_tts.say\ntarget:\n  entity_id: media_player.macbook_air\ndata:\n  tts_platform: google_translate\n  message:\n    - chime: https://www.zapsplat.com/wp-content/uploads/2015/sound-effects-three/household_clock_cuckoo_strike_001.mp3\n      repeat: 3\n      offset: -800\n    - tts: It's 3 o'clock\n"})}),"\n",(0,s.jsx)("audio",{controls:!0,src:(0,i.Ay)("/audio/parameters/repeat.mp3?v=1")})]})}function p(e={}){const{wrapper:t}={...(0,a.R)(),...e.components};return t?(0,s.jsx)(t,{...e,children:(0,s.jsx)(h,{...e})}):h(e)}},8453:(e,t,n)=>{n.d(t,{R:()=>d,x:()=>r});var s=n(6540);const a={},i=s.createContext(a);function d(e){const t=s.useContext(i);return s.useMemo((function(){return"function"==typeof e?e(t):{...t,...e}}),[t,e])}function r(e){let t;return t=e.disableParentContext?"function"==typeof e.components?e.components(a):e.components||a:d(e.components),s.createElement(i.Provider,{value:t},e.children)}}}]);