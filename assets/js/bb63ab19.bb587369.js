"use strict";(self.webpackChunkchime_tts=self.webpackChunkchime_tts||[]).push([[4629],{4513:(e,i,s)=>{s.r(i),s.d(i,{assets:()=>h,contentTitle:()=>r,default:()=>d,frontMatter:()=>c,metadata:()=>o,toc:()=>a});var t=s(4848),n=s(8453);s(6025);const c={sidebar_position:1,title:"Service"},r="chime_tts.say Service",o={id:"say-service/service",title:"Service",description:'The chimetts.say service joins together audio files, or *"chimes"*, and TTS audio, and then streams it to mediaplayer target/s.',source:"@site/docs/say-service/service.mdx",sourceDirName:"say-service",slug:"/say-service/service",permalink:"/chime_tts/docs/say-service/service",draft:!1,unlisted:!1,tags:[],version:"current",sidebarPosition:1,frontMatter:{sidebar_position:1,title:"Service"},sidebar:"tutorialSidebar",previous:{title:"Say Service",permalink:"/chime_tts/docs/category/say-service"},next:{title:"Parameters",permalink:"/chime_tts/docs/say-service/parameters"}},h={},a=[{value:"Selecting Chimes",id:"selecting-chimes",level:2},{value:"1. Select chimes from the user-interface",id:"1-select-chimes-from-the-user-interface",level:3},{value:"2. Custom local audio files and external URLs",id:"2-custom-local-audio-files-and-external-urls",level:3},{value:"Local Files",id:"local-files",level:4},{value:"External audio file URLs",id:"external-audio-file-urls",level:4},{value:"3. Custom chime slots for the chime list UI",id:"3-custom-chime-slots-for-the-chime-list-ui",level:3}];function l(e){const i={a:"a",code:"code",em:"em",h1:"h1",h2:"h2",h3:"h3",h4:"h4",hr:"hr",img:"img",li:"li",p:"p",strong:"strong",ul:"ul",...(0,n.R)(),...e.components};return(0,t.jsxs)(t.Fragment,{children:[(0,t.jsxs)(i.h1,{id:"chime_ttssay-service",children:[(0,t.jsx)(i.code,{children:"chime_tts.say"})," Service"]}),"\n",(0,t.jsxs)(i.p,{children:["The ",(0,t.jsx)(i.code,{children:"chime_tts.say"})," service joins together audio files, or ",(0,t.jsx)(i.em,{children:'"chimes"'}),", and TTS audio, and then streams it to ",(0,t.jsx)(i.code,{children:"media_player"})," target/s."]}),"\n",(0,t.jsxs)(i.p,{children:[(0,t.jsx)(i.strong,{children:"Please note"})," that Chime TTS works ",(0,t.jsx)(i.strong,{children:"with"})," ",(0,t.jsx)(i.a,{href:"https://www.home-assistant.io/integrations/#text-to-speech",children:"TTS Platform integrations"}),", but you need to add them to your Home Assistant instance beforehand."]}),"\n",(0,t.jsx)(i.hr,{}),"\n",(0,t.jsx)(i.h2,{id:"selecting-chimes",children:"Selecting Chimes"}),"\n",(0,t.jsxs)(i.p,{children:["Chimes are audio files that can be incorporated into notifications. You can find the preset chimes that ship with Chime TTS ",(0,t.jsx)(i.a,{href:"https://github.com/nimroddolev/chime_tts/tree/main/custom_components/chime_tts/mp3s",children:"here"}),"."]}),"\n",(0,t.jsx)(i.p,{children:"You can add chimes to your notifications in different places:"}),"\n",(0,t.jsxs)(i.ul,{children:["\n",(0,t.jsxs)(i.li,{children:[(0,t.jsx)(i.strong,{children:"Before"})," TTS audio ",(0,t.jsx)(i.em,{children:"(see the"})," ",(0,t.jsx)(i.a,{href:"../say-service/parameters#chime_path",children:(0,t.jsx)(i.code,{children:"chime_path"})})," ",(0,t.jsx)(i.em,{children:"parameter)."})]}),"\n",(0,t.jsxs)(i.li,{children:[(0,t.jsx)(i.strong,{children:"After"})," TTS audio ",(0,t.jsx)(i.em,{children:"(see the"})," ",(0,t.jsx)(i.a,{href:"../say-service/parameters#end_chime_path",children:(0,t.jsx)(i.code,{children:"end_chime_path"})})," ",(0,t.jsx)(i.em,{children:"parameter)"}),", and"]}),"\n",(0,t.jsxs)(i.li,{children:[(0,t.jsx)(i.strong,{children:"Between"})," TTS audio ",(0,t.jsx)(i.em,{children:"(see the use of"})," ",(0,t.jsx)(i.a,{href:"../say-service/parameters#advanced-usage-segment-sequences",children:(0,t.jsx)(i.code,{children:"message"})})," ",(0,t.jsx)(i.em,{children:"segments)."})]}),"\n"]}),"\n",(0,t.jsx)(i.p,{children:"There are 3 different ways to define which chime/s to include in your notification:"}),"\n",(0,t.jsx)(i.h3,{id:"1-select-chimes-from-the-user-interface",children:"1. Select chimes from the user-interface"}),"\n",(0,t.jsx)(i.p,{children:"Use the drop-down chime list in the UI to select a preset chime sound effect:"}),"\n",(0,t.jsx)(i.p,{children:(0,t.jsx)(i.img,{src:"https://raw.githubusercontent.com/nimroddolev/chime_tts/main/images/wiki/chimes/chime_options.gif",alt:"chime_options"})}),"\n",(0,t.jsx)(i.h3,{id:"2-custom-local-audio-files-and-external-urls",children:"2. Custom local audio files and external URLs"}),"\n",(0,t.jsxs)(i.ul,{children:["\n",(0,t.jsxs)(i.li,{children:["\n",(0,t.jsx)(i.h4,{id:"local-files",children:"Local Files"}),"\n",(0,t.jsx)(i.p,{children:"You can specify local file paths to your own audio files from your Home Assistant instance's media folder, or any other folder."}),"\n",(0,t.jsx)(i.p,{children:(0,t.jsx)(i.img,{src:"https://raw.githubusercontent.com/nimroddolev/chime_tts/main/images/wiki/chimes/chime_path.png",alt:"chime_path"})}),"\n"]}),"\n",(0,t.jsxs)(i.li,{children:["\n",(0,t.jsx)(i.h4,{id:"external-audio-file-urls",children:"External audio file URLs"}),"\n",(0,t.jsxs)(i.p,{children:["You can also specify URLs to audio files hosted online. Chime TTS will download the files and you can optionally save them to your chimes folder if the ",(0,t.jsx)(i.a,{href:"../say-service/parameters#cache",children:(0,t.jsx)(i.code,{children:"cache"})})," property is set to ",(0,t.jsx)(i.code,{children:"true"}),"."]}),"\n",(0,t.jsx)(i.p,{children:(0,t.jsx)(i.img,{src:"https://github.com/nimroddolev/chime_tts/assets/1849295/91adf68c-f77d-4c45-b341-93e392792e31",alt:"external_chime_path"})}),"\n"]}),"\n"]}),"\n",(0,t.jsx)(i.h3,{id:"3-custom-chime-slots-for-the-chime-list-ui",children:"3. Custom chime slots for the chime list UI"}),"\n",(0,t.jsx)(i.p,{children:"You can set up to 5 custom chime slots which appear at the end of the drop-down list in the UI, allowing you to easily select your custom chimes when creating automations.\nTo configure the custom chime slots, open the Chime TTS configuration page and enter the full file path to your local custom audio file, or the URL to an audio file hosted online."}),"\n",(0,t.jsx)(i.p,{children:"The configuration page is located at:"}),"\n",(0,t.jsxs)(i.p,{children:[(0,t.jsx)(i.code,{children:"Settings"})," --\x3e ",(0,t.jsx)(i.code,{children:"Devices & services"})," --\x3e ",(0,t.jsx)(i.code,{children:"Chime TTS"})," --\x3e ",(0,t.jsx)(i.code,{children:"CONFIGURE"})]}),"\n",(0,t.jsx)(i.p,{children:(0,t.jsx)(i.img,{src:"https://github.com/nimroddolev/chime_tts/assets/1849295/c0e186a2-5fc5-4b0c-9eb8-7089bcec6721",alt:"configuration"})}),"\n",(0,t.jsx)(i.p,{children:"Once added, you can use your custom chimes by selecting them from the chime list UI:"}),"\n",(0,t.jsx)(i.p,{children:(0,t.jsx)(i.img,{src:"https://raw.githubusercontent.com/nimroddolev/chime_tts/main/images/wiki/chimes/custom_1.gif",alt:"custom"})})]})}function d(e={}){const{wrapper:i}={...(0,n.R)(),...e.components};return i?(0,t.jsx)(i,{...e,children:(0,t.jsx)(l,{...e})}):l(e)}},8453:(e,i,s)=>{s.d(i,{R:()=>r,x:()=>o});var t=s(6540);const n={},c=t.createContext(n);function r(e){const i=t.useContext(c);return t.useMemo((function(){return"function"==typeof e?e(i):{...i,...e}}),[i,e])}function o(e){let i;return i=e.disableParentContext?"function"==typeof e.components?e.components(n):e.components||n:r(e.components),t.createElement(c.Provider,{value:i},e.children)}}}]);