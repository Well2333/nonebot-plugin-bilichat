import{j as t,F as e,k as n,m as o,x as r,g as l,i,r as s,b as a,c as u,aq as d,a as c,U as f,C as h,ar as p,B as m,n as v,D as g,a5 as b,u as y,o as w,q as x,as as S,w as R,O as T,E as $,Z as M,at as z,an as C,e as I,f as E,K as B,aa as F,M as O,a6 as L,N as W,s as A,au as j,av as N,aw as k,ax as D,ay as P,az as V,aA as X,aB as H,ap as Y,aC as U}from"./vendor.cCBPk__2.js";function q(t,e,n="default"){const o=e[n];if(void 0===o)throw new Error(`[vueuc/${t}]: slot[${n}] is empty.`);return o()}function K(o,r=!0,l=[]){return o.forEach((o=>{if(null!==o)if("object"==typeof o)if(Array.isArray(o))K(o,r,l);else if(o.type===e){if(null===o.children)return;Array.isArray(o.children)&&K(o.children,r,l)}else o.type!==n&&l.push(o);else"string"!=typeof o&&"number"!=typeof o||l.push(t(String(o)))})),l}function _(t,e,n="default"){const o=e[n];if(void 0===o)throw new Error(`[vueuc/${t}]: slot[${n}] is empty.`);const r=K(o());if(1===r.length)return r[0];throw new Error(`[vueuc/${t}]: slot[${n}] should have exactly one child.`)}let G=null;function Z(){if(null===G&&(G=document.getElementById("v-binder-view-measurer"),null===G)){G=document.createElement("div"),G.id="v-binder-view-measurer";const{style:t}=G;t.position="fixed",t.left="0",t.right="0",t.top="0",t.bottom="0",t.pointerEvents="none",t.visibility="hidden",document.body.appendChild(G)}return G.getBoundingClientRect()}function J(t){const e=t.getBoundingClientRect(),n=Z();return{left:e.left-n.left,top:e.top-n.top,bottom:n.height+n.top-e.bottom,right:n.width+n.left-e.right,width:e.width,height:e.height}}function Q(t){if(null===t)return null;const e=function(t){return 9===t.nodeType?null:t.parentNode}(t);if(null===e)return null;if(9===e.nodeType)return document;if(1===e.nodeType){const{overflow:t,overflowX:n,overflowY:o}=getComputedStyle(e);if(/(auto|scroll|overlay)/.test(t+o+n))return e}return Q(e)}const tt=o({name:"Binder",props:{syncTargetWithParent:Boolean,syncTarget:{type:Boolean,default:!0}},setup(t){var e;r("VBinder",null===(e=l())||void 0===e?void 0:e.proxy);const n=i("VBinder",null),o=s(null);let f=[];const h=()=>{for(const t of f)u("scroll",t,m,!0);f=[]},p=new Set,m=()=>{d(v)},v=()=>{p.forEach((t=>t()))},g=new Set,b=()=>{g.forEach((t=>t()))};return a((()=>{u("resize",window,b),h()})),{targetRef:o,setTargetRef:e=>{o.value=e,n&&t.syncTargetWithParent&&n.setTargetRef(e)},addScrollListener:t=>{0===p.size&&(()=>{let t=o.value;for(;t=Q(t),null!==t;)f.push(t);for(const e of f)c("scroll",e,m,!0)})(),p.has(t)||p.add(t)},removeScrollListener:t=>{p.has(t)&&p.delete(t),0===p.size&&h()},addResizeListener:t=>{0===g.size&&c("resize",window,b),g.has(t)||g.add(t)},removeResizeListener:t=>{g.has(t)&&g.delete(t),0===g.size&&u("resize",window,b)}}},render(){return q("binder",this.$slots)}}),et=o({name:"Target",setup(){const{setTargetRef:t,syncTarget:e}=i("VBinder");return{syncTarget:e,setTargetDirective:{mounted:t,updated:t}}},render(){const{syncTarget:t,setTargetDirective:e}=this;return t?f(_("follower",this.$slots),[[e]]):_("follower",this.$slots)}});function nt(t,e){console.error(`[vueuc/${t}]: ${e}`)}const{c:ot}=h(),rt="vueuc-style";function lt(t){return t&-t}class it{constructor(t,e){this.l=t,this.min=e;const n=new Array(t+1);for(let o=0;o<t+1;++o)n[o]=0;this.ft=n}add(t,e){if(0===e)return;const{l:n,ft:o}=this;for(t+=1;t<=n;)o[t]+=e,t+=lt(t)}get(t){return this.sum(t+1)-this.sum(t)}sum(t){if(void 0===t&&(t=this.l),t<=0)return 0;const{ft:e,min:n,l:o}=this;if(t>o)throw new Error("[FinweckTree.sum]: `i` is larger than length.");let r=t*n;for(;t>0;)r+=e[t],t-=lt(t);return r}getBound(t){let e=0,n=this.l;for(;n>e;){const o=Math.floor((e+n)/2),r=this.sum(o);if(r>t)n=o;else{if(!(r<t))return o;if(e===o)return this.sum(e+1)<=t?e+1:o;e=o}}return e}}function st(t){return"string"==typeof t?document.querySelector(t):t()}const at=o({name:"LazyTeleport",props:{to:{type:[String,Object],default:void 0},disabled:Boolean,show:{type:Boolean,required:!0}},setup:t=>({showTeleport:p(m(t,"show")),mergedTo:v((()=>{const{to:e}=t;return null!=e?e:"body"}))}),render(){return this.showTeleport?this.disabled?q("lazy-teleport",this.$slots):g(b,{disabled:this.disabled,to:this.mergedTo},q("lazy-teleport",this.$slots)):null}}),ut={top:"bottom",bottom:"top",left:"right",right:"left"},dt={start:"end",center:"center",end:"start"},ct={top:"height",bottom:"height",left:"width",right:"width"},ft={"bottom-start":"top left",bottom:"top center","bottom-end":"top right","top-start":"bottom left",top:"bottom center","top-end":"bottom right","right-start":"top left",right:"center left","right-end":"bottom left","left-start":"top right",left:"center right","left-end":"bottom right"},ht={"bottom-start":"bottom left",bottom:"bottom center","bottom-end":"bottom right","top-start":"top left",top:"top center","top-end":"top right","right-start":"top right",right:"center right","right-end":"bottom right","left-start":"top left",left:"center left","left-end":"bottom left"},pt={"bottom-start":"right","bottom-end":"left","top-start":"right","top-end":"left","right-start":"bottom","right-end":"top","left-start":"bottom","left-end":"top"},mt={top:!0,bottom:!1,left:!0,right:!1},vt={top:"end",bottom:"start",left:"end",right:"start"},gt=ot([ot(".v-binder-follower-container",{position:"absolute",left:"0",right:"0",top:"0",height:"0",pointerEvents:"none",zIndex:"auto"}),ot(".v-binder-follower-content",{position:"absolute",zIndex:"auto"},[ot("> *",{pointerEvents:"all"})])]),bt=o({name:"Follower",inheritAttrs:!1,props:{show:Boolean,enabled:{type:Boolean,default:void 0},placement:{type:String,default:"bottom"},syncTrigger:{type:Array,default:["resize","scroll"]},to:[String,Object],flip:{type:Boolean,default:!0},internalShift:Boolean,x:Number,y:Number,width:String,minWidth:String,containerClass:String,teleportDisabled:Boolean,zindexable:{type:Boolean,default:!0},zIndex:Number,overlap:Boolean},setup(t){const e=i("VBinder"),n=y((()=>void 0!==t.enabled?t.enabled:t.show)),o=s(null),r=s(null),l=()=>{const{syncTrigger:n}=t;n.includes("scroll")&&e.addScrollListener(c),n.includes("resize")&&e.addResizeListener(c)},u=()=>{e.removeScrollListener(c),e.removeResizeListener(c)};w((()=>{n.value&&(c(),l())}));const d=x();gt.mount({id:"vueuc/binder",head:!0,anchorMetaName:rt,ssr:d}),a((()=>{u()})),S((()=>{n.value&&c()}));const c=()=>{if(!n.value)return;const l=o.value;if(null===l)return;const i=e.targetRef,{x:s,y:a,overlap:u}=t,d=void 0!==s&&void 0!==a?function(t,e){const n=Z();return{top:e,left:t,height:0,width:0,right:n.width-t,bottom:n.height-e}}(s,a):J(i);l.style.setProperty("--v-target-width",`${Math.round(d.width)}px`),l.style.setProperty("--v-target-height",`${Math.round(d.height)}px`);const{width:c,minWidth:f,placement:h,internalShift:p,flip:m}=t;l.setAttribute("v-placement",h),u?l.setAttribute("v-overlap",""):l.removeAttribute("v-overlap");const{style:v}=l;v.width="target"===c?`${d.width}px`:void 0!==c?c:"",v.minWidth="target"===f?`${d.width}px`:void 0!==f?f:"";const g=J(l),b=J(r.value),{left:y,top:w,placement:x}=function(t,e,n,o,r,l){if(!r||l)return{placement:t,top:0,left:0};const[i,s]=t.split("-");let a=null!=s?s:"center",u={top:0,left:0};const d=(t,r,l)=>{let i=0,s=0;const a=n[t]-e[r]-e[t];return a>0&&o&&(l?s=mt[r]?a:-a:i=mt[r]?a:-a),{left:i,top:s}},c="left"===i||"right"===i;if("center"!==a){const o=pt[t],r=ut[o],l=ct[o];if(n[l]>e[l]){if(e[o]+e[l]<n[l]){const t=(n[l]-e[l])/2;e[o]<t||e[r]<t?e[o]<e[r]?(a=dt[s],u=d(l,r,c)):u=d(l,o,c):a="center"}}else n[l]<e[l]&&e[r]<0&&e[o]>e[r]&&(a=dt[s])}else{const t="bottom"===i||"top"===i?"left":"top",o=ut[t],r=ct[t],l=(n[r]-e[r])/2;(e[t]<l||e[o]<l)&&(e[t]>e[o]?(a=vt[t],u=d(r,t,c)):(a=vt[o],u=d(r,o,c)))}let f=i;return e[i]<n[ct[i]]&&e[i]<e[ut[i]]&&(f=ut[i]),{placement:"center"!==a?`${f}-${a}`:f,left:u.left,top:u.top}}(h,d,g,p,m,u),S=function(t,e){return e?ht[t]:ft[t]}(x,u),{left:R,top:T,transform:$}=function(t,e,n,o,r,l){if(l)switch(t){case"bottom-start":case"left-end":return{top:`${Math.round(n.top-e.top+n.height)}px`,left:`${Math.round(n.left-e.left)}px`,transform:"translateY(-100%)"};case"bottom-end":case"right-end":return{top:`${Math.round(n.top-e.top+n.height)}px`,left:`${Math.round(n.left-e.left+n.width)}px`,transform:"translateX(-100%) translateY(-100%)"};case"top-start":case"left-start":return{top:`${Math.round(n.top-e.top)}px`,left:`${Math.round(n.left-e.left)}px`,transform:""};case"top-end":case"right-start":return{top:`${Math.round(n.top-e.top)}px`,left:`${Math.round(n.left-e.left+n.width)}px`,transform:"translateX(-100%)"};case"top":return{top:`${Math.round(n.top-e.top)}px`,left:`${Math.round(n.left-e.left+n.width/2)}px`,transform:"translateX(-50%)"};case"right":return{top:`${Math.round(n.top-e.top+n.height/2)}px`,left:`${Math.round(n.left-e.left+n.width)}px`,transform:"translateX(-100%) translateY(-50%)"};case"left":return{top:`${Math.round(n.top-e.top+n.height/2)}px`,left:`${Math.round(n.left-e.left)}px`,transform:"translateY(-50%)"};default:return{top:`${Math.round(n.top-e.top+n.height)}px`,left:`${Math.round(n.left-e.left+n.width/2)}px`,transform:"translateX(-50%) translateY(-100%)"}}switch(t){case"bottom-start":return{top:`${Math.round(n.top-e.top+n.height+o)}px`,left:`${Math.round(n.left-e.left+r)}px`,transform:""};case"bottom-end":return{top:`${Math.round(n.top-e.top+n.height+o)}px`,left:`${Math.round(n.left-e.left+n.width+r)}px`,transform:"translateX(-100%)"};case"top-start":return{top:`${Math.round(n.top-e.top+o)}px`,left:`${Math.round(n.left-e.left+r)}px`,transform:"translateY(-100%)"};case"top-end":return{top:`${Math.round(n.top-e.top+o)}px`,left:`${Math.round(n.left-e.left+n.width+r)}px`,transform:"translateX(-100%) translateY(-100%)"};case"right-start":return{top:`${Math.round(n.top-e.top+o)}px`,left:`${Math.round(n.left-e.left+n.width+r)}px`,transform:""};case"right-end":return{top:`${Math.round(n.top-e.top+n.height+o)}px`,left:`${Math.round(n.left-e.left+n.width+r)}px`,transform:"translateY(-100%)"};case"left-start":return{top:`${Math.round(n.top-e.top+o)}px`,left:`${Math.round(n.left-e.left+r)}px`,transform:"translateX(-100%)"};case"left-end":return{top:`${Math.round(n.top-e.top+n.height+o)}px`,left:`${Math.round(n.left-e.left+r)}px`,transform:"translateX(-100%) translateY(-100%)"};case"top":return{top:`${Math.round(n.top-e.top+o)}px`,left:`${Math.round(n.left-e.left+n.width/2+r)}px`,transform:"translateY(-100%) translateX(-50%)"};case"right":return{top:`${Math.round(n.top-e.top+n.height/2+o)}px`,left:`${Math.round(n.left-e.left+n.width+r)}px`,transform:"translateY(-50%)"};case"left":return{top:`${Math.round(n.top-e.top+n.height/2+o)}px`,left:`${Math.round(n.left-e.left+r)}px`,transform:"translateY(-50%) translateX(-100%)"};default:return{top:`${Math.round(n.top-e.top+n.height+o)}px`,left:`${Math.round(n.left-e.left+n.width/2+r)}px`,transform:"translateX(-50%)"}}}(x,b,d,w,y,u);l.setAttribute("v-placement",x),l.style.setProperty("--v-offset-left",`${Math.round(y)}px`),l.style.setProperty("--v-offset-top",`${Math.round(w)}px`),l.style.transform=`translateX(${R}) translateY(${T}) ${$}`,l.style.setProperty("--v-transform-origin",S),l.style.transformOrigin=S};R(n,(t=>{t?(l(),f()):u()}));const f=()=>{T().then(c).catch((t=>console.error(t)))};["placement","x","y","internalShift","flip","width","overlap","minWidth"].forEach((e=>{R(m(t,e),c)})),["teleportDisabled"].forEach((e=>{R(m(t,e),f)})),R(m(t,"syncTrigger"),(t=>{t.includes("resize")?e.addResizeListener(c):e.removeResizeListener(c),t.includes("scroll")?e.addScrollListener(c):e.removeScrollListener(c)}));const h=$(),p=y((()=>{const{to:e}=t;if(void 0!==e)return e;h.value}));return{VBinder:e,mergedEnabled:n,offsetContainerRef:r,followerRef:o,mergedTo:p,syncPosition:c}},render(){return g(at,{show:this.show,to:this.mergedTo,disabled:this.teleportDisabled},{default:()=>{var t,e;const n=g("div",{class:["v-binder-follower-container",this.containerClass],ref:"offsetContainerRef"},[g("div",{class:"v-binder-follower-content",ref:"followerRef"},null===(e=(t=this.$slots).default)||void 0===e?void 0:e.call(t))]);return this.zindexable?f(n,[[M,{enabled:this.mergedEnabled,zIndex:this.zIndex}]]):n}})}}),yt=new class{constructor(){this.handleResize=this.handleResize.bind(this),this.observer=new("undefined"!=typeof window&&window.ResizeObserver||z)(this.handleResize),this.elHandlersMap=new Map}handleResize(t){for(const e of t){const t=this.elHandlersMap.get(e.target);void 0!==t&&t(e)}}registerHandler(t,e){this.elHandlersMap.set(t,e),this.observer.observe(t)}unregisterHandler(t){this.elHandlersMap.has(t)&&(this.elHandlersMap.delete(t),this.observer.unobserve(t))}},wt=o({name:"ResizeObserver",props:{onResize:Function},setup(t){let e=!1;const n=l().proxy;function o(e){const{onResize:n}=t;void 0!==n&&n(e)}w((()=>{const t=n.$el;void 0!==t?t.nextElementSibling===t.nextSibling||3!==t.nodeType||""===t.nodeValue?null!==t.nextElementSibling&&(yt.registerHandler(t.nextElementSibling,o),e=!0):nt("resize-observer","$el can not be observed (it may be a text node)."):nt("resize-observer","$el does not exist.")})),a((()=>{e&&yt.unregisterHandler(n.$el.nextElementSibling)}))},render(){return C(this.$slots,"default")}});let xt,St;function Rt(){return"undefined"==typeof document?1:(void 0===St&&(St="chrome"in window?window.devicePixelRatio:1),St)}const Tt="VVirtualListXScroll",$t=o({name:"VirtualListRow",props:{index:{type:Number,required:!0},item:{type:Object,required:!0}},setup(){const{startIndexRef:t,endIndexRef:e,columnsRef:n,getLeft:o,renderColRef:r,renderItemWithColsRef:l}=i(Tt);return{startIndex:t,endIndex:e,columns:n,renderCol:r,renderItemWithCols:l,getLeft:o}},render(){const{startIndex:t,endIndex:e,columns:n,renderCol:o,renderItemWithCols:r,getLeft:l,item:i}=this;if(null!=r)return r({itemIndex:this.index,startColIndex:t,endColIndex:e,allColumns:n,item:i,getLeft:l});if(null!=o){const r=[];for(let s=t;s<=e;++s){const t=n[s];r.push(o({column:t,left:l(s),item:i}))}return r}return null}}),Mt=ot(".v-vl",{maxHeight:"inherit",height:"100%",overflow:"auto",minWidth:"1px"},[ot("&:not(.v-vl--show-scrollbar)",{scrollbarWidth:"none"},[ot("&::-webkit-scrollbar, &::-webkit-scrollbar-track-piece, &::-webkit-scrollbar-thumb",{width:0,height:0,display:"none"})])]),zt=o({name:"VirtualList",inheritAttrs:!1,props:{showScrollbar:{type:Boolean,default:!0},columns:{type:Array,default:()=>[]},renderCol:Function,renderItemWithCols:Function,items:{type:Array,default:()=>[]},itemSize:{type:Number,required:!0},itemResizable:Boolean,itemsStyle:[String,Object],visibleItemsTag:{type:[String,Object],default:"div"},visibleItemsProps:Object,ignoreItemResize:Boolean,onScroll:Function,onWheel:Function,onResize:Function,defaultScrollKey:[Number,String],defaultScrollIndex:Number,keyField:{type:String,default:"key"},paddingTop:{type:[Number,String],default:0},paddingBottom:{type:[Number,String],default:0}},setup(t){const e=x();Mt.mount({id:"vueuc/virtual-list",head:!0,anchorMetaName:rt,ssr:e}),w((()=>{const{defaultScrollIndex:e,defaultScrollKey:n}=t;null!=e?T({index:e}):null!=n&&T({key:n})}));let n=!1,o=!1;I((()=>{n=!1,o?T({top:b.value,left:a.value}):o=!0})),E((()=>{n=!0,o||(o=!0)}));const l=y((()=>{if(null==t.renderCol&&null==t.renderItemWithCols)return;if(0===t.columns.length)return;let e=0;return t.columns.forEach((t=>{e+=t.width})),e})),i=v((()=>{const e=new Map,{keyField:n}=t;return t.items.forEach(((t,o)=>{e.set(t[n],o)})),e})),{scrollLeftRef:a,listWidthRef:u}=function({columnsRef:t,renderColRef:e,renderItemWithColsRef:n}){const o=s(0),l=s(0),i=v((()=>{const e=t.value;if(0===e.length)return null;const n=new it(e.length,0);return e.forEach(((t,e)=>{n.add(e,t.width)})),n})),a=y((()=>{const t=i.value;return null!==t?Math.max(t.getBound(l.value)-1,0):0})),u=y((()=>{const e=i.value;return null!==e?Math.min(e.getBound(l.value+o.value)+1,t.value.length-1):0}));return r(Tt,{startIndexRef:a,endIndexRef:u,columnsRef:t,renderColRef:e,renderItemWithColsRef:n,getLeft:t=>{const e=i.value;return null!==e?e.sum(t):0}}),{listWidthRef:o,scrollLeftRef:l}}({columnsRef:m(t,"columns"),renderColRef:m(t,"renderCol"),renderItemWithColsRef:m(t,"renderItemWithCols")}),c=s(null),f=s(void 0),h=new Map,p=v((()=>{const{items:e,itemSize:n,keyField:o}=t,r=new it(e.length,n);return e.forEach(((t,e)=>{const n=t[o],l=h.get(n);void 0!==l&&r.add(e,l)})),r})),g=s(0),b=s(0),S=y((()=>Math.max(p.value.getBound(b.value-B(t.paddingTop))-1,0))),R=v((()=>{const{value:e}=f;if(void 0===e)return[];const{items:n,itemSize:o}=t,r=S.value,l=Math.min(r+Math.ceil(e/o+1),n.length-1),i=[];for(let t=r;t<=l;++t)i.push(n[t]);return i})),T=(t,e)=>{if("number"==typeof t)return void C(t,e,"auto");const{left:n,top:o,index:r,key:l,position:s,behavior:a,debounce:u=!0}=t;if(void 0!==n||void 0!==o)C(n,o,a);else if(void 0!==r)z(r,a,u);else if(void 0!==l){const t=i.value.get(l);void 0!==t&&z(t,a,u)}else"bottom"===s?C(0,Number.MAX_SAFE_INTEGER,a):"top"===s&&C(0,0,a)};let $,M=null;function z(e,n,o){const{value:r}=p,l=r.sum(e)+B(t.paddingTop);if(o){$=e,null!==M&&window.clearTimeout(M),M=window.setTimeout((()=>{$=void 0,M=null}),16);const{scrollTop:t,offsetHeight:o}=c.value;if(l>t){const i=r.get(e);l+i<=t+o||c.value.scrollTo({left:0,top:l+i-o,behavior:n})}else c.value.scrollTo({left:0,top:l,behavior:n})}else c.value.scrollTo({left:0,top:l,behavior:n})}function C(t,e,n){c.value.scrollTo({left:t,top:e,behavior:n})}const O=!("undefined"!=typeof document&&(void 0===xt&&(xt="matchMedia"in window&&window.matchMedia("(pointer:coarse)").matches),xt));let L=!1;function W(){const{value:t}=c;null!=t&&(b.value=t.scrollTop,a.value=t.scrollLeft)}function A(t){let e=t;for(;null!==e;){if("none"===e.style.display)return!0;e=e.parentElement}return!1}return{listHeight:f,listStyle:{overflow:"auto"},keyToIndex:i,itemsStyle:v((()=>{const{itemResizable:e}=t,n=F(p.value.sum());return g.value,[t.itemsStyle,{boxSizing:"content-box",width:F(l.value),height:e?"":n,minHeight:e?n:"",paddingTop:F(t.paddingTop),paddingBottom:F(t.paddingBottom)}]})),visibleItemsStyle:v((()=>(g.value,{transform:`translateY(${F(p.value.sum(S.value))})`}))),viewportItems:R,listElRef:c,itemsElRef:s(null),scrollTo:T,handleListResize:function(e){if(n)return;if(A(e.target))return;if(null==t.renderCol&&null==t.renderItemWithCols){if(e.contentRect.height===f.value)return}else if(e.contentRect.height===f.value&&e.contentRect.width===u.value)return;f.value=e.contentRect.height,u.value=e.contentRect.width;const{onResize:o}=t;void 0!==o&&o(e)},handleListScroll:function(e){var n;null===(n=t.onScroll)||void 0===n||n.call(t,e),O&&L||W()},handleListWheel:function(e){var n;if(null===(n=t.onWheel)||void 0===n||n.call(t,e),O){const t=c.value;if(null!=t){if(0===e.deltaX){if(0===t.scrollTop&&e.deltaY<=0)return;if(t.scrollTop+t.offsetHeight>=t.scrollHeight&&e.deltaY>=0)return}e.preventDefault(),t.scrollTop+=e.deltaY/Rt(),t.scrollLeft+=e.deltaX/Rt(),W(),L=!0,d((()=>{L=!1}))}}},handleItemResize:function(e,o){var r,l,s;if(n)return;if(t.ignoreItemResize)return;if(A(o.target))return;const{value:a}=p,u=i.value.get(e),d=a.get(u),f=null!==(s=null===(l=null===(r=o.borderBoxSize)||void 0===r?void 0:r[0])||void 0===l?void 0:l.blockSize)&&void 0!==s?s:o.contentRect.height;if(f===d)return;0==f-t.itemSize?h.delete(e):h.set(e,f-t.itemSize);const m=f-d;if(0===m)return;a.add(u,m);const v=c.value;if(null!=v){if(void 0===$){const t=a.sum(u);v.scrollTop>t&&v.scrollBy(0,m)}else(u<$||u===$&&f+a.sum(u)>v.scrollTop+v.offsetHeight)&&v.scrollBy(0,m);W()}g.value++}}},render(){const{itemResizable:t,keyField:e,keyToIndex:n,visibleItemsTag:o}=this;return g(wt,{onResize:this.handleListResize},{default:()=>{var r,l;return g("div",O(this.$attrs,{class:["v-vl",this.showScrollbar&&"v-vl--show-scrollbar"],onScroll:this.handleListScroll,onWheel:this.handleListWheel,ref:"listElRef"}),[0!==this.items.length?g("div",{ref:"itemsElRef",class:"v-vl-items",style:this.itemsStyle},[g(o,Object.assign({class:"v-vl-visible-items",style:this.visibleItemsStyle},this.visibleItemsProps),{default:()=>{const{renderCol:o,renderItemWithCols:r}=this;return this.viewportItems.map((l=>{const i=l[e],s=n.get(i),a=null!=o?g($t,{index:s,item:l}):void 0,u=null!=r?g($t,{index:s,item:l}):void 0,d=this.$slots.default({item:l,renderedCols:a,renderedItemWithCols:u,index:s})[0];return t?g(wt,{key:i,onResize:t=>this.handleItemResize(i,t)},{default:()=>d}):(d.key=i,d)}))}})]):null===(l=(r=this.$slots).empty)||void 0===l?void 0:l.call(r)])}})}}),Ct="v-hidden",It=ot("[v-hidden]",{display:"none!important"}),Et=o({name:"Overflow",props:{getCounter:Function,getTail:Function,updateCounter:Function,onUpdateCount:Function,onUpdateOverflow:Function},setup(t,{slots:e}){const n=s(null),o=s(null);function r(r){const{value:l}=n,{getCounter:i,getTail:s}=t;let a;if(a=void 0!==i?i():o.value,!l||!a)return;a.hasAttribute(Ct)&&a.removeAttribute(Ct);const{children:u}=l;if(r.showAllItemsBeforeCalculate)for(const t of u)t.hasAttribute(Ct)&&t.removeAttribute(Ct);const d=l.offsetWidth,c=[],f=e.tail?null==s?void 0:s():null;let h=f?f.offsetWidth:0,p=!1;const m=l.children.length-(e.tail?1:0);for(let e=0;e<m-1;++e){if(e<0)continue;const n=u[e];if(p){n.hasAttribute(Ct)||n.setAttribute(Ct,"");continue}n.hasAttribute(Ct)&&n.removeAttribute(Ct);const o=n.offsetWidth;if(h+=o,c[e]=o,h>d){const{updateCounter:n}=t;for(let o=e;o>=0;--o){const r=m-1-o;void 0!==n?n(r):a.textContent=`${r}`;const l=a.offsetWidth;if(h-=c[o],h+l<=d||0===o){p=!0,e=o-1,f&&(-1===e?(f.style.maxWidth=d-l+"px",f.style.boxSizing="border-box"):f.style.maxWidth="");const{onUpdateCount:n}=t;n&&n(r);break}}}}const{onUpdateOverflow:v}=t;p?void 0!==v&&v(!0):(void 0!==v&&v(!1),a.setAttribute(Ct,""))}const l=x();return It.mount({id:"vueuc/overflow",head:!0,anchorMetaName:rt,ssr:l}),w((()=>r({showAllItemsBeforeCalculate:!1}))),{selfRef:n,counterRef:o,sync:r}},render(){const{$slots:t}=this;return T((()=>this.sync({showAllItemsBeforeCalculate:!1}))),g("div",{class:"v-overflow",ref:"selfRef"},[C(t,"default"),t.counter?t.counter():g("span",{style:{display:"inline-block"},ref:"counterRef"}),t.tail?t.tail():null])}});function Bt(t){return t instanceof HTMLElement}function Ft(t){for(let e=0;e<t.childNodes.length;e++){const n=t.childNodes[e];if(Bt(n)&&(Lt(n)||Ft(n)))return!0}return!1}function Ot(t){for(let e=t.childNodes.length-1;e>=0;e--){const n=t.childNodes[e];if(Bt(n)&&(Lt(n)||Ot(n)))return!0}return!1}function Lt(t){if(!function(t){if(t.tabIndex>0||0===t.tabIndex&&null!==t.getAttribute("tabIndex"))return!0;if(t.getAttribute("disabled"))return!1;switch(t.nodeName){case"A":return!!t.href&&"ignore"!==t.rel;case"INPUT":return"hidden"!==t.type&&"file"!==t.type;case"BUTTON":case"SELECT":case"TEXTAREA":return!0;default:return!1}}(t))return!1;try{t.focus({preventScroll:!0})}catch(Nt){}return document.activeElement===t}let Wt=[];const At=o({name:"FocusTrap",props:{disabled:Boolean,active:Boolean,autoFocus:{type:Boolean,default:!0},onEsc:Function,initialFocusTo:String,finalFocusTo:String,returnFocusOnDeactivated:{type:Boolean,default:!0}},setup(t){const e=L(),n=s(null),o=s(null);let r=!1,l=!1;const i="undefined"==typeof document?null:document.activeElement;function d(){return Wt[Wt.length-1]===e}function f(e){var n;"Escape"===e.code&&d()&&(null===(n=t.onEsc)||void 0===n||n.call(t,e))}function h(t){if(!l&&d()){const e=p();if(null===e)return;if(e.contains(W(t)))return;v("first")}}function p(){const t=n.value;if(null===t)return null;let e=t;for(;e=e.nextSibling,!(null===e||e instanceof Element&&"DIV"===e.tagName););return e}function m(){var n;if(t.disabled)return;if(document.removeEventListener("focus",h,!0),Wt=Wt.filter((t=>t!==e)),d())return;const{finalFocusTo:o}=t;void 0!==o?null===(n=st(o))||void 0===n||n.focus({preventScroll:!0}):t.returnFocusOnDeactivated&&i instanceof HTMLElement&&(l=!0,i.focus({preventScroll:!0}),l=!1)}function v(e){if(d()&&t.active){const t=n.value,r=o.value;if(null!==t&&null!==r){const n=p();if(null==n||n===r)return l=!0,t.focus({preventScroll:!0}),void(l=!1);l=!0;const o="first"===e?Ft(n):Ot(n);l=!1,o||(l=!0,t.focus({preventScroll:!0}),l=!1)}}}return w((()=>{R((()=>t.active),(n=>{n?(function(){var n;if(!t.disabled){if(Wt.push(e),t.autoFocus){const{initialFocusTo:e}=t;void 0===e?v("first"):null===(n=st(e))||void 0===n||n.focus({preventScroll:!0})}r=!0,document.addEventListener("focus",h,!0)}}(),c("keydown",document,f)):(u("keydown",document,f),r&&m())}),{immediate:!0})})),a((()=>{u("keydown",document,f),r&&m()})),{focusableStartRef:n,focusableEndRef:o,focusableStyle:"position: absolute; height: 0; width: 0;",handleStartFocus:function(t){if(l)return;const e=p();null!==e&&(null!==t.relatedTarget&&e.contains(t.relatedTarget)?v("last"):v("first"))},handleEndFocus:function(t){l||(null!==t.relatedTarget&&t.relatedTarget===n.value?v("last"):v("first"))}}},render(){const{default:t}=this.$slots;if(void 0===t)return null;if(this.disabled)return t();const{active:n,focusableStyle:o}=this;return g(e,null,[g("div",{"aria-hidden":"true",tabindex:n?"0":"-1",ref:"focusableStartRef",style:o,onFocus:this.handleStartFocus}),t(),g("div",{"aria-hidden":"true",style:o,ref:"focusableEndRef",tabindex:n?"0":"-1",onFocus:this.handleEndFocus})])}});var jt,Nt,kt=Object.freeze({autofocus:!1,disabled:!1,indentWithTab:!0,tabSize:2,placeholder:"",autoDestroy:!0,extensions:[X]}),Dt=Symbol("vue-codemirror-global-config"),Pt=function(t){var e=new U;return{compartment:e,run:function(n){e.get(t.state)?t.dispatch({effects:e.reconfigure(n)}):t.dispatch({effects:H.appendConfig.of(e.of(n))})}}},Vt=function(t,e){var n=Pt(t),o=n.compartment,r=n.run;return function(n){var l=o.get(t.state);r((null!=n?n:l!==e)?e:[])}},Xt={type:Boolean,default:void 0},Ht={autofocus:Xt,disabled:Xt,indentWithTab:Xt,tabSize:Number,placeholder:String,style:Object,autoDestroy:Xt,phrases:Object,root:Object,extensions:Array,selection:Object},Yt={modelValue:{type:String,default:""}},Ut=Object.assign(Object.assign({},Ht),Yt);(Nt=jt||(jt={})).Change="change",Nt.Update="update",Nt.Focus="focus",Nt.Blur="blur",Nt.Ready="ready",Nt.ModelUpdate="update:modelValue";var qt={};qt[jt.Change]=function(t,e){return!0},qt[jt.Update]=function(t){return!0},qt[jt.Focus]=function(t){return!0},qt[jt.Blur]=function(t){return!0},qt[jt.Ready]=function(t){return!0};var Kt={};Kt[jt.ModelUpdate]=qt[jt.Change];var _t=Object.assign(Object.assign({},qt),Kt),Gt=o({name:"VueCodemirror",props:Object.assign({},Ut),emits:Object.assign({},_t),setup:function(t,e){var n=A(),o=A(),r=A(),l=Object.assign(Object.assign({},kt),i(Dt,{})),s=v((function(){var e={};return Object.keys(Y(t)).forEach((function(n){var o;"modelValue"!==n&&(e[n]=null!==(o=t[n])&&void 0!==o?o:l[n])})),e}));return w((function(){var i,a;o.value=function(t){var e=t.onUpdate,n=t.onChange,o=t.onFocus,r=t.onBlur,l=function(t,e){var n={};for(var o in t)Object.prototype.hasOwnProperty.call(t,o)&&e.indexOf(o)<0&&(n[o]=t[o]);if(null!=t&&"function"==typeof Object.getOwnPropertySymbols){var r=0;for(o=Object.getOwnPropertySymbols(t);r<o.length;r++)e.indexOf(o[r])<0&&Object.prototype.propertyIsEnumerable.call(t,o[r])&&(n[o[r]]=t[o[r]])}return n}(t,["onUpdate","onChange","onFocus","onBlur"]);return N.create({doc:l.doc,selection:l.selection,extensions:(Array.isArray(l.extensions)?l.extensions:[l.extensions]).concat([j.updateListener.of((function(t){e(t),t.docChanged&&n(t.state.doc.toString(),t),t.focusChanged&&(t.view.hasFocus?o(t):r(t))}))])})}({doc:t.modelValue,selection:s.value.selection,extensions:null!==(i=l.extensions)&&void 0!==i?i:[],onFocus:function(t){return e.emit(jt.Focus,t)},onBlur:function(t){return e.emit(jt.Blur,t)},onUpdate:function(t){return e.emit(jt.Update,t)},onChange:function(n,o){n!==t.modelValue&&(e.emit(jt.Change,n,o),e.emit(jt.ModelUpdate,n,o))}}),r.value=(a={state:o.value,parent:n.value,root:s.value.root},new j(Object.assign({},a)));var u=function(t){var e=function(){return t.state.doc.toString()},n=Pt(t).run,o=Vt(t,[j.editable.of(!1),N.readOnly.of(!0)]),r=Vt(t,k.of([D])),l=Pt(t).run,i=Pt(t).run,s=Pt(t).run,a=Pt(t).run;return{focus:function(){return t.focus()},getDoc:e,setDoc:function(n){n!==e()&&t.dispatch({changes:{from:0,to:t.state.doc.length,insert:n}})},reExtensions:n,toggleDisabled:o,toggleIndentWithTab:r,setTabSize:function(t){l([N.tabSize.of(t),P.of(" ".repeat(t))])},setPhrases:function(t){i([N.phrases.of(t)])},setPlaceholder:function(t){s(V(t))},setStyle:function(t){void 0===t&&(t={}),a(j.theme({"&":Object.assign({},t)}))}}}(r.value);R((function(){return t.modelValue}),(function(t){t!==u.getDoc()&&u.setDoc(t)})),R((function(){return t.extensions}),(function(t){return u.reExtensions(t||[])}),{immediate:!0}),R((function(){return s.value.disabled}),(function(t){return u.toggleDisabled(t)}),{immediate:!0}),R((function(){return s.value.indentWithTab}),(function(t){return u.toggleIndentWithTab(t)}),{immediate:!0}),R((function(){return s.value.tabSize}),(function(t){return u.setTabSize(t)}),{immediate:!0}),R((function(){return s.value.phrases}),(function(t){return u.setPhrases(t||{})}),{immediate:!0}),R((function(){return s.value.placeholder}),(function(t){return u.setPlaceholder(t)}),{immediate:!0}),R((function(){return s.value.style}),(function(t){return u.setStyle(t)}),{immediate:!0}),s.value.autofocus&&u.focus(),e.emit(jt.Ready,{state:o.value,view:r.value,container:n.value})})),a((function(){s.value.autoDestroy&&r.value&&function(t){t.destroy()}(r.value)})),function(){return g("div",{class:"v-codemirror",style:{display:"contents"},ref:n})}}}),Zt=function(t,e){var n;t.component(Gt.name,Gt),t.component("Codemirror",Gt),n=e,t.provide(Dt,n)};export{tt as B,At as F,at as L,wt as V,zt as a,bt as b,et as c,Et as d,Zt as e,yt as r};
