"use strict";(self.webpackChunkchime_tts=self.webpackChunkchime_tts||[]).push([[9552],{1111:(e,t,s)=>{s.r(t),s.d(t,{assets:()=>l,contentTitle:()=>c,default:()=>x,frontMatter:()=>o,metadata:()=>d,toc:()=>h});var i=s(4848),r=s(8453),n=s(6025);const o={sidebar_position:3},c="3. Configuration",d={id:"quick-start/configuration",title:"3. Configuration",description:"You can customise the following elements for the chimetts.say and chimetts.say_url services through the configuration page, located at:",source:"@site/docs/quick-start/configuration.mdx",sourceDirName:"quick-start",slug:"/quick-start/configuration",permalink:"/chime_tts/docs/quick-start/configuration",draft:!1,unlisted:!1,tags:[],version:"current",sidebarPosition:3,frontMatter:{sidebar_position:3},sidebar:"tutorialSidebar",previous:{title:"2. Adding the Integration",permalink:"/chime_tts/docs/quick-start/adding-the-integration"},next:{title:"Say Service",permalink:"/chime_tts/docs/category/say-service"}},l={},h=[];function a(e){const t={a:"a",code:"code",em:"em",h1:"h1",p:"p",strong:"strong",table:"table",tbody:"tbody",td:"td",th:"th",thead:"thead",tr:"tr",...(0,r.R)(),...e.components};return(0,i.jsxs)(i.Fragment,{children:[(0,i.jsx)(t.h1,{id:"3-configuration",children:"3. Configuration"}),"\n",(0,i.jsxs)(t.p,{children:["You can customise the following elements for the ",(0,i.jsx)(t.code,{children:"chime_tts.say"})," and ",(0,i.jsx)(t.code,{children:"chime_tts.say_url"})," services through the configuration page, located at:"]}),"\n",(0,i.jsxs)(t.p,{children:[(0,i.jsx)(t.code,{children:"Settings"})," --\x3e ",(0,i.jsx)(t.code,{children:"Devices & services"})," --\x3e ",(0,i.jsx)(t.code,{children:"Chime TTS"})," --\x3e ",(0,i.jsx)(t.code,{children:"CONFIGURE"})]}),"\n",(0,i.jsx)("img",{src:(0,n.A)("/img/quick-start/configuration.png")}),"\n",(0,i.jsxs)(t.table,{children:[(0,i.jsx)(t.thead,{children:(0,i.jsxs)(t.tr,{children:[(0,i.jsx)(t.th,{children:"Config Option"}),(0,i.jsx)(t.th,{children:"Description"}),(0,i.jsx)(t.th,{children:"Default Value"})]})}),(0,i.jsxs)(t.tbody,{children:[(0,i.jsxs)(t.tr,{children:[(0,i.jsx)(t.td,{children:(0,i.jsx)(t.strong,{children:"Timeout"})}),(0,i.jsx)(t.td,{children:"Set the time (in seconds) to wait before service calls are terminated."}),(0,i.jsx)(t.td,{children:(0,i.jsx)(t.code,{children:"60"})})]}),(0,i.jsxs)(t.tr,{children:[(0,i.jsx)(t.td,{children:(0,i.jsx)(t.strong,{children:"Default TTS Platform"})}),(0,i.jsxs)(t.td,{children:["The TTS platform to use if service calls are missing the ",(0,i.jsx)(t.code,{children:"tts_platform"})," parameter."]}),(0,i.jsx)(t.td,{children:(0,i.jsx)(t.em,{children:"The first TTS platform configured in your Home Assistant instance."})})]}),(0,i.jsxs)(t.tr,{children:[(0,i.jsx)(t.td,{children:(0,i.jsx)(t.strong,{children:"Default Offset"})}),(0,i.jsx)(t.td,{children:"The default offset (in milliseconds) to insert between chimes & TTS audio. Positive values will add a delay and negative values will overlay audio segments on top of each other."}),(0,i.jsx)(t.td,{children:(0,i.jsx)(t.code,{children:"450"})})]}),(0,i.jsxs)(t.tr,{children:[(0,i.jsx)(t.td,{children:(0,i.jsx)(t.strong,{children:"Media Folder"})}),(0,i.jsx)(t.td,{children:"The name of your media folder."}),(0,i.jsx)(t.td,{children:(0,i.jsx)(t.code,{children:"local"})})]}),(0,i.jsxs)(t.tr,{children:[(0,i.jsx)(t.td,{children:(0,i.jsx)(t.strong,{children:"Downloaded Chimes Folder"})}),(0,i.jsx)(t.td,{children:"The local folder path to store downloaded chime mp3 files."}),(0,i.jsx)(t.td,{children:(0,i.jsx)(t.code,{children:"{root}/media/sounds/temp/chime_tts/"})})]}),(0,i.jsxs)(t.tr,{children:[(0,i.jsx)(t.td,{children:(0,i.jsx)(t.strong,{children:"Temporary MP3 Folder"})}),(0,i.jsx)(t.td,{children:"The local folder path to store the generated mp3 files."}),(0,i.jsx)(t.td,{children:(0,i.jsx)(t.code,{children:"{root}/media/sounds/temp/chime_tts/"})})]}),(0,i.jsxs)(t.tr,{children:[(0,i.jsx)(t.td,{children:(0,i.jsx)(t.strong,{children:"chime_tts.say_url Folder"})}),(0,i.jsxs)(t.td,{children:["The folder path to store MP3 files generated by the ",(0,i.jsx)(t.a,{href:"../say_url-service/service",children:"chime_tts.say_url"})," service."]}),(0,i.jsx)(t.td,{children:(0,i.jsx)(t.code,{children:"{root}/config/www/chime_tts/"})})]}),(0,i.jsxs)(t.tr,{children:[(0,i.jsx)(t.td,{children:(0,i.jsx)(t.strong,{children:"Custom Chimes"})}),(0,i.jsx)(t.td,{children:"Add up to 5 file paths / URLs to your own custom chime files."}),(0,i.jsx)(t.td,{children:"None"})]})]})]})]})}function x(e={}){const{wrapper:t}={...(0,r.R)(),...e.components};return t?(0,i.jsx)(t,{...e,children:(0,i.jsx)(a,{...e})}):a(e)}},8453:(e,t,s)=>{s.d(t,{R:()=>o,x:()=>c});var i=s(6540);const r={},n=i.createContext(r);function o(e){const t=i.useContext(n);return i.useMemo((function(){return"function"==typeof e?e(t):{...t,...e}}),[t,e])}function c(e){let t;return t=e.disableParentContext?"function"==typeof e.components?e.components(r):e.components||r:o(e.components),i.createElement(n.Provider,{value:t},e.children)}}}]);