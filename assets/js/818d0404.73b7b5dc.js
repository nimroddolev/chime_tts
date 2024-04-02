"use strict";(self.webpackChunkchime_tts=self.webpackChunkchime_tts||[]).push([[6618],{1193:(e,c,t)=>{t.r(c),t.d(c,{assets:()=>h,contentTitle:()=>i,default:()=>o,frontMatter:()=>a,metadata:()=>n,toc:()=>l});var s=t(4848),r=t(8453);t(6025);const a={sidebar_position:5,title:"Clear Cache Service"},i="chime_tts.clear_cache Service",n={id:"documentation/clear-cache-service",title:"Clear Cache Service",description:"The chimetts.clearcache service can be used to remove cached audio files from the chimetts.say and chimetts.sayurl services as well as Home Assistant's TTS cache.",source:"@site/docs/documentation/clear-cache-service.mdx",sourceDirName:"documentation",slug:"/documentation/clear-cache-service",permalink:"/chime_tts/docs/documentation/clear-cache-service",draft:!1,unlisted:!1,tags:[],version:"current",sidebarPosition:5,frontMatter:{sidebar_position:5,title:"Clear Cache Service"},sidebar:"tutorialSidebar",previous:{title:"Examples",permalink:"/chime_tts/docs/documentation/say_url-service/examples"}},h={},l=[{value:"Parameters",id:"parameters",level:2},{value:"YAML Example",id:"yaml-example",level:2}];function d(e){const c={a:"a",code:"code",h1:"h1",h2:"h2",p:"p",pre:"pre",table:"table",tbody:"tbody",td:"td",th:"th",thead:"thead",tr:"tr",...(0,r.R)(),...e.components};return(0,s.jsxs)(s.Fragment,{children:[(0,s.jsxs)(c.h1,{id:"chime_ttsclear_cache-service",children:[(0,s.jsx)(c.code,{children:"chime_tts.clear_cache"})," Service"]}),"\n",(0,s.jsxs)(c.p,{children:["The ",(0,s.jsx)(c.code,{children:"chime_tts.clear_cache"})," service can be used to remove cached audio files from the ",(0,s.jsx)(c.a,{href:"./say-service",children:(0,s.jsx)(c.code,{children:"chime_tts.say"})})," and ",(0,s.jsx)(c.a,{href:"./say_url-service",children:(0,s.jsx)(c.code,{children:"chime_tts.say_url"})})," services as well as Home Assistant's TTS cache."]}),"\n",(0,s.jsx)(c.h2,{id:"parameters",children:"Parameters"}),"\n",(0,s.jsx)(c.p,{children:"The following parameters allow you to control which type of cached files to clear:"}),"\n",(0,s.jsxs)(c.table,{children:[(0,s.jsx)(c.thead,{children:(0,s.jsxs)(c.tr,{children:[(0,s.jsx)(c.th,{children:"Parameter"}),(0,s.jsx)(c.th,{children:"Description"})]})}),(0,s.jsxs)(c.tbody,{children:[(0,s.jsxs)(c.tr,{children:[(0,s.jsx)(c.td,{children:(0,s.jsx)(c.code,{children:"clear_chimes_cache"})}),(0,s.jsx)(c.td,{children:"Remove the cached local chime files downloaded by Chime TTS"})]}),(0,s.jsxs)(c.tr,{children:[(0,s.jsx)(c.td,{children:(0,s.jsx)(c.code,{children:"clear_temp_tts_cache"})}),(0,s.jsx)(c.td,{children:"Remove the local temporary audio files stored in the Chime TTS cache"})]}),(0,s.jsxs)(c.tr,{children:[(0,s.jsx)(c.td,{children:(0,s.jsx)(c.code,{children:"clear_www_tts_cache"})}),(0,s.jsx)(c.td,{children:"Remove the publicly accessible audio files stored in the Chime TTS cache"})]}),(0,s.jsxs)(c.tr,{children:[(0,s.jsx)(c.td,{children:(0,s.jsx)(c.code,{children:"clear_ha_tts_cache"})}),(0,s.jsx)(c.td,{children:"Remove the TTS audio files stored in the Home Assistant TTS cache"})]})]})]}),"\n",(0,s.jsx)(c.h2,{id:"yaml-example",children:"YAML Example"}),"\n",(0,s.jsx)(c.pre,{children:(0,s.jsx)(c.code,{children:"service: chime_tts.clear_cache\ndata:\n  clear_chimes_cache: true\n  clear_temp_tts_cache: true\n  clear_www_tts_cache: true\n  clear_ha_tts_cache: true\n"})})]})}function o(e={}){const{wrapper:c}={...(0,r.R)(),...e.components};return c?(0,s.jsx)(c,{...e,children:(0,s.jsx)(d,{...e})}):d(e)}},8453:(e,c,t)=>{t.d(c,{R:()=>i,x:()=>n});var s=t(6540);const r={},a=s.createContext(r);function i(e){const c=s.useContext(a);return s.useMemo((function(){return"function"==typeof e?e(c):{...c,...e}}),[c,e])}function n(e){let c;return c=e.disableParentContext?"function"==typeof e.components?e.components(r):e.components||r:i(e.components),s.createElement(a.Provider,{value:c},e.children)}}}]);