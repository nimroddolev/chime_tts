"use strict";(self.webpackChunkchime_tts=self.webpackChunkchime_tts||[]).push([[4890],{7073:(e,t,n)=>{n.r(t),n.d(t,{assets:()=>o,contentTitle:()=>c,default:()=>u,frontMatter:()=>l,metadata:()=>i,toc:()=>a});const i=JSON.parse('{"id":"documentation/configuration","title":"Configuration","description":"You can configure the following options for the chimetts.say and chimetts.sayurl actions through the integration\'s configuration page:","source":"@site/docs/documentation/configuration.mdx","sourceDirName":"documentation","slug":"/documentation/configuration","permalink":"/chime_tts/docs/documentation/configuration","draft":false,"unlisted":false,"tags":[],"version":"current","sidebarPosition":1,"frontMatter":{"sidebar_position":1},"sidebar":"tutorialSidebar","previous":{"title":"1. Documentation","permalink":"/chime_tts/docs/documentation/"},"next":{"title":"1. Actions","permalink":"/chime_tts/docs/documentation/actions/"}}');var s=n(4848),d=n(8453),r=n(6025);const l={sidebar_position:1},c="Configuration",o={},a=[{value:"Timeout",id:"timeout",level:3},{value:"Default TTS Platform",id:"default-tts-platform",level:3},{value:"Default Language",id:"default-language",level:3},{value:"Default Voice",id:"default-voice",level:3},{value:"Default Dialect",id:"default-dialect",level:3},{value:"Fallback TTS Platform",id:"fallback-tts-platform",level:3},{value:"Default Offset",id:"default-offset",level:3},{value:"Fade Transition",id:"fade-transition",level:3},{value:"Delay Before Removing Temporary Files",id:"delay-before-removing-temporary-files",level:3},{value:"Custom Chimes Folder",id:"custom-chimes-folder",level:3},{value:"Downloaded Chimes Folder",id:"downloaded-chimes-folder",level:3},{value:"Temporary MP3 Folder",id:"temporary-mp3-folder",level:3},{value:"<code>chime_tts.say_url</code> Folder",id:"chime_ttssay_url-folder",level:3},{value:"MP3 Cover Art",id:"mp3-cover-art",level:3}];function h(e){const t={a:"a",admonition:"admonition",code:"code",em:"em",h1:"h1",h3:"h3",header:"header",hr:"hr",p:"p",...(0,d.R)(),...e.components};return(0,s.jsxs)(s.Fragment,{children:[(0,s.jsx)(t.header,{children:(0,s.jsx)(t.h1,{id:"configuration",children:"Configuration"})}),"\n",(0,s.jsxs)(t.p,{children:["You can configure the following options for the ",(0,s.jsx)(t.a,{href:"/chime_tts/docs/documentation/actions/say-action",children:(0,s.jsx)(t.code,{children:"chime_tts.say"})})," and ",(0,s.jsx)(t.a,{href:"/chime_tts/docs/documentation/actions/say_url-action",children:(0,s.jsx)(t.code,{children:"chime_tts.say_url"})})," actions through the integration's configuration page:"]}),"\n",(0,s.jsx)("a",{href:"https://my.home-assistant.io/redirect/integration/?domain=chime_tts",alt:"Chime TTS integration",target:"_blank",children:(0,s.jsx)("img",{src:(0,r.Ay)("/img/documentation/show_chime_tts_on_my.png")})}),"\n",(0,s.jsx)(t.h3,{id:"timeout",children:"Timeout"}),"\n",(0,s.jsxs)(t.p,{children:["The duration (in seconds) to wait before cancelling the ",(0,s.jsx)(t.a,{href:"/chime_tts/docs/documentation/actions/say-action",children:(0,s.jsx)(t.code,{children:"chime_tts.say"})})," or ",(0,s.jsx)(t.a,{href:"/chime_tts/docs/documentation/actions/say_url-action",children:(0,s.jsx)(t.code,{children:"chime_tts.say_url"})})," action calls."]}),"\n",(0,s.jsxs)("table",{children:[(0,s.jsxs)("tr",{children:[(0,s.jsx)("td",{children:(0,s.jsx)("b",{children:"Default Value:"})}),(0,s.jsx)("td",{children:(0,s.jsx)(t.code,{children:"60"})})]}),(0,s.jsxs)("tr",{children:[(0,s.jsx)("td",{children:(0,s.jsx)("b",{children:"Required:"})}),(0,s.jsx)("td",{children:"Yes"})]})]}),"\n",(0,s.jsx)(t.admonition,{type:"tip",children:(0,s.jsx)(t.p,{children:"Increase the timeout duration intend to generate audio longer than 60 seconds in length."})}),"\n",(0,s.jsx)(t.hr,{}),"\n",(0,s.jsx)(t.h3,{id:"default-tts-platform",children:"Default TTS Platform"}),"\n",(0,s.jsxs)(t.p,{children:["The default ",(0,s.jsx)(t.a,{href:"/chime_tts/docs/documentation/actions/say-action/parameters#tts_platform",children:(0,s.jsx)(t.code,{children:"tts_platform"})})," value to use when not specified."]}),"\n",(0,s.jsxs)("table",{children:[(0,s.jsxs)("tr",{children:[(0,s.jsx)("td",{children:(0,s.jsx)("b",{children:"Default Value:"})}),(0,s.jsx)("td",{children:"None"})]}),(0,s.jsxs)("tr",{children:[(0,s.jsx)("td",{children:(0,s.jsx)("b",{children:"Required:"})}),(0,s.jsx)("td",{children:"No"})]})]}),"\n",(0,s.jsx)(t.hr,{}),"\n",(0,s.jsx)(t.h3,{id:"default-language",children:"Default Language"}),"\n",(0,s.jsxs)(t.p,{children:["The default [",(0,s.jsx)(t.code,{children:"language"}),"]((/chime_tts/docs/documentation/actions/say-action/parameters#language) value to use if the [",(0,s.jsx)(t.code,{children:"tts_platform"}),"]((/chime_tts/docs/documentation/actions/say-action/parameters#tts_platform) is set to the default TTS platform."]}),"\n",(0,s.jsxs)("table",{children:[(0,s.jsxs)("tr",{children:[(0,s.jsx)("td",{children:(0,s.jsx)("b",{children:"Default Value:"})}),(0,s.jsx)("td",{children:"None"})]}),(0,s.jsxs)("tr",{children:[(0,s.jsx)("td",{children:(0,s.jsx)("b",{children:"Required:"})}),(0,s.jsx)("td",{children:"No"})]})]}),"\n",(0,s.jsx)(t.hr,{}),"\n",(0,s.jsx)(t.h3,{id:"default-voice",children:"Default Voice"}),"\n",(0,s.jsxs)(t.p,{children:["The default [",(0,s.jsx)(t.code,{children:"voice"}),"]((/chime_tts/docs/documentation/actions/say-action/parameters#voice) value to use if the [",(0,s.jsx)(t.code,{children:"tts_platform"}),"]((/chime_tts/docs/documentation/actions/say-action/parameters#tts_platform) is set to the default TTS platform."]}),"\n",(0,s.jsxs)("table",{children:[(0,s.jsxs)("tr",{children:[(0,s.jsx)("td",{children:(0,s.jsx)("b",{children:"Default Value:"})}),(0,s.jsx)("td",{children:"None"})]}),(0,s.jsxs)("tr",{children:[(0,s.jsx)("td",{children:(0,s.jsx)("b",{children:"Required:"})}),(0,s.jsx)("td",{children:"No"})]})]}),"\n",(0,s.jsx)(t.hr,{}),"\n",(0,s.jsx)(t.h3,{id:"default-dialect",children:"Default Dialect"}),"\n",(0,s.jsxs)(t.p,{children:["The default dialect domain (",(0,s.jsx)(t.a,{href:"/chime_tts/docs/documentation/actions/say-action/parameters#tld",children:(0,s.jsx)(t.code,{children:"tld"})}),") value if the [",(0,s.jsx)(t.code,{children:"tts_platform"}),"]((/chime_tts/docs/documentation/actions/say-action/parameters#tts_platform) is set to Google Translate."]}),"\n",(0,s.jsxs)("table",{children:[(0,s.jsxs)("tr",{children:[(0,s.jsx)("td",{children:(0,s.jsx)("b",{children:"Default Value:"})}),(0,s.jsx)("td",{children:"None"})]}),(0,s.jsxs)("tr",{children:[(0,s.jsx)("td",{children:(0,s.jsx)("b",{children:"Required:"})}),(0,s.jsx)("td",{children:"No"})]})]}),"\n",(0,s.jsx)(t.hr,{}),"\n",(0,s.jsx)(t.h3,{id:"fallback-tts-platform",children:"Fallback TTS Platform"}),"\n",(0,s.jsx)(t.p,{children:"The TTS platform to use if an error occured when using the specified or default platform."}),"\n",(0,s.jsxs)("table",{children:[(0,s.jsxs)("tr",{children:[(0,s.jsx)("td",{children:(0,s.jsx)("b",{children:"Default Value:"})}),(0,s.jsx)("td",{children:"None"})]}),(0,s.jsxs)("tr",{children:[(0,s.jsx)("td",{children:(0,s.jsx)("b",{children:"Required:"})}),(0,s.jsx)("td",{children:"No"})]})]}),"\n",(0,s.jsx)(t.hr,{}),"\n",(0,s.jsx)(t.h3,{id:"default-offset",children:"Default Offset"}),"\n",(0,s.jsxs)(t.p,{children:["The default [offset]((/chime_tts/docs/documentation/actions/say-action/parameters#offset) duration (in milliseconds) between chimes and TTS audio.",(0,s.jsx)("br",{}),"\nPositive values introduce a delay, while negative values overlap the audio segments."]}),"\n",(0,s.jsxs)("table",{children:[(0,s.jsxs)("tr",{children:[(0,s.jsx)("td",{children:(0,s.jsx)("b",{children:"Default Value:"})}),(0,s.jsx)("td",{children:(0,s.jsx)(t.code,{children:"450"})})]}),(0,s.jsxs)("tr",{children:[(0,s.jsx)("td",{children:(0,s.jsx)("b",{children:"Required:"})}),(0,s.jsx)("td",{children:"No"})]})]}),"\n",(0,s.jsx)(t.hr,{}),"\n",(0,s.jsx)(t.h3,{id:"fade-transition",children:"Fade Transition"}),"\n",(0,s.jsxs)(t.p,{children:["The fade out duration (in milliseconds) of the now playing audio ",(0,s.jsx)(t.em,{children:"before"})," an announcement and fading it duration of the now playing music ",(0,s.jsx)(t.em,{children:"afterwards"}),"."]}),"\n",(0,s.jsx)(t.p,{children:(0,s.jsxs)(t.em,{children:["This applies to [",(0,s.jsx)(t.code,{children:"chime_tts.say"}),"]((/chime_tts/docs/documentation/actions/say-action) action calls when the [",(0,s.jsx)(t.code,{children:"announce"}),"]((/chime_tts/docs/documentation/actions/say-action/parameters#announce) or [",(0,s.jsx)(t.code,{children:"fade_audio"}),"]((/chime_tts/docs/documentation/actions/say-action/parameters#fade_audio) parameters are used."]})}),"\n",(0,s.jsxs)("table",{children:[(0,s.jsxs)("tr",{children:[(0,s.jsx)("td",{children:(0,s.jsx)("b",{children:"Default Value:"})}),(0,s.jsx)("td",{children:(0,s.jsx)(t.code,{children:"500"})})]}),(0,s.jsxs)("tr",{children:[(0,s.jsx)("td",{children:(0,s.jsx)("b",{children:"Required:"})}),(0,s.jsx)("td",{children:"No"})]})]}),"\n",(0,s.jsx)(t.hr,{}),"\n",(0,s.jsx)(t.h3,{id:"delay-before-removing-temporary-files",children:"Delay Before Removing Temporary Files"}),"\n",(0,s.jsxs)(t.p,{children:["The delay duaration after [",(0,s.jsx)(t.code,{children:"chime_tts.say"}),"]((/chime_tts/docs/documentation/actions/say-action) playback is completed (in milliseconds), before removing the generated temporary audio file."]}),"\n",(0,s.jsxs)("table",{children:[(0,s.jsxs)("tr",{children:[(0,s.jsx)("td",{children:(0,s.jsx)("b",{children:"Default Value:"})}),(0,s.jsx)("td",{children:"None"})]}),(0,s.jsxs)("tr",{children:[(0,s.jsx)("td",{children:(0,s.jsx)("b",{children:"Required:"})}),(0,s.jsx)("td",{children:"No"})]})]}),"\n",(0,s.jsx)(t.hr,{}),"\n",(0,s.jsx)(t.h3,{id:"custom-chimes-folder",children:"Custom Chimes Folder"}),"\n",(0,s.jsx)(t.p,{children:"The local folder path containing custom audio files."}),"\n",(0,s.jsx)(t.p,{children:"Any changes to the folder path or its contents will require a restart to take effect. [More info]((/chime_tts/docs/documentation/actions/say-action/#custom-chimes-folder)"}),"\n",(0,s.jsxs)("table",{children:[(0,s.jsxs)("tr",{children:[(0,s.jsx)("td",{children:(0,s.jsx)("b",{children:"Default Value:"})}),(0,s.jsx)("td",{children:"None"})]}),(0,s.jsxs)("tr",{children:[(0,s.jsx)("td",{children:(0,s.jsx)("b",{children:"Required:"})}),(0,s.jsx)("td",{children:"No"})]})]}),"\n",(0,s.jsx)(t.hr,{}),"\n",(0,s.jsx)(t.h3,{id:"downloaded-chimes-folder",children:"Downloaded Chimes Folder"}),"\n",(0,s.jsx)(t.p,{children:"The local folder path where downloaded chime MP3 files will be stored."}),"\n",(0,s.jsxs)("table",{children:[(0,s.jsxs)("tr",{children:[(0,s.jsx)("td",{children:(0,s.jsx)("b",{children:"Default Value:"})}),(0,s.jsx)("td",{children:(0,s.jsx)(t.code,{children:"{root}/media/sounds/temp/chime_tts/chimes/"})})]}),(0,s.jsxs)("tr",{children:[(0,s.jsx)("td",{children:(0,s.jsx)("b",{children:"Required:"})}),(0,s.jsx)("td",{children:"Yes"})]})]}),"\n",(0,s.jsx)(t.hr,{}),"\n",(0,s.jsx)(t.h3,{id:"temporary-mp3-folder",children:"Temporary MP3 Folder"}),"\n",(0,s.jsx)(t.p,{children:"The local folder path where generated MP3 files will be stored."}),"\n",(0,s.jsxs)("table",{children:[(0,s.jsxs)("tr",{children:[(0,s.jsx)("td",{children:(0,s.jsx)("b",{children:"Default Value:"})}),(0,s.jsx)("td",{children:(0,s.jsx)(t.code,{children:"{root}/media/sounds/temp/chime_tts/"})})]}),(0,s.jsxs)("tr",{children:[(0,s.jsx)("td",{children:(0,s.jsx)("b",{children:"Required:"})}),(0,s.jsx)("td",{children:"Yes"})]})]}),"\n",(0,s.jsx)(t.admonition,{title:"Please Note",type:"warning",children:(0,s.jsxs)(t.p,{children:["Make sure the temporary folder path is inside a ",(0,s.jsx)(t.a,{href:"https://www.home-assistant.io/integrations/media_source/",children:"media folder"})," of your Home Assistant, otherwise the [",(0,s.jsx)(t.code,{children:"chime_tts.say"}),"]((/chime_tts/docs/documentation/actions/say-action) action will not be able to play the generated MP3 on your media_players."]})}),"\n",(0,s.jsx)(t.hr,{}),"\n",(0,s.jsxs)(t.h3,{id:"chime_ttssay_url-folder",children:[(0,s.jsx)(t.code,{children:"chime_tts.say_url"})," Folder"]}),"\n",(0,s.jsxs)(t.p,{children:["The publicly facing folder path where MP3 files generated by the [",(0,s.jsx)(t.code,{children:"chime_tts.say_url"}),"]((/chime_tts/docs/documentation/actions/say_url-action) action will be stored."]}),"\n",(0,s.jsxs)("table",{children:[(0,s.jsxs)("tr",{children:[(0,s.jsx)("td",{children:(0,s.jsx)("b",{children:"Default Value:"})}),(0,s.jsx)("td",{children:(0,s.jsx)(t.code,{children:"{root}/config/www/chime_tts/"})})]}),(0,s.jsxs)("tr",{children:[(0,s.jsx)("td",{children:(0,s.jsx)("b",{children:"Required:"})}),(0,s.jsx)("td",{children:"Yes"})]})]}),"\n",(0,s.jsx)(t.hr,{}),"\n",(0,s.jsx)(t.h3,{id:"mp3-cover-art",children:"MP3 Cover Art"}),"\n",(0,s.jsx)(t.p,{children:"When enabled, adds the Chime TTS logo as the cover art in generated MP3 files."}),"\n",(0,s.jsxs)("table",{children:[(0,s.jsxs)("tr",{children:[(0,s.jsx)("td",{children:(0,s.jsx)("b",{children:"Default Value:"})}),(0,s.jsx)("td",{children:(0,s.jsx)(t.code,{children:"false"})})]}),(0,s.jsxs)("tr",{children:[(0,s.jsx)("td",{children:(0,s.jsx)("b",{children:"Required:"})}),(0,s.jsx)("td",{children:"No"})]})]})]})}function u(e={}){const{wrapper:t}={...(0,d.R)(),...e.components};return t?(0,s.jsx)(t,{...e,children:(0,s.jsx)(h,{...e})}):h(e)}},8453:(e,t,n)=>{n.d(t,{R:()=>r,x:()=>l});var i=n(6540);const s={},d=i.createContext(s);function r(e){const t=i.useContext(d);return i.useMemo((function(){return"function"==typeof e?e(t):{...t,...e}}),[t,e])}function l(e){let t;return t=e.disableParentContext?"function"==typeof e.components?e.components(s):e.components||s:r(e.components),i.createElement(d.Provider,{value:t},e.children)}}}]);