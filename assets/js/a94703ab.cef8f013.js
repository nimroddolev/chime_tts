"use strict";(self.webpackChunkchime_tts=self.webpackChunkchime_tts||[]).push([[9048],{1377:(e,t,n)=>{n.r(t),n.d(t,{default:()=>pe});var a=n(6540),i=n(4164),o=n(1213),s=n(7559),l=n(6972),c=n(609),r=n(1312),d=n(3104),m=n(5062);const u={backToTopButton:"backToTopButton_sjWU",backToTopButtonShow:"backToTopButtonShow_xfvO"};var h=n(4848);function b(){const{shown:e,scrollToTop:t}=function(e){let{threshold:t}=e;const[n,i]=(0,a.useState)(!1),o=(0,a.useRef)(!1),{startScroll:s,cancelScroll:l}=(0,d.gk)();return(0,d.Mq)(((e,n)=>{let{scrollY:a}=e;const s=n?.scrollY;s&&(o.current?o.current=!1:a>=s?(l(),i(!1)):a<t?i(!1):a+window.innerHeight<document.documentElement.scrollHeight&&i(!0))})),(0,m.$)((e=>{e.location.hash&&(o.current=!0,i(!1))})),{shown:n,scrollToTop:()=>s(0)}}({threshold:300});return(0,h.jsx)("button",{"aria-label":(0,r.T)({id:"theme.BackToTopButton.buttonAriaLabel",message:"Scroll back to top",description:"The ARIA label for the back to top button"}),className:(0,i.A)("clean-btn",s.G.common.backToTopButton,u.backToTopButton,e&&u.backToTopButtonShow),type:"button",onClick:t})}var p=n(3109),x=n(6347),j=n(4581),f=n(6342),g=n(3465);function _(e){return(0,h.jsx)("svg",{width:"20",height:"20","aria-hidden":"true",...e,children:(0,h.jsxs)("g",{fill:"#7a7a7a",children:[(0,h.jsx)("path",{d:"M9.992 10.023c0 .2-.062.399-.172.547l-4.996 7.492a.982.982 0 01-.828.454H1c-.55 0-1-.453-1-1 0-.2.059-.403.168-.551l4.629-6.942L.168 3.078A.939.939 0 010 2.528c0-.548.45-.997 1-.997h2.996c.352 0 .649.18.828.45L9.82 9.472c.11.148.172.347.172.55zm0 0"}),(0,h.jsx)("path",{d:"M19.98 10.023c0 .2-.058.399-.168.547l-4.996 7.492a.987.987 0 01-.828.454h-3c-.547 0-.996-.453-.996-1 0-.2.059-.403.168-.551l4.625-6.942-4.625-6.945a.939.939 0 01-.168-.55 1 1 0 01.996-.997h3c.348 0 .649.18.828.45l4.996 7.492c.11.148.168.347.168.55zm0 0"})]})})}const v="collapseSidebarButton_PEFL",A="collapseSidebarButtonIcon_kv0_";function C(e){let{onClick:t}=e;return(0,h.jsx)("button",{type:"button",title:(0,r.T)({id:"theme.docs.sidebar.collapseButtonTitle",message:"Collapse sidebar",description:"The title attribute for collapse button of doc sidebar"}),"aria-label":(0,r.T)({id:"theme.docs.sidebar.collapseButtonAriaLabel",message:"Collapse sidebar",description:"The title attribute for collapse button of doc sidebar"}),className:(0,i.A)("button button--secondary button--outline",v),onClick:t,children:(0,h.jsx)(_,{className:A})})}var k=n(5041),S=n(9532);const T=Symbol("EmptyContext"),N=a.createContext(T);function I(e){let{children:t}=e;const[n,i]=(0,a.useState)(null),o=(0,a.useMemo)((()=>({expandedItem:n,setExpandedItem:i})),[n]);return(0,h.jsx)(N.Provider,{value:o,children:t})}var y=n(1422),B=n(9169),w=n(8774),L=n(2303);function E(e){let{collapsed:t,categoryLabel:n,onClick:a}=e;return(0,h.jsx)("button",{"aria-label":t?(0,r.T)({id:"theme.DocSidebarItem.expandCategoryAriaLabel",message:"Expand sidebar category '{label}'",description:"The ARIA label to expand the sidebar category"},{label:n}):(0,r.T)({id:"theme.DocSidebarItem.collapseCategoryAriaLabel",message:"Collapse sidebar category '{label}'",description:"The ARIA label to collapse the sidebar category"},{label:n}),"aria-expanded":!t,type:"button",className:"clean-btn menu__caret",onClick:a})}function M(e){let{item:t,onItemClick:n,activePath:o,level:c,index:r,...d}=e;const{items:m,label:u,collapsible:b,className:p,href:x}=t,{docs:{sidebar:{autoCollapseCategories:j}}}=(0,f.p)(),g=function(e){const t=(0,L.A)();return(0,a.useMemo)((()=>e.href&&!e.linkUnlisted?e.href:!t&&e.collapsible?(0,l.Nr)(e):void 0),[e,t])}(t),_=(0,l.w8)(t,o),v=(0,B.ys)(x,o),{collapsed:A,setCollapsed:C}=(0,y.u)({initialState:()=>!!b&&(!_&&t.collapsed)}),{expandedItem:k,setExpandedItem:I}=function(){const e=(0,a.useContext)(N);if(e===T)throw new S.dV("DocSidebarItemsExpandedStateProvider");return e}(),M=function(e){void 0===e&&(e=!A),I(e?null:r),C(e)};return function(e){let{isActive:t,collapsed:n,updateCollapsed:i}=e;const o=(0,S.ZC)(t);(0,a.useEffect)((()=>{t&&!o&&n&&i(!1)}),[t,o,n,i])}({isActive:_,collapsed:A,updateCollapsed:M}),(0,a.useEffect)((()=>{b&&null!=k&&k!==r&&j&&C(!0)}),[b,k,r,C,j]),(0,h.jsxs)("li",{className:(0,i.A)(s.G.docs.docSidebarItemCategory,s.G.docs.docSidebarItemCategoryLevel(c),"menu__list-item",{"menu__list-item--collapsed":A},p),children:[(0,h.jsxs)("div",{className:(0,i.A)("menu__list-item-collapsible",{"menu__list-item-collapsible--active":v}),children:[(0,h.jsx)(w.A,{className:(0,i.A)("menu__link",{"menu__link--sublist":b,"menu__link--sublist-caret":!x&&b,"menu__link--active":_}),onClick:b?e=>{n?.(t),x?M(!1):(e.preventDefault(),M())}:()=>{n?.(t)},"aria-current":v?"page":void 0,role:b&&!x?"button":void 0,"aria-expanded":b&&!x?!A:void 0,href:b?g??"#":g,...d,children:u}),x&&b&&(0,h.jsx)(E,{collapsed:A,categoryLabel:u,onClick:e=>{e.preventDefault(),M()}})]}),(0,h.jsx)(y.N,{lazy:!0,as:"ul",className:"menu__list",collapsed:A,children:(0,h.jsx)(V,{items:m,tabIndex:A?-1:0,onItemClick:n,activePath:o,level:c+1})})]})}var H=n(6654),G=n(3186);const P="menuExternalLink_NmtK";function R(e){let{item:t,onItemClick:n,activePath:a,level:o,index:c,...r}=e;const{href:d,label:m,className:u,autoAddBaseUrl:b}=t,p=(0,l.w8)(t,a),x=(0,H.A)(d);return(0,h.jsx)("li",{className:(0,i.A)(s.G.docs.docSidebarItemLink,s.G.docs.docSidebarItemLinkLevel(o),"menu__list-item",u),children:(0,h.jsxs)(w.A,{className:(0,i.A)("menu__link",!x&&P,{"menu__link--active":p}),autoAddBaseUrl:b,"aria-current":p?"page":void 0,to:d,...x&&{onClick:n?()=>n(t):void 0},...r,children:[m,!x&&(0,h.jsx)(G.A,{})]})},m)}const W="menuHtmlItem_M9Kj";function D(e){let{item:t,level:n,index:a}=e;const{value:o,defaultStyle:l,className:c}=t;return(0,h.jsx)("li",{className:(0,i.A)(s.G.docs.docSidebarItemLink,s.G.docs.docSidebarItemLinkLevel(n),l&&[W,"menu__list-item"],c),dangerouslySetInnerHTML:{__html:o}},a)}function F(e){let{item:t,...n}=e;switch(t.type){case"category":return(0,h.jsx)(M,{item:t,...n});case"html":return(0,h.jsx)(D,{item:t,...n});default:return(0,h.jsx)(R,{item:t,...n})}}function U(e){let{items:t,...n}=e;const a=(0,l.Y)(t,n.activePath);return(0,h.jsx)(I,{children:a.map(((e,t)=>(0,h.jsx)(F,{item:e,index:t,...n},t)))})}const V=(0,a.memo)(U),Y="menu_SIkG",K="menuWithAnnouncementBar_GW3s";function z(e){let{path:t,sidebar:n,className:o}=e;const l=function(){const{isActive:e}=(0,k.M)(),[t,n]=(0,a.useState)(e);return(0,d.Mq)((t=>{let{scrollY:a}=t;e&&n(0===a)}),[e]),e&&t}();return(0,h.jsx)("nav",{"aria-label":(0,r.T)({id:"theme.docs.sidebar.navAriaLabel",message:"Docs sidebar",description:"The ARIA label for the sidebar navigation"}),className:(0,i.A)("menu thin-scrollbar",Y,l&&K,o),children:(0,h.jsx)("ul",{className:(0,i.A)(s.G.docs.docSidebarMenu,"menu__list"),children:(0,h.jsx)(V,{items:n,activePath:t,level:1})})})}const q="sidebar_njMd",O="sidebarWithHideableNavbar_wUlq",J="sidebarHidden_VK0M",Q="sidebarLogo_isFc";function X(e){let{path:t,sidebar:n,onCollapse:a,isHidden:o}=e;const{navbar:{hideOnScroll:s},docs:{sidebar:{hideable:l}}}=(0,f.p)();return(0,h.jsxs)("div",{className:(0,i.A)(q,s&&O,o&&J),children:[s&&(0,h.jsx)(g.A,{tabIndex:-1,className:Q}),(0,h.jsx)(z,{path:t,sidebar:n}),l&&(0,h.jsx)(C,{onClick:a})]})}const Z=a.memo(X);var $=n(5600),ee=n(9876);const te=e=>{let{sidebar:t,path:n}=e;const a=(0,ee.M)();return(0,h.jsx)("ul",{className:(0,i.A)(s.G.docs.docSidebarMenu,"menu__list"),children:(0,h.jsx)(V,{items:t,activePath:n,onItemClick:e=>{"category"===e.type&&e.href&&a.toggle(),"link"===e.type&&a.toggle()},level:1})})};function ne(e){return(0,h.jsx)($.GX,{component:te,props:e})}const ae=a.memo(ne);function ie(e){const t=(0,j.l)(),n="desktop"===t||"ssr"===t,a="mobile"===t;return(0,h.jsxs)(h.Fragment,{children:[n&&(0,h.jsx)(Z,{...e}),a&&(0,h.jsx)(ae,{...e})]})}const oe={expandButton:"expandButton_TmdG",expandButtonIcon:"expandButtonIcon_i1dp"};function se(e){let{toggleSidebar:t}=e;return(0,h.jsx)("div",{className:oe.expandButton,title:(0,r.T)({id:"theme.docs.sidebar.expandButtonTitle",message:"Expand sidebar",description:"The ARIA label and title attribute for expand button of doc sidebar"}),"aria-label":(0,r.T)({id:"theme.docs.sidebar.expandButtonAriaLabel",message:"Expand sidebar",description:"The ARIA label and title attribute for expand button of doc sidebar"}),tabIndex:0,role:"button",onKeyDown:t,onClick:t,children:(0,h.jsx)(_,{className:oe.expandButtonIcon})})}const le={docSidebarContainer:"docSidebarContainer_YfHR",docSidebarContainerHidden:"docSidebarContainerHidden_DPk8",sidebarViewport:"sidebarViewport_aRkj"};function ce(e){let{children:t}=e;const n=(0,c.t)();return(0,h.jsx)(a.Fragment,{children:t},n?.name??"noSidebar")}function re(e){let{sidebar:t,hiddenSidebarContainer:n,setHiddenSidebarContainer:o}=e;const{pathname:l}=(0,x.zy)(),[c,r]=(0,a.useState)(!1),d=(0,a.useCallback)((()=>{c&&r(!1),!c&&(0,p.O)()&&r(!0),o((e=>!e))}),[o,c]);return(0,h.jsx)("aside",{className:(0,i.A)(s.G.docs.docSidebarContainer,le.docSidebarContainer,n&&le.docSidebarContainerHidden),onTransitionEnd:e=>{e.currentTarget.classList.contains(le.docSidebarContainer)&&n&&r(!0)},children:(0,h.jsx)(ce,{children:(0,h.jsxs)("div",{className:(0,i.A)(le.sidebarViewport,c&&le.sidebarViewportHidden),children:[(0,h.jsx)(ie,{sidebar:t,path:l,onCollapse:d,isHidden:c}),c&&(0,h.jsx)(se,{toggleSidebar:d})]})})})}const de={docMainContainer:"docMainContainer_TBSr",docMainContainerEnhanced:"docMainContainerEnhanced_lQrH",docItemWrapperEnhanced:"docItemWrapperEnhanced_JWYK"};function me(e){let{hiddenSidebarContainer:t,children:n}=e;const a=(0,c.t)();return(0,h.jsx)("main",{className:(0,i.A)(de.docMainContainer,(t||!a)&&de.docMainContainerEnhanced),children:(0,h.jsx)("div",{className:(0,i.A)("container padding-top--md padding-bottom--lg",de.docItemWrapper,t&&de.docItemWrapperEnhanced),children:n})})}const ue={docRoot:"docRoot_UBD9",docsWrapper:"docsWrapper_hBAB"};function he(e){let{children:t}=e;const n=(0,c.t)(),[i,o]=(0,a.useState)(!1);return(0,h.jsxs)("div",{className:ue.docsWrapper,children:[(0,h.jsx)(b,{}),(0,h.jsxs)("div",{className:ue.docRoot,children:[n&&(0,h.jsx)(re,{sidebar:n.items,hiddenSidebarContainer:i,setHiddenSidebarContainer:o}),(0,h.jsx)(me,{hiddenSidebarContainer:i,children:t})]})]})}var be=n(5955);function pe(e){const t=(0,l.B5)(e);if(!t)return(0,h.jsx)(be.A,{});const{docElement:n,sidebarName:a,sidebarItems:r}=t;return(0,h.jsx)(o.e3,{className:(0,i.A)(s.G.page.docsDocPage),children:(0,h.jsx)(c.V,{name:a,items:r,children:(0,h.jsx)(he,{children:n})})})}},5955:(e,t,n)=>{n.d(t,{A:()=>c});n(6540);var a=n(4164),i=n(1312),o=n(1107),s=n(6025),l=n(4848);function c(e){let{className:t}=e;return(0,l.jsx)("main",{className:(0,a.A)("container margin-vert--xl",t),children:(0,l.jsxs)("div",{className:"row",children:[(0,l.jsxs)("div",{class:"animContainer",children:[(0,l.jsx)("img",{src:(0,s.Ay)("/img/chime_tts.png"),class:"bottom-image hideAnimation"}),(0,l.jsx)("img",{src:(0,s.Ay)("/img/animations/missing_chime_tts.png"),class:"bottom-image showAnimation hidden"}),(0,l.jsx)("div",{class:"top-image animation"})]}),(0,l.jsxs)("div",{className:"col col--6 col--offset-1",children:[(0,l.jsx)(o.A,{as:"h1",className:"hero__title",children:(0,l.jsx)(i.A,{id:"theme.NotFound.title",description:"The title of the 404 page",children:"Page Not Found"})}),(0,l.jsx)("p",{children:(0,l.jsx)(i.A,{id:"theme.NotFound.p1",description:"The first paragraph of the 404 page",children:"We could not find what you were looking for."})}),(0,l.jsx)("p",{children:(0,l.jsx)(i.A,{id:"theme.NotFound.p2",description:"The 2nd paragraph of the 404 page",children:"Please contact the owner of the site that linked you to the original URL and let them know their link is broken."})})]})]})})}}}]);