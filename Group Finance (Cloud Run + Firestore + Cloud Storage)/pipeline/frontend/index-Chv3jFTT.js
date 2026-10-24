(function(){const q=document.createElement("link").relList;if(q&&q.supports&&q.supports("modulepreload"))return;for(const G of document.querySelectorAll('link[rel="modulepreload"]'))m(G);new MutationObserver(G=>{for(const C of G)if(C.type==="childList")for(const el of C.addedNodes)el.tagName==="LINK"&&el.rel==="modulepreload"&&m(el)}).observe(document,{childList:!0,subtree:!0});function B(G){const C={};return G.integrity&&(C.integrity=G.integrity),G.referrerPolicy&&(C.referrerPolicy=G.referrerPolicy),G.crossOrigin==="use-credentials"?C.credentials="include":G.crossOrigin==="anonymous"?C.credentials="omit":C.credentials="same-origin",C}function m(G){if(G.ep)return;G.ep=!0;const C=B(G);fetch(G.href,C)}})();function jd(E){return E&&E.__esModule&&Object.prototype.hasOwnProperty.call(E,"default")?E.default:E}var cf={exports:{}},xu={};/**
 * @license React
 * react-jsx-runtime.production.js
 *
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var gd;function ny(){if(gd)return xu;gd=1;var E=Symbol.for("react.transitional.element"),q=Symbol.for("react.fragment");function B(m,G,C){var el=null;if(C!==void 0&&(el=""+C),G.key!==void 0&&(el=""+G.key),"key"in G){C={};for(var ol in G)ol!=="key"&&(C[ol]=G[ol])}else C=G;return G=C.ref,{$$typeof:E,type:m,key:el,ref:G!==void 0?G:null,props:C}}return xu.Fragment=q,xu.jsx=B,xu.jsxs=B,xu}var bd;function iy(){return bd||(bd=1,cf.exports=ny()),cf.exports}var v=iy(),ff={exports:{}},X={};/**
 * @license React
 * react.production.js
 *
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var Sd;function cy(){if(Sd)return X;Sd=1;var E=Symbol.for("react.transitional.element"),q=Symbol.for("react.portal"),B=Symbol.for("react.fragment"),m=Symbol.for("react.strict_mode"),G=Symbol.for("react.profiler"),C=Symbol.for("react.consumer"),el=Symbol.for("react.context"),ol=Symbol.for("react.forward_ref"),N=Symbol.for("react.suspense"),z=Symbol.for("react.memo"),L=Symbol.for("react.lazy"),j=Symbol.for("react.activity"),W=Symbol.iterator;function Ul(o){return o===null||typeof o!="object"?null:(o=W&&o[W]||o["@@iterator"],typeof o=="function"?o:null)}var Hl={isMounted:function(){return!1},enqueueForceUpdate:function(){},enqueueReplaceState:function(){},enqueueSetState:function(){}},_l=Object.assign,rt={};function Sl(o,T,_){this.props=o,this.context=T,this.refs=rt,this.updater=_||Hl}Sl.prototype.isReactComponent={},Sl.prototype.setState=function(o,T){if(typeof o!="object"&&typeof o!="function"&&o!=null)throw Error("takes an object of state variables to update or a function which returns an object of state variables.");this.updater.enqueueSetState(this,o,T,"setState")},Sl.prototype.forceUpdate=function(o){this.updater.enqueueForceUpdate(this,o,"forceUpdate")};function At(){}At.prototype=Sl.prototype;function Cl(o,T,_){this.props=o,this.context=T,this.refs=rt,this.updater=_||Hl}var Jl=Cl.prototype=new At;Jl.constructor=Cl,_l(Jl,Sl.prototype),Jl.isPureReactComponent=!0;var wl=Array.isArray;function Ll(){}var K={H:null,A:null,T:null,S:null},Bl=Object.prototype.hasOwnProperty;function H(o,T,_){var O=_.ref;return{$$typeof:E,type:o,key:T,ref:O!==void 0?O:null,props:_}}function gl(o,T){return H(o.type,T,o.props)}function dl(o){return typeof o=="object"&&o!==null&&o.$$typeof===E}function xl(o){var T={"=":"=0",":":"=2"};return"$"+o.replace(/[=:]/g,function(_){return T[_]})}var yt=/\/+/g;function Ct(o,T){return typeof o=="object"&&o!==null&&o.key!=null?xl(""+o.key):T.toString(36)}function _t(o){switch(o.status){case"fulfilled":return o.value;case"rejected":throw o.reason;default:switch(typeof o.status=="string"?o.then(Ll,Ll):(o.status="pending",o.then(function(T){o.status==="pending"&&(o.status="fulfilled",o.value=T)},function(T){o.status==="pending"&&(o.status="rejected",o.reason=T)})),o.status){case"fulfilled":return o.value;case"rejected":throw o.reason}}throw o}function S(o,T,_,O,Q){var J=typeof o;(J==="undefined"||J==="boolean")&&(o=null);var al=!1;if(o===null)al=!0;else switch(J){case"bigint":case"string":case"number":al=!0;break;case"object":switch(o.$$typeof){case E:case q:al=!0;break;case L:return al=o._init,S(al(o._payload),T,_,O,Q)}}if(al)return Q=Q(o),al=O===""?"."+Ct(o,0):O,wl(Q)?(_="",al!=null&&(_=al.replace(yt,"$&/")+"/"),S(Q,T,_,"",function(Na){return Na})):Q!=null&&(dl(Q)&&(Q=gl(Q,_+(Q.key==null||o&&o.key===Q.key?"":(""+Q.key).replace(yt,"$&/")+"/")+al)),T.push(Q)),1;al=0;var kl=O===""?".":O+":";if(wl(o))for(var Tl=0;Tl<o.length;Tl++)O=o[Tl],J=kl+Ct(O,Tl),al+=S(O,T,_,J,Q);else if(Tl=Ul(o),typeof Tl=="function")for(o=Tl.call(o),Tl=0;!(O=o.next()).done;)O=O.value,J=kl+Ct(O,Tl++),al+=S(O,T,_,J,Q);else if(J==="object"){if(typeof o.then=="function")return S(_t(o),T,_,O,Q);throw T=String(o),Error("Objects are not valid as a React child (found: "+(T==="[object Object]"?"object with keys {"+Object.keys(o).join(", ")+"}":T)+"). If you meant to render a collection of children, use an array instead.")}return al}function A(o,T,_){if(o==null)return o;var O=[],Q=0;return S(o,O,"","",function(J){return T.call(_,J,Q++)}),O}function Y(o){if(o._status===-1){var T=o._result;T=T(),T.then(function(_){(o._status===0||o._status===-1)&&(o._status=1,o._result=_)},function(_){(o._status===0||o._status===-1)&&(o._status=2,o._result=_)}),o._status===-1&&(o._status=0,o._result=T)}if(o._status===1)return o._result.default;throw o._result}var il=typeof reportError=="function"?reportError:function(o){if(typeof window=="object"&&typeof window.ErrorEvent=="function"){var T=new window.ErrorEvent("error",{bubbles:!0,cancelable:!0,message:typeof o=="object"&&o!==null&&typeof o.message=="string"?String(o.message):String(o),error:o});if(!window.dispatchEvent(T))return}else if(typeof process=="object"&&typeof process.emit=="function"){process.emit("uncaughtException",o);return}console.error(o)},ml={map:A,forEach:function(o,T,_){A(o,function(){T.apply(this,arguments)},_)},count:function(o){var T=0;return A(o,function(){T++}),T},toArray:function(o){return A(o,function(T){return T})||[]},only:function(o){if(!dl(o))throw Error("React.Children.only expected to receive a single React element child.");return o}};return X.Activity=j,X.Children=ml,X.Component=Sl,X.Fragment=B,X.Profiler=G,X.PureComponent=Cl,X.StrictMode=m,X.Suspense=N,X.__CLIENT_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE=K,X.__COMPILER_RUNTIME={__proto__:null,c:function(o){return K.H.useMemoCache(o)}},X.cache=function(o){return function(){return o.apply(null,arguments)}},X.cacheSignal=function(){return null},X.cloneElement=function(o,T,_){if(o==null)throw Error("The argument must be a React element, but you passed "+o+".");var O=_l({},o.props),Q=o.key;if(T!=null)for(J in T.key!==void 0&&(Q=""+T.key),T)!Bl.call(T,J)||J==="key"||J==="__self"||J==="__source"||J==="ref"&&T.ref===void 0||(O[J]=T[J]);var J=arguments.length-2;if(J===1)O.children=_;else if(1<J){for(var al=Array(J),kl=0;kl<J;kl++)al[kl]=arguments[kl+2];O.children=al}return H(o.type,Q,O)},X.createContext=function(o){return o={$$typeof:el,_currentValue:o,_currentValue2:o,_threadCount:0,Provider:null,Consumer:null},o.Provider=o,o.Consumer={$$typeof:C,_context:o},o},X.createElement=function(o,T,_){var O,Q={},J=null;if(T!=null)for(O in T.key!==void 0&&(J=""+T.key),T)Bl.call(T,O)&&O!=="key"&&O!=="__self"&&O!=="__source"&&(Q[O]=T[O]);var al=arguments.length-2;if(al===1)Q.children=_;else if(1<al){for(var kl=Array(al),Tl=0;Tl<al;Tl++)kl[Tl]=arguments[Tl+2];Q.children=kl}if(o&&o.defaultProps)for(O in al=o.defaultProps,al)Q[O]===void 0&&(Q[O]=al[O]);return H(o,J,Q)},X.createRef=function(){return{current:null}},X.forwardRef=function(o){return{$$typeof:ol,render:o}},X.isValidElement=dl,X.lazy=function(o){return{$$typeof:L,_payload:{_status:-1,_result:o},_init:Y}},X.memo=function(o,T){return{$$typeof:z,type:o,compare:T===void 0?null:T}},X.startTransition=function(o){var T=K.T,_={};K.T=_;try{var O=o(),Q=K.S;Q!==null&&Q(_,O),typeof O=="object"&&O!==null&&typeof O.then=="function"&&O.then(Ll,il)}catch(J){il(J)}finally{T!==null&&_.types!==null&&(T.types=_.types),K.T=T}},X.unstable_useCacheRefresh=function(){return K.H.useCacheRefresh()},X.use=function(o){return K.H.use(o)},X.useActionState=function(o,T,_){return K.H.useActionState(o,T,_)},X.useCallback=function(o,T){return K.H.useCallback(o,T)},X.useContext=function(o){return K.H.useContext(o)},X.useDebugValue=function(){},X.useDeferredValue=function(o,T){return K.H.useDeferredValue(o,T)},X.useEffect=function(o,T){return K.H.useEffect(o,T)},X.useEffectEvent=function(o){return K.H.useEffectEvent(o)},X.useId=function(){return K.H.useId()},X.useImperativeHandle=function(o,T,_){return K.H.useImperativeHandle(o,T,_)},X.useInsertionEffect=function(o,T){return K.H.useInsertionEffect(o,T)},X.useLayoutEffect=function(o,T){return K.H.useLayoutEffect(o,T)},X.useMemo=function(o,T){return K.H.useMemo(o,T)},X.useOptimistic=function(o,T){return K.H.useOptimistic(o,T)},X.useReducer=function(o,T,_){return K.H.useReducer(o,T,_)},X.useRef=function(o){return K.H.useRef(o)},X.useState=function(o){return K.H.useState(o)},X.useSyncExternalStore=function(o,T,_){return K.H.useSyncExternalStore(o,T,_)},X.useTransition=function(){return K.H.useTransition()},X.version="19.2.3",X}var xd;function yf(){return xd||(xd=1,ff.exports=cy()),ff.exports}var yl=yf();const fy=jd(yl);var sf={exports:{}},pu={},of={exports:{}},df={};/**
 * @license React
 * scheduler.production.js
 *
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var pd;function sy(){return pd||(pd=1,(function(E){function q(S,A){var Y=S.length;S.push(A);l:for(;0<Y;){var il=Y-1>>>1,ml=S[il];if(0<G(ml,A))S[il]=A,S[Y]=ml,Y=il;else break l}}function B(S){return S.length===0?null:S[0]}function m(S){if(S.length===0)return null;var A=S[0],Y=S.pop();if(Y!==A){S[0]=Y;l:for(var il=0,ml=S.length,o=ml>>>1;il<o;){var T=2*(il+1)-1,_=S[T],O=T+1,Q=S[O];if(0>G(_,Y))O<ml&&0>G(Q,_)?(S[il]=Q,S[O]=Y,il=O):(S[il]=_,S[T]=Y,il=T);else if(O<ml&&0>G(Q,Y))S[il]=Q,S[O]=Y,il=O;else break l}}return A}function G(S,A){var Y=S.sortIndex-A.sortIndex;return Y!==0?Y:S.id-A.id}if(E.unstable_now=void 0,typeof performance=="object"&&typeof performance.now=="function"){var C=performance;E.unstable_now=function(){return C.now()}}else{var el=Date,ol=el.now();E.unstable_now=function(){return el.now()-ol}}var N=[],z=[],L=1,j=null,W=3,Ul=!1,Hl=!1,_l=!1,rt=!1,Sl=typeof setTimeout=="function"?setTimeout:null,At=typeof clearTimeout=="function"?clearTimeout:null,Cl=typeof setImmediate<"u"?setImmediate:null;function Jl(S){for(var A=B(z);A!==null;){if(A.callback===null)m(z);else if(A.startTime<=S)m(z),A.sortIndex=A.expirationTime,q(N,A);else break;A=B(z)}}function wl(S){if(_l=!1,Jl(S),!Hl)if(B(N)!==null)Hl=!0,Ll||(Ll=!0,xl());else{var A=B(z);A!==null&&_t(wl,A.startTime-S)}}var Ll=!1,K=-1,Bl=5,H=-1;function gl(){return rt?!0:!(E.unstable_now()-H<Bl)}function dl(){if(rt=!1,Ll){var S=E.unstable_now();H=S;var A=!0;try{l:{Hl=!1,_l&&(_l=!1,At(K),K=-1),Ul=!0;var Y=W;try{t:{for(Jl(S),j=B(N);j!==null&&!(j.expirationTime>S&&gl());){var il=j.callback;if(typeof il=="function"){j.callback=null,W=j.priorityLevel;var ml=il(j.expirationTime<=S);if(S=E.unstable_now(),typeof ml=="function"){j.callback=ml,Jl(S),A=!0;break t}j===B(N)&&m(N),Jl(S)}else m(N);j=B(N)}if(j!==null)A=!0;else{var o=B(z);o!==null&&_t(wl,o.startTime-S),A=!1}}break l}finally{j=null,W=Y,Ul=!1}A=void 0}}finally{A?xl():Ll=!1}}}var xl;if(typeof Cl=="function")xl=function(){Cl(dl)};else if(typeof MessageChannel<"u"){var yt=new MessageChannel,Ct=yt.port2;yt.port1.onmessage=dl,xl=function(){Ct.postMessage(null)}}else xl=function(){Sl(dl,0)};function _t(S,A){K=Sl(function(){S(E.unstable_now())},A)}E.unstable_IdlePriority=5,E.unstable_ImmediatePriority=1,E.unstable_LowPriority=4,E.unstable_NormalPriority=3,E.unstable_Profiling=null,E.unstable_UserBlockingPriority=2,E.unstable_cancelCallback=function(S){S.callback=null},E.unstable_forceFrameRate=function(S){0>S||125<S?console.error("forceFrameRate takes a positive int between 0 and 125, forcing frame rates higher than 125 fps is not supported"):Bl=0<S?Math.floor(1e3/S):5},E.unstable_getCurrentPriorityLevel=function(){return W},E.unstable_next=function(S){switch(W){case 1:case 2:case 3:var A=3;break;default:A=W}var Y=W;W=A;try{return S()}finally{W=Y}},E.unstable_requestPaint=function(){rt=!0},E.unstable_runWithPriority=function(S,A){switch(S){case 1:case 2:case 3:case 4:case 5:break;default:S=3}var Y=W;W=S;try{return A()}finally{W=Y}},E.unstable_scheduleCallback=function(S,A,Y){var il=E.unstable_now();switch(typeof Y=="object"&&Y!==null?(Y=Y.delay,Y=typeof Y=="number"&&0<Y?il+Y:il):Y=il,S){case 1:var ml=-1;break;case 2:ml=250;break;case 5:ml=1073741823;break;case 4:ml=1e4;break;default:ml=5e3}return ml=Y+ml,S={id:L++,callback:A,priorityLevel:S,startTime:Y,expirationTime:ml,sortIndex:-1},Y>il?(S.sortIndex=Y,q(z,S),B(N)===null&&S===B(z)&&(_l?(At(K),K=-1):_l=!0,_t(wl,Y-il))):(S.sortIndex=ml,q(N,S),Hl||Ul||(Hl=!0,Ll||(Ll=!0,xl()))),S},E.unstable_shouldYield=gl,E.unstable_wrapCallback=function(S){var A=W;return function(){var Y=W;W=A;try{return S.apply(this,arguments)}finally{W=Y}}}})(df)),df}var zd;function oy(){return zd||(zd=1,of.exports=sy()),of.exports}var mf={exports:{}},Vl={};/**
 * @license React
 * react-dom.production.js
 *
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var Td;function dy(){if(Td)return Vl;Td=1;var E=yf();function q(N){var z="https://react.dev/errors/"+N;if(1<arguments.length){z+="?args[]="+encodeURIComponent(arguments[1]);for(var L=2;L<arguments.length;L++)z+="&args[]="+encodeURIComponent(arguments[L])}return"Minified React error #"+N+"; visit "+z+" for the full message or use the non-minified dev environment for full errors and additional helpful warnings."}function B(){}var m={d:{f:B,r:function(){throw Error(q(522))},D:B,C:B,L:B,m:B,X:B,S:B,M:B},p:0,findDOMNode:null},G=Symbol.for("react.portal");function C(N,z,L){var j=3<arguments.length&&arguments[3]!==void 0?arguments[3]:null;return{$$typeof:G,key:j==null?null:""+j,children:N,containerInfo:z,implementation:L}}var el=E.__CLIENT_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE;function ol(N,z){if(N==="font")return"";if(typeof z=="string")return z==="use-credentials"?z:""}return Vl.__DOM_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE=m,Vl.createPortal=function(N,z){var L=2<arguments.length&&arguments[2]!==void 0?arguments[2]:null;if(!z||z.nodeType!==1&&z.nodeType!==9&&z.nodeType!==11)throw Error(q(299));return C(N,z,null,L)},Vl.flushSync=function(N){var z=el.T,L=m.p;try{if(el.T=null,m.p=2,N)return N()}finally{el.T=z,m.p=L,m.d.f()}},Vl.preconnect=function(N,z){typeof N=="string"&&(z?(z=z.crossOrigin,z=typeof z=="string"?z==="use-credentials"?z:"":void 0):z=null,m.d.C(N,z))},Vl.prefetchDNS=function(N){typeof N=="string"&&m.d.D(N)},Vl.preinit=function(N,z){if(typeof N=="string"&&z&&typeof z.as=="string"){var L=z.as,j=ol(L,z.crossOrigin),W=typeof z.integrity=="string"?z.integrity:void 0,Ul=typeof z.fetchPriority=="string"?z.fetchPriority:void 0;L==="style"?m.d.S(N,typeof z.precedence=="string"?z.precedence:void 0,{crossOrigin:j,integrity:W,fetchPriority:Ul}):L==="script"&&m.d.X(N,{crossOrigin:j,integrity:W,fetchPriority:Ul,nonce:typeof z.nonce=="string"?z.nonce:void 0})}},Vl.preinitModule=function(N,z){if(typeof N=="string")if(typeof z=="object"&&z!==null){if(z.as==null||z.as==="script"){var L=ol(z.as,z.crossOrigin);m.d.M(N,{crossOrigin:L,integrity:typeof z.integrity=="string"?z.integrity:void 0,nonce:typeof z.nonce=="string"?z.nonce:void 0})}}else z==null&&m.d.M(N)},Vl.preload=function(N,z){if(typeof N=="string"&&typeof z=="object"&&z!==null&&typeof z.as=="string"){var L=z.as,j=ol(L,z.crossOrigin);m.d.L(N,L,{crossOrigin:j,integrity:typeof z.integrity=="string"?z.integrity:void 0,nonce:typeof z.nonce=="string"?z.nonce:void 0,type:typeof z.type=="string"?z.type:void 0,fetchPriority:typeof z.fetchPriority=="string"?z.fetchPriority:void 0,referrerPolicy:typeof z.referrerPolicy=="string"?z.referrerPolicy:void 0,imageSrcSet:typeof z.imageSrcSet=="string"?z.imageSrcSet:void 0,imageSizes:typeof z.imageSizes=="string"?z.imageSizes:void 0,media:typeof z.media=="string"?z.media:void 0})}},Vl.preloadModule=function(N,z){if(typeof N=="string")if(z){var L=ol(z.as,z.crossOrigin);m.d.m(N,{as:typeof z.as=="string"&&z.as!=="script"?z.as:void 0,crossOrigin:L,integrity:typeof z.integrity=="string"?z.integrity:void 0})}else m.d.m(N)},Vl.requestFormReset=function(N){m.d.r(N)},Vl.unstable_batchedUpdates=function(N,z){return N(z)},Vl.useFormState=function(N,z,L){return el.H.useFormState(N,z,L)},Vl.useFormStatus=function(){return el.H.useHostTransitionStatus()},Vl.version="19.2.3",Vl}var Ed;function my(){if(Ed)return mf.exports;Ed=1;function E(){if(!(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__>"u"||typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE!="function"))try{__REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE(E)}catch(q){console.error(q)}}return E(),mf.exports=dy(),mf.exports}/**
 * @license React
 * react-dom-client.production.js
 *
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var Ad;function ry(){if(Ad)return pu;Ad=1;var E=oy(),q=yf(),B=my();function m(l){var t="https://react.dev/errors/"+l;if(1<arguments.length){t+="?args[]="+encodeURIComponent(arguments[1]);for(var e=2;e<arguments.length;e++)t+="&args[]="+encodeURIComponent(arguments[e])}return"Minified React error #"+l+"; visit "+t+" for the full message or use the non-minified dev environment for full errors and additional helpful warnings."}function G(l){return!(!l||l.nodeType!==1&&l.nodeType!==9&&l.nodeType!==11)}function C(l){var t=l,e=l;if(l.alternate)for(;t.return;)t=t.return;else{l=t;do t=l,(t.flags&4098)!==0&&(e=t.return),l=t.return;while(l)}return t.tag===3?e:null}function el(l){if(l.tag===13){var t=l.memoizedState;if(t===null&&(l=l.alternate,l!==null&&(t=l.memoizedState)),t!==null)return t.dehydrated}return null}function ol(l){if(l.tag===31){var t=l.memoizedState;if(t===null&&(l=l.alternate,l!==null&&(t=l.memoizedState)),t!==null)return t.dehydrated}return null}function N(l){if(C(l)!==l)throw Error(m(188))}function z(l){var t=l.alternate;if(!t){if(t=C(l),t===null)throw Error(m(188));return t!==l?null:l}for(var e=l,a=t;;){var u=e.return;if(u===null)break;var n=u.alternate;if(n===null){if(a=u.return,a!==null){e=a;continue}break}if(u.child===n.child){for(n=u.child;n;){if(n===e)return N(u),l;if(n===a)return N(u),t;n=n.sibling}throw Error(m(188))}if(e.return!==a.return)e=u,a=n;else{for(var i=!1,c=u.child;c;){if(c===e){i=!0,e=u,a=n;break}if(c===a){i=!0,a=u,e=n;break}c=c.sibling}if(!i){for(c=n.child;c;){if(c===e){i=!0,e=n,a=u;break}if(c===a){i=!0,a=n,e=u;break}c=c.sibling}if(!i)throw Error(m(189))}}if(e.alternate!==a)throw Error(m(190))}if(e.tag!==3)throw Error(m(188));return e.stateNode.current===e?l:t}function L(l){var t=l.tag;if(t===5||t===26||t===27||t===6)return l;for(l=l.child;l!==null;){if(t=L(l),t!==null)return t;l=l.sibling}return null}var j=Object.assign,W=Symbol.for("react.element"),Ul=Symbol.for("react.transitional.element"),Hl=Symbol.for("react.portal"),_l=Symbol.for("react.fragment"),rt=Symbol.for("react.strict_mode"),Sl=Symbol.for("react.profiler"),At=Symbol.for("react.consumer"),Cl=Symbol.for("react.context"),Jl=Symbol.for("react.forward_ref"),wl=Symbol.for("react.suspense"),Ll=Symbol.for("react.suspense_list"),K=Symbol.for("react.memo"),Bl=Symbol.for("react.lazy"),H=Symbol.for("react.activity"),gl=Symbol.for("react.memo_cache_sentinel"),dl=Symbol.iterator;function xl(l){return l===null||typeof l!="object"?null:(l=dl&&l[dl]||l["@@iterator"],typeof l=="function"?l:null)}var yt=Symbol.for("react.client.reference");function Ct(l){if(l==null)return null;if(typeof l=="function")return l.$$typeof===yt?null:l.displayName||l.name||null;if(typeof l=="string")return l;switch(l){case _l:return"Fragment";case Sl:return"Profiler";case rt:return"StrictMode";case wl:return"Suspense";case Ll:return"SuspenseList";case H:return"Activity"}if(typeof l=="object")switch(l.$$typeof){case Hl:return"Portal";case Cl:return l.displayName||"Context";case At:return(l._context.displayName||"Context")+".Consumer";case Jl:var t=l.render;return l=l.displayName,l||(l=t.displayName||t.name||"",l=l!==""?"ForwardRef("+l+")":"ForwardRef"),l;case K:return t=l.displayName||null,t!==null?t:Ct(l.type)||"Memo";case Bl:t=l._payload,l=l._init;try{return Ct(l(t))}catch{}}return null}var _t=Array.isArray,S=q.__CLIENT_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE,A=B.__DOM_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE,Y={pending:!1,data:null,method:null,action:null},il=[],ml=-1;function o(l){return{current:l}}function T(l){0>ml||(l.current=il[ml],il[ml]=null,ml--)}function _(l,t){ml++,il[ml]=l.current,l.current=t}var O=o(null),Q=o(null),J=o(null),al=o(null);function kl(l,t){switch(_(J,t),_(Q,l),_(O,null),t.nodeType){case 9:case 11:l=(l=t.documentElement)&&(l=l.namespaceURI)?Xo(l):0;break;default:if(l=t.tagName,t=t.namespaceURI)t=Xo(t),l=Qo(t,l);else switch(l){case"svg":l=1;break;case"math":l=2;break;default:l=0}}T(O),_(O,l)}function Tl(){T(O),T(Q),T(J)}function Na(l){l.memoizedState!==null&&_(al,l);var t=O.current,e=Qo(t,l.type);t!==e&&(_(Q,l),_(O,e))}function zu(l){Q.current===l&&(T(O),T(Q)),al.current===l&&(T(al),hu._currentValue=Y)}var Zn,vf;function Ee(l){if(Zn===void 0)try{throw Error()}catch(e){var t=e.stack.trim().match(/\n( *(at )?)/);Zn=t&&t[1]||"",vf=-1<e.stack.indexOf(`
    at`)?" (<anonymous>)":-1<e.stack.indexOf("@")?"@unknown:0:0":""}return`
`+Zn+l+vf}var Ln=!1;function Vn(l,t){if(!l||Ln)return"";Ln=!0;var e=Error.prepareStackTrace;Error.prepareStackTrace=void 0;try{var a={DetermineComponentFrameRoot:function(){try{if(t){var p=function(){throw Error()};if(Object.defineProperty(p.prototype,"props",{set:function(){throw Error()}}),typeof Reflect=="object"&&Reflect.construct){try{Reflect.construct(p,[])}catch(g){var h=g}Reflect.construct(l,[],p)}else{try{p.call()}catch(g){h=g}l.call(p.prototype)}}else{try{throw Error()}catch(g){h=g}(p=l())&&typeof p.catch=="function"&&p.catch(function(){})}}catch(g){if(g&&h&&typeof g.stack=="string")return[g.stack,h.stack]}return[null,null]}};a.DetermineComponentFrameRoot.displayName="DetermineComponentFrameRoot";var u=Object.getOwnPropertyDescriptor(a.DetermineComponentFrameRoot,"name");u&&u.configurable&&Object.defineProperty(a.DetermineComponentFrameRoot,"name",{value:"DetermineComponentFrameRoot"});var n=a.DetermineComponentFrameRoot(),i=n[0],c=n[1];if(i&&c){var f=i.split(`
`),y=c.split(`
`);for(u=a=0;a<f.length&&!f[a].includes("DetermineComponentFrameRoot");)a++;for(;u<y.length&&!y[u].includes("DetermineComponentFrameRoot");)u++;if(a===f.length||u===y.length)for(a=f.length-1,u=y.length-1;1<=a&&0<=u&&f[a]!==y[u];)u--;for(;1<=a&&0<=u;a--,u--)if(f[a]!==y[u]){if(a!==1||u!==1)do if(a--,u--,0>u||f[a]!==y[u]){var b=`
`+f[a].replace(" at new "," at ");return l.displayName&&b.includes("<anonymous>")&&(b=b.replace("<anonymous>",l.displayName)),b}while(1<=a&&0<=u);break}}}finally{Ln=!1,Error.prepareStackTrace=e}return(e=l?l.displayName||l.name:"")?Ee(e):""}function qd(l,t){switch(l.tag){case 26:case 27:case 5:return Ee(l.type);case 16:return Ee("Lazy");case 13:return l.child!==t&&t!==null?Ee("Suspense Fallback"):Ee("Suspense");case 19:return Ee("SuspenseList");case 0:case 15:return Vn(l.type,!1);case 11:return Vn(l.type.render,!1);case 1:return Vn(l.type,!0);case 31:return Ee("Activity");default:return""}}function hf(l){try{var t="",e=null;do t+=qd(l,e),e=l,l=l.return;while(l);return t}catch(a){return`
Error generating stack: `+a.message+`
`+a.stack}}var Kn=Object.prototype.hasOwnProperty,Jn=E.unstable_scheduleCallback,wn=E.unstable_cancelCallback,Bd=E.unstable_shouldYield,Yd=E.unstable_requestPaint,at=E.unstable_now,Gd=E.unstable_getCurrentPriorityLevel,gf=E.unstable_ImmediatePriority,bf=E.unstable_UserBlockingPriority,Tu=E.unstable_NormalPriority,Xd=E.unstable_LowPriority,Sf=E.unstable_IdlePriority,Qd=E.log,Zd=E.unstable_setDisableYieldValue,Ma=null,ut=null;function Pt(l){if(typeof Qd=="function"&&Zd(l),ut&&typeof ut.setStrictMode=="function")try{ut.setStrictMode(Ma,l)}catch{}}var nt=Math.clz32?Math.clz32:Kd,Ld=Math.log,Vd=Math.LN2;function Kd(l){return l>>>=0,l===0?32:31-(Ld(l)/Vd|0)|0}var Eu=256,Au=262144,_u=4194304;function Ae(l){var t=l&42;if(t!==0)return t;switch(l&-l){case 1:return 1;case 2:return 2;case 4:return 4;case 8:return 8;case 16:return 16;case 32:return 32;case 64:return 64;case 128:return 128;case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:return l&261888;case 262144:case 524288:case 1048576:case 2097152:return l&3932160;case 4194304:case 8388608:case 16777216:case 33554432:return l&62914560;case 67108864:return 67108864;case 134217728:return 134217728;case 268435456:return 268435456;case 536870912:return 536870912;case 1073741824:return 0;default:return l}}function Nu(l,t,e){var a=l.pendingLanes;if(a===0)return 0;var u=0,n=l.suspendedLanes,i=l.pingedLanes;l=l.warmLanes;var c=a&134217727;return c!==0?(a=c&~n,a!==0?u=Ae(a):(i&=c,i!==0?u=Ae(i):e||(e=c&~l,e!==0&&(u=Ae(e))))):(c=a&~n,c!==0?u=Ae(c):i!==0?u=Ae(i):e||(e=a&~l,e!==0&&(u=Ae(e)))),u===0?0:t!==0&&t!==u&&(t&n)===0&&(n=u&-u,e=t&-t,n>=e||n===32&&(e&4194048)!==0)?t:u}function Oa(l,t){return(l.pendingLanes&~(l.suspendedLanes&~l.pingedLanes)&t)===0}function Jd(l,t){switch(l){case 1:case 2:case 4:case 8:case 64:return t+250;case 16:case 32:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:return t+5e3;case 4194304:case 8388608:case 16777216:case 33554432:return-1;case 67108864:case 134217728:case 268435456:case 536870912:case 1073741824:return-1;default:return-1}}function xf(){var l=_u;return _u<<=1,(_u&62914560)===0&&(_u=4194304),l}function kn(l){for(var t=[],e=0;31>e;e++)t.push(l);return t}function Da(l,t){l.pendingLanes|=t,t!==268435456&&(l.suspendedLanes=0,l.pingedLanes=0,l.warmLanes=0)}function wd(l,t,e,a,u,n){var i=l.pendingLanes;l.pendingLanes=e,l.suspendedLanes=0,l.pingedLanes=0,l.warmLanes=0,l.expiredLanes&=e,l.entangledLanes&=e,l.errorRecoveryDisabledLanes&=e,l.shellSuspendCounter=0;var c=l.entanglements,f=l.expirationTimes,y=l.hiddenUpdates;for(e=i&~e;0<e;){var b=31-nt(e),p=1<<b;c[b]=0,f[b]=-1;var h=y[b];if(h!==null)for(y[b]=null,b=0;b<h.length;b++){var g=h[b];g!==null&&(g.lane&=-536870913)}e&=~p}a!==0&&pf(l,a,0),n!==0&&u===0&&l.tag!==0&&(l.suspendedLanes|=n&~(i&~t))}function pf(l,t,e){l.pendingLanes|=t,l.suspendedLanes&=~t;var a=31-nt(t);l.entangledLanes|=t,l.entanglements[a]=l.entanglements[a]|1073741824|e&261930}function zf(l,t){var e=l.entangledLanes|=t;for(l=l.entanglements;e;){var a=31-nt(e),u=1<<a;u&t|l[a]&t&&(l[a]|=t),e&=~u}}function Tf(l,t){var e=t&-t;return e=(e&42)!==0?1:Wn(e),(e&(l.suspendedLanes|t))!==0?0:e}function Wn(l){switch(l){case 2:l=1;break;case 8:l=4;break;case 32:l=16;break;case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:case 4194304:case 8388608:case 16777216:case 33554432:l=128;break;case 268435456:l=134217728;break;default:l=0}return l}function $n(l){return l&=-l,2<l?8<l?(l&134217727)!==0?32:268435456:8:2}function Ef(){var l=A.p;return l!==0?l:(l=window.event,l===void 0?32:od(l.type))}function Af(l,t){var e=A.p;try{return A.p=l,t()}finally{A.p=e}}var le=Math.random().toString(36).slice(2),Yl="__reactFiber$"+le,$l="__reactProps$"+le,Le="__reactContainer$"+le,Fn="__reactEvents$"+le,kd="__reactListeners$"+le,Wd="__reactHandles$"+le,_f="__reactResources$"+le,ja="__reactMarker$"+le;function In(l){delete l[Yl],delete l[$l],delete l[Fn],delete l[kd],delete l[Wd]}function Ve(l){var t=l[Yl];if(t)return t;for(var e=l.parentNode;e;){if(t=e[Le]||e[Yl]){if(e=t.alternate,t.child!==null||e!==null&&e.child!==null)for(l=ko(l);l!==null;){if(e=l[Yl])return e;l=ko(l)}return t}l=e,e=l.parentNode}return null}function Ke(l){if(l=l[Yl]||l[Le]){var t=l.tag;if(t===5||t===6||t===13||t===31||t===26||t===27||t===3)return l}return null}function Ua(l){var t=l.tag;if(t===5||t===26||t===27||t===6)return l.stateNode;throw Error(m(33))}function Je(l){var t=l[_f];return t||(t=l[_f]={hoistableStyles:new Map,hoistableScripts:new Map}),t}function Rl(l){l[ja]=!0}var Nf=new Set,Mf={};function _e(l,t){we(l,t),we(l+"Capture",t)}function we(l,t){for(Mf[l]=t,l=0;l<t.length;l++)Nf.add(t[l])}var $d=RegExp("^[:A-Z_a-z\\u00C0-\\u00D6\\u00D8-\\u00F6\\u00F8-\\u02FF\\u0370-\\u037D\\u037F-\\u1FFF\\u200C-\\u200D\\u2070-\\u218F\\u2C00-\\u2FEF\\u3001-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFFD][:A-Z_a-z\\u00C0-\\u00D6\\u00D8-\\u00F6\\u00F8-\\u02FF\\u0370-\\u037D\\u037F-\\u1FFF\\u200C-\\u200D\\u2070-\\u218F\\u2C00-\\u2FEF\\u3001-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFFD\\-.0-9\\u00B7\\u0300-\\u036F\\u203F-\\u2040]*$"),Of={},Df={};function Fd(l){return Kn.call(Df,l)?!0:Kn.call(Of,l)?!1:$d.test(l)?Df[l]=!0:(Of[l]=!0,!1)}function Mu(l,t,e){if(Fd(t))if(e===null)l.removeAttribute(t);else{switch(typeof e){case"undefined":case"function":case"symbol":l.removeAttribute(t);return;case"boolean":var a=t.toLowerCase().slice(0,5);if(a!=="data-"&&a!=="aria-"){l.removeAttribute(t);return}}l.setAttribute(t,""+e)}}function Ou(l,t,e){if(e===null)l.removeAttribute(t);else{switch(typeof e){case"undefined":case"function":case"symbol":case"boolean":l.removeAttribute(t);return}l.setAttribute(t,""+e)}}function Rt(l,t,e,a){if(a===null)l.removeAttribute(e);else{switch(typeof a){case"undefined":case"function":case"symbol":case"boolean":l.removeAttribute(e);return}l.setAttributeNS(t,e,""+a)}}function vt(l){switch(typeof l){case"bigint":case"boolean":case"number":case"string":case"undefined":return l;case"object":return l;default:return""}}function jf(l){var t=l.type;return(l=l.nodeName)&&l.toLowerCase()==="input"&&(t==="checkbox"||t==="radio")}function Id(l,t,e){var a=Object.getOwnPropertyDescriptor(l.constructor.prototype,t);if(!l.hasOwnProperty(t)&&typeof a<"u"&&typeof a.get=="function"&&typeof a.set=="function"){var u=a.get,n=a.set;return Object.defineProperty(l,t,{configurable:!0,get:function(){return u.call(this)},set:function(i){e=""+i,n.call(this,i)}}),Object.defineProperty(l,t,{enumerable:a.enumerable}),{getValue:function(){return e},setValue:function(i){e=""+i},stopTracking:function(){l._valueTracker=null,delete l[t]}}}}function Pn(l){if(!l._valueTracker){var t=jf(l)?"checked":"value";l._valueTracker=Id(l,t,""+l[t])}}function Uf(l){if(!l)return!1;var t=l._valueTracker;if(!t)return!0;var e=t.getValue(),a="";return l&&(a=jf(l)?l.checked?"true":"false":l.value),l=a,l!==e?(t.setValue(l),!0):!1}function Du(l){if(l=l||(typeof document<"u"?document:void 0),typeof l>"u")return null;try{return l.activeElement||l.body}catch{return l.body}}var Pd=/[\n"\\]/g;function ht(l){return l.replace(Pd,function(t){return"\\"+t.charCodeAt(0).toString(16)+" "})}function li(l,t,e,a,u,n,i,c){l.name="",i!=null&&typeof i!="function"&&typeof i!="symbol"&&typeof i!="boolean"?l.type=i:l.removeAttribute("type"),t!=null?i==="number"?(t===0&&l.value===""||l.value!=t)&&(l.value=""+vt(t)):l.value!==""+vt(t)&&(l.value=""+vt(t)):i!=="submit"&&i!=="reset"||l.removeAttribute("value"),t!=null?ti(l,i,vt(t)):e!=null?ti(l,i,vt(e)):a!=null&&l.removeAttribute("value"),u==null&&n!=null&&(l.defaultChecked=!!n),u!=null&&(l.checked=u&&typeof u!="function"&&typeof u!="symbol"),c!=null&&typeof c!="function"&&typeof c!="symbol"&&typeof c!="boolean"?l.name=""+vt(c):l.removeAttribute("name")}function Hf(l,t,e,a,u,n,i,c){if(n!=null&&typeof n!="function"&&typeof n!="symbol"&&typeof n!="boolean"&&(l.type=n),t!=null||e!=null){if(!(n!=="submit"&&n!=="reset"||t!=null)){Pn(l);return}e=e!=null?""+vt(e):"",t=t!=null?""+vt(t):e,c||t===l.value||(l.value=t),l.defaultValue=t}a=a??u,a=typeof a!="function"&&typeof a!="symbol"&&!!a,l.checked=c?l.checked:!!a,l.defaultChecked=!!a,i!=null&&typeof i!="function"&&typeof i!="symbol"&&typeof i!="boolean"&&(l.name=i),Pn(l)}function ti(l,t,e){t==="number"&&Du(l.ownerDocument)===l||l.defaultValue===""+e||(l.defaultValue=""+e)}function ke(l,t,e,a){if(l=l.options,t){t={};for(var u=0;u<e.length;u++)t["$"+e[u]]=!0;for(e=0;e<l.length;e++)u=t.hasOwnProperty("$"+l[e].value),l[e].selected!==u&&(l[e].selected=u),u&&a&&(l[e].defaultSelected=!0)}else{for(e=""+vt(e),t=null,u=0;u<l.length;u++){if(l[u].value===e){l[u].selected=!0,a&&(l[u].defaultSelected=!0);return}t!==null||l[u].disabled||(t=l[u])}t!==null&&(t.selected=!0)}}function Cf(l,t,e){if(t!=null&&(t=""+vt(t),t!==l.value&&(l.value=t),e==null)){l.defaultValue!==t&&(l.defaultValue=t);return}l.defaultValue=e!=null?""+vt(e):""}function Rf(l,t,e,a){if(t==null){if(a!=null){if(e!=null)throw Error(m(92));if(_t(a)){if(1<a.length)throw Error(m(93));a=a[0]}e=a}e==null&&(e=""),t=e}e=vt(t),l.defaultValue=e,a=l.textContent,a===e&&a!==""&&a!==null&&(l.value=a),Pn(l)}function We(l,t){if(t){var e=l.firstChild;if(e&&e===l.lastChild&&e.nodeType===3){e.nodeValue=t;return}}l.textContent=t}var lm=new Set("animationIterationCount aspectRatio borderImageOutset borderImageSlice borderImageWidth boxFlex boxFlexGroup boxOrdinalGroup columnCount columns flex flexGrow flexPositive flexShrink flexNegative flexOrder gridArea gridRow gridRowEnd gridRowSpan gridRowStart gridColumn gridColumnEnd gridColumnSpan gridColumnStart fontWeight lineClamp lineHeight opacity order orphans scale tabSize widows zIndex zoom fillOpacity floodOpacity stopOpacity strokeDasharray strokeDashoffset strokeMiterlimit strokeOpacity strokeWidth MozAnimationIterationCount MozBoxFlex MozBoxFlexGroup MozLineClamp msAnimationIterationCount msFlex msZoom msFlexGrow msFlexNegative msFlexOrder msFlexPositive msFlexShrink msGridColumn msGridColumnSpan msGridRow msGridRowSpan WebkitAnimationIterationCount WebkitBoxFlex WebKitBoxFlexGroup WebkitBoxOrdinalGroup WebkitColumnCount WebkitColumns WebkitFlex WebkitFlexGrow WebkitFlexPositive WebkitFlexShrink WebkitLineClamp".split(" "));function qf(l,t,e){var a=t.indexOf("--")===0;e==null||typeof e=="boolean"||e===""?a?l.setProperty(t,""):t==="float"?l.cssFloat="":l[t]="":a?l.setProperty(t,e):typeof e!="number"||e===0||lm.has(t)?t==="float"?l.cssFloat=e:l[t]=(""+e).trim():l[t]=e+"px"}function Bf(l,t,e){if(t!=null&&typeof t!="object")throw Error(m(62));if(l=l.style,e!=null){for(var a in e)!e.hasOwnProperty(a)||t!=null&&t.hasOwnProperty(a)||(a.indexOf("--")===0?l.setProperty(a,""):a==="float"?l.cssFloat="":l[a]="");for(var u in t)a=t[u],t.hasOwnProperty(u)&&e[u]!==a&&qf(l,u,a)}else for(var n in t)t.hasOwnProperty(n)&&qf(l,n,t[n])}function ei(l){if(l.indexOf("-")===-1)return!1;switch(l){case"annotation-xml":case"color-profile":case"font-face":case"font-face-src":case"font-face-uri":case"font-face-format":case"font-face-name":case"missing-glyph":return!1;default:return!0}}var tm=new Map([["acceptCharset","accept-charset"],["htmlFor","for"],["httpEquiv","http-equiv"],["crossOrigin","crossorigin"],["accentHeight","accent-height"],["alignmentBaseline","alignment-baseline"],["arabicForm","arabic-form"],["baselineShift","baseline-shift"],["capHeight","cap-height"],["clipPath","clip-path"],["clipRule","clip-rule"],["colorInterpolation","color-interpolation"],["colorInterpolationFilters","color-interpolation-filters"],["colorProfile","color-profile"],["colorRendering","color-rendering"],["dominantBaseline","dominant-baseline"],["enableBackground","enable-background"],["fillOpacity","fill-opacity"],["fillRule","fill-rule"],["floodColor","flood-color"],["floodOpacity","flood-opacity"],["fontFamily","font-family"],["fontSize","font-size"],["fontSizeAdjust","font-size-adjust"],["fontStretch","font-stretch"],["fontStyle","font-style"],["fontVariant","font-variant"],["fontWeight","font-weight"],["glyphName","glyph-name"],["glyphOrientationHorizontal","glyph-orientation-horizontal"],["glyphOrientationVertical","glyph-orientation-vertical"],["horizAdvX","horiz-adv-x"],["horizOriginX","horiz-origin-x"],["imageRendering","image-rendering"],["letterSpacing","letter-spacing"],["lightingColor","lighting-color"],["markerEnd","marker-end"],["markerMid","marker-mid"],["markerStart","marker-start"],["overlinePosition","overline-position"],["overlineThickness","overline-thickness"],["paintOrder","paint-order"],["panose-1","panose-1"],["pointerEvents","pointer-events"],["renderingIntent","rendering-intent"],["shapeRendering","shape-rendering"],["stopColor","stop-color"],["stopOpacity","stop-opacity"],["strikethroughPosition","strikethrough-position"],["strikethroughThickness","strikethrough-thickness"],["strokeDasharray","stroke-dasharray"],["strokeDashoffset","stroke-dashoffset"],["strokeLinecap","stroke-linecap"],["strokeLinejoin","stroke-linejoin"],["strokeMiterlimit","stroke-miterlimit"],["strokeOpacity","stroke-opacity"],["strokeWidth","stroke-width"],["textAnchor","text-anchor"],["textDecoration","text-decoration"],["textRendering","text-rendering"],["transformOrigin","transform-origin"],["underlinePosition","underline-position"],["underlineThickness","underline-thickness"],["unicodeBidi","unicode-bidi"],["unicodeRange","unicode-range"],["unitsPerEm","units-per-em"],["vAlphabetic","v-alphabetic"],["vHanging","v-hanging"],["vIdeographic","v-ideographic"],["vMathematical","v-mathematical"],["vectorEffect","vector-effect"],["vertAdvY","vert-adv-y"],["vertOriginX","vert-origin-x"],["vertOriginY","vert-origin-y"],["wordSpacing","word-spacing"],["writingMode","writing-mode"],["xmlnsXlink","xmlns:xlink"],["xHeight","x-height"]]),em=/^[\u0000-\u001F ]*j[\r\n\t]*a[\r\n\t]*v[\r\n\t]*a[\r\n\t]*s[\r\n\t]*c[\r\n\t]*r[\r\n\t]*i[\r\n\t]*p[\r\n\t]*t[\r\n\t]*:/i;function ju(l){return em.test(""+l)?"javascript:throw new Error('React has blocked a javascript: URL as a security precaution.')":l}function qt(){}var ai=null;function ui(l){return l=l.target||l.srcElement||window,l.correspondingUseElement&&(l=l.correspondingUseElement),l.nodeType===3?l.parentNode:l}var $e=null,Fe=null;function Yf(l){var t=Ke(l);if(t&&(l=t.stateNode)){var e=l[$l]||null;l:switch(l=t.stateNode,t.type){case"input":if(li(l,e.value,e.defaultValue,e.defaultValue,e.checked,e.defaultChecked,e.type,e.name),t=e.name,e.type==="radio"&&t!=null){for(e=l;e.parentNode;)e=e.parentNode;for(e=e.querySelectorAll('input[name="'+ht(""+t)+'"][type="radio"]'),t=0;t<e.length;t++){var a=e[t];if(a!==l&&a.form===l.form){var u=a[$l]||null;if(!u)throw Error(m(90));li(a,u.value,u.defaultValue,u.defaultValue,u.checked,u.defaultChecked,u.type,u.name)}}for(t=0;t<e.length;t++)a=e[t],a.form===l.form&&Uf(a)}break l;case"textarea":Cf(l,e.value,e.defaultValue);break l;case"select":t=e.value,t!=null&&ke(l,!!e.multiple,t,!1)}}}var ni=!1;function Gf(l,t,e){if(ni)return l(t,e);ni=!0;try{var a=l(t);return a}finally{if(ni=!1,($e!==null||Fe!==null)&&(Sn(),$e&&(t=$e,l=Fe,Fe=$e=null,Yf(t),l)))for(t=0;t<l.length;t++)Yf(l[t])}}function Ha(l,t){var e=l.stateNode;if(e===null)return null;var a=e[$l]||null;if(a===null)return null;e=a[t];l:switch(t){case"onClick":case"onClickCapture":case"onDoubleClick":case"onDoubleClickCapture":case"onMouseDown":case"onMouseDownCapture":case"onMouseMove":case"onMouseMoveCapture":case"onMouseUp":case"onMouseUpCapture":case"onMouseEnter":(a=!a.disabled)||(l=l.type,a=!(l==="button"||l==="input"||l==="select"||l==="textarea")),l=!a;break l;default:l=!1}if(l)return null;if(e&&typeof e!="function")throw Error(m(231,t,typeof e));return e}var Bt=!(typeof window>"u"||typeof window.document>"u"||typeof window.document.createElement>"u"),ii=!1;if(Bt)try{var Ca={};Object.defineProperty(Ca,"passive",{get:function(){ii=!0}}),window.addEventListener("test",Ca,Ca),window.removeEventListener("test",Ca,Ca)}catch{ii=!1}var te=null,ci=null,Uu=null;function Xf(){if(Uu)return Uu;var l,t=ci,e=t.length,a,u="value"in te?te.value:te.textContent,n=u.length;for(l=0;l<e&&t[l]===u[l];l++);var i=e-l;for(a=1;a<=i&&t[e-a]===u[n-a];a++);return Uu=u.slice(l,1<a?1-a:void 0)}function Hu(l){var t=l.keyCode;return"charCode"in l?(l=l.charCode,l===0&&t===13&&(l=13)):l=t,l===10&&(l=13),32<=l||l===13?l:0}function Cu(){return!0}function Qf(){return!1}function Fl(l){function t(e,a,u,n,i){this._reactName=e,this._targetInst=u,this.type=a,this.nativeEvent=n,this.target=i,this.currentTarget=null;for(var c in l)l.hasOwnProperty(c)&&(e=l[c],this[c]=e?e(n):n[c]);return this.isDefaultPrevented=(n.defaultPrevented!=null?n.defaultPrevented:n.returnValue===!1)?Cu:Qf,this.isPropagationStopped=Qf,this}return j(t.prototype,{preventDefault:function(){this.defaultPrevented=!0;var e=this.nativeEvent;e&&(e.preventDefault?e.preventDefault():typeof e.returnValue!="unknown"&&(e.returnValue=!1),this.isDefaultPrevented=Cu)},stopPropagation:function(){var e=this.nativeEvent;e&&(e.stopPropagation?e.stopPropagation():typeof e.cancelBubble!="unknown"&&(e.cancelBubble=!0),this.isPropagationStopped=Cu)},persist:function(){},isPersistent:Cu}),t}var Ne={eventPhase:0,bubbles:0,cancelable:0,timeStamp:function(l){return l.timeStamp||Date.now()},defaultPrevented:0,isTrusted:0},Ru=Fl(Ne),Ra=j({},Ne,{view:0,detail:0}),am=Fl(Ra),fi,si,qa,qu=j({},Ra,{screenX:0,screenY:0,clientX:0,clientY:0,pageX:0,pageY:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,getModifierState:di,button:0,buttons:0,relatedTarget:function(l){return l.relatedTarget===void 0?l.fromElement===l.srcElement?l.toElement:l.fromElement:l.relatedTarget},movementX:function(l){return"movementX"in l?l.movementX:(l!==qa&&(qa&&l.type==="mousemove"?(fi=l.screenX-qa.screenX,si=l.screenY-qa.screenY):si=fi=0,qa=l),fi)},movementY:function(l){return"movementY"in l?l.movementY:si}}),Zf=Fl(qu),um=j({},qu,{dataTransfer:0}),nm=Fl(um),im=j({},Ra,{relatedTarget:0}),oi=Fl(im),cm=j({},Ne,{animationName:0,elapsedTime:0,pseudoElement:0}),fm=Fl(cm),sm=j({},Ne,{clipboardData:function(l){return"clipboardData"in l?l.clipboardData:window.clipboardData}}),om=Fl(sm),dm=j({},Ne,{data:0}),Lf=Fl(dm),mm={Esc:"Escape",Spacebar:" ",Left:"ArrowLeft",Up:"ArrowUp",Right:"ArrowRight",Down:"ArrowDown",Del:"Delete",Win:"OS",Menu:"ContextMenu",Apps:"ContextMenu",Scroll:"ScrollLock",MozPrintableKey:"Unidentified"},rm={8:"Backspace",9:"Tab",12:"Clear",13:"Enter",16:"Shift",17:"Control",18:"Alt",19:"Pause",20:"CapsLock",27:"Escape",32:" ",33:"PageUp",34:"PageDown",35:"End",36:"Home",37:"ArrowLeft",38:"ArrowUp",39:"ArrowRight",40:"ArrowDown",45:"Insert",46:"Delete",112:"F1",113:"F2",114:"F3",115:"F4",116:"F5",117:"F6",118:"F7",119:"F8",120:"F9",121:"F10",122:"F11",123:"F12",144:"NumLock",145:"ScrollLock",224:"Meta"},ym={Alt:"altKey",Control:"ctrlKey",Meta:"metaKey",Shift:"shiftKey"};function vm(l){var t=this.nativeEvent;return t.getModifierState?t.getModifierState(l):(l=ym[l])?!!t[l]:!1}function di(){return vm}var hm=j({},Ra,{key:function(l){if(l.key){var t=mm[l.key]||l.key;if(t!=="Unidentified")return t}return l.type==="keypress"?(l=Hu(l),l===13?"Enter":String.fromCharCode(l)):l.type==="keydown"||l.type==="keyup"?rm[l.keyCode]||"Unidentified":""},code:0,location:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,repeat:0,locale:0,getModifierState:di,charCode:function(l){return l.type==="keypress"?Hu(l):0},keyCode:function(l){return l.type==="keydown"||l.type==="keyup"?l.keyCode:0},which:function(l){return l.type==="keypress"?Hu(l):l.type==="keydown"||l.type==="keyup"?l.keyCode:0}}),gm=Fl(hm),bm=j({},qu,{pointerId:0,width:0,height:0,pressure:0,tangentialPressure:0,tiltX:0,tiltY:0,twist:0,pointerType:0,isPrimary:0}),Vf=Fl(bm),Sm=j({},Ra,{touches:0,targetTouches:0,changedTouches:0,altKey:0,metaKey:0,ctrlKey:0,shiftKey:0,getModifierState:di}),xm=Fl(Sm),pm=j({},Ne,{propertyName:0,elapsedTime:0,pseudoElement:0}),zm=Fl(pm),Tm=j({},qu,{deltaX:function(l){return"deltaX"in l?l.deltaX:"wheelDeltaX"in l?-l.wheelDeltaX:0},deltaY:function(l){return"deltaY"in l?l.deltaY:"wheelDeltaY"in l?-l.wheelDeltaY:"wheelDelta"in l?-l.wheelDelta:0},deltaZ:0,deltaMode:0}),Em=Fl(Tm),Am=j({},Ne,{newState:0,oldState:0}),_m=Fl(Am),Nm=[9,13,27,32],mi=Bt&&"CompositionEvent"in window,Ba=null;Bt&&"documentMode"in document&&(Ba=document.documentMode);var Mm=Bt&&"TextEvent"in window&&!Ba,Kf=Bt&&(!mi||Ba&&8<Ba&&11>=Ba),Jf=" ",wf=!1;function kf(l,t){switch(l){case"keyup":return Nm.indexOf(t.keyCode)!==-1;case"keydown":return t.keyCode!==229;case"keypress":case"mousedown":case"focusout":return!0;default:return!1}}function Wf(l){return l=l.detail,typeof l=="object"&&"data"in l?l.data:null}var Ie=!1;function Om(l,t){switch(l){case"compositionend":return Wf(t);case"keypress":return t.which!==32?null:(wf=!0,Jf);case"textInput":return l=t.data,l===Jf&&wf?null:l;default:return null}}function Dm(l,t){if(Ie)return l==="compositionend"||!mi&&kf(l,t)?(l=Xf(),Uu=ci=te=null,Ie=!1,l):null;switch(l){case"paste":return null;case"keypress":if(!(t.ctrlKey||t.altKey||t.metaKey)||t.ctrlKey&&t.altKey){if(t.char&&1<t.char.length)return t.char;if(t.which)return String.fromCharCode(t.which)}return null;case"compositionend":return Kf&&t.locale!=="ko"?null:t.data;default:return null}}var jm={color:!0,date:!0,datetime:!0,"datetime-local":!0,email:!0,month:!0,number:!0,password:!0,range:!0,search:!0,tel:!0,text:!0,time:!0,url:!0,week:!0};function $f(l){var t=l&&l.nodeName&&l.nodeName.toLowerCase();return t==="input"?!!jm[l.type]:t==="textarea"}function Ff(l,t,e,a){$e?Fe?Fe.push(a):Fe=[a]:$e=a,t=_n(t,"onChange"),0<t.length&&(e=new Ru("onChange","change",null,e,a),l.push({event:e,listeners:t}))}var Ya=null,Ga=null;function Um(l){Co(l,0)}function Bu(l){var t=Ua(l);if(Uf(t))return l}function If(l,t){if(l==="change")return t}var Pf=!1;if(Bt){var ri;if(Bt){var yi="oninput"in document;if(!yi){var ls=document.createElement("div");ls.setAttribute("oninput","return;"),yi=typeof ls.oninput=="function"}ri=yi}else ri=!1;Pf=ri&&(!document.documentMode||9<document.documentMode)}function ts(){Ya&&(Ya.detachEvent("onpropertychange",es),Ga=Ya=null)}function es(l){if(l.propertyName==="value"&&Bu(Ga)){var t=[];Ff(t,Ga,l,ui(l)),Gf(Um,t)}}function Hm(l,t,e){l==="focusin"?(ts(),Ya=t,Ga=e,Ya.attachEvent("onpropertychange",es)):l==="focusout"&&ts()}function Cm(l){if(l==="selectionchange"||l==="keyup"||l==="keydown")return Bu(Ga)}function Rm(l,t){if(l==="click")return Bu(t)}function qm(l,t){if(l==="input"||l==="change")return Bu(t)}function Bm(l,t){return l===t&&(l!==0||1/l===1/t)||l!==l&&t!==t}var it=typeof Object.is=="function"?Object.is:Bm;function Xa(l,t){if(it(l,t))return!0;if(typeof l!="object"||l===null||typeof t!="object"||t===null)return!1;var e=Object.keys(l),a=Object.keys(t);if(e.length!==a.length)return!1;for(a=0;a<e.length;a++){var u=e[a];if(!Kn.call(t,u)||!it(l[u],t[u]))return!1}return!0}function as(l){for(;l&&l.firstChild;)l=l.firstChild;return l}function us(l,t){var e=as(l);l=0;for(var a;e;){if(e.nodeType===3){if(a=l+e.textContent.length,l<=t&&a>=t)return{node:e,offset:t-l};l=a}l:{for(;e;){if(e.nextSibling){e=e.nextSibling;break l}e=e.parentNode}e=void 0}e=as(e)}}function ns(l,t){return l&&t?l===t?!0:l&&l.nodeType===3?!1:t&&t.nodeType===3?ns(l,t.parentNode):"contains"in l?l.contains(t):l.compareDocumentPosition?!!(l.compareDocumentPosition(t)&16):!1:!1}function is(l){l=l!=null&&l.ownerDocument!=null&&l.ownerDocument.defaultView!=null?l.ownerDocument.defaultView:window;for(var t=Du(l.document);t instanceof l.HTMLIFrameElement;){try{var e=typeof t.contentWindow.location.href=="string"}catch{e=!1}if(e)l=t.contentWindow;else break;t=Du(l.document)}return t}function vi(l){var t=l&&l.nodeName&&l.nodeName.toLowerCase();return t&&(t==="input"&&(l.type==="text"||l.type==="search"||l.type==="tel"||l.type==="url"||l.type==="password")||t==="textarea"||l.contentEditable==="true")}var Ym=Bt&&"documentMode"in document&&11>=document.documentMode,Pe=null,hi=null,Qa=null,gi=!1;function cs(l,t,e){var a=e.window===e?e.document:e.nodeType===9?e:e.ownerDocument;gi||Pe==null||Pe!==Du(a)||(a=Pe,"selectionStart"in a&&vi(a)?a={start:a.selectionStart,end:a.selectionEnd}:(a=(a.ownerDocument&&a.ownerDocument.defaultView||window).getSelection(),a={anchorNode:a.anchorNode,anchorOffset:a.anchorOffset,focusNode:a.focusNode,focusOffset:a.focusOffset}),Qa&&Xa(Qa,a)||(Qa=a,a=_n(hi,"onSelect"),0<a.length&&(t=new Ru("onSelect","select",null,t,e),l.push({event:t,listeners:a}),t.target=Pe)))}function Me(l,t){var e={};return e[l.toLowerCase()]=t.toLowerCase(),e["Webkit"+l]="webkit"+t,e["Moz"+l]="moz"+t,e}var la={animationend:Me("Animation","AnimationEnd"),animationiteration:Me("Animation","AnimationIteration"),animationstart:Me("Animation","AnimationStart"),transitionrun:Me("Transition","TransitionRun"),transitionstart:Me("Transition","TransitionStart"),transitioncancel:Me("Transition","TransitionCancel"),transitionend:Me("Transition","TransitionEnd")},bi={},fs={};Bt&&(fs=document.createElement("div").style,"AnimationEvent"in window||(delete la.animationend.animation,delete la.animationiteration.animation,delete la.animationstart.animation),"TransitionEvent"in window||delete la.transitionend.transition);function Oe(l){if(bi[l])return bi[l];if(!la[l])return l;var t=la[l],e;for(e in t)if(t.hasOwnProperty(e)&&e in fs)return bi[l]=t[e];return l}var ss=Oe("animationend"),os=Oe("animationiteration"),ds=Oe("animationstart"),Gm=Oe("transitionrun"),Xm=Oe("transitionstart"),Qm=Oe("transitioncancel"),ms=Oe("transitionend"),rs=new Map,Si="abort auxClick beforeToggle cancel canPlay canPlayThrough click close contextMenu copy cut drag dragEnd dragEnter dragExit dragLeave dragOver dragStart drop durationChange emptied encrypted ended error gotPointerCapture input invalid keyDown keyPress keyUp load loadedData loadedMetadata loadStart lostPointerCapture mouseDown mouseMove mouseOut mouseOver mouseUp paste pause play playing pointerCancel pointerDown pointerMove pointerOut pointerOver pointerUp progress rateChange reset resize seeked seeking stalled submit suspend timeUpdate touchCancel touchEnd touchStart volumeChange scroll toggle touchMove waiting wheel".split(" ");Si.push("scrollEnd");function Nt(l,t){rs.set(l,t),_e(t,[l])}var Yu=typeof reportError=="function"?reportError:function(l){if(typeof window=="object"&&typeof window.ErrorEvent=="function"){var t=new window.ErrorEvent("error",{bubbles:!0,cancelable:!0,message:typeof l=="object"&&l!==null&&typeof l.message=="string"?String(l.message):String(l),error:l});if(!window.dispatchEvent(t))return}else if(typeof process=="object"&&typeof process.emit=="function"){process.emit("uncaughtException",l);return}console.error(l)},gt=[],ta=0,xi=0;function Gu(){for(var l=ta,t=xi=ta=0;t<l;){var e=gt[t];gt[t++]=null;var a=gt[t];gt[t++]=null;var u=gt[t];gt[t++]=null;var n=gt[t];if(gt[t++]=null,a!==null&&u!==null){var i=a.pending;i===null?u.next=u:(u.next=i.next,i.next=u),a.pending=u}n!==0&&ys(e,u,n)}}function Xu(l,t,e,a){gt[ta++]=l,gt[ta++]=t,gt[ta++]=e,gt[ta++]=a,xi|=a,l.lanes|=a,l=l.alternate,l!==null&&(l.lanes|=a)}function pi(l,t,e,a){return Xu(l,t,e,a),Qu(l)}function De(l,t){return Xu(l,null,null,t),Qu(l)}function ys(l,t,e){l.lanes|=e;var a=l.alternate;a!==null&&(a.lanes|=e);for(var u=!1,n=l.return;n!==null;)n.childLanes|=e,a=n.alternate,a!==null&&(a.childLanes|=e),n.tag===22&&(l=n.stateNode,l===null||l._visibility&1||(u=!0)),l=n,n=n.return;return l.tag===3?(n=l.stateNode,u&&t!==null&&(u=31-nt(e),l=n.hiddenUpdates,a=l[u],a===null?l[u]=[t]:a.push(t),t.lane=e|536870912),n):null}function Qu(l){if(50<su)throw su=0,Dc=null,Error(m(185));for(var t=l.return;t!==null;)l=t,t=l.return;return l.tag===3?l.stateNode:null}var ea={};function Zm(l,t,e,a){this.tag=l,this.key=e,this.sibling=this.child=this.return=this.stateNode=this.type=this.elementType=null,this.index=0,this.refCleanup=this.ref=null,this.pendingProps=t,this.dependencies=this.memoizedState=this.updateQueue=this.memoizedProps=null,this.mode=a,this.subtreeFlags=this.flags=0,this.deletions=null,this.childLanes=this.lanes=0,this.alternate=null}function ct(l,t,e,a){return new Zm(l,t,e,a)}function zi(l){return l=l.prototype,!(!l||!l.isReactComponent)}function Yt(l,t){var e=l.alternate;return e===null?(e=ct(l.tag,t,l.key,l.mode),e.elementType=l.elementType,e.type=l.type,e.stateNode=l.stateNode,e.alternate=l,l.alternate=e):(e.pendingProps=t,e.type=l.type,e.flags=0,e.subtreeFlags=0,e.deletions=null),e.flags=l.flags&65011712,e.childLanes=l.childLanes,e.lanes=l.lanes,e.child=l.child,e.memoizedProps=l.memoizedProps,e.memoizedState=l.memoizedState,e.updateQueue=l.updateQueue,t=l.dependencies,e.dependencies=t===null?null:{lanes:t.lanes,firstContext:t.firstContext},e.sibling=l.sibling,e.index=l.index,e.ref=l.ref,e.refCleanup=l.refCleanup,e}function vs(l,t){l.flags&=65011714;var e=l.alternate;return e===null?(l.childLanes=0,l.lanes=t,l.child=null,l.subtreeFlags=0,l.memoizedProps=null,l.memoizedState=null,l.updateQueue=null,l.dependencies=null,l.stateNode=null):(l.childLanes=e.childLanes,l.lanes=e.lanes,l.child=e.child,l.subtreeFlags=0,l.deletions=null,l.memoizedProps=e.memoizedProps,l.memoizedState=e.memoizedState,l.updateQueue=e.updateQueue,l.type=e.type,t=e.dependencies,l.dependencies=t===null?null:{lanes:t.lanes,firstContext:t.firstContext}),l}function Zu(l,t,e,a,u,n){var i=0;if(a=l,typeof l=="function")zi(l)&&(i=1);else if(typeof l=="string")i=wr(l,e,O.current)?26:l==="html"||l==="head"||l==="body"?27:5;else l:switch(l){case H:return l=ct(31,e,t,u),l.elementType=H,l.lanes=n,l;case _l:return je(e.children,u,n,t);case rt:i=8,u|=24;break;case Sl:return l=ct(12,e,t,u|2),l.elementType=Sl,l.lanes=n,l;case wl:return l=ct(13,e,t,u),l.elementType=wl,l.lanes=n,l;case Ll:return l=ct(19,e,t,u),l.elementType=Ll,l.lanes=n,l;default:if(typeof l=="object"&&l!==null)switch(l.$$typeof){case Cl:i=10;break l;case At:i=9;break l;case Jl:i=11;break l;case K:i=14;break l;case Bl:i=16,a=null;break l}i=29,e=Error(m(130,l===null?"null":typeof l,"")),a=null}return t=ct(i,e,t,u),t.elementType=l,t.type=a,t.lanes=n,t}function je(l,t,e,a){return l=ct(7,l,a,t),l.lanes=e,l}function Ti(l,t,e){return l=ct(6,l,null,t),l.lanes=e,l}function hs(l){var t=ct(18,null,null,0);return t.stateNode=l,t}function Ei(l,t,e){return t=ct(4,l.children!==null?l.children:[],l.key,t),t.lanes=e,t.stateNode={containerInfo:l.containerInfo,pendingChildren:null,implementation:l.implementation},t}var gs=new WeakMap;function bt(l,t){if(typeof l=="object"&&l!==null){var e=gs.get(l);return e!==void 0?e:(t={value:l,source:t,stack:hf(t)},gs.set(l,t),t)}return{value:l,source:t,stack:hf(t)}}var aa=[],ua=0,Lu=null,Za=0,St=[],xt=0,ee=null,Dt=1,jt="";function Gt(l,t){aa[ua++]=Za,aa[ua++]=Lu,Lu=l,Za=t}function bs(l,t,e){St[xt++]=Dt,St[xt++]=jt,St[xt++]=ee,ee=l;var a=Dt;l=jt;var u=32-nt(a)-1;a&=~(1<<u),e+=1;var n=32-nt(t)+u;if(30<n){var i=u-u%5;n=(a&(1<<i)-1).toString(32),a>>=i,u-=i,Dt=1<<32-nt(t)+u|e<<u|a,jt=n+l}else Dt=1<<n|e<<u|a,jt=l}function Ai(l){l.return!==null&&(Gt(l,1),bs(l,1,0))}function _i(l){for(;l===Lu;)Lu=aa[--ua],aa[ua]=null,Za=aa[--ua],aa[ua]=null;for(;l===ee;)ee=St[--xt],St[xt]=null,jt=St[--xt],St[xt]=null,Dt=St[--xt],St[xt]=null}function Ss(l,t){St[xt++]=Dt,St[xt++]=jt,St[xt++]=ee,Dt=t.id,jt=t.overflow,ee=l}var Gl=null,vl=null,I=!1,ae=null,pt=!1,Ni=Error(m(519));function ue(l){var t=Error(m(418,1<arguments.length&&arguments[1]!==void 0&&arguments[1]?"text":"HTML",""));throw La(bt(t,l)),Ni}function xs(l){var t=l.stateNode,e=l.type,a=l.memoizedProps;switch(t[Yl]=l,t[$l]=a,e){case"dialog":k("cancel",t),k("close",t);break;case"iframe":case"object":case"embed":k("load",t);break;case"video":case"audio":for(e=0;e<du.length;e++)k(du[e],t);break;case"source":k("error",t);break;case"img":case"image":case"link":k("error",t),k("load",t);break;case"details":k("toggle",t);break;case"input":k("invalid",t),Hf(t,a.value,a.defaultValue,a.checked,a.defaultChecked,a.type,a.name,!0);break;case"select":k("invalid",t);break;case"textarea":k("invalid",t),Rf(t,a.value,a.defaultValue,a.children)}e=a.children,typeof e!="string"&&typeof e!="number"&&typeof e!="bigint"||t.textContent===""+e||a.suppressHydrationWarning===!0||Yo(t.textContent,e)?(a.popover!=null&&(k("beforetoggle",t),k("toggle",t)),a.onScroll!=null&&k("scroll",t),a.onScrollEnd!=null&&k("scrollend",t),a.onClick!=null&&(t.onclick=qt),t=!0):t=!1,t||ue(l,!0)}function ps(l){for(Gl=l.return;Gl;)switch(Gl.tag){case 5:case 31:case 13:pt=!1;return;case 27:case 3:pt=!0;return;default:Gl=Gl.return}}function na(l){if(l!==Gl)return!1;if(!I)return ps(l),I=!0,!1;var t=l.tag,e;if((e=t!==3&&t!==27)&&((e=t===5)&&(e=l.type,e=!(e!=="form"&&e!=="button")||Kc(l.type,l.memoizedProps)),e=!e),e&&vl&&ue(l),ps(l),t===13){if(l=l.memoizedState,l=l!==null?l.dehydrated:null,!l)throw Error(m(317));vl=wo(l)}else if(t===31){if(l=l.memoizedState,l=l!==null?l.dehydrated:null,!l)throw Error(m(317));vl=wo(l)}else t===27?(t=vl,be(l.type)?(l=$c,$c=null,vl=l):vl=t):vl=Gl?Tt(l.stateNode.nextSibling):null;return!0}function Ue(){vl=Gl=null,I=!1}function Mi(){var l=ae;return l!==null&&(tt===null?tt=l:tt.push.apply(tt,l),ae=null),l}function La(l){ae===null?ae=[l]:ae.push(l)}var Oi=o(null),He=null,Xt=null;function ne(l,t,e){_(Oi,t._currentValue),t._currentValue=e}function Qt(l){l._currentValue=Oi.current,T(Oi)}function Di(l,t,e){for(;l!==null;){var a=l.alternate;if((l.childLanes&t)!==t?(l.childLanes|=t,a!==null&&(a.childLanes|=t)):a!==null&&(a.childLanes&t)!==t&&(a.childLanes|=t),l===e)break;l=l.return}}function ji(l,t,e,a){var u=l.child;for(u!==null&&(u.return=l);u!==null;){var n=u.dependencies;if(n!==null){var i=u.child;n=n.firstContext;l:for(;n!==null;){var c=n;n=u;for(var f=0;f<t.length;f++)if(c.context===t[f]){n.lanes|=e,c=n.alternate,c!==null&&(c.lanes|=e),Di(n.return,e,l),a||(i=null);break l}n=c.next}}else if(u.tag===18){if(i=u.return,i===null)throw Error(m(341));i.lanes|=e,n=i.alternate,n!==null&&(n.lanes|=e),Di(i,e,l),i=null}else i=u.child;if(i!==null)i.return=u;else for(i=u;i!==null;){if(i===l){i=null;break}if(u=i.sibling,u!==null){u.return=i.return,i=u;break}i=i.return}u=i}}function ia(l,t,e,a){l=null;for(var u=t,n=!1;u!==null;){if(!n){if((u.flags&524288)!==0)n=!0;else if((u.flags&262144)!==0)break}if(u.tag===10){var i=u.alternate;if(i===null)throw Error(m(387));if(i=i.memoizedProps,i!==null){var c=u.type;it(u.pendingProps.value,i.value)||(l!==null?l.push(c):l=[c])}}else if(u===al.current){if(i=u.alternate,i===null)throw Error(m(387));i.memoizedState.memoizedState!==u.memoizedState.memoizedState&&(l!==null?l.push(hu):l=[hu])}u=u.return}l!==null&&ji(t,l,e,a),t.flags|=262144}function Vu(l){for(l=l.firstContext;l!==null;){if(!it(l.context._currentValue,l.memoizedValue))return!0;l=l.next}return!1}function Ce(l){He=l,Xt=null,l=l.dependencies,l!==null&&(l.firstContext=null)}function Xl(l){return zs(He,l)}function Ku(l,t){return He===null&&Ce(l),zs(l,t)}function zs(l,t){var e=t._currentValue;if(t={context:t,memoizedValue:e,next:null},Xt===null){if(l===null)throw Error(m(308));Xt=t,l.dependencies={lanes:0,firstContext:t},l.flags|=524288}else Xt=Xt.next=t;return e}var Lm=typeof AbortController<"u"?AbortController:function(){var l=[],t=this.signal={aborted:!1,addEventListener:function(e,a){l.push(a)}};this.abort=function(){t.aborted=!0,l.forEach(function(e){return e()})}},Vm=E.unstable_scheduleCallback,Km=E.unstable_NormalPriority,Nl={$$typeof:Cl,Consumer:null,Provider:null,_currentValue:null,_currentValue2:null,_threadCount:0};function Ui(){return{controller:new Lm,data:new Map,refCount:0}}function Va(l){l.refCount--,l.refCount===0&&Vm(Km,function(){l.controller.abort()})}var Ka=null,Hi=0,ca=0,fa=null;function Jm(l,t){if(Ka===null){var e=Ka=[];Hi=0,ca=qc(),fa={status:"pending",value:void 0,then:function(a){e.push(a)}}}return Hi++,t.then(Ts,Ts),t}function Ts(){if(--Hi===0&&Ka!==null){fa!==null&&(fa.status="fulfilled");var l=Ka;Ka=null,ca=0,fa=null;for(var t=0;t<l.length;t++)(0,l[t])()}}function wm(l,t){var e=[],a={status:"pending",value:null,reason:null,then:function(u){e.push(u)}};return l.then(function(){a.status="fulfilled",a.value=t;for(var u=0;u<e.length;u++)(0,e[u])(t)},function(u){for(a.status="rejected",a.reason=u,u=0;u<e.length;u++)(0,e[u])(void 0)}),a}var Es=S.S;S.S=function(l,t){co=at(),typeof t=="object"&&t!==null&&typeof t.then=="function"&&Jm(l,t),Es!==null&&Es(l,t)};var Re=o(null);function Ci(){var l=Re.current;return l!==null?l:rl.pooledCache}function Ju(l,t){t===null?_(Re,Re.current):_(Re,t.pool)}function As(){var l=Ci();return l===null?null:{parent:Nl._currentValue,pool:l}}var sa=Error(m(460)),Ri=Error(m(474)),wu=Error(m(542)),ku={then:function(){}};function _s(l){return l=l.status,l==="fulfilled"||l==="rejected"}function Ns(l,t,e){switch(e=l[e],e===void 0?l.push(t):e!==t&&(t.then(qt,qt),t=e),t.status){case"fulfilled":return t.value;case"rejected":throw l=t.reason,Os(l),l;default:if(typeof t.status=="string")t.then(qt,qt);else{if(l=rl,l!==null&&100<l.shellSuspendCounter)throw Error(m(482));l=t,l.status="pending",l.then(function(a){if(t.status==="pending"){var u=t;u.status="fulfilled",u.value=a}},function(a){if(t.status==="pending"){var u=t;u.status="rejected",u.reason=a}})}switch(t.status){case"fulfilled":return t.value;case"rejected":throw l=t.reason,Os(l),l}throw Be=t,sa}}function qe(l){try{var t=l._init;return t(l._payload)}catch(e){throw e!==null&&typeof e=="object"&&typeof e.then=="function"?(Be=e,sa):e}}var Be=null;function Ms(){if(Be===null)throw Error(m(459));var l=Be;return Be=null,l}function Os(l){if(l===sa||l===wu)throw Error(m(483))}var oa=null,Ja=0;function Wu(l){var t=Ja;return Ja+=1,oa===null&&(oa=[]),Ns(oa,l,t)}function wa(l,t){t=t.props.ref,l.ref=t!==void 0?t:null}function $u(l,t){throw t.$$typeof===W?Error(m(525)):(l=Object.prototype.toString.call(t),Error(m(31,l==="[object Object]"?"object with keys {"+Object.keys(t).join(", ")+"}":l)))}function Ds(l){function t(d,s){if(l){var r=d.deletions;r===null?(d.deletions=[s],d.flags|=16):r.push(s)}}function e(d,s){if(!l)return null;for(;s!==null;)t(d,s),s=s.sibling;return null}function a(d){for(var s=new Map;d!==null;)d.key!==null?s.set(d.key,d):s.set(d.index,d),d=d.sibling;return s}function u(d,s){return d=Yt(d,s),d.index=0,d.sibling=null,d}function n(d,s,r){return d.index=r,l?(r=d.alternate,r!==null?(r=r.index,r<s?(d.flags|=67108866,s):r):(d.flags|=67108866,s)):(d.flags|=1048576,s)}function i(d){return l&&d.alternate===null&&(d.flags|=67108866),d}function c(d,s,r,x){return s===null||s.tag!==6?(s=Ti(r,d.mode,x),s.return=d,s):(s=u(s,r),s.return=d,s)}function f(d,s,r,x){var U=r.type;return U===_l?b(d,s,r.props.children,x,r.key):s!==null&&(s.elementType===U||typeof U=="object"&&U!==null&&U.$$typeof===Bl&&qe(U)===s.type)?(s=u(s,r.props),wa(s,r),s.return=d,s):(s=Zu(r.type,r.key,r.props,null,d.mode,x),wa(s,r),s.return=d,s)}function y(d,s,r,x){return s===null||s.tag!==4||s.stateNode.containerInfo!==r.containerInfo||s.stateNode.implementation!==r.implementation?(s=Ei(r,d.mode,x),s.return=d,s):(s=u(s,r.children||[]),s.return=d,s)}function b(d,s,r,x,U){return s===null||s.tag!==7?(s=je(r,d.mode,x,U),s.return=d,s):(s=u(s,r),s.return=d,s)}function p(d,s,r){if(typeof s=="string"&&s!==""||typeof s=="number"||typeof s=="bigint")return s=Ti(""+s,d.mode,r),s.return=d,s;if(typeof s=="object"&&s!==null){switch(s.$$typeof){case Ul:return r=Zu(s.type,s.key,s.props,null,d.mode,r),wa(r,s),r.return=d,r;case Hl:return s=Ei(s,d.mode,r),s.return=d,s;case Bl:return s=qe(s),p(d,s,r)}if(_t(s)||xl(s))return s=je(s,d.mode,r,null),s.return=d,s;if(typeof s.then=="function")return p(d,Wu(s),r);if(s.$$typeof===Cl)return p(d,Ku(d,s),r);$u(d,s)}return null}function h(d,s,r,x){var U=s!==null?s.key:null;if(typeof r=="string"&&r!==""||typeof r=="number"||typeof r=="bigint")return U!==null?null:c(d,s,""+r,x);if(typeof r=="object"&&r!==null){switch(r.$$typeof){case Ul:return r.key===U?f(d,s,r,x):null;case Hl:return r.key===U?y(d,s,r,x):null;case Bl:return r=qe(r),h(d,s,r,x)}if(_t(r)||xl(r))return U!==null?null:b(d,s,r,x,null);if(typeof r.then=="function")return h(d,s,Wu(r),x);if(r.$$typeof===Cl)return h(d,s,Ku(d,r),x);$u(d,r)}return null}function g(d,s,r,x,U){if(typeof x=="string"&&x!==""||typeof x=="number"||typeof x=="bigint")return d=d.get(r)||null,c(s,d,""+x,U);if(typeof x=="object"&&x!==null){switch(x.$$typeof){case Ul:return d=d.get(x.key===null?r:x.key)||null,f(s,d,x,U);case Hl:return d=d.get(x.key===null?r:x.key)||null,y(s,d,x,U);case Bl:return x=qe(x),g(d,s,r,x,U)}if(_t(x)||xl(x))return d=d.get(r)||null,b(s,d,x,U,null);if(typeof x.then=="function")return g(d,s,r,Wu(x),U);if(x.$$typeof===Cl)return g(d,s,r,Ku(s,x),U);$u(s,x)}return null}function M(d,s,r,x){for(var U=null,P=null,D=s,V=s=0,F=null;D!==null&&V<r.length;V++){D.index>V?(F=D,D=null):F=D.sibling;var ll=h(d,D,r[V],x);if(ll===null){D===null&&(D=F);break}l&&D&&ll.alternate===null&&t(d,D),s=n(ll,s,V),P===null?U=ll:P.sibling=ll,P=ll,D=F}if(V===r.length)return e(d,D),I&&Gt(d,V),U;if(D===null){for(;V<r.length;V++)D=p(d,r[V],x),D!==null&&(s=n(D,s,V),P===null?U=D:P.sibling=D,P=D);return I&&Gt(d,V),U}for(D=a(D);V<r.length;V++)F=g(D,d,V,r[V],x),F!==null&&(l&&F.alternate!==null&&D.delete(F.key===null?V:F.key),s=n(F,s,V),P===null?U=F:P.sibling=F,P=F);return l&&D.forEach(function(Te){return t(d,Te)}),I&&Gt(d,V),U}function R(d,s,r,x){if(r==null)throw Error(m(151));for(var U=null,P=null,D=s,V=s=0,F=null,ll=r.next();D!==null&&!ll.done;V++,ll=r.next()){D.index>V?(F=D,D=null):F=D.sibling;var Te=h(d,D,ll.value,x);if(Te===null){D===null&&(D=F);break}l&&D&&Te.alternate===null&&t(d,D),s=n(Te,s,V),P===null?U=Te:P.sibling=Te,P=Te,D=F}if(ll.done)return e(d,D),I&&Gt(d,V),U;if(D===null){for(;!ll.done;V++,ll=r.next())ll=p(d,ll.value,x),ll!==null&&(s=n(ll,s,V),P===null?U=ll:P.sibling=ll,P=ll);return I&&Gt(d,V),U}for(D=a(D);!ll.done;V++,ll=r.next())ll=g(D,d,V,ll.value,x),ll!==null&&(l&&ll.alternate!==null&&D.delete(ll.key===null?V:ll.key),s=n(ll,s,V),P===null?U=ll:P.sibling=ll,P=ll);return l&&D.forEach(function(uy){return t(d,uy)}),I&&Gt(d,V),U}function sl(d,s,r,x){if(typeof r=="object"&&r!==null&&r.type===_l&&r.key===null&&(r=r.props.children),typeof r=="object"&&r!==null){switch(r.$$typeof){case Ul:l:{for(var U=r.key;s!==null;){if(s.key===U){if(U=r.type,U===_l){if(s.tag===7){e(d,s.sibling),x=u(s,r.props.children),x.return=d,d=x;break l}}else if(s.elementType===U||typeof U=="object"&&U!==null&&U.$$typeof===Bl&&qe(U)===s.type){e(d,s.sibling),x=u(s,r.props),wa(x,r),x.return=d,d=x;break l}e(d,s);break}else t(d,s);s=s.sibling}r.type===_l?(x=je(r.props.children,d.mode,x,r.key),x.return=d,d=x):(x=Zu(r.type,r.key,r.props,null,d.mode,x),wa(x,r),x.return=d,d=x)}return i(d);case Hl:l:{for(U=r.key;s!==null;){if(s.key===U)if(s.tag===4&&s.stateNode.containerInfo===r.containerInfo&&s.stateNode.implementation===r.implementation){e(d,s.sibling),x=u(s,r.children||[]),x.return=d,d=x;break l}else{e(d,s);break}else t(d,s);s=s.sibling}x=Ei(r,d.mode,x),x.return=d,d=x}return i(d);case Bl:return r=qe(r),sl(d,s,r,x)}if(_t(r))return M(d,s,r,x);if(xl(r)){if(U=xl(r),typeof U!="function")throw Error(m(150));return r=U.call(r),R(d,s,r,x)}if(typeof r.then=="function")return sl(d,s,Wu(r),x);if(r.$$typeof===Cl)return sl(d,s,Ku(d,r),x);$u(d,r)}return typeof r=="string"&&r!==""||typeof r=="number"||typeof r=="bigint"?(r=""+r,s!==null&&s.tag===6?(e(d,s.sibling),x=u(s,r),x.return=d,d=x):(e(d,s),x=Ti(r,d.mode,x),x.return=d,d=x),i(d)):e(d,s)}return function(d,s,r,x){try{Ja=0;var U=sl(d,s,r,x);return oa=null,U}catch(D){if(D===sa||D===wu)throw D;var P=ct(29,D,null,d.mode);return P.lanes=x,P.return=d,P}finally{}}}var Ye=Ds(!0),js=Ds(!1),ie=!1;function qi(l){l.updateQueue={baseState:l.memoizedState,firstBaseUpdate:null,lastBaseUpdate:null,shared:{pending:null,lanes:0,hiddenCallbacks:null},callbacks:null}}function Bi(l,t){l=l.updateQueue,t.updateQueue===l&&(t.updateQueue={baseState:l.baseState,firstBaseUpdate:l.firstBaseUpdate,lastBaseUpdate:l.lastBaseUpdate,shared:l.shared,callbacks:null})}function ce(l){return{lane:l,tag:0,payload:null,callback:null,next:null}}function fe(l,t,e){var a=l.updateQueue;if(a===null)return null;if(a=a.shared,(tl&2)!==0){var u=a.pending;return u===null?t.next=t:(t.next=u.next,u.next=t),a.pending=t,t=Qu(l),ys(l,null,e),t}return Xu(l,a,t,e),Qu(l)}function ka(l,t,e){if(t=t.updateQueue,t!==null&&(t=t.shared,(e&4194048)!==0)){var a=t.lanes;a&=l.pendingLanes,e|=a,t.lanes=e,zf(l,e)}}function Yi(l,t){var e=l.updateQueue,a=l.alternate;if(a!==null&&(a=a.updateQueue,e===a)){var u=null,n=null;if(e=e.firstBaseUpdate,e!==null){do{var i={lane:e.lane,tag:e.tag,payload:e.payload,callback:null,next:null};n===null?u=n=i:n=n.next=i,e=e.next}while(e!==null);n===null?u=n=t:n=n.next=t}else u=n=t;e={baseState:a.baseState,firstBaseUpdate:u,lastBaseUpdate:n,shared:a.shared,callbacks:a.callbacks},l.updateQueue=e;return}l=e.lastBaseUpdate,l===null?e.firstBaseUpdate=t:l.next=t,e.lastBaseUpdate=t}var Gi=!1;function Wa(){if(Gi){var l=fa;if(l!==null)throw l}}function $a(l,t,e,a){Gi=!1;var u=l.updateQueue;ie=!1;var n=u.firstBaseUpdate,i=u.lastBaseUpdate,c=u.shared.pending;if(c!==null){u.shared.pending=null;var f=c,y=f.next;f.next=null,i===null?n=y:i.next=y,i=f;var b=l.alternate;b!==null&&(b=b.updateQueue,c=b.lastBaseUpdate,c!==i&&(c===null?b.firstBaseUpdate=y:c.next=y,b.lastBaseUpdate=f))}if(n!==null){var p=u.baseState;i=0,b=y=f=null,c=n;do{var h=c.lane&-536870913,g=h!==c.lane;if(g?($&h)===h:(a&h)===h){h!==0&&h===ca&&(Gi=!0),b!==null&&(b=b.next={lane:0,tag:c.tag,payload:c.payload,callback:null,next:null});l:{var M=l,R=c;h=t;var sl=e;switch(R.tag){case 1:if(M=R.payload,typeof M=="function"){p=M.call(sl,p,h);break l}p=M;break l;case 3:M.flags=M.flags&-65537|128;case 0:if(M=R.payload,h=typeof M=="function"?M.call(sl,p,h):M,h==null)break l;p=j({},p,h);break l;case 2:ie=!0}}h=c.callback,h!==null&&(l.flags|=64,g&&(l.flags|=8192),g=u.callbacks,g===null?u.callbacks=[h]:g.push(h))}else g={lane:h,tag:c.tag,payload:c.payload,callback:c.callback,next:null},b===null?(y=b=g,f=p):b=b.next=g,i|=h;if(c=c.next,c===null){if(c=u.shared.pending,c===null)break;g=c,c=g.next,g.next=null,u.lastBaseUpdate=g,u.shared.pending=null}}while(!0);b===null&&(f=p),u.baseState=f,u.firstBaseUpdate=y,u.lastBaseUpdate=b,n===null&&(u.shared.lanes=0),re|=i,l.lanes=i,l.memoizedState=p}}function Us(l,t){if(typeof l!="function")throw Error(m(191,l));l.call(t)}function Hs(l,t){var e=l.callbacks;if(e!==null)for(l.callbacks=null,l=0;l<e.length;l++)Us(e[l],t)}var da=o(null),Fu=o(0);function Cs(l,t){l=$t,_(Fu,l),_(da,t),$t=l|t.baseLanes}function Xi(){_(Fu,$t),_(da,da.current)}function Qi(){$t=Fu.current,T(da),T(Fu)}var ft=o(null),zt=null;function se(l){var t=l.alternate;_(El,El.current&1),_(ft,l),zt===null&&(t===null||da.current!==null||t.memoizedState!==null)&&(zt=l)}function Zi(l){_(El,El.current),_(ft,l),zt===null&&(zt=l)}function Rs(l){l.tag===22?(_(El,El.current),_(ft,l),zt===null&&(zt=l)):oe()}function oe(){_(El,El.current),_(ft,ft.current)}function st(l){T(ft),zt===l&&(zt=null),T(El)}var El=o(0);function Iu(l){for(var t=l;t!==null;){if(t.tag===13){var e=t.memoizedState;if(e!==null&&(e=e.dehydrated,e===null||kc(e)||Wc(e)))return t}else if(t.tag===19&&(t.memoizedProps.revealOrder==="forwards"||t.memoizedProps.revealOrder==="backwards"||t.memoizedProps.revealOrder==="unstable_legacy-backwards"||t.memoizedProps.revealOrder==="together")){if((t.flags&128)!==0)return t}else if(t.child!==null){t.child.return=t,t=t.child;continue}if(t===l)break;for(;t.sibling===null;){if(t.return===null||t.return===l)return null;t=t.return}t.sibling.return=t.return,t=t.sibling}return null}var Zt=0,Z=null,cl=null,Ml=null,Pu=!1,ma=!1,Ge=!1,ln=0,Fa=0,ra=null,km=0;function pl(){throw Error(m(321))}function Li(l,t){if(t===null)return!1;for(var e=0;e<t.length&&e<l.length;e++)if(!it(l[e],t[e]))return!1;return!0}function Vi(l,t,e,a,u,n){return Zt=n,Z=t,t.memoizedState=null,t.updateQueue=null,t.lanes=0,S.H=l===null||l.memoizedState===null?b0:nc,Ge=!1,n=e(a,u),Ge=!1,ma&&(n=Bs(t,e,a,u)),qs(l),n}function qs(l){S.H=lu;var t=cl!==null&&cl.next!==null;if(Zt=0,Ml=cl=Z=null,Pu=!1,Fa=0,ra=null,t)throw Error(m(300));l===null||Ol||(l=l.dependencies,l!==null&&Vu(l)&&(Ol=!0))}function Bs(l,t,e,a){Z=l;var u=0;do{if(ma&&(ra=null),Fa=0,ma=!1,25<=u)throw Error(m(301));if(u+=1,Ml=cl=null,l.updateQueue!=null){var n=l.updateQueue;n.lastEffect=null,n.events=null,n.stores=null,n.memoCache!=null&&(n.memoCache.index=0)}S.H=S0,n=t(e,a)}while(ma);return n}function Wm(){var l=S.H,t=l.useState()[0];return t=typeof t.then=="function"?Ia(t):t,l=l.useState()[0],(cl!==null?cl.memoizedState:null)!==l&&(Z.flags|=1024),t}function Ki(){var l=ln!==0;return ln=0,l}function Ji(l,t,e){t.updateQueue=l.updateQueue,t.flags&=-2053,l.lanes&=~e}function wi(l){if(Pu){for(l=l.memoizedState;l!==null;){var t=l.queue;t!==null&&(t.pending=null),l=l.next}Pu=!1}Zt=0,Ml=cl=Z=null,ma=!1,Fa=ln=0,ra=null}function Wl(){var l={memoizedState:null,baseState:null,baseQueue:null,queue:null,next:null};return Ml===null?Z.memoizedState=Ml=l:Ml=Ml.next=l,Ml}function Al(){if(cl===null){var l=Z.alternate;l=l!==null?l.memoizedState:null}else l=cl.next;var t=Ml===null?Z.memoizedState:Ml.next;if(t!==null)Ml=t,cl=l;else{if(l===null)throw Z.alternate===null?Error(m(467)):Error(m(310));cl=l,l={memoizedState:cl.memoizedState,baseState:cl.baseState,baseQueue:cl.baseQueue,queue:cl.queue,next:null},Ml===null?Z.memoizedState=Ml=l:Ml=Ml.next=l}return Ml}function tn(){return{lastEffect:null,events:null,stores:null,memoCache:null}}function Ia(l){var t=Fa;return Fa+=1,ra===null&&(ra=[]),l=Ns(ra,l,t),t=Z,(Ml===null?t.memoizedState:Ml.next)===null&&(t=t.alternate,S.H=t===null||t.memoizedState===null?b0:nc),l}function en(l){if(l!==null&&typeof l=="object"){if(typeof l.then=="function")return Ia(l);if(l.$$typeof===Cl)return Xl(l)}throw Error(m(438,String(l)))}function ki(l){var t=null,e=Z.updateQueue;if(e!==null&&(t=e.memoCache),t==null){var a=Z.alternate;a!==null&&(a=a.updateQueue,a!==null&&(a=a.memoCache,a!=null&&(t={data:a.data.map(function(u){return u.slice()}),index:0})))}if(t==null&&(t={data:[],index:0}),e===null&&(e=tn(),Z.updateQueue=e),e.memoCache=t,e=t.data[t.index],e===void 0)for(e=t.data[t.index]=Array(l),a=0;a<l;a++)e[a]=gl;return t.index++,e}function Lt(l,t){return typeof t=="function"?t(l):t}function an(l){var t=Al();return Wi(t,cl,l)}function Wi(l,t,e){var a=l.queue;if(a===null)throw Error(m(311));a.lastRenderedReducer=e;var u=l.baseQueue,n=a.pending;if(n!==null){if(u!==null){var i=u.next;u.next=n.next,n.next=i}t.baseQueue=u=n,a.pending=null}if(n=l.baseState,u===null)l.memoizedState=n;else{t=u.next;var c=i=null,f=null,y=t,b=!1;do{var p=y.lane&-536870913;if(p!==y.lane?($&p)===p:(Zt&p)===p){var h=y.revertLane;if(h===0)f!==null&&(f=f.next={lane:0,revertLane:0,gesture:null,action:y.action,hasEagerState:y.hasEagerState,eagerState:y.eagerState,next:null}),p===ca&&(b=!0);else if((Zt&h)===h){y=y.next,h===ca&&(b=!0);continue}else p={lane:0,revertLane:y.revertLane,gesture:null,action:y.action,hasEagerState:y.hasEagerState,eagerState:y.eagerState,next:null},f===null?(c=f=p,i=n):f=f.next=p,Z.lanes|=h,re|=h;p=y.action,Ge&&e(n,p),n=y.hasEagerState?y.eagerState:e(n,p)}else h={lane:p,revertLane:y.revertLane,gesture:y.gesture,action:y.action,hasEagerState:y.hasEagerState,eagerState:y.eagerState,next:null},f===null?(c=f=h,i=n):f=f.next=h,Z.lanes|=p,re|=p;y=y.next}while(y!==null&&y!==t);if(f===null?i=n:f.next=c,!it(n,l.memoizedState)&&(Ol=!0,b&&(e=fa,e!==null)))throw e;l.memoizedState=n,l.baseState=i,l.baseQueue=f,a.lastRenderedState=n}return u===null&&(a.lanes=0),[l.memoizedState,a.dispatch]}function $i(l){var t=Al(),e=t.queue;if(e===null)throw Error(m(311));e.lastRenderedReducer=l;var a=e.dispatch,u=e.pending,n=t.memoizedState;if(u!==null){e.pending=null;var i=u=u.next;do n=l(n,i.action),i=i.next;while(i!==u);it(n,t.memoizedState)||(Ol=!0),t.memoizedState=n,t.baseQueue===null&&(t.baseState=n),e.lastRenderedState=n}return[n,a]}function Ys(l,t,e){var a=Z,u=Al(),n=I;if(n){if(e===void 0)throw Error(m(407));e=e()}else e=t();var i=!it((cl||u).memoizedState,e);if(i&&(u.memoizedState=e,Ol=!0),u=u.queue,Pi(Qs.bind(null,a,u,l),[l]),u.getSnapshot!==t||i||Ml!==null&&Ml.memoizedState.tag&1){if(a.flags|=2048,ya(9,{destroy:void 0},Xs.bind(null,a,u,e,t),null),rl===null)throw Error(m(349));n||(Zt&127)!==0||Gs(a,t,e)}return e}function Gs(l,t,e){l.flags|=16384,l={getSnapshot:t,value:e},t=Z.updateQueue,t===null?(t=tn(),Z.updateQueue=t,t.stores=[l]):(e=t.stores,e===null?t.stores=[l]:e.push(l))}function Xs(l,t,e,a){t.value=e,t.getSnapshot=a,Zs(t)&&Ls(l)}function Qs(l,t,e){return e(function(){Zs(t)&&Ls(l)})}function Zs(l){var t=l.getSnapshot;l=l.value;try{var e=t();return!it(l,e)}catch{return!0}}function Ls(l){var t=De(l,2);t!==null&&et(t,l,2)}function Fi(l){var t=Wl();if(typeof l=="function"){var e=l;if(l=e(),Ge){Pt(!0);try{e()}finally{Pt(!1)}}}return t.memoizedState=t.baseState=l,t.queue={pending:null,lanes:0,dispatch:null,lastRenderedReducer:Lt,lastRenderedState:l},t}function Vs(l,t,e,a){return l.baseState=e,Wi(l,cl,typeof a=="function"?a:Lt)}function $m(l,t,e,a,u){if(cn(l))throw Error(m(485));if(l=t.action,l!==null){var n={payload:u,action:l,next:null,isTransition:!0,status:"pending",value:null,reason:null,listeners:[],then:function(i){n.listeners.push(i)}};S.T!==null?e(!0):n.isTransition=!1,a(n),e=t.pending,e===null?(n.next=t.pending=n,Ks(t,n)):(n.next=e.next,t.pending=e.next=n)}}function Ks(l,t){var e=t.action,a=t.payload,u=l.state;if(t.isTransition){var n=S.T,i={};S.T=i;try{var c=e(u,a),f=S.S;f!==null&&f(i,c),Js(l,t,c)}catch(y){Ii(l,t,y)}finally{n!==null&&i.types!==null&&(n.types=i.types),S.T=n}}else try{n=e(u,a),Js(l,t,n)}catch(y){Ii(l,t,y)}}function Js(l,t,e){e!==null&&typeof e=="object"&&typeof e.then=="function"?e.then(function(a){ws(l,t,a)},function(a){return Ii(l,t,a)}):ws(l,t,e)}function ws(l,t,e){t.status="fulfilled",t.value=e,ks(t),l.state=e,t=l.pending,t!==null&&(e=t.next,e===t?l.pending=null:(e=e.next,t.next=e,Ks(l,e)))}function Ii(l,t,e){var a=l.pending;if(l.pending=null,a!==null){a=a.next;do t.status="rejected",t.reason=e,ks(t),t=t.next;while(t!==a)}l.action=null}function ks(l){l=l.listeners;for(var t=0;t<l.length;t++)(0,l[t])()}function Ws(l,t){return t}function $s(l,t){if(I){var e=rl.formState;if(e!==null){l:{var a=Z;if(I){if(vl){t:{for(var u=vl,n=pt;u.nodeType!==8;){if(!n){u=null;break t}if(u=Tt(u.nextSibling),u===null){u=null;break t}}n=u.data,u=n==="F!"||n==="F"?u:null}if(u){vl=Tt(u.nextSibling),a=u.data==="F!";break l}}ue(a)}a=!1}a&&(t=e[0])}}return e=Wl(),e.memoizedState=e.baseState=t,a={pending:null,lanes:0,dispatch:null,lastRenderedReducer:Ws,lastRenderedState:t},e.queue=a,e=v0.bind(null,Z,a),a.dispatch=e,a=Fi(!1),n=uc.bind(null,Z,!1,a.queue),a=Wl(),u={state:t,dispatch:null,action:l,pending:null},a.queue=u,e=$m.bind(null,Z,u,n,e),u.dispatch=e,a.memoizedState=l,[t,e,!1]}function Fs(l){var t=Al();return Is(t,cl,l)}function Is(l,t,e){if(t=Wi(l,t,Ws)[0],l=an(Lt)[0],typeof t=="object"&&t!==null&&typeof t.then=="function")try{var a=Ia(t)}catch(i){throw i===sa?wu:i}else a=t;t=Al();var u=t.queue,n=u.dispatch;return e!==t.memoizedState&&(Z.flags|=2048,ya(9,{destroy:void 0},Fm.bind(null,u,e),null)),[a,n,l]}function Fm(l,t){l.action=t}function Ps(l){var t=Al(),e=cl;if(e!==null)return Is(t,e,l);Al(),t=t.memoizedState,e=Al();var a=e.queue.dispatch;return e.memoizedState=l,[t,a,!1]}function ya(l,t,e,a){return l={tag:l,create:e,deps:a,inst:t,next:null},t=Z.updateQueue,t===null&&(t=tn(),Z.updateQueue=t),e=t.lastEffect,e===null?t.lastEffect=l.next=l:(a=e.next,e.next=l,l.next=a,t.lastEffect=l),l}function l0(){return Al().memoizedState}function un(l,t,e,a){var u=Wl();Z.flags|=l,u.memoizedState=ya(1|t,{destroy:void 0},e,a===void 0?null:a)}function nn(l,t,e,a){var u=Al();a=a===void 0?null:a;var n=u.memoizedState.inst;cl!==null&&a!==null&&Li(a,cl.memoizedState.deps)?u.memoizedState=ya(t,n,e,a):(Z.flags|=l,u.memoizedState=ya(1|t,n,e,a))}function t0(l,t){un(8390656,8,l,t)}function Pi(l,t){nn(2048,8,l,t)}function Im(l){Z.flags|=4;var t=Z.updateQueue;if(t===null)t=tn(),Z.updateQueue=t,t.events=[l];else{var e=t.events;e===null?t.events=[l]:e.push(l)}}function e0(l){var t=Al().memoizedState;return Im({ref:t,nextImpl:l}),function(){if((tl&2)!==0)throw Error(m(440));return t.impl.apply(void 0,arguments)}}function a0(l,t){return nn(4,2,l,t)}function u0(l,t){return nn(4,4,l,t)}function n0(l,t){if(typeof t=="function"){l=l();var e=t(l);return function(){typeof e=="function"?e():t(null)}}if(t!=null)return l=l(),t.current=l,function(){t.current=null}}function i0(l,t,e){e=e!=null?e.concat([l]):null,nn(4,4,n0.bind(null,t,l),e)}function lc(){}function c0(l,t){var e=Al();t=t===void 0?null:t;var a=e.memoizedState;return t!==null&&Li(t,a[1])?a[0]:(e.memoizedState=[l,t],l)}function f0(l,t){var e=Al();t=t===void 0?null:t;var a=e.memoizedState;if(t!==null&&Li(t,a[1]))return a[0];if(a=l(),Ge){Pt(!0);try{l()}finally{Pt(!1)}}return e.memoizedState=[a,t],a}function tc(l,t,e){return e===void 0||(Zt&1073741824)!==0&&($&261930)===0?l.memoizedState=t:(l.memoizedState=e,l=so(),Z.lanes|=l,re|=l,e)}function s0(l,t,e,a){return it(e,t)?e:da.current!==null?(l=tc(l,e,a),it(l,t)||(Ol=!0),l):(Zt&42)===0||(Zt&1073741824)!==0&&($&261930)===0?(Ol=!0,l.memoizedState=e):(l=so(),Z.lanes|=l,re|=l,t)}function o0(l,t,e,a,u){var n=A.p;A.p=n!==0&&8>n?n:8;var i=S.T,c={};S.T=c,uc(l,!1,t,e);try{var f=u(),y=S.S;if(y!==null&&y(c,f),f!==null&&typeof f=="object"&&typeof f.then=="function"){var b=wm(f,a);Pa(l,t,b,mt(l))}else Pa(l,t,a,mt(l))}catch(p){Pa(l,t,{then:function(){},status:"rejected",reason:p},mt())}finally{A.p=n,i!==null&&c.types!==null&&(i.types=c.types),S.T=i}}function Pm(){}function ec(l,t,e,a){if(l.tag!==5)throw Error(m(476));var u=d0(l).queue;o0(l,u,t,Y,e===null?Pm:function(){return m0(l),e(a)})}function d0(l){var t=l.memoizedState;if(t!==null)return t;t={memoizedState:Y,baseState:Y,baseQueue:null,queue:{pending:null,lanes:0,dispatch:null,lastRenderedReducer:Lt,lastRenderedState:Y},next:null};var e={};return t.next={memoizedState:e,baseState:e,baseQueue:null,queue:{pending:null,lanes:0,dispatch:null,lastRenderedReducer:Lt,lastRenderedState:e},next:null},l.memoizedState=t,l=l.alternate,l!==null&&(l.memoizedState=t),t}function m0(l){var t=d0(l);t.next===null&&(t=l.alternate.memoizedState),Pa(l,t.next.queue,{},mt())}function ac(){return Xl(hu)}function r0(){return Al().memoizedState}function y0(){return Al().memoizedState}function lr(l){for(var t=l.return;t!==null;){switch(t.tag){case 24:case 3:var e=mt();l=ce(e);var a=fe(t,l,e);a!==null&&(et(a,t,e),ka(a,t,e)),t={cache:Ui()},l.payload=t;return}t=t.return}}function tr(l,t,e){var a=mt();e={lane:a,revertLane:0,gesture:null,action:e,hasEagerState:!1,eagerState:null,next:null},cn(l)?h0(t,e):(e=pi(l,t,e,a),e!==null&&(et(e,l,a),g0(e,t,a)))}function v0(l,t,e){var a=mt();Pa(l,t,e,a)}function Pa(l,t,e,a){var u={lane:a,revertLane:0,gesture:null,action:e,hasEagerState:!1,eagerState:null,next:null};if(cn(l))h0(t,u);else{var n=l.alternate;if(l.lanes===0&&(n===null||n.lanes===0)&&(n=t.lastRenderedReducer,n!==null))try{var i=t.lastRenderedState,c=n(i,e);if(u.hasEagerState=!0,u.eagerState=c,it(c,i))return Xu(l,t,u,0),rl===null&&Gu(),!1}catch{}finally{}if(e=pi(l,t,u,a),e!==null)return et(e,l,a),g0(e,t,a),!0}return!1}function uc(l,t,e,a){if(a={lane:2,revertLane:qc(),gesture:null,action:a,hasEagerState:!1,eagerState:null,next:null},cn(l)){if(t)throw Error(m(479))}else t=pi(l,e,a,2),t!==null&&et(t,l,2)}function cn(l){var t=l.alternate;return l===Z||t!==null&&t===Z}function h0(l,t){ma=Pu=!0;var e=l.pending;e===null?t.next=t:(t.next=e.next,e.next=t),l.pending=t}function g0(l,t,e){if((e&4194048)!==0){var a=t.lanes;a&=l.pendingLanes,e|=a,t.lanes=e,zf(l,e)}}var lu={readContext:Xl,use:en,useCallback:pl,useContext:pl,useEffect:pl,useImperativeHandle:pl,useLayoutEffect:pl,useInsertionEffect:pl,useMemo:pl,useReducer:pl,useRef:pl,useState:pl,useDebugValue:pl,useDeferredValue:pl,useTransition:pl,useSyncExternalStore:pl,useId:pl,useHostTransitionStatus:pl,useFormState:pl,useActionState:pl,useOptimistic:pl,useMemoCache:pl,useCacheRefresh:pl};lu.useEffectEvent=pl;var b0={readContext:Xl,use:en,useCallback:function(l,t){return Wl().memoizedState=[l,t===void 0?null:t],l},useContext:Xl,useEffect:t0,useImperativeHandle:function(l,t,e){e=e!=null?e.concat([l]):null,un(4194308,4,n0.bind(null,t,l),e)},useLayoutEffect:function(l,t){return un(4194308,4,l,t)},useInsertionEffect:function(l,t){un(4,2,l,t)},useMemo:function(l,t){var e=Wl();t=t===void 0?null:t;var a=l();if(Ge){Pt(!0);try{l()}finally{Pt(!1)}}return e.memoizedState=[a,t],a},useReducer:function(l,t,e){var a=Wl();if(e!==void 0){var u=e(t);if(Ge){Pt(!0);try{e(t)}finally{Pt(!1)}}}else u=t;return a.memoizedState=a.baseState=u,l={pending:null,lanes:0,dispatch:null,lastRenderedReducer:l,lastRenderedState:u},a.queue=l,l=l.dispatch=tr.bind(null,Z,l),[a.memoizedState,l]},useRef:function(l){var t=Wl();return l={current:l},t.memoizedState=l},useState:function(l){l=Fi(l);var t=l.queue,e=v0.bind(null,Z,t);return t.dispatch=e,[l.memoizedState,e]},useDebugValue:lc,useDeferredValue:function(l,t){var e=Wl();return tc(e,l,t)},useTransition:function(){var l=Fi(!1);return l=o0.bind(null,Z,l.queue,!0,!1),Wl().memoizedState=l,[!1,l]},useSyncExternalStore:function(l,t,e){var a=Z,u=Wl();if(I){if(e===void 0)throw Error(m(407));e=e()}else{if(e=t(),rl===null)throw Error(m(349));($&127)!==0||Gs(a,t,e)}u.memoizedState=e;var n={value:e,getSnapshot:t};return u.queue=n,t0(Qs.bind(null,a,n,l),[l]),a.flags|=2048,ya(9,{destroy:void 0},Xs.bind(null,a,n,e,t),null),e},useId:function(){var l=Wl(),t=rl.identifierPrefix;if(I){var e=jt,a=Dt;e=(a&~(1<<32-nt(a)-1)).toString(32)+e,t="_"+t+"R_"+e,e=ln++,0<e&&(t+="H"+e.toString(32)),t+="_"}else e=km++,t="_"+t+"r_"+e.toString(32)+"_";return l.memoizedState=t},useHostTransitionStatus:ac,useFormState:$s,useActionState:$s,useOptimistic:function(l){var t=Wl();t.memoizedState=t.baseState=l;var e={pending:null,lanes:0,dispatch:null,lastRenderedReducer:null,lastRenderedState:null};return t.queue=e,t=uc.bind(null,Z,!0,e),e.dispatch=t,[l,t]},useMemoCache:ki,useCacheRefresh:function(){return Wl().memoizedState=lr.bind(null,Z)},useEffectEvent:function(l){var t=Wl(),e={impl:l};return t.memoizedState=e,function(){if((tl&2)!==0)throw Error(m(440));return e.impl.apply(void 0,arguments)}}},nc={readContext:Xl,use:en,useCallback:c0,useContext:Xl,useEffect:Pi,useImperativeHandle:i0,useInsertionEffect:a0,useLayoutEffect:u0,useMemo:f0,useReducer:an,useRef:l0,useState:function(){return an(Lt)},useDebugValue:lc,useDeferredValue:function(l,t){var e=Al();return s0(e,cl.memoizedState,l,t)},useTransition:function(){var l=an(Lt)[0],t=Al().memoizedState;return[typeof l=="boolean"?l:Ia(l),t]},useSyncExternalStore:Ys,useId:r0,useHostTransitionStatus:ac,useFormState:Fs,useActionState:Fs,useOptimistic:function(l,t){var e=Al();return Vs(e,cl,l,t)},useMemoCache:ki,useCacheRefresh:y0};nc.useEffectEvent=e0;var S0={readContext:Xl,use:en,useCallback:c0,useContext:Xl,useEffect:Pi,useImperativeHandle:i0,useInsertionEffect:a0,useLayoutEffect:u0,useMemo:f0,useReducer:$i,useRef:l0,useState:function(){return $i(Lt)},useDebugValue:lc,useDeferredValue:function(l,t){var e=Al();return cl===null?tc(e,l,t):s0(e,cl.memoizedState,l,t)},useTransition:function(){var l=$i(Lt)[0],t=Al().memoizedState;return[typeof l=="boolean"?l:Ia(l),t]},useSyncExternalStore:Ys,useId:r0,useHostTransitionStatus:ac,useFormState:Ps,useActionState:Ps,useOptimistic:function(l,t){var e=Al();return cl!==null?Vs(e,cl,l,t):(e.baseState=l,[l,e.queue.dispatch])},useMemoCache:ki,useCacheRefresh:y0};S0.useEffectEvent=e0;function ic(l,t,e,a){t=l.memoizedState,e=e(a,t),e=e==null?t:j({},t,e),l.memoizedState=e,l.lanes===0&&(l.updateQueue.baseState=e)}var cc={enqueueSetState:function(l,t,e){l=l._reactInternals;var a=mt(),u=ce(a);u.payload=t,e!=null&&(u.callback=e),t=fe(l,u,a),t!==null&&(et(t,l,a),ka(t,l,a))},enqueueReplaceState:function(l,t,e){l=l._reactInternals;var a=mt(),u=ce(a);u.tag=1,u.payload=t,e!=null&&(u.callback=e),t=fe(l,u,a),t!==null&&(et(t,l,a),ka(t,l,a))},enqueueForceUpdate:function(l,t){l=l._reactInternals;var e=mt(),a=ce(e);a.tag=2,t!=null&&(a.callback=t),t=fe(l,a,e),t!==null&&(et(t,l,e),ka(t,l,e))}};function x0(l,t,e,a,u,n,i){return l=l.stateNode,typeof l.shouldComponentUpdate=="function"?l.shouldComponentUpdate(a,n,i):t.prototype&&t.prototype.isPureReactComponent?!Xa(e,a)||!Xa(u,n):!0}function p0(l,t,e,a){l=t.state,typeof t.componentWillReceiveProps=="function"&&t.componentWillReceiveProps(e,a),typeof t.UNSAFE_componentWillReceiveProps=="function"&&t.UNSAFE_componentWillReceiveProps(e,a),t.state!==l&&cc.enqueueReplaceState(t,t.state,null)}function Xe(l,t){var e=t;if("ref"in t){e={};for(var a in t)a!=="ref"&&(e[a]=t[a])}if(l=l.defaultProps){e===t&&(e=j({},e));for(var u in l)e[u]===void 0&&(e[u]=l[u])}return e}function z0(l){Yu(l)}function T0(l){console.error(l)}function E0(l){Yu(l)}function fn(l,t){try{var e=l.onUncaughtError;e(t.value,{componentStack:t.stack})}catch(a){setTimeout(function(){throw a})}}function A0(l,t,e){try{var a=l.onCaughtError;a(e.value,{componentStack:e.stack,errorBoundary:t.tag===1?t.stateNode:null})}catch(u){setTimeout(function(){throw u})}}function fc(l,t,e){return e=ce(e),e.tag=3,e.payload={element:null},e.callback=function(){fn(l,t)},e}function _0(l){return l=ce(l),l.tag=3,l}function N0(l,t,e,a){var u=e.type.getDerivedStateFromError;if(typeof u=="function"){var n=a.value;l.payload=function(){return u(n)},l.callback=function(){A0(t,e,a)}}var i=e.stateNode;i!==null&&typeof i.componentDidCatch=="function"&&(l.callback=function(){A0(t,e,a),typeof u!="function"&&(ye===null?ye=new Set([this]):ye.add(this));var c=a.stack;this.componentDidCatch(a.value,{componentStack:c!==null?c:""})})}function er(l,t,e,a,u){if(e.flags|=32768,a!==null&&typeof a=="object"&&typeof a.then=="function"){if(t=e.alternate,t!==null&&ia(t,e,u,!0),e=ft.current,e!==null){switch(e.tag){case 31:case 13:return zt===null?xn():e.alternate===null&&zl===0&&(zl=3),e.flags&=-257,e.flags|=65536,e.lanes=u,a===ku?e.flags|=16384:(t=e.updateQueue,t===null?e.updateQueue=new Set([a]):t.add(a),Hc(l,a,u)),!1;case 22:return e.flags|=65536,a===ku?e.flags|=16384:(t=e.updateQueue,t===null?(t={transitions:null,markerInstances:null,retryQueue:new Set([a])},e.updateQueue=t):(e=t.retryQueue,e===null?t.retryQueue=new Set([a]):e.add(a)),Hc(l,a,u)),!1}throw Error(m(435,e.tag))}return Hc(l,a,u),xn(),!1}if(I)return t=ft.current,t!==null?((t.flags&65536)===0&&(t.flags|=256),t.flags|=65536,t.lanes=u,a!==Ni&&(l=Error(m(422),{cause:a}),La(bt(l,e)))):(a!==Ni&&(t=Error(m(423),{cause:a}),La(bt(t,e))),l=l.current.alternate,l.flags|=65536,u&=-u,l.lanes|=u,a=bt(a,e),u=fc(l.stateNode,a,u),Yi(l,u),zl!==4&&(zl=2)),!1;var n=Error(m(520),{cause:a});if(n=bt(n,e),fu===null?fu=[n]:fu.push(n),zl!==4&&(zl=2),t===null)return!0;a=bt(a,e),e=t;do{switch(e.tag){case 3:return e.flags|=65536,l=u&-u,e.lanes|=l,l=fc(e.stateNode,a,l),Yi(e,l),!1;case 1:if(t=e.type,n=e.stateNode,(e.flags&128)===0&&(typeof t.getDerivedStateFromError=="function"||n!==null&&typeof n.componentDidCatch=="function"&&(ye===null||!ye.has(n))))return e.flags|=65536,u&=-u,e.lanes|=u,u=_0(u),N0(u,l,e,a),Yi(e,u),!1}e=e.return}while(e!==null);return!1}var sc=Error(m(461)),Ol=!1;function Ql(l,t,e,a){t.child=l===null?js(t,null,e,a):Ye(t,l.child,e,a)}function M0(l,t,e,a,u){e=e.render;var n=t.ref;if("ref"in a){var i={};for(var c in a)c!=="ref"&&(i[c]=a[c])}else i=a;return Ce(t),a=Vi(l,t,e,i,n,u),c=Ki(),l!==null&&!Ol?(Ji(l,t,u),Vt(l,t,u)):(I&&c&&Ai(t),t.flags|=1,Ql(l,t,a,u),t.child)}function O0(l,t,e,a,u){if(l===null){var n=e.type;return typeof n=="function"&&!zi(n)&&n.defaultProps===void 0&&e.compare===null?(t.tag=15,t.type=n,D0(l,t,n,a,u)):(l=Zu(e.type,null,a,t,t.mode,u),l.ref=t.ref,l.return=t,t.child=l)}if(n=l.child,!gc(l,u)){var i=n.memoizedProps;if(e=e.compare,e=e!==null?e:Xa,e(i,a)&&l.ref===t.ref)return Vt(l,t,u)}return t.flags|=1,l=Yt(n,a),l.ref=t.ref,l.return=t,t.child=l}function D0(l,t,e,a,u){if(l!==null){var n=l.memoizedProps;if(Xa(n,a)&&l.ref===t.ref)if(Ol=!1,t.pendingProps=a=n,gc(l,u))(l.flags&131072)!==0&&(Ol=!0);else return t.lanes=l.lanes,Vt(l,t,u)}return oc(l,t,e,a,u)}function j0(l,t,e,a){var u=a.children,n=l!==null?l.memoizedState:null;if(l===null&&t.stateNode===null&&(t.stateNode={_visibility:1,_pendingMarkers:null,_retryCache:null,_transitions:null}),a.mode==="hidden"){if((t.flags&128)!==0){if(n=n!==null?n.baseLanes|e:e,l!==null){for(a=t.child=l.child,u=0;a!==null;)u=u|a.lanes|a.childLanes,a=a.sibling;a=u&~n}else a=0,t.child=null;return U0(l,t,n,e,a)}if((e&536870912)!==0)t.memoizedState={baseLanes:0,cachePool:null},l!==null&&Ju(t,n!==null?n.cachePool:null),n!==null?Cs(t,n):Xi(),Rs(t);else return a=t.lanes=536870912,U0(l,t,n!==null?n.baseLanes|e:e,e,a)}else n!==null?(Ju(t,n.cachePool),Cs(t,n),oe(),t.memoizedState=null):(l!==null&&Ju(t,null),Xi(),oe());return Ql(l,t,u,e),t.child}function tu(l,t){return l!==null&&l.tag===22||t.stateNode!==null||(t.stateNode={_visibility:1,_pendingMarkers:null,_retryCache:null,_transitions:null}),t.sibling}function U0(l,t,e,a,u){var n=Ci();return n=n===null?null:{parent:Nl._currentValue,pool:n},t.memoizedState={baseLanes:e,cachePool:n},l!==null&&Ju(t,null),Xi(),Rs(t),l!==null&&ia(l,t,a,!0),t.childLanes=u,null}function sn(l,t){return t=dn({mode:t.mode,children:t.children},l.mode),t.ref=l.ref,l.child=t,t.return=l,t}function H0(l,t,e){return Ye(t,l.child,null,e),l=sn(t,t.pendingProps),l.flags|=2,st(t),t.memoizedState=null,l}function ar(l,t,e){var a=t.pendingProps,u=(t.flags&128)!==0;if(t.flags&=-129,l===null){if(I){if(a.mode==="hidden")return l=sn(t,a),t.lanes=536870912,tu(null,l);if(Zi(t),(l=vl)?(l=Jo(l,pt),l=l!==null&&l.data==="&"?l:null,l!==null&&(t.memoizedState={dehydrated:l,treeContext:ee!==null?{id:Dt,overflow:jt}:null,retryLane:536870912,hydrationErrors:null},e=hs(l),e.return=t,t.child=e,Gl=t,vl=null)):l=null,l===null)throw ue(t);return t.lanes=536870912,null}return sn(t,a)}var n=l.memoizedState;if(n!==null){var i=n.dehydrated;if(Zi(t),u)if(t.flags&256)t.flags&=-257,t=H0(l,t,e);else if(t.memoizedState!==null)t.child=l.child,t.flags|=128,t=null;else throw Error(m(558));else if(Ol||ia(l,t,e,!1),u=(e&l.childLanes)!==0,Ol||u){if(a=rl,a!==null&&(i=Tf(a,e),i!==0&&i!==n.retryLane))throw n.retryLane=i,De(l,i),et(a,l,i),sc;xn(),t=H0(l,t,e)}else l=n.treeContext,vl=Tt(i.nextSibling),Gl=t,I=!0,ae=null,pt=!1,l!==null&&Ss(t,l),t=sn(t,a),t.flags|=4096;return t}return l=Yt(l.child,{mode:a.mode,children:a.children}),l.ref=t.ref,t.child=l,l.return=t,l}function on(l,t){var e=t.ref;if(e===null)l!==null&&l.ref!==null&&(t.flags|=4194816);else{if(typeof e!="function"&&typeof e!="object")throw Error(m(284));(l===null||l.ref!==e)&&(t.flags|=4194816)}}function oc(l,t,e,a,u){return Ce(t),e=Vi(l,t,e,a,void 0,u),a=Ki(),l!==null&&!Ol?(Ji(l,t,u),Vt(l,t,u)):(I&&a&&Ai(t),t.flags|=1,Ql(l,t,e,u),t.child)}function C0(l,t,e,a,u,n){return Ce(t),t.updateQueue=null,e=Bs(t,a,e,u),qs(l),a=Ki(),l!==null&&!Ol?(Ji(l,t,n),Vt(l,t,n)):(I&&a&&Ai(t),t.flags|=1,Ql(l,t,e,n),t.child)}function R0(l,t,e,a,u){if(Ce(t),t.stateNode===null){var n=ea,i=e.contextType;typeof i=="object"&&i!==null&&(n=Xl(i)),n=new e(a,n),t.memoizedState=n.state!==null&&n.state!==void 0?n.state:null,n.updater=cc,t.stateNode=n,n._reactInternals=t,n=t.stateNode,n.props=a,n.state=t.memoizedState,n.refs={},qi(t),i=e.contextType,n.context=typeof i=="object"&&i!==null?Xl(i):ea,n.state=t.memoizedState,i=e.getDerivedStateFromProps,typeof i=="function"&&(ic(t,e,i,a),n.state=t.memoizedState),typeof e.getDerivedStateFromProps=="function"||typeof n.getSnapshotBeforeUpdate=="function"||typeof n.UNSAFE_componentWillMount!="function"&&typeof n.componentWillMount!="function"||(i=n.state,typeof n.componentWillMount=="function"&&n.componentWillMount(),typeof n.UNSAFE_componentWillMount=="function"&&n.UNSAFE_componentWillMount(),i!==n.state&&cc.enqueueReplaceState(n,n.state,null),$a(t,a,n,u),Wa(),n.state=t.memoizedState),typeof n.componentDidMount=="function"&&(t.flags|=4194308),a=!0}else if(l===null){n=t.stateNode;var c=t.memoizedProps,f=Xe(e,c);n.props=f;var y=n.context,b=e.contextType;i=ea,typeof b=="object"&&b!==null&&(i=Xl(b));var p=e.getDerivedStateFromProps;b=typeof p=="function"||typeof n.getSnapshotBeforeUpdate=="function",c=t.pendingProps!==c,b||typeof n.UNSAFE_componentWillReceiveProps!="function"&&typeof n.componentWillReceiveProps!="function"||(c||y!==i)&&p0(t,n,a,i),ie=!1;var h=t.memoizedState;n.state=h,$a(t,a,n,u),Wa(),y=t.memoizedState,c||h!==y||ie?(typeof p=="function"&&(ic(t,e,p,a),y=t.memoizedState),(f=ie||x0(t,e,f,a,h,y,i))?(b||typeof n.UNSAFE_componentWillMount!="function"&&typeof n.componentWillMount!="function"||(typeof n.componentWillMount=="function"&&n.componentWillMount(),typeof n.UNSAFE_componentWillMount=="function"&&n.UNSAFE_componentWillMount()),typeof n.componentDidMount=="function"&&(t.flags|=4194308)):(typeof n.componentDidMount=="function"&&(t.flags|=4194308),t.memoizedProps=a,t.memoizedState=y),n.props=a,n.state=y,n.context=i,a=f):(typeof n.componentDidMount=="function"&&(t.flags|=4194308),a=!1)}else{n=t.stateNode,Bi(l,t),i=t.memoizedProps,b=Xe(e,i),n.props=b,p=t.pendingProps,h=n.context,y=e.contextType,f=ea,typeof y=="object"&&y!==null&&(f=Xl(y)),c=e.getDerivedStateFromProps,(y=typeof c=="function"||typeof n.getSnapshotBeforeUpdate=="function")||typeof n.UNSAFE_componentWillReceiveProps!="function"&&typeof n.componentWillReceiveProps!="function"||(i!==p||h!==f)&&p0(t,n,a,f),ie=!1,h=t.memoizedState,n.state=h,$a(t,a,n,u),Wa();var g=t.memoizedState;i!==p||h!==g||ie||l!==null&&l.dependencies!==null&&Vu(l.dependencies)?(typeof c=="function"&&(ic(t,e,c,a),g=t.memoizedState),(b=ie||x0(t,e,b,a,h,g,f)||l!==null&&l.dependencies!==null&&Vu(l.dependencies))?(y||typeof n.UNSAFE_componentWillUpdate!="function"&&typeof n.componentWillUpdate!="function"||(typeof n.componentWillUpdate=="function"&&n.componentWillUpdate(a,g,f),typeof n.UNSAFE_componentWillUpdate=="function"&&n.UNSAFE_componentWillUpdate(a,g,f)),typeof n.componentDidUpdate=="function"&&(t.flags|=4),typeof n.getSnapshotBeforeUpdate=="function"&&(t.flags|=1024)):(typeof n.componentDidUpdate!="function"||i===l.memoizedProps&&h===l.memoizedState||(t.flags|=4),typeof n.getSnapshotBeforeUpdate!="function"||i===l.memoizedProps&&h===l.memoizedState||(t.flags|=1024),t.memoizedProps=a,t.memoizedState=g),n.props=a,n.state=g,n.context=f,a=b):(typeof n.componentDidUpdate!="function"||i===l.memoizedProps&&h===l.memoizedState||(t.flags|=4),typeof n.getSnapshotBeforeUpdate!="function"||i===l.memoizedProps&&h===l.memoizedState||(t.flags|=1024),a=!1)}return n=a,on(l,t),a=(t.flags&128)!==0,n||a?(n=t.stateNode,e=a&&typeof e.getDerivedStateFromError!="function"?null:n.render(),t.flags|=1,l!==null&&a?(t.child=Ye(t,l.child,null,u),t.child=Ye(t,null,e,u)):Ql(l,t,e,u),t.memoizedState=n.state,l=t.child):l=Vt(l,t,u),l}function q0(l,t,e,a){return Ue(),t.flags|=256,Ql(l,t,e,a),t.child}var dc={dehydrated:null,treeContext:null,retryLane:0,hydrationErrors:null};function mc(l){return{baseLanes:l,cachePool:As()}}function rc(l,t,e){return l=l!==null?l.childLanes&~e:0,t&&(l|=dt),l}function B0(l,t,e){var a=t.pendingProps,u=!1,n=(t.flags&128)!==0,i;if((i=n)||(i=l!==null&&l.memoizedState===null?!1:(El.current&2)!==0),i&&(u=!0,t.flags&=-129),i=(t.flags&32)!==0,t.flags&=-33,l===null){if(I){if(u?se(t):oe(),(l=vl)?(l=Jo(l,pt),l=l!==null&&l.data!=="&"?l:null,l!==null&&(t.memoizedState={dehydrated:l,treeContext:ee!==null?{id:Dt,overflow:jt}:null,retryLane:536870912,hydrationErrors:null},e=hs(l),e.return=t,t.child=e,Gl=t,vl=null)):l=null,l===null)throw ue(t);return Wc(l)?t.lanes=32:t.lanes=536870912,null}var c=a.children;return a=a.fallback,u?(oe(),u=t.mode,c=dn({mode:"hidden",children:c},u),a=je(a,u,e,null),c.return=t,a.return=t,c.sibling=a,t.child=c,a=t.child,a.memoizedState=mc(e),a.childLanes=rc(l,i,e),t.memoizedState=dc,tu(null,a)):(se(t),yc(t,c))}var f=l.memoizedState;if(f!==null&&(c=f.dehydrated,c!==null)){if(n)t.flags&256?(se(t),t.flags&=-257,t=vc(l,t,e)):t.memoizedState!==null?(oe(),t.child=l.child,t.flags|=128,t=null):(oe(),c=a.fallback,u=t.mode,a=dn({mode:"visible",children:a.children},u),c=je(c,u,e,null),c.flags|=2,a.return=t,c.return=t,a.sibling=c,t.child=a,Ye(t,l.child,null,e),a=t.child,a.memoizedState=mc(e),a.childLanes=rc(l,i,e),t.memoizedState=dc,t=tu(null,a));else if(se(t),Wc(c)){if(i=c.nextSibling&&c.nextSibling.dataset,i)var y=i.dgst;i=y,a=Error(m(419)),a.stack="",a.digest=i,La({value:a,source:null,stack:null}),t=vc(l,t,e)}else if(Ol||ia(l,t,e,!1),i=(e&l.childLanes)!==0,Ol||i){if(i=rl,i!==null&&(a=Tf(i,e),a!==0&&a!==f.retryLane))throw f.retryLane=a,De(l,a),et(i,l,a),sc;kc(c)||xn(),t=vc(l,t,e)}else kc(c)?(t.flags|=192,t.child=l.child,t=null):(l=f.treeContext,vl=Tt(c.nextSibling),Gl=t,I=!0,ae=null,pt=!1,l!==null&&Ss(t,l),t=yc(t,a.children),t.flags|=4096);return t}return u?(oe(),c=a.fallback,u=t.mode,f=l.child,y=f.sibling,a=Yt(f,{mode:"hidden",children:a.children}),a.subtreeFlags=f.subtreeFlags&65011712,y!==null?c=Yt(y,c):(c=je(c,u,e,null),c.flags|=2),c.return=t,a.return=t,a.sibling=c,t.child=a,tu(null,a),a=t.child,c=l.child.memoizedState,c===null?c=mc(e):(u=c.cachePool,u!==null?(f=Nl._currentValue,u=u.parent!==f?{parent:f,pool:f}:u):u=As(),c={baseLanes:c.baseLanes|e,cachePool:u}),a.memoizedState=c,a.childLanes=rc(l,i,e),t.memoizedState=dc,tu(l.child,a)):(se(t),e=l.child,l=e.sibling,e=Yt(e,{mode:"visible",children:a.children}),e.return=t,e.sibling=null,l!==null&&(i=t.deletions,i===null?(t.deletions=[l],t.flags|=16):i.push(l)),t.child=e,t.memoizedState=null,e)}function yc(l,t){return t=dn({mode:"visible",children:t},l.mode),t.return=l,l.child=t}function dn(l,t){return l=ct(22,l,null,t),l.lanes=0,l}function vc(l,t,e){return Ye(t,l.child,null,e),l=yc(t,t.pendingProps.children),l.flags|=2,t.memoizedState=null,l}function Y0(l,t,e){l.lanes|=t;var a=l.alternate;a!==null&&(a.lanes|=t),Di(l.return,t,e)}function hc(l,t,e,a,u,n){var i=l.memoizedState;i===null?l.memoizedState={isBackwards:t,rendering:null,renderingStartTime:0,last:a,tail:e,tailMode:u,treeForkCount:n}:(i.isBackwards=t,i.rendering=null,i.renderingStartTime=0,i.last=a,i.tail=e,i.tailMode=u,i.treeForkCount=n)}function G0(l,t,e){var a=t.pendingProps,u=a.revealOrder,n=a.tail;a=a.children;var i=El.current,c=(i&2)!==0;if(c?(i=i&1|2,t.flags|=128):i&=1,_(El,i),Ql(l,t,a,e),a=I?Za:0,!c&&l!==null&&(l.flags&128)!==0)l:for(l=t.child;l!==null;){if(l.tag===13)l.memoizedState!==null&&Y0(l,e,t);else if(l.tag===19)Y0(l,e,t);else if(l.child!==null){l.child.return=l,l=l.child;continue}if(l===t)break l;for(;l.sibling===null;){if(l.return===null||l.return===t)break l;l=l.return}l.sibling.return=l.return,l=l.sibling}switch(u){case"forwards":for(e=t.child,u=null;e!==null;)l=e.alternate,l!==null&&Iu(l)===null&&(u=e),e=e.sibling;e=u,e===null?(u=t.child,t.child=null):(u=e.sibling,e.sibling=null),hc(t,!1,u,e,n,a);break;case"backwards":case"unstable_legacy-backwards":for(e=null,u=t.child,t.child=null;u!==null;){if(l=u.alternate,l!==null&&Iu(l)===null){t.child=u;break}l=u.sibling,u.sibling=e,e=u,u=l}hc(t,!0,e,null,n,a);break;case"together":hc(t,!1,null,null,void 0,a);break;default:t.memoizedState=null}return t.child}function Vt(l,t,e){if(l!==null&&(t.dependencies=l.dependencies),re|=t.lanes,(e&t.childLanes)===0)if(l!==null){if(ia(l,t,e,!1),(e&t.childLanes)===0)return null}else return null;if(l!==null&&t.child!==l.child)throw Error(m(153));if(t.child!==null){for(l=t.child,e=Yt(l,l.pendingProps),t.child=e,e.return=t;l.sibling!==null;)l=l.sibling,e=e.sibling=Yt(l,l.pendingProps),e.return=t;e.sibling=null}return t.child}function gc(l,t){return(l.lanes&t)!==0?!0:(l=l.dependencies,!!(l!==null&&Vu(l)))}function ur(l,t,e){switch(t.tag){case 3:kl(t,t.stateNode.containerInfo),ne(t,Nl,l.memoizedState.cache),Ue();break;case 27:case 5:Na(t);break;case 4:kl(t,t.stateNode.containerInfo);break;case 10:ne(t,t.type,t.memoizedProps.value);break;case 31:if(t.memoizedState!==null)return t.flags|=128,Zi(t),null;break;case 13:var a=t.memoizedState;if(a!==null)return a.dehydrated!==null?(se(t),t.flags|=128,null):(e&t.child.childLanes)!==0?B0(l,t,e):(se(t),l=Vt(l,t,e),l!==null?l.sibling:null);se(t);break;case 19:var u=(l.flags&128)!==0;if(a=(e&t.childLanes)!==0,a||(ia(l,t,e,!1),a=(e&t.childLanes)!==0),u){if(a)return G0(l,t,e);t.flags|=128}if(u=t.memoizedState,u!==null&&(u.rendering=null,u.tail=null,u.lastEffect=null),_(El,El.current),a)break;return null;case 22:return t.lanes=0,j0(l,t,e,t.pendingProps);case 24:ne(t,Nl,l.memoizedState.cache)}return Vt(l,t,e)}function X0(l,t,e){if(l!==null)if(l.memoizedProps!==t.pendingProps)Ol=!0;else{if(!gc(l,e)&&(t.flags&128)===0)return Ol=!1,ur(l,t,e);Ol=(l.flags&131072)!==0}else Ol=!1,I&&(t.flags&1048576)!==0&&bs(t,Za,t.index);switch(t.lanes=0,t.tag){case 16:l:{var a=t.pendingProps;if(l=qe(t.elementType),t.type=l,typeof l=="function")zi(l)?(a=Xe(l,a),t.tag=1,t=R0(null,t,l,a,e)):(t.tag=0,t=oc(null,t,l,a,e));else{if(l!=null){var u=l.$$typeof;if(u===Jl){t.tag=11,t=M0(null,t,l,a,e);break l}else if(u===K){t.tag=14,t=O0(null,t,l,a,e);break l}}throw t=Ct(l)||l,Error(m(306,t,""))}}return t;case 0:return oc(l,t,t.type,t.pendingProps,e);case 1:return a=t.type,u=Xe(a,t.pendingProps),R0(l,t,a,u,e);case 3:l:{if(kl(t,t.stateNode.containerInfo),l===null)throw Error(m(387));a=t.pendingProps;var n=t.memoizedState;u=n.element,Bi(l,t),$a(t,a,null,e);var i=t.memoizedState;if(a=i.cache,ne(t,Nl,a),a!==n.cache&&ji(t,[Nl],e,!0),Wa(),a=i.element,n.isDehydrated)if(n={element:a,isDehydrated:!1,cache:i.cache},t.updateQueue.baseState=n,t.memoizedState=n,t.flags&256){t=q0(l,t,a,e);break l}else if(a!==u){u=bt(Error(m(424)),t),La(u),t=q0(l,t,a,e);break l}else{switch(l=t.stateNode.containerInfo,l.nodeType){case 9:l=l.body;break;default:l=l.nodeName==="HTML"?l.ownerDocument.body:l}for(vl=Tt(l.firstChild),Gl=t,I=!0,ae=null,pt=!0,e=js(t,null,a,e),t.child=e;e;)e.flags=e.flags&-3|4096,e=e.sibling}else{if(Ue(),a===u){t=Vt(l,t,e);break l}Ql(l,t,a,e)}t=t.child}return t;case 26:return on(l,t),l===null?(e=Io(t.type,null,t.pendingProps,null))?t.memoizedState=e:I||(e=t.type,l=t.pendingProps,a=Nn(J.current).createElement(e),a[Yl]=t,a[$l]=l,Zl(a,e,l),Rl(a),t.stateNode=a):t.memoizedState=Io(t.type,l.memoizedProps,t.pendingProps,l.memoizedState),null;case 27:return Na(t),l===null&&I&&(a=t.stateNode=Wo(t.type,t.pendingProps,J.current),Gl=t,pt=!0,u=vl,be(t.type)?($c=u,vl=Tt(a.firstChild)):vl=u),Ql(l,t,t.pendingProps.children,e),on(l,t),l===null&&(t.flags|=4194304),t.child;case 5:return l===null&&I&&((u=a=vl)&&(a=Cr(a,t.type,t.pendingProps,pt),a!==null?(t.stateNode=a,Gl=t,vl=Tt(a.firstChild),pt=!1,u=!0):u=!1),u||ue(t)),Na(t),u=t.type,n=t.pendingProps,i=l!==null?l.memoizedProps:null,a=n.children,Kc(u,n)?a=null:i!==null&&Kc(u,i)&&(t.flags|=32),t.memoizedState!==null&&(u=Vi(l,t,Wm,null,null,e),hu._currentValue=u),on(l,t),Ql(l,t,a,e),t.child;case 6:return l===null&&I&&((l=e=vl)&&(e=Rr(e,t.pendingProps,pt),e!==null?(t.stateNode=e,Gl=t,vl=null,l=!0):l=!1),l||ue(t)),null;case 13:return B0(l,t,e);case 4:return kl(t,t.stateNode.containerInfo),a=t.pendingProps,l===null?t.child=Ye(t,null,a,e):Ql(l,t,a,e),t.child;case 11:return M0(l,t,t.type,t.pendingProps,e);case 7:return Ql(l,t,t.pendingProps,e),t.child;case 8:return Ql(l,t,t.pendingProps.children,e),t.child;case 12:return Ql(l,t,t.pendingProps.children,e),t.child;case 10:return a=t.pendingProps,ne(t,t.type,a.value),Ql(l,t,a.children,e),t.child;case 9:return u=t.type._context,a=t.pendingProps.children,Ce(t),u=Xl(u),a=a(u),t.flags|=1,Ql(l,t,a,e),t.child;case 14:return O0(l,t,t.type,t.pendingProps,e);case 15:return D0(l,t,t.type,t.pendingProps,e);case 19:return G0(l,t,e);case 31:return ar(l,t,e);case 22:return j0(l,t,e,t.pendingProps);case 24:return Ce(t),a=Xl(Nl),l===null?(u=Ci(),u===null&&(u=rl,n=Ui(),u.pooledCache=n,n.refCount++,n!==null&&(u.pooledCacheLanes|=e),u=n),t.memoizedState={parent:a,cache:u},qi(t),ne(t,Nl,u)):((l.lanes&e)!==0&&(Bi(l,t),$a(t,null,null,e),Wa()),u=l.memoizedState,n=t.memoizedState,u.parent!==a?(u={parent:a,cache:a},t.memoizedState=u,t.lanes===0&&(t.memoizedState=t.updateQueue.baseState=u),ne(t,Nl,a)):(a=n.cache,ne(t,Nl,a),a!==u.cache&&ji(t,[Nl],e,!0))),Ql(l,t,t.pendingProps.children,e),t.child;case 29:throw t.pendingProps}throw Error(m(156,t.tag))}function Kt(l){l.flags|=4}function bc(l,t,e,a,u){if((t=(l.mode&32)!==0)&&(t=!1),t){if(l.flags|=16777216,(u&335544128)===u)if(l.stateNode.complete)l.flags|=8192;else if(yo())l.flags|=8192;else throw Be=ku,Ri}else l.flags&=-16777217}function Q0(l,t){if(t.type!=="stylesheet"||(t.state.loading&4)!==0)l.flags&=-16777217;else if(l.flags|=16777216,!ad(t))if(yo())l.flags|=8192;else throw Be=ku,Ri}function mn(l,t){t!==null&&(l.flags|=4),l.flags&16384&&(t=l.tag!==22?xf():536870912,l.lanes|=t,ba|=t)}function eu(l,t){if(!I)switch(l.tailMode){case"hidden":t=l.tail;for(var e=null;t!==null;)t.alternate!==null&&(e=t),t=t.sibling;e===null?l.tail=null:e.sibling=null;break;case"collapsed":e=l.tail;for(var a=null;e!==null;)e.alternate!==null&&(a=e),e=e.sibling;a===null?t||l.tail===null?l.tail=null:l.tail.sibling=null:a.sibling=null}}function hl(l){var t=l.alternate!==null&&l.alternate.child===l.child,e=0,a=0;if(t)for(var u=l.child;u!==null;)e|=u.lanes|u.childLanes,a|=u.subtreeFlags&65011712,a|=u.flags&65011712,u.return=l,u=u.sibling;else for(u=l.child;u!==null;)e|=u.lanes|u.childLanes,a|=u.subtreeFlags,a|=u.flags,u.return=l,u=u.sibling;return l.subtreeFlags|=a,l.childLanes=e,t}function nr(l,t,e){var a=t.pendingProps;switch(_i(t),t.tag){case 16:case 15:case 0:case 11:case 7:case 8:case 12:case 9:case 14:return hl(t),null;case 1:return hl(t),null;case 3:return e=t.stateNode,a=null,l!==null&&(a=l.memoizedState.cache),t.memoizedState.cache!==a&&(t.flags|=2048),Qt(Nl),Tl(),e.pendingContext&&(e.context=e.pendingContext,e.pendingContext=null),(l===null||l.child===null)&&(na(t)?Kt(t):l===null||l.memoizedState.isDehydrated&&(t.flags&256)===0||(t.flags|=1024,Mi())),hl(t),null;case 26:var u=t.type,n=t.memoizedState;return l===null?(Kt(t),n!==null?(hl(t),Q0(t,n)):(hl(t),bc(t,u,null,a,e))):n?n!==l.memoizedState?(Kt(t),hl(t),Q0(t,n)):(hl(t),t.flags&=-16777217):(l=l.memoizedProps,l!==a&&Kt(t),hl(t),bc(t,u,l,a,e)),null;case 27:if(zu(t),e=J.current,u=t.type,l!==null&&t.stateNode!=null)l.memoizedProps!==a&&Kt(t);else{if(!a){if(t.stateNode===null)throw Error(m(166));return hl(t),null}l=O.current,na(t)?xs(t):(l=Wo(u,a,e),t.stateNode=l,Kt(t))}return hl(t),null;case 5:if(zu(t),u=t.type,l!==null&&t.stateNode!=null)l.memoizedProps!==a&&Kt(t);else{if(!a){if(t.stateNode===null)throw Error(m(166));return hl(t),null}if(n=O.current,na(t))xs(t);else{var i=Nn(J.current);switch(n){case 1:n=i.createElementNS("http://www.w3.org/2000/svg",u);break;case 2:n=i.createElementNS("http://www.w3.org/1998/Math/MathML",u);break;default:switch(u){case"svg":n=i.createElementNS("http://www.w3.org/2000/svg",u);break;case"math":n=i.createElementNS("http://www.w3.org/1998/Math/MathML",u);break;case"script":n=i.createElement("div"),n.innerHTML="<script><\/script>",n=n.removeChild(n.firstChild);break;case"select":n=typeof a.is=="string"?i.createElement("select",{is:a.is}):i.createElement("select"),a.multiple?n.multiple=!0:a.size&&(n.size=a.size);break;default:n=typeof a.is=="string"?i.createElement(u,{is:a.is}):i.createElement(u)}}n[Yl]=t,n[$l]=a;l:for(i=t.child;i!==null;){if(i.tag===5||i.tag===6)n.appendChild(i.stateNode);else if(i.tag!==4&&i.tag!==27&&i.child!==null){i.child.return=i,i=i.child;continue}if(i===t)break l;for(;i.sibling===null;){if(i.return===null||i.return===t)break l;i=i.return}i.sibling.return=i.return,i=i.sibling}t.stateNode=n;l:switch(Zl(n,u,a),u){case"button":case"input":case"select":case"textarea":a=!!a.autoFocus;break l;case"img":a=!0;break l;default:a=!1}a&&Kt(t)}}return hl(t),bc(t,t.type,l===null?null:l.memoizedProps,t.pendingProps,e),null;case 6:if(l&&t.stateNode!=null)l.memoizedProps!==a&&Kt(t);else{if(typeof a!="string"&&t.stateNode===null)throw Error(m(166));if(l=J.current,na(t)){if(l=t.stateNode,e=t.memoizedProps,a=null,u=Gl,u!==null)switch(u.tag){case 27:case 5:a=u.memoizedProps}l[Yl]=t,l=!!(l.nodeValue===e||a!==null&&a.suppressHydrationWarning===!0||Yo(l.nodeValue,e)),l||ue(t,!0)}else l=Nn(l).createTextNode(a),l[Yl]=t,t.stateNode=l}return hl(t),null;case 31:if(e=t.memoizedState,l===null||l.memoizedState!==null){if(a=na(t),e!==null){if(l===null){if(!a)throw Error(m(318));if(l=t.memoizedState,l=l!==null?l.dehydrated:null,!l)throw Error(m(557));l[Yl]=t}else Ue(),(t.flags&128)===0&&(t.memoizedState=null),t.flags|=4;hl(t),l=!1}else e=Mi(),l!==null&&l.memoizedState!==null&&(l.memoizedState.hydrationErrors=e),l=!0;if(!l)return t.flags&256?(st(t),t):(st(t),null);if((t.flags&128)!==0)throw Error(m(558))}return hl(t),null;case 13:if(a=t.memoizedState,l===null||l.memoizedState!==null&&l.memoizedState.dehydrated!==null){if(u=na(t),a!==null&&a.dehydrated!==null){if(l===null){if(!u)throw Error(m(318));if(u=t.memoizedState,u=u!==null?u.dehydrated:null,!u)throw Error(m(317));u[Yl]=t}else Ue(),(t.flags&128)===0&&(t.memoizedState=null),t.flags|=4;hl(t),u=!1}else u=Mi(),l!==null&&l.memoizedState!==null&&(l.memoizedState.hydrationErrors=u),u=!0;if(!u)return t.flags&256?(st(t),t):(st(t),null)}return st(t),(t.flags&128)!==0?(t.lanes=e,t):(e=a!==null,l=l!==null&&l.memoizedState!==null,e&&(a=t.child,u=null,a.alternate!==null&&a.alternate.memoizedState!==null&&a.alternate.memoizedState.cachePool!==null&&(u=a.alternate.memoizedState.cachePool.pool),n=null,a.memoizedState!==null&&a.memoizedState.cachePool!==null&&(n=a.memoizedState.cachePool.pool),n!==u&&(a.flags|=2048)),e!==l&&e&&(t.child.flags|=8192),mn(t,t.updateQueue),hl(t),null);case 4:return Tl(),l===null&&Xc(t.stateNode.containerInfo),hl(t),null;case 10:return Qt(t.type),hl(t),null;case 19:if(T(El),a=t.memoizedState,a===null)return hl(t),null;if(u=(t.flags&128)!==0,n=a.rendering,n===null)if(u)eu(a,!1);else{if(zl!==0||l!==null&&(l.flags&128)!==0)for(l=t.child;l!==null;){if(n=Iu(l),n!==null){for(t.flags|=128,eu(a,!1),l=n.updateQueue,t.updateQueue=l,mn(t,l),t.subtreeFlags=0,l=e,e=t.child;e!==null;)vs(e,l),e=e.sibling;return _(El,El.current&1|2),I&&Gt(t,a.treeForkCount),t.child}l=l.sibling}a.tail!==null&&at()>gn&&(t.flags|=128,u=!0,eu(a,!1),t.lanes=4194304)}else{if(!u)if(l=Iu(n),l!==null){if(t.flags|=128,u=!0,l=l.updateQueue,t.updateQueue=l,mn(t,l),eu(a,!0),a.tail===null&&a.tailMode==="hidden"&&!n.alternate&&!I)return hl(t),null}else 2*at()-a.renderingStartTime>gn&&e!==536870912&&(t.flags|=128,u=!0,eu(a,!1),t.lanes=4194304);a.isBackwards?(n.sibling=t.child,t.child=n):(l=a.last,l!==null?l.sibling=n:t.child=n,a.last=n)}return a.tail!==null?(l=a.tail,a.rendering=l,a.tail=l.sibling,a.renderingStartTime=at(),l.sibling=null,e=El.current,_(El,u?e&1|2:e&1),I&&Gt(t,a.treeForkCount),l):(hl(t),null);case 22:case 23:return st(t),Qi(),a=t.memoizedState!==null,l!==null?l.memoizedState!==null!==a&&(t.flags|=8192):a&&(t.flags|=8192),a?(e&536870912)!==0&&(t.flags&128)===0&&(hl(t),t.subtreeFlags&6&&(t.flags|=8192)):hl(t),e=t.updateQueue,e!==null&&mn(t,e.retryQueue),e=null,l!==null&&l.memoizedState!==null&&l.memoizedState.cachePool!==null&&(e=l.memoizedState.cachePool.pool),a=null,t.memoizedState!==null&&t.memoizedState.cachePool!==null&&(a=t.memoizedState.cachePool.pool),a!==e&&(t.flags|=2048),l!==null&&T(Re),null;case 24:return e=null,l!==null&&(e=l.memoizedState.cache),t.memoizedState.cache!==e&&(t.flags|=2048),Qt(Nl),hl(t),null;case 25:return null;case 30:return null}throw Error(m(156,t.tag))}function ir(l,t){switch(_i(t),t.tag){case 1:return l=t.flags,l&65536?(t.flags=l&-65537|128,t):null;case 3:return Qt(Nl),Tl(),l=t.flags,(l&65536)!==0&&(l&128)===0?(t.flags=l&-65537|128,t):null;case 26:case 27:case 5:return zu(t),null;case 31:if(t.memoizedState!==null){if(st(t),t.alternate===null)throw Error(m(340));Ue()}return l=t.flags,l&65536?(t.flags=l&-65537|128,t):null;case 13:if(st(t),l=t.memoizedState,l!==null&&l.dehydrated!==null){if(t.alternate===null)throw Error(m(340));Ue()}return l=t.flags,l&65536?(t.flags=l&-65537|128,t):null;case 19:return T(El),null;case 4:return Tl(),null;case 10:return Qt(t.type),null;case 22:case 23:return st(t),Qi(),l!==null&&T(Re),l=t.flags,l&65536?(t.flags=l&-65537|128,t):null;case 24:return Qt(Nl),null;case 25:return null;default:return null}}function Z0(l,t){switch(_i(t),t.tag){case 3:Qt(Nl),Tl();break;case 26:case 27:case 5:zu(t);break;case 4:Tl();break;case 31:t.memoizedState!==null&&st(t);break;case 13:st(t);break;case 19:T(El);break;case 10:Qt(t.type);break;case 22:case 23:st(t),Qi(),l!==null&&T(Re);break;case 24:Qt(Nl)}}function au(l,t){try{var e=t.updateQueue,a=e!==null?e.lastEffect:null;if(a!==null){var u=a.next;e=u;do{if((e.tag&l)===l){a=void 0;var n=e.create,i=e.inst;a=n(),i.destroy=a}e=e.next}while(e!==u)}}catch(c){nl(t,t.return,c)}}function de(l,t,e){try{var a=t.updateQueue,u=a!==null?a.lastEffect:null;if(u!==null){var n=u.next;a=n;do{if((a.tag&l)===l){var i=a.inst,c=i.destroy;if(c!==void 0){i.destroy=void 0,u=t;var f=e,y=c;try{y()}catch(b){nl(u,f,b)}}}a=a.next}while(a!==n)}}catch(b){nl(t,t.return,b)}}function L0(l){var t=l.updateQueue;if(t!==null){var e=l.stateNode;try{Hs(t,e)}catch(a){nl(l,l.return,a)}}}function V0(l,t,e){e.props=Xe(l.type,l.memoizedProps),e.state=l.memoizedState;try{e.componentWillUnmount()}catch(a){nl(l,t,a)}}function uu(l,t){try{var e=l.ref;if(e!==null){switch(l.tag){case 26:case 27:case 5:var a=l.stateNode;break;case 30:a=l.stateNode;break;default:a=l.stateNode}typeof e=="function"?l.refCleanup=e(a):e.current=a}}catch(u){nl(l,t,u)}}function Ut(l,t){var e=l.ref,a=l.refCleanup;if(e!==null)if(typeof a=="function")try{a()}catch(u){nl(l,t,u)}finally{l.refCleanup=null,l=l.alternate,l!=null&&(l.refCleanup=null)}else if(typeof e=="function")try{e(null)}catch(u){nl(l,t,u)}else e.current=null}function K0(l){var t=l.type,e=l.memoizedProps,a=l.stateNode;try{l:switch(t){case"button":case"input":case"select":case"textarea":e.autoFocus&&a.focus();break l;case"img":e.src?a.src=e.src:e.srcSet&&(a.srcset=e.srcSet)}}catch(u){nl(l,l.return,u)}}function Sc(l,t,e){try{var a=l.stateNode;Mr(a,l.type,e,t),a[$l]=t}catch(u){nl(l,l.return,u)}}function J0(l){return l.tag===5||l.tag===3||l.tag===26||l.tag===27&&be(l.type)||l.tag===4}function xc(l){l:for(;;){for(;l.sibling===null;){if(l.return===null||J0(l.return))return null;l=l.return}for(l.sibling.return=l.return,l=l.sibling;l.tag!==5&&l.tag!==6&&l.tag!==18;){if(l.tag===27&&be(l.type)||l.flags&2||l.child===null||l.tag===4)continue l;l.child.return=l,l=l.child}if(!(l.flags&2))return l.stateNode}}function pc(l,t,e){var a=l.tag;if(a===5||a===6)l=l.stateNode,t?(e.nodeType===9?e.body:e.nodeName==="HTML"?e.ownerDocument.body:e).insertBefore(l,t):(t=e.nodeType===9?e.body:e.nodeName==="HTML"?e.ownerDocument.body:e,t.appendChild(l),e=e._reactRootContainer,e!=null||t.onclick!==null||(t.onclick=qt));else if(a!==4&&(a===27&&be(l.type)&&(e=l.stateNode,t=null),l=l.child,l!==null))for(pc(l,t,e),l=l.sibling;l!==null;)pc(l,t,e),l=l.sibling}function rn(l,t,e){var a=l.tag;if(a===5||a===6)l=l.stateNode,t?e.insertBefore(l,t):e.appendChild(l);else if(a!==4&&(a===27&&be(l.type)&&(e=l.stateNode),l=l.child,l!==null))for(rn(l,t,e),l=l.sibling;l!==null;)rn(l,t,e),l=l.sibling}function w0(l){var t=l.stateNode,e=l.memoizedProps;try{for(var a=l.type,u=t.attributes;u.length;)t.removeAttributeNode(u[0]);Zl(t,a,e),t[Yl]=l,t[$l]=e}catch(n){nl(l,l.return,n)}}var Jt=!1,Dl=!1,zc=!1,k0=typeof WeakSet=="function"?WeakSet:Set,ql=null;function cr(l,t){if(l=l.containerInfo,Lc=Cn,l=is(l),vi(l)){if("selectionStart"in l)var e={start:l.selectionStart,end:l.selectionEnd};else l:{e=(e=l.ownerDocument)&&e.defaultView||window;var a=e.getSelection&&e.getSelection();if(a&&a.rangeCount!==0){e=a.anchorNode;var u=a.anchorOffset,n=a.focusNode;a=a.focusOffset;try{e.nodeType,n.nodeType}catch{e=null;break l}var i=0,c=-1,f=-1,y=0,b=0,p=l,h=null;t:for(;;){for(var g;p!==e||u!==0&&p.nodeType!==3||(c=i+u),p!==n||a!==0&&p.nodeType!==3||(f=i+a),p.nodeType===3&&(i+=p.nodeValue.length),(g=p.firstChild)!==null;)h=p,p=g;for(;;){if(p===l)break t;if(h===e&&++y===u&&(c=i),h===n&&++b===a&&(f=i),(g=p.nextSibling)!==null)break;p=h,h=p.parentNode}p=g}e=c===-1||f===-1?null:{start:c,end:f}}else e=null}e=e||{start:0,end:0}}else e=null;for(Vc={focusedElem:l,selectionRange:e},Cn=!1,ql=t;ql!==null;)if(t=ql,l=t.child,(t.subtreeFlags&1028)!==0&&l!==null)l.return=t,ql=l;else for(;ql!==null;){switch(t=ql,n=t.alternate,l=t.flags,t.tag){case 0:if((l&4)!==0&&(l=t.updateQueue,l=l!==null?l.events:null,l!==null))for(e=0;e<l.length;e++)u=l[e],u.ref.impl=u.nextImpl;break;case 11:case 15:break;case 1:if((l&1024)!==0&&n!==null){l=void 0,e=t,u=n.memoizedProps,n=n.memoizedState,a=e.stateNode;try{var M=Xe(e.type,u);l=a.getSnapshotBeforeUpdate(M,n),a.__reactInternalSnapshotBeforeUpdate=l}catch(R){nl(e,e.return,R)}}break;case 3:if((l&1024)!==0){if(l=t.stateNode.containerInfo,e=l.nodeType,e===9)wc(l);else if(e===1)switch(l.nodeName){case"HEAD":case"HTML":case"BODY":wc(l);break;default:l.textContent=""}}break;case 5:case 26:case 27:case 6:case 4:case 17:break;default:if((l&1024)!==0)throw Error(m(163))}if(l=t.sibling,l!==null){l.return=t.return,ql=l;break}ql=t.return}}function W0(l,t,e){var a=e.flags;switch(e.tag){case 0:case 11:case 15:kt(l,e),a&4&&au(5,e);break;case 1:if(kt(l,e),a&4)if(l=e.stateNode,t===null)try{l.componentDidMount()}catch(i){nl(e,e.return,i)}else{var u=Xe(e.type,t.memoizedProps);t=t.memoizedState;try{l.componentDidUpdate(u,t,l.__reactInternalSnapshotBeforeUpdate)}catch(i){nl(e,e.return,i)}}a&64&&L0(e),a&512&&uu(e,e.return);break;case 3:if(kt(l,e),a&64&&(l=e.updateQueue,l!==null)){if(t=null,e.child!==null)switch(e.child.tag){case 27:case 5:t=e.child.stateNode;break;case 1:t=e.child.stateNode}try{Hs(l,t)}catch(i){nl(e,e.return,i)}}break;case 27:t===null&&a&4&&w0(e);case 26:case 5:kt(l,e),t===null&&a&4&&K0(e),a&512&&uu(e,e.return);break;case 12:kt(l,e);break;case 31:kt(l,e),a&4&&I0(l,e);break;case 13:kt(l,e),a&4&&P0(l,e),a&64&&(l=e.memoizedState,l!==null&&(l=l.dehydrated,l!==null&&(e=hr.bind(null,e),qr(l,e))));break;case 22:if(a=e.memoizedState!==null||Jt,!a){t=t!==null&&t.memoizedState!==null||Dl,u=Jt;var n=Dl;Jt=a,(Dl=t)&&!n?Wt(l,e,(e.subtreeFlags&8772)!==0):kt(l,e),Jt=u,Dl=n}break;case 30:break;default:kt(l,e)}}function $0(l){var t=l.alternate;t!==null&&(l.alternate=null,$0(t)),l.child=null,l.deletions=null,l.sibling=null,l.tag===5&&(t=l.stateNode,t!==null&&In(t)),l.stateNode=null,l.return=null,l.dependencies=null,l.memoizedProps=null,l.memoizedState=null,l.pendingProps=null,l.stateNode=null,l.updateQueue=null}var bl=null,Il=!1;function wt(l,t,e){for(e=e.child;e!==null;)F0(l,t,e),e=e.sibling}function F0(l,t,e){if(ut&&typeof ut.onCommitFiberUnmount=="function")try{ut.onCommitFiberUnmount(Ma,e)}catch{}switch(e.tag){case 26:Dl||Ut(e,t),wt(l,t,e),e.memoizedState?e.memoizedState.count--:e.stateNode&&(e=e.stateNode,e.parentNode.removeChild(e));break;case 27:Dl||Ut(e,t);var a=bl,u=Il;be(e.type)&&(bl=e.stateNode,Il=!1),wt(l,t,e),ru(e.stateNode),bl=a,Il=u;break;case 5:Dl||Ut(e,t);case 6:if(a=bl,u=Il,bl=null,wt(l,t,e),bl=a,Il=u,bl!==null)if(Il)try{(bl.nodeType===9?bl.body:bl.nodeName==="HTML"?bl.ownerDocument.body:bl).removeChild(e.stateNode)}catch(n){nl(e,t,n)}else try{bl.removeChild(e.stateNode)}catch(n){nl(e,t,n)}break;case 18:bl!==null&&(Il?(l=bl,Vo(l.nodeType===9?l.body:l.nodeName==="HTML"?l.ownerDocument.body:l,e.stateNode),_a(l)):Vo(bl,e.stateNode));break;case 4:a=bl,u=Il,bl=e.stateNode.containerInfo,Il=!0,wt(l,t,e),bl=a,Il=u;break;case 0:case 11:case 14:case 15:de(2,e,t),Dl||de(4,e,t),wt(l,t,e);break;case 1:Dl||(Ut(e,t),a=e.stateNode,typeof a.componentWillUnmount=="function"&&V0(e,t,a)),wt(l,t,e);break;case 21:wt(l,t,e);break;case 22:Dl=(a=Dl)||e.memoizedState!==null,wt(l,t,e),Dl=a;break;default:wt(l,t,e)}}function I0(l,t){if(t.memoizedState===null&&(l=t.alternate,l!==null&&(l=l.memoizedState,l!==null))){l=l.dehydrated;try{_a(l)}catch(e){nl(t,t.return,e)}}}function P0(l,t){if(t.memoizedState===null&&(l=t.alternate,l!==null&&(l=l.memoizedState,l!==null&&(l=l.dehydrated,l!==null))))try{_a(l)}catch(e){nl(t,t.return,e)}}function fr(l){switch(l.tag){case 31:case 13:case 19:var t=l.stateNode;return t===null&&(t=l.stateNode=new k0),t;case 22:return l=l.stateNode,t=l._retryCache,t===null&&(t=l._retryCache=new k0),t;default:throw Error(m(435,l.tag))}}function yn(l,t){var e=fr(l);t.forEach(function(a){if(!e.has(a)){e.add(a);var u=gr.bind(null,l,a);a.then(u,u)}})}function Pl(l,t){var e=t.deletions;if(e!==null)for(var a=0;a<e.length;a++){var u=e[a],n=l,i=t,c=i;l:for(;c!==null;){switch(c.tag){case 27:if(be(c.type)){bl=c.stateNode,Il=!1;break l}break;case 5:bl=c.stateNode,Il=!1;break l;case 3:case 4:bl=c.stateNode.containerInfo,Il=!0;break l}c=c.return}if(bl===null)throw Error(m(160));F0(n,i,u),bl=null,Il=!1,n=u.alternate,n!==null&&(n.return=null),u.return=null}if(t.subtreeFlags&13886)for(t=t.child;t!==null;)lo(t,l),t=t.sibling}var Mt=null;function lo(l,t){var e=l.alternate,a=l.flags;switch(l.tag){case 0:case 11:case 14:case 15:Pl(t,l),lt(l),a&4&&(de(3,l,l.return),au(3,l),de(5,l,l.return));break;case 1:Pl(t,l),lt(l),a&512&&(Dl||e===null||Ut(e,e.return)),a&64&&Jt&&(l=l.updateQueue,l!==null&&(a=l.callbacks,a!==null&&(e=l.shared.hiddenCallbacks,l.shared.hiddenCallbacks=e===null?a:e.concat(a))));break;case 26:var u=Mt;if(Pl(t,l),lt(l),a&512&&(Dl||e===null||Ut(e,e.return)),a&4){var n=e!==null?e.memoizedState:null;if(a=l.memoizedState,e===null)if(a===null)if(l.stateNode===null){l:{a=l.type,e=l.memoizedProps,u=u.ownerDocument||u;t:switch(a){case"title":n=u.getElementsByTagName("title")[0],(!n||n[ja]||n[Yl]||n.namespaceURI==="http://www.w3.org/2000/svg"||n.hasAttribute("itemprop"))&&(n=u.createElement(a),u.head.insertBefore(n,u.querySelector("head > title"))),Zl(n,a,e),n[Yl]=l,Rl(n),a=n;break l;case"link":var i=td("link","href",u).get(a+(e.href||""));if(i){for(var c=0;c<i.length;c++)if(n=i[c],n.getAttribute("href")===(e.href==null||e.href===""?null:e.href)&&n.getAttribute("rel")===(e.rel==null?null:e.rel)&&n.getAttribute("title")===(e.title==null?null:e.title)&&n.getAttribute("crossorigin")===(e.crossOrigin==null?null:e.crossOrigin)){i.splice(c,1);break t}}n=u.createElement(a),Zl(n,a,e),u.head.appendChild(n);break;case"meta":if(i=td("meta","content",u).get(a+(e.content||""))){for(c=0;c<i.length;c++)if(n=i[c],n.getAttribute("content")===(e.content==null?null:""+e.content)&&n.getAttribute("name")===(e.name==null?null:e.name)&&n.getAttribute("property")===(e.property==null?null:e.property)&&n.getAttribute("http-equiv")===(e.httpEquiv==null?null:e.httpEquiv)&&n.getAttribute("charset")===(e.charSet==null?null:e.charSet)){i.splice(c,1);break t}}n=u.createElement(a),Zl(n,a,e),u.head.appendChild(n);break;default:throw Error(m(468,a))}n[Yl]=l,Rl(n),a=n}l.stateNode=a}else ed(u,l.type,l.stateNode);else l.stateNode=ld(u,a,l.memoizedProps);else n!==a?(n===null?e.stateNode!==null&&(e=e.stateNode,e.parentNode.removeChild(e)):n.count--,a===null?ed(u,l.type,l.stateNode):ld(u,a,l.memoizedProps)):a===null&&l.stateNode!==null&&Sc(l,l.memoizedProps,e.memoizedProps)}break;case 27:Pl(t,l),lt(l),a&512&&(Dl||e===null||Ut(e,e.return)),e!==null&&a&4&&Sc(l,l.memoizedProps,e.memoizedProps);break;case 5:if(Pl(t,l),lt(l),a&512&&(Dl||e===null||Ut(e,e.return)),l.flags&32){u=l.stateNode;try{We(u,"")}catch(M){nl(l,l.return,M)}}a&4&&l.stateNode!=null&&(u=l.memoizedProps,Sc(l,u,e!==null?e.memoizedProps:u)),a&1024&&(zc=!0);break;case 6:if(Pl(t,l),lt(l),a&4){if(l.stateNode===null)throw Error(m(162));a=l.memoizedProps,e=l.stateNode;try{e.nodeValue=a}catch(M){nl(l,l.return,M)}}break;case 3:if(Dn=null,u=Mt,Mt=Mn(t.containerInfo),Pl(t,l),Mt=u,lt(l),a&4&&e!==null&&e.memoizedState.isDehydrated)try{_a(t.containerInfo)}catch(M){nl(l,l.return,M)}zc&&(zc=!1,to(l));break;case 4:a=Mt,Mt=Mn(l.stateNode.containerInfo),Pl(t,l),lt(l),Mt=a;break;case 12:Pl(t,l),lt(l);break;case 31:Pl(t,l),lt(l),a&4&&(a=l.updateQueue,a!==null&&(l.updateQueue=null,yn(l,a)));break;case 13:Pl(t,l),lt(l),l.child.flags&8192&&l.memoizedState!==null!=(e!==null&&e.memoizedState!==null)&&(hn=at()),a&4&&(a=l.updateQueue,a!==null&&(l.updateQueue=null,yn(l,a)));break;case 22:u=l.memoizedState!==null;var f=e!==null&&e.memoizedState!==null,y=Jt,b=Dl;if(Jt=y||u,Dl=b||f,Pl(t,l),Dl=b,Jt=y,lt(l),a&8192)l:for(t=l.stateNode,t._visibility=u?t._visibility&-2:t._visibility|1,u&&(e===null||f||Jt||Dl||Qe(l)),e=null,t=l;;){if(t.tag===5||t.tag===26){if(e===null){f=e=t;try{if(n=f.stateNode,u)i=n.style,typeof i.setProperty=="function"?i.setProperty("display","none","important"):i.display="none";else{c=f.stateNode;var p=f.memoizedProps.style,h=p!=null&&p.hasOwnProperty("display")?p.display:null;c.style.display=h==null||typeof h=="boolean"?"":(""+h).trim()}}catch(M){nl(f,f.return,M)}}}else if(t.tag===6){if(e===null){f=t;try{f.stateNode.nodeValue=u?"":f.memoizedProps}catch(M){nl(f,f.return,M)}}}else if(t.tag===18){if(e===null){f=t;try{var g=f.stateNode;u?Ko(g,!0):Ko(f.stateNode,!1)}catch(M){nl(f,f.return,M)}}}else if((t.tag!==22&&t.tag!==23||t.memoizedState===null||t===l)&&t.child!==null){t.child.return=t,t=t.child;continue}if(t===l)break l;for(;t.sibling===null;){if(t.return===null||t.return===l)break l;e===t&&(e=null),t=t.return}e===t&&(e=null),t.sibling.return=t.return,t=t.sibling}a&4&&(a=l.updateQueue,a!==null&&(e=a.retryQueue,e!==null&&(a.retryQueue=null,yn(l,e))));break;case 19:Pl(t,l),lt(l),a&4&&(a=l.updateQueue,a!==null&&(l.updateQueue=null,yn(l,a)));break;case 30:break;case 21:break;default:Pl(t,l),lt(l)}}function lt(l){var t=l.flags;if(t&2){try{for(var e,a=l.return;a!==null;){if(J0(a)){e=a;break}a=a.return}if(e==null)throw Error(m(160));switch(e.tag){case 27:var u=e.stateNode,n=xc(l);rn(l,n,u);break;case 5:var i=e.stateNode;e.flags&32&&(We(i,""),e.flags&=-33);var c=xc(l);rn(l,c,i);break;case 3:case 4:var f=e.stateNode.containerInfo,y=xc(l);pc(l,y,f);break;default:throw Error(m(161))}}catch(b){nl(l,l.return,b)}l.flags&=-3}t&4096&&(l.flags&=-4097)}function to(l){if(l.subtreeFlags&1024)for(l=l.child;l!==null;){var t=l;to(t),t.tag===5&&t.flags&1024&&t.stateNode.reset(),l=l.sibling}}function kt(l,t){if(t.subtreeFlags&8772)for(t=t.child;t!==null;)W0(l,t.alternate,t),t=t.sibling}function Qe(l){for(l=l.child;l!==null;){var t=l;switch(t.tag){case 0:case 11:case 14:case 15:de(4,t,t.return),Qe(t);break;case 1:Ut(t,t.return);var e=t.stateNode;typeof e.componentWillUnmount=="function"&&V0(t,t.return,e),Qe(t);break;case 27:ru(t.stateNode);case 26:case 5:Ut(t,t.return),Qe(t);break;case 22:t.memoizedState===null&&Qe(t);break;case 30:Qe(t);break;default:Qe(t)}l=l.sibling}}function Wt(l,t,e){for(e=e&&(t.subtreeFlags&8772)!==0,t=t.child;t!==null;){var a=t.alternate,u=l,n=t,i=n.flags;switch(n.tag){case 0:case 11:case 15:Wt(u,n,e),au(4,n);break;case 1:if(Wt(u,n,e),a=n,u=a.stateNode,typeof u.componentDidMount=="function")try{u.componentDidMount()}catch(y){nl(a,a.return,y)}if(a=n,u=a.updateQueue,u!==null){var c=a.stateNode;try{var f=u.shared.hiddenCallbacks;if(f!==null)for(u.shared.hiddenCallbacks=null,u=0;u<f.length;u++)Us(f[u],c)}catch(y){nl(a,a.return,y)}}e&&i&64&&L0(n),uu(n,n.return);break;case 27:w0(n);case 26:case 5:Wt(u,n,e),e&&a===null&&i&4&&K0(n),uu(n,n.return);break;case 12:Wt(u,n,e);break;case 31:Wt(u,n,e),e&&i&4&&I0(u,n);break;case 13:Wt(u,n,e),e&&i&4&&P0(u,n);break;case 22:n.memoizedState===null&&Wt(u,n,e),uu(n,n.return);break;case 30:break;default:Wt(u,n,e)}t=t.sibling}}function Tc(l,t){var e=null;l!==null&&l.memoizedState!==null&&l.memoizedState.cachePool!==null&&(e=l.memoizedState.cachePool.pool),l=null,t.memoizedState!==null&&t.memoizedState.cachePool!==null&&(l=t.memoizedState.cachePool.pool),l!==e&&(l!=null&&l.refCount++,e!=null&&Va(e))}function Ec(l,t){l=null,t.alternate!==null&&(l=t.alternate.memoizedState.cache),t=t.memoizedState.cache,t!==l&&(t.refCount++,l!=null&&Va(l))}function Ot(l,t,e,a){if(t.subtreeFlags&10256)for(t=t.child;t!==null;)eo(l,t,e,a),t=t.sibling}function eo(l,t,e,a){var u=t.flags;switch(t.tag){case 0:case 11:case 15:Ot(l,t,e,a),u&2048&&au(9,t);break;case 1:Ot(l,t,e,a);break;case 3:Ot(l,t,e,a),u&2048&&(l=null,t.alternate!==null&&(l=t.alternate.memoizedState.cache),t=t.memoizedState.cache,t!==l&&(t.refCount++,l!=null&&Va(l)));break;case 12:if(u&2048){Ot(l,t,e,a),l=t.stateNode;try{var n=t.memoizedProps,i=n.id,c=n.onPostCommit;typeof c=="function"&&c(i,t.alternate===null?"mount":"update",l.passiveEffectDuration,-0)}catch(f){nl(t,t.return,f)}}else Ot(l,t,e,a);break;case 31:Ot(l,t,e,a);break;case 13:Ot(l,t,e,a);break;case 23:break;case 22:n=t.stateNode,i=t.alternate,t.memoizedState!==null?n._visibility&2?Ot(l,t,e,a):nu(l,t):n._visibility&2?Ot(l,t,e,a):(n._visibility|=2,va(l,t,e,a,(t.subtreeFlags&10256)!==0||!1)),u&2048&&Tc(i,t);break;case 24:Ot(l,t,e,a),u&2048&&Ec(t.alternate,t);break;default:Ot(l,t,e,a)}}function va(l,t,e,a,u){for(u=u&&((t.subtreeFlags&10256)!==0||!1),t=t.child;t!==null;){var n=l,i=t,c=e,f=a,y=i.flags;switch(i.tag){case 0:case 11:case 15:va(n,i,c,f,u),au(8,i);break;case 23:break;case 22:var b=i.stateNode;i.memoizedState!==null?b._visibility&2?va(n,i,c,f,u):nu(n,i):(b._visibility|=2,va(n,i,c,f,u)),u&&y&2048&&Tc(i.alternate,i);break;case 24:va(n,i,c,f,u),u&&y&2048&&Ec(i.alternate,i);break;default:va(n,i,c,f,u)}t=t.sibling}}function nu(l,t){if(t.subtreeFlags&10256)for(t=t.child;t!==null;){var e=l,a=t,u=a.flags;switch(a.tag){case 22:nu(e,a),u&2048&&Tc(a.alternate,a);break;case 24:nu(e,a),u&2048&&Ec(a.alternate,a);break;default:nu(e,a)}t=t.sibling}}var iu=8192;function ha(l,t,e){if(l.subtreeFlags&iu)for(l=l.child;l!==null;)ao(l,t,e),l=l.sibling}function ao(l,t,e){switch(l.tag){case 26:ha(l,t,e),l.flags&iu&&l.memoizedState!==null&&kr(e,Mt,l.memoizedState,l.memoizedProps);break;case 5:ha(l,t,e);break;case 3:case 4:var a=Mt;Mt=Mn(l.stateNode.containerInfo),ha(l,t,e),Mt=a;break;case 22:l.memoizedState===null&&(a=l.alternate,a!==null&&a.memoizedState!==null?(a=iu,iu=16777216,ha(l,t,e),iu=a):ha(l,t,e));break;default:ha(l,t,e)}}function uo(l){var t=l.alternate;if(t!==null&&(l=t.child,l!==null)){t.child=null;do t=l.sibling,l.sibling=null,l=t;while(l!==null)}}function cu(l){var t=l.deletions;if((l.flags&16)!==0){if(t!==null)for(var e=0;e<t.length;e++){var a=t[e];ql=a,io(a,l)}uo(l)}if(l.subtreeFlags&10256)for(l=l.child;l!==null;)no(l),l=l.sibling}function no(l){switch(l.tag){case 0:case 11:case 15:cu(l),l.flags&2048&&de(9,l,l.return);break;case 3:cu(l);break;case 12:cu(l);break;case 22:var t=l.stateNode;l.memoizedState!==null&&t._visibility&2&&(l.return===null||l.return.tag!==13)?(t._visibility&=-3,vn(l)):cu(l);break;default:cu(l)}}function vn(l){var t=l.deletions;if((l.flags&16)!==0){if(t!==null)for(var e=0;e<t.length;e++){var a=t[e];ql=a,io(a,l)}uo(l)}for(l=l.child;l!==null;){switch(t=l,t.tag){case 0:case 11:case 15:de(8,t,t.return),vn(t);break;case 22:e=t.stateNode,e._visibility&2&&(e._visibility&=-3,vn(t));break;default:vn(t)}l=l.sibling}}function io(l,t){for(;ql!==null;){var e=ql;switch(e.tag){case 0:case 11:case 15:de(8,e,t);break;case 23:case 22:if(e.memoizedState!==null&&e.memoizedState.cachePool!==null){var a=e.memoizedState.cachePool.pool;a!=null&&a.refCount++}break;case 24:Va(e.memoizedState.cache)}if(a=e.child,a!==null)a.return=e,ql=a;else l:for(e=l;ql!==null;){a=ql;var u=a.sibling,n=a.return;if($0(a),a===e){ql=null;break l}if(u!==null){u.return=n,ql=u;break l}ql=n}}}var sr={getCacheForType:function(l){var t=Xl(Nl),e=t.data.get(l);return e===void 0&&(e=l(),t.data.set(l,e)),e},cacheSignal:function(){return Xl(Nl).controller.signal}},or=typeof WeakMap=="function"?WeakMap:Map,tl=0,rl=null,w=null,$=0,ul=0,ot=null,me=!1,ga=!1,Ac=!1,$t=0,zl=0,re=0,Ze=0,_c=0,dt=0,ba=0,fu=null,tt=null,Nc=!1,hn=0,co=0,gn=1/0,bn=null,ye=null,jl=0,ve=null,Sa=null,Ft=0,Mc=0,Oc=null,fo=null,su=0,Dc=null;function mt(){return(tl&2)!==0&&$!==0?$&-$:S.T!==null?qc():Ef()}function so(){if(dt===0)if(($&536870912)===0||I){var l=Au;Au<<=1,(Au&3932160)===0&&(Au=262144),dt=l}else dt=536870912;return l=ft.current,l!==null&&(l.flags|=32),dt}function et(l,t,e){(l===rl&&(ul===2||ul===9)||l.cancelPendingCommit!==null)&&(xa(l,0),he(l,$,dt,!1)),Da(l,e),((tl&2)===0||l!==rl)&&(l===rl&&((tl&2)===0&&(Ze|=e),zl===4&&he(l,$,dt,!1)),Ht(l))}function oo(l,t,e){if((tl&6)!==0)throw Error(m(327));var a=!e&&(t&127)===0&&(t&l.expiredLanes)===0||Oa(l,t),u=a?rr(l,t):Uc(l,t,!0),n=a;do{if(u===0){ga&&!a&&he(l,t,0,!1);break}else{if(e=l.current.alternate,n&&!dr(e)){u=Uc(l,t,!1),n=!1;continue}if(u===2){if(n=t,l.errorRecoveryDisabledLanes&n)var i=0;else i=l.pendingLanes&-536870913,i=i!==0?i:i&536870912?536870912:0;if(i!==0){t=i;l:{var c=l;u=fu;var f=c.current.memoizedState.isDehydrated;if(f&&(xa(c,i).flags|=256),i=Uc(c,i,!1),i!==2){if(Ac&&!f){c.errorRecoveryDisabledLanes|=n,Ze|=n,u=4;break l}n=tt,tt=u,n!==null&&(tt===null?tt=n:tt.push.apply(tt,n))}u=i}if(n=!1,u!==2)continue}}if(u===1){xa(l,0),he(l,t,0,!0);break}l:{switch(a=l,n=u,n){case 0:case 1:throw Error(m(345));case 4:if((t&4194048)!==t)break;case 6:he(a,t,dt,!me);break l;case 2:tt=null;break;case 3:case 5:break;default:throw Error(m(329))}if((t&62914560)===t&&(u=hn+300-at(),10<u)){if(he(a,t,dt,!me),Nu(a,0,!0)!==0)break l;Ft=t,a.timeoutHandle=Zo(mo.bind(null,a,e,tt,bn,Nc,t,dt,Ze,ba,me,n,"Throttled",-0,0),u);break l}mo(a,e,tt,bn,Nc,t,dt,Ze,ba,me,n,null,-0,0)}}break}while(!0);Ht(l)}function mo(l,t,e,a,u,n,i,c,f,y,b,p,h,g){if(l.timeoutHandle=-1,p=t.subtreeFlags,p&8192||(p&16785408)===16785408){p={stylesheets:null,count:0,imgCount:0,imgBytes:0,suspenseyImages:[],waitingForImages:!0,waitingForViewTransition:!1,unsuspend:qt},ao(t,n,p);var M=(n&62914560)===n?hn-at():(n&4194048)===n?co-at():0;if(M=Wr(p,M),M!==null){Ft=n,l.cancelPendingCommit=M(xo.bind(null,l,t,n,e,a,u,i,c,f,b,p,null,h,g)),he(l,n,i,!y);return}}xo(l,t,n,e,a,u,i,c,f)}function dr(l){for(var t=l;;){var e=t.tag;if((e===0||e===11||e===15)&&t.flags&16384&&(e=t.updateQueue,e!==null&&(e=e.stores,e!==null)))for(var a=0;a<e.length;a++){var u=e[a],n=u.getSnapshot;u=u.value;try{if(!it(n(),u))return!1}catch{return!1}}if(e=t.child,t.subtreeFlags&16384&&e!==null)e.return=t,t=e;else{if(t===l)break;for(;t.sibling===null;){if(t.return===null||t.return===l)return!0;t=t.return}t.sibling.return=t.return,t=t.sibling}}return!0}function he(l,t,e,a){t&=~_c,t&=~Ze,l.suspendedLanes|=t,l.pingedLanes&=~t,a&&(l.warmLanes|=t),a=l.expirationTimes;for(var u=t;0<u;){var n=31-nt(u),i=1<<n;a[n]=-1,u&=~i}e!==0&&pf(l,e,t)}function Sn(){return(tl&6)===0?(ou(0),!1):!0}function jc(){if(w!==null){if(ul===0)var l=w.return;else l=w,Xt=He=null,wi(l),oa=null,Ja=0,l=w;for(;l!==null;)Z0(l.alternate,l),l=l.return;w=null}}function xa(l,t){var e=l.timeoutHandle;e!==-1&&(l.timeoutHandle=-1,jr(e)),e=l.cancelPendingCommit,e!==null&&(l.cancelPendingCommit=null,e()),Ft=0,jc(),rl=l,w=e=Yt(l.current,null),$=t,ul=0,ot=null,me=!1,ga=Oa(l,t),Ac=!1,ba=dt=_c=Ze=re=zl=0,tt=fu=null,Nc=!1,(t&8)!==0&&(t|=t&32);var a=l.entangledLanes;if(a!==0)for(l=l.entanglements,a&=t;0<a;){var u=31-nt(a),n=1<<u;t|=l[u],a&=~n}return $t=t,Gu(),e}function ro(l,t){Z=null,S.H=lu,t===sa||t===wu?(t=Ms(),ul=3):t===Ri?(t=Ms(),ul=4):ul=t===sc?8:t!==null&&typeof t=="object"&&typeof t.then=="function"?6:1,ot=t,w===null&&(zl=1,fn(l,bt(t,l.current)))}function yo(){var l=ft.current;return l===null?!0:($&4194048)===$?zt===null:($&62914560)===$||($&536870912)!==0?l===zt:!1}function vo(){var l=S.H;return S.H=lu,l===null?lu:l}function ho(){var l=S.A;return S.A=sr,l}function xn(){zl=4,me||($&4194048)!==$&&ft.current!==null||(ga=!0),(re&134217727)===0&&(Ze&134217727)===0||rl===null||he(rl,$,dt,!1)}function Uc(l,t,e){var a=tl;tl|=2;var u=vo(),n=ho();(rl!==l||$!==t)&&(bn=null,xa(l,t)),t=!1;var i=zl;l:do try{if(ul!==0&&w!==null){var c=w,f=ot;switch(ul){case 8:jc(),i=6;break l;case 3:case 2:case 9:case 6:ft.current===null&&(t=!0);var y=ul;if(ul=0,ot=null,pa(l,c,f,y),e&&ga){i=0;break l}break;default:y=ul,ul=0,ot=null,pa(l,c,f,y)}}mr(),i=zl;break}catch(b){ro(l,b)}while(!0);return t&&l.shellSuspendCounter++,Xt=He=null,tl=a,S.H=u,S.A=n,w===null&&(rl=null,$=0,Gu()),i}function mr(){for(;w!==null;)go(w)}function rr(l,t){var e=tl;tl|=2;var a=vo(),u=ho();rl!==l||$!==t?(bn=null,gn=at()+500,xa(l,t)):ga=Oa(l,t);l:do try{if(ul!==0&&w!==null){t=w;var n=ot;t:switch(ul){case 1:ul=0,ot=null,pa(l,t,n,1);break;case 2:case 9:if(_s(n)){ul=0,ot=null,bo(t);break}t=function(){ul!==2&&ul!==9||rl!==l||(ul=7),Ht(l)},n.then(t,t);break l;case 3:ul=7;break l;case 4:ul=5;break l;case 7:_s(n)?(ul=0,ot=null,bo(t)):(ul=0,ot=null,pa(l,t,n,7));break;case 5:var i=null;switch(w.tag){case 26:i=w.memoizedState;case 5:case 27:var c=w;if(i?ad(i):c.stateNode.complete){ul=0,ot=null;var f=c.sibling;if(f!==null)w=f;else{var y=c.return;y!==null?(w=y,pn(y)):w=null}break t}}ul=0,ot=null,pa(l,t,n,5);break;case 6:ul=0,ot=null,pa(l,t,n,6);break;case 8:jc(),zl=6;break l;default:throw Error(m(462))}}yr();break}catch(b){ro(l,b)}while(!0);return Xt=He=null,S.H=a,S.A=u,tl=e,w!==null?0:(rl=null,$=0,Gu(),zl)}function yr(){for(;w!==null&&!Bd();)go(w)}function go(l){var t=X0(l.alternate,l,$t);l.memoizedProps=l.pendingProps,t===null?pn(l):w=t}function bo(l){var t=l,e=t.alternate;switch(t.tag){case 15:case 0:t=C0(e,t,t.pendingProps,t.type,void 0,$);break;case 11:t=C0(e,t,t.pendingProps,t.type.render,t.ref,$);break;case 5:wi(t);default:Z0(e,t),t=w=vs(t,$t),t=X0(e,t,$t)}l.memoizedProps=l.pendingProps,t===null?pn(l):w=t}function pa(l,t,e,a){Xt=He=null,wi(t),oa=null,Ja=0;var u=t.return;try{if(er(l,u,t,e,$)){zl=1,fn(l,bt(e,l.current)),w=null;return}}catch(n){if(u!==null)throw w=u,n;zl=1,fn(l,bt(e,l.current)),w=null;return}t.flags&32768?(I||a===1?l=!0:ga||($&536870912)!==0?l=!1:(me=l=!0,(a===2||a===9||a===3||a===6)&&(a=ft.current,a!==null&&a.tag===13&&(a.flags|=16384))),So(t,l)):pn(t)}function pn(l){var t=l;do{if((t.flags&32768)!==0){So(t,me);return}l=t.return;var e=nr(t.alternate,t,$t);if(e!==null){w=e;return}if(t=t.sibling,t!==null){w=t;return}w=t=l}while(t!==null);zl===0&&(zl=5)}function So(l,t){do{var e=ir(l.alternate,l);if(e!==null){e.flags&=32767,w=e;return}if(e=l.return,e!==null&&(e.flags|=32768,e.subtreeFlags=0,e.deletions=null),!t&&(l=l.sibling,l!==null)){w=l;return}w=l=e}while(l!==null);zl=6,w=null}function xo(l,t,e,a,u,n,i,c,f){l.cancelPendingCommit=null;do zn();while(jl!==0);if((tl&6)!==0)throw Error(m(327));if(t!==null){if(t===l.current)throw Error(m(177));if(n=t.lanes|t.childLanes,n|=xi,wd(l,e,n,i,c,f),l===rl&&(w=rl=null,$=0),Sa=t,ve=l,Ft=e,Mc=n,Oc=u,fo=a,(t.subtreeFlags&10256)!==0||(t.flags&10256)!==0?(l.callbackNode=null,l.callbackPriority=0,br(Tu,function(){return Ao(),null})):(l.callbackNode=null,l.callbackPriority=0),a=(t.flags&13878)!==0,(t.subtreeFlags&13878)!==0||a){a=S.T,S.T=null,u=A.p,A.p=2,i=tl,tl|=4;try{cr(l,t,e)}finally{tl=i,A.p=u,S.T=a}}jl=1,po(),zo(),To()}}function po(){if(jl===1){jl=0;var l=ve,t=Sa,e=(t.flags&13878)!==0;if((t.subtreeFlags&13878)!==0||e){e=S.T,S.T=null;var a=A.p;A.p=2;var u=tl;tl|=4;try{lo(t,l);var n=Vc,i=is(l.containerInfo),c=n.focusedElem,f=n.selectionRange;if(i!==c&&c&&c.ownerDocument&&ns(c.ownerDocument.documentElement,c)){if(f!==null&&vi(c)){var y=f.start,b=f.end;if(b===void 0&&(b=y),"selectionStart"in c)c.selectionStart=y,c.selectionEnd=Math.min(b,c.value.length);else{var p=c.ownerDocument||document,h=p&&p.defaultView||window;if(h.getSelection){var g=h.getSelection(),M=c.textContent.length,R=Math.min(f.start,M),sl=f.end===void 0?R:Math.min(f.end,M);!g.extend&&R>sl&&(i=sl,sl=R,R=i);var d=us(c,R),s=us(c,sl);if(d&&s&&(g.rangeCount!==1||g.anchorNode!==d.node||g.anchorOffset!==d.offset||g.focusNode!==s.node||g.focusOffset!==s.offset)){var r=p.createRange();r.setStart(d.node,d.offset),g.removeAllRanges(),R>sl?(g.addRange(r),g.extend(s.node,s.offset)):(r.setEnd(s.node,s.offset),g.addRange(r))}}}}for(p=[],g=c;g=g.parentNode;)g.nodeType===1&&p.push({element:g,left:g.scrollLeft,top:g.scrollTop});for(typeof c.focus=="function"&&c.focus(),c=0;c<p.length;c++){var x=p[c];x.element.scrollLeft=x.left,x.element.scrollTop=x.top}}Cn=!!Lc,Vc=Lc=null}finally{tl=u,A.p=a,S.T=e}}l.current=t,jl=2}}function zo(){if(jl===2){jl=0;var l=ve,t=Sa,e=(t.flags&8772)!==0;if((t.subtreeFlags&8772)!==0||e){e=S.T,S.T=null;var a=A.p;A.p=2;var u=tl;tl|=4;try{W0(l,t.alternate,t)}finally{tl=u,A.p=a,S.T=e}}jl=3}}function To(){if(jl===4||jl===3){jl=0,Yd();var l=ve,t=Sa,e=Ft,a=fo;(t.subtreeFlags&10256)!==0||(t.flags&10256)!==0?jl=5:(jl=0,Sa=ve=null,Eo(l,l.pendingLanes));var u=l.pendingLanes;if(u===0&&(ye=null),$n(e),t=t.stateNode,ut&&typeof ut.onCommitFiberRoot=="function")try{ut.onCommitFiberRoot(Ma,t,void 0,(t.current.flags&128)===128)}catch{}if(a!==null){t=S.T,u=A.p,A.p=2,S.T=null;try{for(var n=l.onRecoverableError,i=0;i<a.length;i++){var c=a[i];n(c.value,{componentStack:c.stack})}}finally{S.T=t,A.p=u}}(Ft&3)!==0&&zn(),Ht(l),u=l.pendingLanes,(e&261930)!==0&&(u&42)!==0?l===Dc?su++:(su=0,Dc=l):su=0,ou(0)}}function Eo(l,t){(l.pooledCacheLanes&=t)===0&&(t=l.pooledCache,t!=null&&(l.pooledCache=null,Va(t)))}function zn(){return po(),zo(),To(),Ao()}function Ao(){if(jl!==5)return!1;var l=ve,t=Mc;Mc=0;var e=$n(Ft),a=S.T,u=A.p;try{A.p=32>e?32:e,S.T=null,e=Oc,Oc=null;var n=ve,i=Ft;if(jl=0,Sa=ve=null,Ft=0,(tl&6)!==0)throw Error(m(331));var c=tl;if(tl|=4,no(n.current),eo(n,n.current,i,e),tl=c,ou(0,!1),ut&&typeof ut.onPostCommitFiberRoot=="function")try{ut.onPostCommitFiberRoot(Ma,n)}catch{}return!0}finally{A.p=u,S.T=a,Eo(l,t)}}function _o(l,t,e){t=bt(e,t),t=fc(l.stateNode,t,2),l=fe(l,t,2),l!==null&&(Da(l,2),Ht(l))}function nl(l,t,e){if(l.tag===3)_o(l,l,e);else for(;t!==null;){if(t.tag===3){_o(t,l,e);break}else if(t.tag===1){var a=t.stateNode;if(typeof t.type.getDerivedStateFromError=="function"||typeof a.componentDidCatch=="function"&&(ye===null||!ye.has(a))){l=bt(e,l),e=_0(2),a=fe(t,e,2),a!==null&&(N0(e,a,t,l),Da(a,2),Ht(a));break}}t=t.return}}function Hc(l,t,e){var a=l.pingCache;if(a===null){a=l.pingCache=new or;var u=new Set;a.set(t,u)}else u=a.get(t),u===void 0&&(u=new Set,a.set(t,u));u.has(e)||(Ac=!0,u.add(e),l=vr.bind(null,l,t,e),t.then(l,l))}function vr(l,t,e){var a=l.pingCache;a!==null&&a.delete(t),l.pingedLanes|=l.suspendedLanes&e,l.warmLanes&=~e,rl===l&&($&e)===e&&(zl===4||zl===3&&($&62914560)===$&&300>at()-hn?(tl&2)===0&&xa(l,0):_c|=e,ba===$&&(ba=0)),Ht(l)}function No(l,t){t===0&&(t=xf()),l=De(l,t),l!==null&&(Da(l,t),Ht(l))}function hr(l){var t=l.memoizedState,e=0;t!==null&&(e=t.retryLane),No(l,e)}function gr(l,t){var e=0;switch(l.tag){case 31:case 13:var a=l.stateNode,u=l.memoizedState;u!==null&&(e=u.retryLane);break;case 19:a=l.stateNode;break;case 22:a=l.stateNode._retryCache;break;default:throw Error(m(314))}a!==null&&a.delete(t),No(l,e)}function br(l,t){return Jn(l,t)}var Tn=null,za=null,Cc=!1,En=!1,Rc=!1,ge=0;function Ht(l){l!==za&&l.next===null&&(za===null?Tn=za=l:za=za.next=l),En=!0,Cc||(Cc=!0,xr())}function ou(l,t){if(!Rc&&En){Rc=!0;do for(var e=!1,a=Tn;a!==null;){if(l!==0){var u=a.pendingLanes;if(u===0)var n=0;else{var i=a.suspendedLanes,c=a.pingedLanes;n=(1<<31-nt(42|l)+1)-1,n&=u&~(i&~c),n=n&201326741?n&201326741|1:n?n|2:0}n!==0&&(e=!0,jo(a,n))}else n=$,n=Nu(a,a===rl?n:0,a.cancelPendingCommit!==null||a.timeoutHandle!==-1),(n&3)===0||Oa(a,n)||(e=!0,jo(a,n));a=a.next}while(e);Rc=!1}}function Sr(){Mo()}function Mo(){En=Cc=!1;var l=0;ge!==0&&Dr()&&(l=ge);for(var t=at(),e=null,a=Tn;a!==null;){var u=a.next,n=Oo(a,t);n===0?(a.next=null,e===null?Tn=u:e.next=u,u===null&&(za=e)):(e=a,(l!==0||(n&3)!==0)&&(En=!0)),a=u}jl!==0&&jl!==5||ou(l),ge!==0&&(ge=0)}function Oo(l,t){for(var e=l.suspendedLanes,a=l.pingedLanes,u=l.expirationTimes,n=l.pendingLanes&-62914561;0<n;){var i=31-nt(n),c=1<<i,f=u[i];f===-1?((c&e)===0||(c&a)!==0)&&(u[i]=Jd(c,t)):f<=t&&(l.expiredLanes|=c),n&=~c}if(t=rl,e=$,e=Nu(l,l===t?e:0,l.cancelPendingCommit!==null||l.timeoutHandle!==-1),a=l.callbackNode,e===0||l===t&&(ul===2||ul===9)||l.cancelPendingCommit!==null)return a!==null&&a!==null&&wn(a),l.callbackNode=null,l.callbackPriority=0;if((e&3)===0||Oa(l,e)){if(t=e&-e,t===l.callbackPriority)return t;switch(a!==null&&wn(a),$n(e)){case 2:case 8:e=bf;break;case 32:e=Tu;break;case 268435456:e=Sf;break;default:e=Tu}return a=Do.bind(null,l),e=Jn(e,a),l.callbackPriority=t,l.callbackNode=e,t}return a!==null&&a!==null&&wn(a),l.callbackPriority=2,l.callbackNode=null,2}function Do(l,t){if(jl!==0&&jl!==5)return l.callbackNode=null,l.callbackPriority=0,null;var e=l.callbackNode;if(zn()&&l.callbackNode!==e)return null;var a=$;return a=Nu(l,l===rl?a:0,l.cancelPendingCommit!==null||l.timeoutHandle!==-1),a===0?null:(oo(l,a,t),Oo(l,at()),l.callbackNode!=null&&l.callbackNode===e?Do.bind(null,l):null)}function jo(l,t){if(zn())return null;oo(l,t,!0)}function xr(){Ur(function(){(tl&6)!==0?Jn(gf,Sr):Mo()})}function qc(){if(ge===0){var l=ca;l===0&&(l=Eu,Eu<<=1,(Eu&261888)===0&&(Eu=256)),ge=l}return ge}function Uo(l){return l==null||typeof l=="symbol"||typeof l=="boolean"?null:typeof l=="function"?l:ju(""+l)}function Ho(l,t){var e=t.ownerDocument.createElement("input");return e.name=t.name,e.value=t.value,l.id&&e.setAttribute("form",l.id),t.parentNode.insertBefore(e,t),l=new FormData(l),e.parentNode.removeChild(e),l}function pr(l,t,e,a,u){if(t==="submit"&&e&&e.stateNode===u){var n=Uo((u[$l]||null).action),i=a.submitter;i&&(t=(t=i[$l]||null)?Uo(t.formAction):i.getAttribute("formAction"),t!==null&&(n=t,i=null));var c=new Ru("action","action",null,a,u);l.push({event:c,listeners:[{instance:null,listener:function(){if(a.defaultPrevented){if(ge!==0){var f=i?Ho(u,i):new FormData(u);ec(e,{pending:!0,data:f,method:u.method,action:n},null,f)}}else typeof n=="function"&&(c.preventDefault(),f=i?Ho(u,i):new FormData(u),ec(e,{pending:!0,data:f,method:u.method,action:n},n,f))},currentTarget:u}]})}}for(var Bc=0;Bc<Si.length;Bc++){var Yc=Si[Bc],zr=Yc.toLowerCase(),Tr=Yc[0].toUpperCase()+Yc.slice(1);Nt(zr,"on"+Tr)}Nt(ss,"onAnimationEnd"),Nt(os,"onAnimationIteration"),Nt(ds,"onAnimationStart"),Nt("dblclick","onDoubleClick"),Nt("focusin","onFocus"),Nt("focusout","onBlur"),Nt(Gm,"onTransitionRun"),Nt(Xm,"onTransitionStart"),Nt(Qm,"onTransitionCancel"),Nt(ms,"onTransitionEnd"),we("onMouseEnter",["mouseout","mouseover"]),we("onMouseLeave",["mouseout","mouseover"]),we("onPointerEnter",["pointerout","pointerover"]),we("onPointerLeave",["pointerout","pointerover"]),_e("onChange","change click focusin focusout input keydown keyup selectionchange".split(" ")),_e("onSelect","focusout contextmenu dragend focusin keydown keyup mousedown mouseup selectionchange".split(" ")),_e("onBeforeInput",["compositionend","keypress","textInput","paste"]),_e("onCompositionEnd","compositionend focusout keydown keypress keyup mousedown".split(" ")),_e("onCompositionStart","compositionstart focusout keydown keypress keyup mousedown".split(" ")),_e("onCompositionUpdate","compositionupdate focusout keydown keypress keyup mousedown".split(" "));var du="abort canplay canplaythrough durationchange emptied encrypted ended error loadeddata loadedmetadata loadstart pause play playing progress ratechange resize seeked seeking stalled suspend timeupdate volumechange waiting".split(" "),Er=new Set("beforetoggle cancel close invalid load scroll scrollend toggle".split(" ").concat(du));function Co(l,t){t=(t&4)!==0;for(var e=0;e<l.length;e++){var a=l[e],u=a.event;a=a.listeners;l:{var n=void 0;if(t)for(var i=a.length-1;0<=i;i--){var c=a[i],f=c.instance,y=c.currentTarget;if(c=c.listener,f!==n&&u.isPropagationStopped())break l;n=c,u.currentTarget=y;try{n(u)}catch(b){Yu(b)}u.currentTarget=null,n=f}else for(i=0;i<a.length;i++){if(c=a[i],f=c.instance,y=c.currentTarget,c=c.listener,f!==n&&u.isPropagationStopped())break l;n=c,u.currentTarget=y;try{n(u)}catch(b){Yu(b)}u.currentTarget=null,n=f}}}}function k(l,t){var e=t[Fn];e===void 0&&(e=t[Fn]=new Set);var a=l+"__bubble";e.has(a)||(Ro(t,l,2,!1),e.add(a))}function Gc(l,t,e){var a=0;t&&(a|=4),Ro(e,l,a,t)}var An="_reactListening"+Math.random().toString(36).slice(2);function Xc(l){if(!l[An]){l[An]=!0,Nf.forEach(function(e){e!=="selectionchange"&&(Er.has(e)||Gc(e,!1,l),Gc(e,!0,l))});var t=l.nodeType===9?l:l.ownerDocument;t===null||t[An]||(t[An]=!0,Gc("selectionchange",!1,t))}}function Ro(l,t,e,a){switch(od(t)){case 2:var u=Ir;break;case 8:u=Pr;break;default:u=tf}e=u.bind(null,t,e,l),u=void 0,!ii||t!=="touchstart"&&t!=="touchmove"&&t!=="wheel"||(u=!0),a?u!==void 0?l.addEventListener(t,e,{capture:!0,passive:u}):l.addEventListener(t,e,!0):u!==void 0?l.addEventListener(t,e,{passive:u}):l.addEventListener(t,e,!1)}function Qc(l,t,e,a,u){var n=a;if((t&1)===0&&(t&2)===0&&a!==null)l:for(;;){if(a===null)return;var i=a.tag;if(i===3||i===4){var c=a.stateNode.containerInfo;if(c===u)break;if(i===4)for(i=a.return;i!==null;){var f=i.tag;if((f===3||f===4)&&i.stateNode.containerInfo===u)return;i=i.return}for(;c!==null;){if(i=Ve(c),i===null)return;if(f=i.tag,f===5||f===6||f===26||f===27){a=n=i;continue l}c=c.parentNode}}a=a.return}Gf(function(){var y=n,b=ui(e),p=[];l:{var h=rs.get(l);if(h!==void 0){var g=Ru,M=l;switch(l){case"keypress":if(Hu(e)===0)break l;case"keydown":case"keyup":g=gm;break;case"focusin":M="focus",g=oi;break;case"focusout":M="blur",g=oi;break;case"beforeblur":case"afterblur":g=oi;break;case"click":if(e.button===2)break l;case"auxclick":case"dblclick":case"mousedown":case"mousemove":case"mouseup":case"mouseout":case"mouseover":case"contextmenu":g=Zf;break;case"drag":case"dragend":case"dragenter":case"dragexit":case"dragleave":case"dragover":case"dragstart":case"drop":g=nm;break;case"touchcancel":case"touchend":case"touchmove":case"touchstart":g=xm;break;case ss:case os:case ds:g=fm;break;case ms:g=zm;break;case"scroll":case"scrollend":g=am;break;case"wheel":g=Em;break;case"copy":case"cut":case"paste":g=om;break;case"gotpointercapture":case"lostpointercapture":case"pointercancel":case"pointerdown":case"pointermove":case"pointerout":case"pointerover":case"pointerup":g=Vf;break;case"toggle":case"beforetoggle":g=_m}var R=(t&4)!==0,sl=!R&&(l==="scroll"||l==="scrollend"),d=R?h!==null?h+"Capture":null:h;R=[];for(var s=y,r;s!==null;){var x=s;if(r=x.stateNode,x=x.tag,x!==5&&x!==26&&x!==27||r===null||d===null||(x=Ha(s,d),x!=null&&R.push(mu(s,x,r))),sl)break;s=s.return}0<R.length&&(h=new g(h,M,null,e,b),p.push({event:h,listeners:R}))}}if((t&7)===0){l:{if(h=l==="mouseover"||l==="pointerover",g=l==="mouseout"||l==="pointerout",h&&e!==ai&&(M=e.relatedTarget||e.fromElement)&&(Ve(M)||M[Le]))break l;if((g||h)&&(h=b.window===b?b:(h=b.ownerDocument)?h.defaultView||h.parentWindow:window,g?(M=e.relatedTarget||e.toElement,g=y,M=M?Ve(M):null,M!==null&&(sl=C(M),R=M.tag,M!==sl||R!==5&&R!==27&&R!==6)&&(M=null)):(g=null,M=y),g!==M)){if(R=Zf,x="onMouseLeave",d="onMouseEnter",s="mouse",(l==="pointerout"||l==="pointerover")&&(R=Vf,x="onPointerLeave",d="onPointerEnter",s="pointer"),sl=g==null?h:Ua(g),r=M==null?h:Ua(M),h=new R(x,s+"leave",g,e,b),h.target=sl,h.relatedTarget=r,x=null,Ve(b)===y&&(R=new R(d,s+"enter",M,e,b),R.target=r,R.relatedTarget=sl,x=R),sl=x,g&&M)t:{for(R=Ar,d=g,s=M,r=0,x=d;x;x=R(x))r++;x=0;for(var U=s;U;U=R(U))x++;for(;0<r-x;)d=R(d),r--;for(;0<x-r;)s=R(s),x--;for(;r--;){if(d===s||s!==null&&d===s.alternate){R=d;break t}d=R(d),s=R(s)}R=null}else R=null;g!==null&&qo(p,h,g,R,!1),M!==null&&sl!==null&&qo(p,sl,M,R,!0)}}l:{if(h=y?Ua(y):window,g=h.nodeName&&h.nodeName.toLowerCase(),g==="select"||g==="input"&&h.type==="file")var P=If;else if($f(h))if(Pf)P=qm;else{P=Cm;var D=Hm}else g=h.nodeName,!g||g.toLowerCase()!=="input"||h.type!=="checkbox"&&h.type!=="radio"?y&&ei(y.elementType)&&(P=If):P=Rm;if(P&&(P=P(l,y))){Ff(p,P,e,b);break l}D&&D(l,h,y),l==="focusout"&&y&&h.type==="number"&&y.memoizedProps.value!=null&&ti(h,"number",h.value)}switch(D=y?Ua(y):window,l){case"focusin":($f(D)||D.contentEditable==="true")&&(Pe=D,hi=y,Qa=null);break;case"focusout":Qa=hi=Pe=null;break;case"mousedown":gi=!0;break;case"contextmenu":case"mouseup":case"dragend":gi=!1,cs(p,e,b);break;case"selectionchange":if(Ym)break;case"keydown":case"keyup":cs(p,e,b)}var V;if(mi)l:{switch(l){case"compositionstart":var F="onCompositionStart";break l;case"compositionend":F="onCompositionEnd";break l;case"compositionupdate":F="onCompositionUpdate";break l}F=void 0}else Ie?kf(l,e)&&(F="onCompositionEnd"):l==="keydown"&&e.keyCode===229&&(F="onCompositionStart");F&&(Kf&&e.locale!=="ko"&&(Ie||F!=="onCompositionStart"?F==="onCompositionEnd"&&Ie&&(V=Xf()):(te=b,ci="value"in te?te.value:te.textContent,Ie=!0)),D=_n(y,F),0<D.length&&(F=new Lf(F,l,null,e,b),p.push({event:F,listeners:D}),V?F.data=V:(V=Wf(e),V!==null&&(F.data=V)))),(V=Mm?Om(l,e):Dm(l,e))&&(F=_n(y,"onBeforeInput"),0<F.length&&(D=new Lf("onBeforeInput","beforeinput",null,e,b),p.push({event:D,listeners:F}),D.data=V)),pr(p,l,y,e,b)}Co(p,t)})}function mu(l,t,e){return{instance:l,listener:t,currentTarget:e}}function _n(l,t){for(var e=t+"Capture",a=[];l!==null;){var u=l,n=u.stateNode;if(u=u.tag,u!==5&&u!==26&&u!==27||n===null||(u=Ha(l,e),u!=null&&a.unshift(mu(l,u,n)),u=Ha(l,t),u!=null&&a.push(mu(l,u,n))),l.tag===3)return a;l=l.return}return[]}function Ar(l){if(l===null)return null;do l=l.return;while(l&&l.tag!==5&&l.tag!==27);return l||null}function qo(l,t,e,a,u){for(var n=t._reactName,i=[];e!==null&&e!==a;){var c=e,f=c.alternate,y=c.stateNode;if(c=c.tag,f!==null&&f===a)break;c!==5&&c!==26&&c!==27||y===null||(f=y,u?(y=Ha(e,n),y!=null&&i.unshift(mu(e,y,f))):u||(y=Ha(e,n),y!=null&&i.push(mu(e,y,f)))),e=e.return}i.length!==0&&l.push({event:t,listeners:i})}var _r=/\r\n?/g,Nr=/\u0000|\uFFFD/g;function Bo(l){return(typeof l=="string"?l:""+l).replace(_r,`
`).replace(Nr,"")}function Yo(l,t){return t=Bo(t),Bo(l)===t}function fl(l,t,e,a,u,n){switch(e){case"children":typeof a=="string"?t==="body"||t==="textarea"&&a===""||We(l,a):(typeof a=="number"||typeof a=="bigint")&&t!=="body"&&We(l,""+a);break;case"className":Ou(l,"class",a);break;case"tabIndex":Ou(l,"tabindex",a);break;case"dir":case"role":case"viewBox":case"width":case"height":Ou(l,e,a);break;case"style":Bf(l,a,n);break;case"data":if(t!=="object"){Ou(l,"data",a);break}case"src":case"href":if(a===""&&(t!=="a"||e!=="href")){l.removeAttribute(e);break}if(a==null||typeof a=="function"||typeof a=="symbol"||typeof a=="boolean"){l.removeAttribute(e);break}a=ju(""+a),l.setAttribute(e,a);break;case"action":case"formAction":if(typeof a=="function"){l.setAttribute(e,"javascript:throw new Error('A React form was unexpectedly submitted. If you called form.submit() manually, consider using form.requestSubmit() instead. If you\\'re trying to use event.stopPropagation() in a submit event handler, consider also calling event.preventDefault().')");break}else typeof n=="function"&&(e==="formAction"?(t!=="input"&&fl(l,t,"name",u.name,u,null),fl(l,t,"formEncType",u.formEncType,u,null),fl(l,t,"formMethod",u.formMethod,u,null),fl(l,t,"formTarget",u.formTarget,u,null)):(fl(l,t,"encType",u.encType,u,null),fl(l,t,"method",u.method,u,null),fl(l,t,"target",u.target,u,null)));if(a==null||typeof a=="symbol"||typeof a=="boolean"){l.removeAttribute(e);break}a=ju(""+a),l.setAttribute(e,a);break;case"onClick":a!=null&&(l.onclick=qt);break;case"onScroll":a!=null&&k("scroll",l);break;case"onScrollEnd":a!=null&&k("scrollend",l);break;case"dangerouslySetInnerHTML":if(a!=null){if(typeof a!="object"||!("__html"in a))throw Error(m(61));if(e=a.__html,e!=null){if(u.children!=null)throw Error(m(60));l.innerHTML=e}}break;case"multiple":l.multiple=a&&typeof a!="function"&&typeof a!="symbol";break;case"muted":l.muted=a&&typeof a!="function"&&typeof a!="symbol";break;case"suppressContentEditableWarning":case"suppressHydrationWarning":case"defaultValue":case"defaultChecked":case"innerHTML":case"ref":break;case"autoFocus":break;case"xlinkHref":if(a==null||typeof a=="function"||typeof a=="boolean"||typeof a=="symbol"){l.removeAttribute("xlink:href");break}e=ju(""+a),l.setAttributeNS("http://www.w3.org/1999/xlink","xlink:href",e);break;case"contentEditable":case"spellCheck":case"draggable":case"value":case"autoReverse":case"externalResourcesRequired":case"focusable":case"preserveAlpha":a!=null&&typeof a!="function"&&typeof a!="symbol"?l.setAttribute(e,""+a):l.removeAttribute(e);break;case"inert":case"allowFullScreen":case"async":case"autoPlay":case"controls":case"default":case"defer":case"disabled":case"disablePictureInPicture":case"disableRemotePlayback":case"formNoValidate":case"hidden":case"loop":case"noModule":case"noValidate":case"open":case"playsInline":case"readOnly":case"required":case"reversed":case"scoped":case"seamless":case"itemScope":a&&typeof a!="function"&&typeof a!="symbol"?l.setAttribute(e,""):l.removeAttribute(e);break;case"capture":case"download":a===!0?l.setAttribute(e,""):a!==!1&&a!=null&&typeof a!="function"&&typeof a!="symbol"?l.setAttribute(e,a):l.removeAttribute(e);break;case"cols":case"rows":case"size":case"span":a!=null&&typeof a!="function"&&typeof a!="symbol"&&!isNaN(a)&&1<=a?l.setAttribute(e,a):l.removeAttribute(e);break;case"rowSpan":case"start":a==null||typeof a=="function"||typeof a=="symbol"||isNaN(a)?l.removeAttribute(e):l.setAttribute(e,a);break;case"popover":k("beforetoggle",l),k("toggle",l),Mu(l,"popover",a);break;case"xlinkActuate":Rt(l,"http://www.w3.org/1999/xlink","xlink:actuate",a);break;case"xlinkArcrole":Rt(l,"http://www.w3.org/1999/xlink","xlink:arcrole",a);break;case"xlinkRole":Rt(l,"http://www.w3.org/1999/xlink","xlink:role",a);break;case"xlinkShow":Rt(l,"http://www.w3.org/1999/xlink","xlink:show",a);break;case"xlinkTitle":Rt(l,"http://www.w3.org/1999/xlink","xlink:title",a);break;case"xlinkType":Rt(l,"http://www.w3.org/1999/xlink","xlink:type",a);break;case"xmlBase":Rt(l,"http://www.w3.org/XML/1998/namespace","xml:base",a);break;case"xmlLang":Rt(l,"http://www.w3.org/XML/1998/namespace","xml:lang",a);break;case"xmlSpace":Rt(l,"http://www.w3.org/XML/1998/namespace","xml:space",a);break;case"is":Mu(l,"is",a);break;case"innerText":case"textContent":break;default:(!(2<e.length)||e[0]!=="o"&&e[0]!=="O"||e[1]!=="n"&&e[1]!=="N")&&(e=tm.get(e)||e,Mu(l,e,a))}}function Zc(l,t,e,a,u,n){switch(e){case"style":Bf(l,a,n);break;case"dangerouslySetInnerHTML":if(a!=null){if(typeof a!="object"||!("__html"in a))throw Error(m(61));if(e=a.__html,e!=null){if(u.children!=null)throw Error(m(60));l.innerHTML=e}}break;case"children":typeof a=="string"?We(l,a):(typeof a=="number"||typeof a=="bigint")&&We(l,""+a);break;case"onScroll":a!=null&&k("scroll",l);break;case"onScrollEnd":a!=null&&k("scrollend",l);break;case"onClick":a!=null&&(l.onclick=qt);break;case"suppressContentEditableWarning":case"suppressHydrationWarning":case"innerHTML":case"ref":break;case"innerText":case"textContent":break;default:if(!Mf.hasOwnProperty(e))l:{if(e[0]==="o"&&e[1]==="n"&&(u=e.endsWith("Capture"),t=e.slice(2,u?e.length-7:void 0),n=l[$l]||null,n=n!=null?n[e]:null,typeof n=="function"&&l.removeEventListener(t,n,u),typeof a=="function")){typeof n!="function"&&n!==null&&(e in l?l[e]=null:l.hasAttribute(e)&&l.removeAttribute(e)),l.addEventListener(t,a,u);break l}e in l?l[e]=a:a===!0?l.setAttribute(e,""):Mu(l,e,a)}}}function Zl(l,t,e){switch(t){case"div":case"span":case"svg":case"path":case"a":case"g":case"p":case"li":break;case"img":k("error",l),k("load",l);var a=!1,u=!1,n;for(n in e)if(e.hasOwnProperty(n)){var i=e[n];if(i!=null)switch(n){case"src":a=!0;break;case"srcSet":u=!0;break;case"children":case"dangerouslySetInnerHTML":throw Error(m(137,t));default:fl(l,t,n,i,e,null)}}u&&fl(l,t,"srcSet",e.srcSet,e,null),a&&fl(l,t,"src",e.src,e,null);return;case"input":k("invalid",l);var c=n=i=u=null,f=null,y=null;for(a in e)if(e.hasOwnProperty(a)){var b=e[a];if(b!=null)switch(a){case"name":u=b;break;case"type":i=b;break;case"checked":f=b;break;case"defaultChecked":y=b;break;case"value":n=b;break;case"defaultValue":c=b;break;case"children":case"dangerouslySetInnerHTML":if(b!=null)throw Error(m(137,t));break;default:fl(l,t,a,b,e,null)}}Hf(l,n,c,f,y,i,u,!1);return;case"select":k("invalid",l),a=i=n=null;for(u in e)if(e.hasOwnProperty(u)&&(c=e[u],c!=null))switch(u){case"value":n=c;break;case"defaultValue":i=c;break;case"multiple":a=c;default:fl(l,t,u,c,e,null)}t=n,e=i,l.multiple=!!a,t!=null?ke(l,!!a,t,!1):e!=null&&ke(l,!!a,e,!0);return;case"textarea":k("invalid",l),n=u=a=null;for(i in e)if(e.hasOwnProperty(i)&&(c=e[i],c!=null))switch(i){case"value":a=c;break;case"defaultValue":u=c;break;case"children":n=c;break;case"dangerouslySetInnerHTML":if(c!=null)throw Error(m(91));break;default:fl(l,t,i,c,e,null)}Rf(l,a,u,n);return;case"option":for(f in e)if(e.hasOwnProperty(f)&&(a=e[f],a!=null))switch(f){case"selected":l.selected=a&&typeof a!="function"&&typeof a!="symbol";break;default:fl(l,t,f,a,e,null)}return;case"dialog":k("beforetoggle",l),k("toggle",l),k("cancel",l),k("close",l);break;case"iframe":case"object":k("load",l);break;case"video":case"audio":for(a=0;a<du.length;a++)k(du[a],l);break;case"image":k("error",l),k("load",l);break;case"details":k("toggle",l);break;case"embed":case"source":case"link":k("error",l),k("load",l);case"area":case"base":case"br":case"col":case"hr":case"keygen":case"meta":case"param":case"track":case"wbr":case"menuitem":for(y in e)if(e.hasOwnProperty(y)&&(a=e[y],a!=null))switch(y){case"children":case"dangerouslySetInnerHTML":throw Error(m(137,t));default:fl(l,t,y,a,e,null)}return;default:if(ei(t)){for(b in e)e.hasOwnProperty(b)&&(a=e[b],a!==void 0&&Zc(l,t,b,a,e,void 0));return}}for(c in e)e.hasOwnProperty(c)&&(a=e[c],a!=null&&fl(l,t,c,a,e,null))}function Mr(l,t,e,a){switch(t){case"div":case"span":case"svg":case"path":case"a":case"g":case"p":case"li":break;case"input":var u=null,n=null,i=null,c=null,f=null,y=null,b=null;for(g in e){var p=e[g];if(e.hasOwnProperty(g)&&p!=null)switch(g){case"checked":break;case"value":break;case"defaultValue":f=p;default:a.hasOwnProperty(g)||fl(l,t,g,null,a,p)}}for(var h in a){var g=a[h];if(p=e[h],a.hasOwnProperty(h)&&(g!=null||p!=null))switch(h){case"type":n=g;break;case"name":u=g;break;case"checked":y=g;break;case"defaultChecked":b=g;break;case"value":i=g;break;case"defaultValue":c=g;break;case"children":case"dangerouslySetInnerHTML":if(g!=null)throw Error(m(137,t));break;default:g!==p&&fl(l,t,h,g,a,p)}}li(l,i,c,f,y,b,n,u);return;case"select":g=i=c=h=null;for(n in e)if(f=e[n],e.hasOwnProperty(n)&&f!=null)switch(n){case"value":break;case"multiple":g=f;default:a.hasOwnProperty(n)||fl(l,t,n,null,a,f)}for(u in a)if(n=a[u],f=e[u],a.hasOwnProperty(u)&&(n!=null||f!=null))switch(u){case"value":h=n;break;case"defaultValue":c=n;break;case"multiple":i=n;default:n!==f&&fl(l,t,u,n,a,f)}t=c,e=i,a=g,h!=null?ke(l,!!e,h,!1):!!a!=!!e&&(t!=null?ke(l,!!e,t,!0):ke(l,!!e,e?[]:"",!1));return;case"textarea":g=h=null;for(c in e)if(u=e[c],e.hasOwnProperty(c)&&u!=null&&!a.hasOwnProperty(c))switch(c){case"value":break;case"children":break;default:fl(l,t,c,null,a,u)}for(i in a)if(u=a[i],n=e[i],a.hasOwnProperty(i)&&(u!=null||n!=null))switch(i){case"value":h=u;break;case"defaultValue":g=u;break;case"children":break;case"dangerouslySetInnerHTML":if(u!=null)throw Error(m(91));break;default:u!==n&&fl(l,t,i,u,a,n)}Cf(l,h,g);return;case"option":for(var M in e)if(h=e[M],e.hasOwnProperty(M)&&h!=null&&!a.hasOwnProperty(M))switch(M){case"selected":l.selected=!1;break;default:fl(l,t,M,null,a,h)}for(f in a)if(h=a[f],g=e[f],a.hasOwnProperty(f)&&h!==g&&(h!=null||g!=null))switch(f){case"selected":l.selected=h&&typeof h!="function"&&typeof h!="symbol";break;default:fl(l,t,f,h,a,g)}return;case"img":case"link":case"area":case"base":case"br":case"col":case"embed":case"hr":case"keygen":case"meta":case"param":case"source":case"track":case"wbr":case"menuitem":for(var R in e)h=e[R],e.hasOwnProperty(R)&&h!=null&&!a.hasOwnProperty(R)&&fl(l,t,R,null,a,h);for(y in a)if(h=a[y],g=e[y],a.hasOwnProperty(y)&&h!==g&&(h!=null||g!=null))switch(y){case"children":case"dangerouslySetInnerHTML":if(h!=null)throw Error(m(137,t));break;default:fl(l,t,y,h,a,g)}return;default:if(ei(t)){for(var sl in e)h=e[sl],e.hasOwnProperty(sl)&&h!==void 0&&!a.hasOwnProperty(sl)&&Zc(l,t,sl,void 0,a,h);for(b in a)h=a[b],g=e[b],!a.hasOwnProperty(b)||h===g||h===void 0&&g===void 0||Zc(l,t,b,h,a,g);return}}for(var d in e)h=e[d],e.hasOwnProperty(d)&&h!=null&&!a.hasOwnProperty(d)&&fl(l,t,d,null,a,h);for(p in a)h=a[p],g=e[p],!a.hasOwnProperty(p)||h===g||h==null&&g==null||fl(l,t,p,h,a,g)}function Go(l){switch(l){case"css":case"script":case"font":case"img":case"image":case"input":case"link":return!0;default:return!1}}function Or(){if(typeof performance.getEntriesByType=="function"){for(var l=0,t=0,e=performance.getEntriesByType("resource"),a=0;a<e.length;a++){var u=e[a],n=u.transferSize,i=u.initiatorType,c=u.duration;if(n&&c&&Go(i)){for(i=0,c=u.responseEnd,a+=1;a<e.length;a++){var f=e[a],y=f.startTime;if(y>c)break;var b=f.transferSize,p=f.initiatorType;b&&Go(p)&&(f=f.responseEnd,i+=b*(f<c?1:(c-y)/(f-y)))}if(--a,t+=8*(n+i)/(u.duration/1e3),l++,10<l)break}}if(0<l)return t/l/1e6}return navigator.connection&&(l=navigator.connection.downlink,typeof l=="number")?l:5}var Lc=null,Vc=null;function Nn(l){return l.nodeType===9?l:l.ownerDocument}function Xo(l){switch(l){case"http://www.w3.org/2000/svg":return 1;case"http://www.w3.org/1998/Math/MathML":return 2;default:return 0}}function Qo(l,t){if(l===0)switch(t){case"svg":return 1;case"math":return 2;default:return 0}return l===1&&t==="foreignObject"?0:l}function Kc(l,t){return l==="textarea"||l==="noscript"||typeof t.children=="string"||typeof t.children=="number"||typeof t.children=="bigint"||typeof t.dangerouslySetInnerHTML=="object"&&t.dangerouslySetInnerHTML!==null&&t.dangerouslySetInnerHTML.__html!=null}var Jc=null;function Dr(){var l=window.event;return l&&l.type==="popstate"?l===Jc?!1:(Jc=l,!0):(Jc=null,!1)}var Zo=typeof setTimeout=="function"?setTimeout:void 0,jr=typeof clearTimeout=="function"?clearTimeout:void 0,Lo=typeof Promise=="function"?Promise:void 0,Ur=typeof queueMicrotask=="function"?queueMicrotask:typeof Lo<"u"?function(l){return Lo.resolve(null).then(l).catch(Hr)}:Zo;function Hr(l){setTimeout(function(){throw l})}function be(l){return l==="head"}function Vo(l,t){var e=t,a=0;do{var u=e.nextSibling;if(l.removeChild(e),u&&u.nodeType===8)if(e=u.data,e==="/$"||e==="/&"){if(a===0){l.removeChild(u),_a(t);return}a--}else if(e==="$"||e==="$?"||e==="$~"||e==="$!"||e==="&")a++;else if(e==="html")ru(l.ownerDocument.documentElement);else if(e==="head"){e=l.ownerDocument.head,ru(e);for(var n=e.firstChild;n;){var i=n.nextSibling,c=n.nodeName;n[ja]||c==="SCRIPT"||c==="STYLE"||c==="LINK"&&n.rel.toLowerCase()==="stylesheet"||e.removeChild(n),n=i}}else e==="body"&&ru(l.ownerDocument.body);e=u}while(e);_a(t)}function Ko(l,t){var e=l;l=0;do{var a=e.nextSibling;if(e.nodeType===1?t?(e._stashedDisplay=e.style.display,e.style.display="none"):(e.style.display=e._stashedDisplay||"",e.getAttribute("style")===""&&e.removeAttribute("style")):e.nodeType===3&&(t?(e._stashedText=e.nodeValue,e.nodeValue=""):e.nodeValue=e._stashedText||""),a&&a.nodeType===8)if(e=a.data,e==="/$"){if(l===0)break;l--}else e!=="$"&&e!=="$?"&&e!=="$~"&&e!=="$!"||l++;e=a}while(e)}function wc(l){var t=l.firstChild;for(t&&t.nodeType===10&&(t=t.nextSibling);t;){var e=t;switch(t=t.nextSibling,e.nodeName){case"HTML":case"HEAD":case"BODY":wc(e),In(e);continue;case"SCRIPT":case"STYLE":continue;case"LINK":if(e.rel.toLowerCase()==="stylesheet")continue}l.removeChild(e)}}function Cr(l,t,e,a){for(;l.nodeType===1;){var u=e;if(l.nodeName.toLowerCase()!==t.toLowerCase()){if(!a&&(l.nodeName!=="INPUT"||l.type!=="hidden"))break}else if(a){if(!l[ja])switch(t){case"meta":if(!l.hasAttribute("itemprop"))break;return l;case"link":if(n=l.getAttribute("rel"),n==="stylesheet"&&l.hasAttribute("data-precedence"))break;if(n!==u.rel||l.getAttribute("href")!==(u.href==null||u.href===""?null:u.href)||l.getAttribute("crossorigin")!==(u.crossOrigin==null?null:u.crossOrigin)||l.getAttribute("title")!==(u.title==null?null:u.title))break;return l;case"style":if(l.hasAttribute("data-precedence"))break;return l;case"script":if(n=l.getAttribute("src"),(n!==(u.src==null?null:u.src)||l.getAttribute("type")!==(u.type==null?null:u.type)||l.getAttribute("crossorigin")!==(u.crossOrigin==null?null:u.crossOrigin))&&n&&l.hasAttribute("async")&&!l.hasAttribute("itemprop"))break;return l;default:return l}}else if(t==="input"&&l.type==="hidden"){var n=u.name==null?null:""+u.name;if(u.type==="hidden"&&l.getAttribute("name")===n)return l}else return l;if(l=Tt(l.nextSibling),l===null)break}return null}function Rr(l,t,e){if(t==="")return null;for(;l.nodeType!==3;)if((l.nodeType!==1||l.nodeName!=="INPUT"||l.type!=="hidden")&&!e||(l=Tt(l.nextSibling),l===null))return null;return l}function Jo(l,t){for(;l.nodeType!==8;)if((l.nodeType!==1||l.nodeName!=="INPUT"||l.type!=="hidden")&&!t||(l=Tt(l.nextSibling),l===null))return null;return l}function kc(l){return l.data==="$?"||l.data==="$~"}function Wc(l){return l.data==="$!"||l.data==="$?"&&l.ownerDocument.readyState!=="loading"}function qr(l,t){var e=l.ownerDocument;if(l.data==="$~")l._reactRetry=t;else if(l.data!=="$?"||e.readyState!=="loading")t();else{var a=function(){t(),e.removeEventListener("DOMContentLoaded",a)};e.addEventListener("DOMContentLoaded",a),l._reactRetry=a}}function Tt(l){for(;l!=null;l=l.nextSibling){var t=l.nodeType;if(t===1||t===3)break;if(t===8){if(t=l.data,t==="$"||t==="$!"||t==="$?"||t==="$~"||t==="&"||t==="F!"||t==="F")break;if(t==="/$"||t==="/&")return null}}return l}var $c=null;function wo(l){l=l.nextSibling;for(var t=0;l;){if(l.nodeType===8){var e=l.data;if(e==="/$"||e==="/&"){if(t===0)return Tt(l.nextSibling);t--}else e!=="$"&&e!=="$!"&&e!=="$?"&&e!=="$~"&&e!=="&"||t++}l=l.nextSibling}return null}function ko(l){l=l.previousSibling;for(var t=0;l;){if(l.nodeType===8){var e=l.data;if(e==="$"||e==="$!"||e==="$?"||e==="$~"||e==="&"){if(t===0)return l;t--}else e!=="/$"&&e!=="/&"||t++}l=l.previousSibling}return null}function Wo(l,t,e){switch(t=Nn(e),l){case"html":if(l=t.documentElement,!l)throw Error(m(452));return l;case"head":if(l=t.head,!l)throw Error(m(453));return l;case"body":if(l=t.body,!l)throw Error(m(454));return l;default:throw Error(m(451))}}function ru(l){for(var t=l.attributes;t.length;)l.removeAttributeNode(t[0]);In(l)}var Et=new Map,$o=new Set;function Mn(l){return typeof l.getRootNode=="function"?l.getRootNode():l.nodeType===9?l:l.ownerDocument}var It=A.d;A.d={f:Br,r:Yr,D:Gr,C:Xr,L:Qr,m:Zr,X:Vr,S:Lr,M:Kr};function Br(){var l=It.f(),t=Sn();return l||t}function Yr(l){var t=Ke(l);t!==null&&t.tag===5&&t.type==="form"?m0(t):It.r(l)}var Ta=typeof document>"u"?null:document;function Fo(l,t,e){var a=Ta;if(a&&typeof t=="string"&&t){var u=ht(t);u='link[rel="'+l+'"][href="'+u+'"]',typeof e=="string"&&(u+='[crossorigin="'+e+'"]'),$o.has(u)||($o.add(u),l={rel:l,crossOrigin:e,href:t},a.querySelector(u)===null&&(t=a.createElement("link"),Zl(t,"link",l),Rl(t),a.head.appendChild(t)))}}function Gr(l){It.D(l),Fo("dns-prefetch",l,null)}function Xr(l,t){It.C(l,t),Fo("preconnect",l,t)}function Qr(l,t,e){It.L(l,t,e);var a=Ta;if(a&&l&&t){var u='link[rel="preload"][as="'+ht(t)+'"]';t==="image"&&e&&e.imageSrcSet?(u+='[imagesrcset="'+ht(e.imageSrcSet)+'"]',typeof e.imageSizes=="string"&&(u+='[imagesizes="'+ht(e.imageSizes)+'"]')):u+='[href="'+ht(l)+'"]';var n=u;switch(t){case"style":n=Ea(l);break;case"script":n=Aa(l)}Et.has(n)||(l=j({rel:"preload",href:t==="image"&&e&&e.imageSrcSet?void 0:l,as:t},e),Et.set(n,l),a.querySelector(u)!==null||t==="style"&&a.querySelector(yu(n))||t==="script"&&a.querySelector(vu(n))||(t=a.createElement("link"),Zl(t,"link",l),Rl(t),a.head.appendChild(t)))}}function Zr(l,t){It.m(l,t);var e=Ta;if(e&&l){var a=t&&typeof t.as=="string"?t.as:"script",u='link[rel="modulepreload"][as="'+ht(a)+'"][href="'+ht(l)+'"]',n=u;switch(a){case"audioworklet":case"paintworklet":case"serviceworker":case"sharedworker":case"worker":case"script":n=Aa(l)}if(!Et.has(n)&&(l=j({rel:"modulepreload",href:l},t),Et.set(n,l),e.querySelector(u)===null)){switch(a){case"audioworklet":case"paintworklet":case"serviceworker":case"sharedworker":case"worker":case"script":if(e.querySelector(vu(n)))return}a=e.createElement("link"),Zl(a,"link",l),Rl(a),e.head.appendChild(a)}}}function Lr(l,t,e){It.S(l,t,e);var a=Ta;if(a&&l){var u=Je(a).hoistableStyles,n=Ea(l);t=t||"default";var i=u.get(n);if(!i){var c={loading:0,preload:null};if(i=a.querySelector(yu(n)))c.loading=5;else{l=j({rel:"stylesheet",href:l,"data-precedence":t},e),(e=Et.get(n))&&Fc(l,e);var f=i=a.createElement("link");Rl(f),Zl(f,"link",l),f._p=new Promise(function(y,b){f.onload=y,f.onerror=b}),f.addEventListener("load",function(){c.loading|=1}),f.addEventListener("error",function(){c.loading|=2}),c.loading|=4,On(i,t,a)}i={type:"stylesheet",instance:i,count:1,state:c},u.set(n,i)}}}function Vr(l,t){It.X(l,t);var e=Ta;if(e&&l){var a=Je(e).hoistableScripts,u=Aa(l),n=a.get(u);n||(n=e.querySelector(vu(u)),n||(l=j({src:l,async:!0},t),(t=Et.get(u))&&Ic(l,t),n=e.createElement("script"),Rl(n),Zl(n,"link",l),e.head.appendChild(n)),n={type:"script",instance:n,count:1,state:null},a.set(u,n))}}function Kr(l,t){It.M(l,t);var e=Ta;if(e&&l){var a=Je(e).hoistableScripts,u=Aa(l),n=a.get(u);n||(n=e.querySelector(vu(u)),n||(l=j({src:l,async:!0,type:"module"},t),(t=Et.get(u))&&Ic(l,t),n=e.createElement("script"),Rl(n),Zl(n,"link",l),e.head.appendChild(n)),n={type:"script",instance:n,count:1,state:null},a.set(u,n))}}function Io(l,t,e,a){var u=(u=J.current)?Mn(u):null;if(!u)throw Error(m(446));switch(l){case"meta":case"title":return null;case"style":return typeof e.precedence=="string"&&typeof e.href=="string"?(t=Ea(e.href),e=Je(u).hoistableStyles,a=e.get(t),a||(a={type:"style",instance:null,count:0,state:null},e.set(t,a)),a):{type:"void",instance:null,count:0,state:null};case"link":if(e.rel==="stylesheet"&&typeof e.href=="string"&&typeof e.precedence=="string"){l=Ea(e.href);var n=Je(u).hoistableStyles,i=n.get(l);if(i||(u=u.ownerDocument||u,i={type:"stylesheet",instance:null,count:0,state:{loading:0,preload:null}},n.set(l,i),(n=u.querySelector(yu(l)))&&!n._p&&(i.instance=n,i.state.loading=5),Et.has(l)||(e={rel:"preload",as:"style",href:e.href,crossOrigin:e.crossOrigin,integrity:e.integrity,media:e.media,hrefLang:e.hrefLang,referrerPolicy:e.referrerPolicy},Et.set(l,e),n||Jr(u,l,e,i.state))),t&&a===null)throw Error(m(528,""));return i}if(t&&a!==null)throw Error(m(529,""));return null;case"script":return t=e.async,e=e.src,typeof e=="string"&&t&&typeof t!="function"&&typeof t!="symbol"?(t=Aa(e),e=Je(u).hoistableScripts,a=e.get(t),a||(a={type:"script",instance:null,count:0,state:null},e.set(t,a)),a):{type:"void",instance:null,count:0,state:null};default:throw Error(m(444,l))}}function Ea(l){return'href="'+ht(l)+'"'}function yu(l){return'link[rel="stylesheet"]['+l+"]"}function Po(l){return j({},l,{"data-precedence":l.precedence,precedence:null})}function Jr(l,t,e,a){l.querySelector('link[rel="preload"][as="style"]['+t+"]")?a.loading=1:(t=l.createElement("link"),a.preload=t,t.addEventListener("load",function(){return a.loading|=1}),t.addEventListener("error",function(){return a.loading|=2}),Zl(t,"link",e),Rl(t),l.head.appendChild(t))}function Aa(l){return'[src="'+ht(l)+'"]'}function vu(l){return"script[async]"+l}function ld(l,t,e){if(t.count++,t.instance===null)switch(t.type){case"style":var a=l.querySelector('style[data-href~="'+ht(e.href)+'"]');if(a)return t.instance=a,Rl(a),a;var u=j({},e,{"data-href":e.href,"data-precedence":e.precedence,href:null,precedence:null});return a=(l.ownerDocument||l).createElement("style"),Rl(a),Zl(a,"style",u),On(a,e.precedence,l),t.instance=a;case"stylesheet":u=Ea(e.href);var n=l.querySelector(yu(u));if(n)return t.state.loading|=4,t.instance=n,Rl(n),n;a=Po(e),(u=Et.get(u))&&Fc(a,u),n=(l.ownerDocument||l).createElement("link"),Rl(n);var i=n;return i._p=new Promise(function(c,f){i.onload=c,i.onerror=f}),Zl(n,"link",a),t.state.loading|=4,On(n,e.precedence,l),t.instance=n;case"script":return n=Aa(e.src),(u=l.querySelector(vu(n)))?(t.instance=u,Rl(u),u):(a=e,(u=Et.get(n))&&(a=j({},e),Ic(a,u)),l=l.ownerDocument||l,u=l.createElement("script"),Rl(u),Zl(u,"link",a),l.head.appendChild(u),t.instance=u);case"void":return null;default:throw Error(m(443,t.type))}else t.type==="stylesheet"&&(t.state.loading&4)===0&&(a=t.instance,t.state.loading|=4,On(a,e.precedence,l));return t.instance}function On(l,t,e){for(var a=e.querySelectorAll('link[rel="stylesheet"][data-precedence],style[data-precedence]'),u=a.length?a[a.length-1]:null,n=u,i=0;i<a.length;i++){var c=a[i];if(c.dataset.precedence===t)n=c;else if(n!==u)break}n?n.parentNode.insertBefore(l,n.nextSibling):(t=e.nodeType===9?e.head:e,t.insertBefore(l,t.firstChild))}function Fc(l,t){l.crossOrigin==null&&(l.crossOrigin=t.crossOrigin),l.referrerPolicy==null&&(l.referrerPolicy=t.referrerPolicy),l.title==null&&(l.title=t.title)}function Ic(l,t){l.crossOrigin==null&&(l.crossOrigin=t.crossOrigin),l.referrerPolicy==null&&(l.referrerPolicy=t.referrerPolicy),l.integrity==null&&(l.integrity=t.integrity)}var Dn=null;function td(l,t,e){if(Dn===null){var a=new Map,u=Dn=new Map;u.set(e,a)}else u=Dn,a=u.get(e),a||(a=new Map,u.set(e,a));if(a.has(l))return a;for(a.set(l,null),e=e.getElementsByTagName(l),u=0;u<e.length;u++){var n=e[u];if(!(n[ja]||n[Yl]||l==="link"&&n.getAttribute("rel")==="stylesheet")&&n.namespaceURI!=="http://www.w3.org/2000/svg"){var i=n.getAttribute(t)||"";i=l+i;var c=a.get(i);c?c.push(n):a.set(i,[n])}}return a}function ed(l,t,e){l=l.ownerDocument||l,l.head.insertBefore(e,t==="title"?l.querySelector("head > title"):null)}function wr(l,t,e){if(e===1||t.itemProp!=null)return!1;switch(l){case"meta":case"title":return!0;case"style":if(typeof t.precedence!="string"||typeof t.href!="string"||t.href==="")break;return!0;case"link":if(typeof t.rel!="string"||typeof t.href!="string"||t.href===""||t.onLoad||t.onError)break;switch(t.rel){case"stylesheet":return l=t.disabled,typeof t.precedence=="string"&&l==null;default:return!0}case"script":if(t.async&&typeof t.async!="function"&&typeof t.async!="symbol"&&!t.onLoad&&!t.onError&&t.src&&typeof t.src=="string")return!0}return!1}function ad(l){return!(l.type==="stylesheet"&&(l.state.loading&3)===0)}function kr(l,t,e,a){if(e.type==="stylesheet"&&(typeof a.media!="string"||matchMedia(a.media).matches!==!1)&&(e.state.loading&4)===0){if(e.instance===null){var u=Ea(a.href),n=t.querySelector(yu(u));if(n){t=n._p,t!==null&&typeof t=="object"&&typeof t.then=="function"&&(l.count++,l=jn.bind(l),t.then(l,l)),e.state.loading|=4,e.instance=n,Rl(n);return}n=t.ownerDocument||t,a=Po(a),(u=Et.get(u))&&Fc(a,u),n=n.createElement("link"),Rl(n);var i=n;i._p=new Promise(function(c,f){i.onload=c,i.onerror=f}),Zl(n,"link",a),e.instance=n}l.stylesheets===null&&(l.stylesheets=new Map),l.stylesheets.set(e,t),(t=e.state.preload)&&(e.state.loading&3)===0&&(l.count++,e=jn.bind(l),t.addEventListener("load",e),t.addEventListener("error",e))}}var Pc=0;function Wr(l,t){return l.stylesheets&&l.count===0&&Hn(l,l.stylesheets),0<l.count||0<l.imgCount?function(e){var a=setTimeout(function(){if(l.stylesheets&&Hn(l,l.stylesheets),l.unsuspend){var n=l.unsuspend;l.unsuspend=null,n()}},6e4+t);0<l.imgBytes&&Pc===0&&(Pc=62500*Or());var u=setTimeout(function(){if(l.waitingForImages=!1,l.count===0&&(l.stylesheets&&Hn(l,l.stylesheets),l.unsuspend)){var n=l.unsuspend;l.unsuspend=null,n()}},(l.imgBytes>Pc?50:800)+t);return l.unsuspend=e,function(){l.unsuspend=null,clearTimeout(a),clearTimeout(u)}}:null}function jn(){if(this.count--,this.count===0&&(this.imgCount===0||!this.waitingForImages)){if(this.stylesheets)Hn(this,this.stylesheets);else if(this.unsuspend){var l=this.unsuspend;this.unsuspend=null,l()}}}var Un=null;function Hn(l,t){l.stylesheets=null,l.unsuspend!==null&&(l.count++,Un=new Map,t.forEach($r,l),Un=null,jn.call(l))}function $r(l,t){if(!(t.state.loading&4)){var e=Un.get(l);if(e)var a=e.get(null);else{e=new Map,Un.set(l,e);for(var u=l.querySelectorAll("link[data-precedence],style[data-precedence]"),n=0;n<u.length;n++){var i=u[n];(i.nodeName==="LINK"||i.getAttribute("media")!=="not all")&&(e.set(i.dataset.precedence,i),a=i)}a&&e.set(null,a)}u=t.instance,i=u.getAttribute("data-precedence"),n=e.get(i)||a,n===a&&e.set(null,u),e.set(i,u),this.count++,a=jn.bind(this),u.addEventListener("load",a),u.addEventListener("error",a),n?n.parentNode.insertBefore(u,n.nextSibling):(l=l.nodeType===9?l.head:l,l.insertBefore(u,l.firstChild)),t.state.loading|=4}}var hu={$$typeof:Cl,Provider:null,Consumer:null,_currentValue:Y,_currentValue2:Y,_threadCount:0};function Fr(l,t,e,a,u,n,i,c,f){this.tag=1,this.containerInfo=l,this.pingCache=this.current=this.pendingChildren=null,this.timeoutHandle=-1,this.callbackNode=this.next=this.pendingContext=this.context=this.cancelPendingCommit=null,this.callbackPriority=0,this.expirationTimes=kn(-1),this.entangledLanes=this.shellSuspendCounter=this.errorRecoveryDisabledLanes=this.expiredLanes=this.warmLanes=this.pingedLanes=this.suspendedLanes=this.pendingLanes=0,this.entanglements=kn(0),this.hiddenUpdates=kn(null),this.identifierPrefix=a,this.onUncaughtError=u,this.onCaughtError=n,this.onRecoverableError=i,this.pooledCache=null,this.pooledCacheLanes=0,this.formState=f,this.incompleteTransitions=new Map}function ud(l,t,e,a,u,n,i,c,f,y,b,p){return l=new Fr(l,t,e,i,f,y,b,p,c),t=1,n===!0&&(t|=24),n=ct(3,null,null,t),l.current=n,n.stateNode=l,t=Ui(),t.refCount++,l.pooledCache=t,t.refCount++,n.memoizedState={element:a,isDehydrated:e,cache:t},qi(n),l}function nd(l){return l?(l=ea,l):ea}function id(l,t,e,a,u,n){u=nd(u),a.context===null?a.context=u:a.pendingContext=u,a=ce(t),a.payload={element:e},n=n===void 0?null:n,n!==null&&(a.callback=n),e=fe(l,a,t),e!==null&&(et(e,l,t),ka(e,l,t))}function cd(l,t){if(l=l.memoizedState,l!==null&&l.dehydrated!==null){var e=l.retryLane;l.retryLane=e!==0&&e<t?e:t}}function lf(l,t){cd(l,t),(l=l.alternate)&&cd(l,t)}function fd(l){if(l.tag===13||l.tag===31){var t=De(l,67108864);t!==null&&et(t,l,67108864),lf(l,67108864)}}function sd(l){if(l.tag===13||l.tag===31){var t=mt();t=Wn(t);var e=De(l,t);e!==null&&et(e,l,t),lf(l,t)}}var Cn=!0;function Ir(l,t,e,a){var u=S.T;S.T=null;var n=A.p;try{A.p=2,tf(l,t,e,a)}finally{A.p=n,S.T=u}}function Pr(l,t,e,a){var u=S.T;S.T=null;var n=A.p;try{A.p=8,tf(l,t,e,a)}finally{A.p=n,S.T=u}}function tf(l,t,e,a){if(Cn){var u=ef(a);if(u===null)Qc(l,t,a,Rn,e),dd(l,a);else if(ty(u,l,t,e,a))a.stopPropagation();else if(dd(l,a),t&4&&-1<ly.indexOf(l)){for(;u!==null;){var n=Ke(u);if(n!==null)switch(n.tag){case 3:if(n=n.stateNode,n.current.memoizedState.isDehydrated){var i=Ae(n.pendingLanes);if(i!==0){var c=n;for(c.pendingLanes|=2,c.entangledLanes|=2;i;){var f=1<<31-nt(i);c.entanglements[1]|=f,i&=~f}Ht(n),(tl&6)===0&&(gn=at()+500,ou(0))}}break;case 31:case 13:c=De(n,2),c!==null&&et(c,n,2),Sn(),lf(n,2)}if(n=ef(a),n===null&&Qc(l,t,a,Rn,e),n===u)break;u=n}u!==null&&a.stopPropagation()}else Qc(l,t,a,null,e)}}function ef(l){return l=ui(l),af(l)}var Rn=null;function af(l){if(Rn=null,l=Ve(l),l!==null){var t=C(l);if(t===null)l=null;else{var e=t.tag;if(e===13){if(l=el(t),l!==null)return l;l=null}else if(e===31){if(l=ol(t),l!==null)return l;l=null}else if(e===3){if(t.stateNode.current.memoizedState.isDehydrated)return t.tag===3?t.stateNode.containerInfo:null;l=null}else t!==l&&(l=null)}}return Rn=l,null}function od(l){switch(l){case"beforetoggle":case"cancel":case"click":case"close":case"contextmenu":case"copy":case"cut":case"auxclick":case"dblclick":case"dragend":case"dragstart":case"drop":case"focusin":case"focusout":case"input":case"invalid":case"keydown":case"keypress":case"keyup":case"mousedown":case"mouseup":case"paste":case"pause":case"play":case"pointercancel":case"pointerdown":case"pointerup":case"ratechange":case"reset":case"resize":case"seeked":case"submit":case"toggle":case"touchcancel":case"touchend":case"touchstart":case"volumechange":case"change":case"selectionchange":case"textInput":case"compositionstart":case"compositionend":case"compositionupdate":case"beforeblur":case"afterblur":case"beforeinput":case"blur":case"fullscreenchange":case"focus":case"hashchange":case"popstate":case"select":case"selectstart":return 2;case"drag":case"dragenter":case"dragexit":case"dragleave":case"dragover":case"mousemove":case"mouseout":case"mouseover":case"pointermove":case"pointerout":case"pointerover":case"scroll":case"touchmove":case"wheel":case"mouseenter":case"mouseleave":case"pointerenter":case"pointerleave":return 8;case"message":switch(Gd()){case gf:return 2;case bf:return 8;case Tu:case Xd:return 32;case Sf:return 268435456;default:return 32}default:return 32}}var uf=!1,Se=null,xe=null,pe=null,gu=new Map,bu=new Map,ze=[],ly="mousedown mouseup touchcancel touchend touchstart auxclick dblclick pointercancel pointerdown pointerup dragend dragstart drop compositionend compositionstart keydown keypress keyup input textInput copy cut paste click change contextmenu reset".split(" ");function dd(l,t){switch(l){case"focusin":case"focusout":Se=null;break;case"dragenter":case"dragleave":xe=null;break;case"mouseover":case"mouseout":pe=null;break;case"pointerover":case"pointerout":gu.delete(t.pointerId);break;case"gotpointercapture":case"lostpointercapture":bu.delete(t.pointerId)}}function Su(l,t,e,a,u,n){return l===null||l.nativeEvent!==n?(l={blockedOn:t,domEventName:e,eventSystemFlags:a,nativeEvent:n,targetContainers:[u]},t!==null&&(t=Ke(t),t!==null&&fd(t)),l):(l.eventSystemFlags|=a,t=l.targetContainers,u!==null&&t.indexOf(u)===-1&&t.push(u),l)}function ty(l,t,e,a,u){switch(t){case"focusin":return Se=Su(Se,l,t,e,a,u),!0;case"dragenter":return xe=Su(xe,l,t,e,a,u),!0;case"mouseover":return pe=Su(pe,l,t,e,a,u),!0;case"pointerover":var n=u.pointerId;return gu.set(n,Su(gu.get(n)||null,l,t,e,a,u)),!0;case"gotpointercapture":return n=u.pointerId,bu.set(n,Su(bu.get(n)||null,l,t,e,a,u)),!0}return!1}function md(l){var t=Ve(l.target);if(t!==null){var e=C(t);if(e!==null){if(t=e.tag,t===13){if(t=el(e),t!==null){l.blockedOn=t,Af(l.priority,function(){sd(e)});return}}else if(t===31){if(t=ol(e),t!==null){l.blockedOn=t,Af(l.priority,function(){sd(e)});return}}else if(t===3&&e.stateNode.current.memoizedState.isDehydrated){l.blockedOn=e.tag===3?e.stateNode.containerInfo:null;return}}}l.blockedOn=null}function qn(l){if(l.blockedOn!==null)return!1;for(var t=l.targetContainers;0<t.length;){var e=ef(l.nativeEvent);if(e===null){e=l.nativeEvent;var a=new e.constructor(e.type,e);ai=a,e.target.dispatchEvent(a),ai=null}else return t=Ke(e),t!==null&&fd(t),l.blockedOn=e,!1;t.shift()}return!0}function rd(l,t,e){qn(l)&&e.delete(t)}function ey(){uf=!1,Se!==null&&qn(Se)&&(Se=null),xe!==null&&qn(xe)&&(xe=null),pe!==null&&qn(pe)&&(pe=null),gu.forEach(rd),bu.forEach(rd)}function Bn(l,t){l.blockedOn===t&&(l.blockedOn=null,uf||(uf=!0,E.unstable_scheduleCallback(E.unstable_NormalPriority,ey)))}var Yn=null;function yd(l){Yn!==l&&(Yn=l,E.unstable_scheduleCallback(E.unstable_NormalPriority,function(){Yn===l&&(Yn=null);for(var t=0;t<l.length;t+=3){var e=l[t],a=l[t+1],u=l[t+2];if(typeof a!="function"){if(af(a||e)===null)continue;break}var n=Ke(e);n!==null&&(l.splice(t,3),t-=3,ec(n,{pending:!0,data:u,method:e.method,action:a},a,u))}}))}function _a(l){function t(f){return Bn(f,l)}Se!==null&&Bn(Se,l),xe!==null&&Bn(xe,l),pe!==null&&Bn(pe,l),gu.forEach(t),bu.forEach(t);for(var e=0;e<ze.length;e++){var a=ze[e];a.blockedOn===l&&(a.blockedOn=null)}for(;0<ze.length&&(e=ze[0],e.blockedOn===null);)md(e),e.blockedOn===null&&ze.shift();if(e=(l.ownerDocument||l).$$reactFormReplay,e!=null)for(a=0;a<e.length;a+=3){var u=e[a],n=e[a+1],i=u[$l]||null;if(typeof n=="function")i||yd(e);else if(i){var c=null;if(n&&n.hasAttribute("formAction")){if(u=n,i=n[$l]||null)c=i.formAction;else if(af(u)!==null)continue}else c=i.action;typeof c=="function"?e[a+1]=c:(e.splice(a,3),a-=3),yd(e)}}}function vd(){function l(n){n.canIntercept&&n.info==="react-transition"&&n.intercept({handler:function(){return new Promise(function(i){return u=i})},focusReset:"manual",scroll:"manual"})}function t(){u!==null&&(u(),u=null),a||setTimeout(e,20)}function e(){if(!a&&!navigation.transition){var n=navigation.currentEntry;n&&n.url!=null&&navigation.navigate(n.url,{state:n.getState(),info:"react-transition",history:"replace"})}}if(typeof navigation=="object"){var a=!1,u=null;return navigation.addEventListener("navigate",l),navigation.addEventListener("navigatesuccess",t),navigation.addEventListener("navigateerror",t),setTimeout(e,100),function(){a=!0,navigation.removeEventListener("navigate",l),navigation.removeEventListener("navigatesuccess",t),navigation.removeEventListener("navigateerror",t),u!==null&&(u(),u=null)}}}function nf(l){this._internalRoot=l}Gn.prototype.render=nf.prototype.render=function(l){var t=this._internalRoot;if(t===null)throw Error(m(409));var e=t.current,a=mt();id(e,a,l,t,null,null)},Gn.prototype.unmount=nf.prototype.unmount=function(){var l=this._internalRoot;if(l!==null){this._internalRoot=null;var t=l.containerInfo;id(l.current,2,null,l,null,null),Sn(),t[Le]=null}};function Gn(l){this._internalRoot=l}Gn.prototype.unstable_scheduleHydration=function(l){if(l){var t=Ef();l={blockedOn:null,target:l,priority:t};for(var e=0;e<ze.length&&t!==0&&t<ze[e].priority;e++);ze.splice(e,0,l),e===0&&md(l)}};var hd=q.version;if(hd!=="19.2.3")throw Error(m(527,hd,"19.2.3"));A.findDOMNode=function(l){var t=l._reactInternals;if(t===void 0)throw typeof l.render=="function"?Error(m(188)):(l=Object.keys(l).join(","),Error(m(268,l)));return l=z(t),l=l!==null?L(l):null,l=l===null?null:l.stateNode,l};var ay={bundleType:0,version:"19.2.3",rendererPackageName:"react-dom",currentDispatcherRef:S,reconcilerVersion:"19.2.3"};if(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__<"u"){var Xn=__REACT_DEVTOOLS_GLOBAL_HOOK__;if(!Xn.isDisabled&&Xn.supportsFiber)try{Ma=Xn.inject(ay),ut=Xn}catch{}}return pu.createRoot=function(l,t){if(!G(l))throw Error(m(299));var e=!1,a="",u=z0,n=T0,i=E0;return t!=null&&(t.unstable_strictMode===!0&&(e=!0),t.identifierPrefix!==void 0&&(a=t.identifierPrefix),t.onUncaughtError!==void 0&&(u=t.onUncaughtError),t.onCaughtError!==void 0&&(n=t.onCaughtError),t.onRecoverableError!==void 0&&(i=t.onRecoverableError)),t=ud(l,1,!1,null,null,e,a,null,u,n,i,vd),l[Le]=t.current,Xc(l),new nf(t)},pu.hydrateRoot=function(l,t,e){if(!G(l))throw Error(m(299));var a=!1,u="",n=z0,i=T0,c=E0,f=null;return e!=null&&(e.unstable_strictMode===!0&&(a=!0),e.identifierPrefix!==void 0&&(u=e.identifierPrefix),e.onUncaughtError!==void 0&&(n=e.onUncaughtError),e.onCaughtError!==void 0&&(i=e.onCaughtError),e.onRecoverableError!==void 0&&(c=e.onRecoverableError),e.formState!==void 0&&(f=e.formState)),t=ud(l,1,!0,t,e??null,a,u,f,n,i,c,vd),t.context=nd(null),e=t.current,a=mt(),a=Wn(a),u=ce(a),u.callback=null,fe(e,u,a),e=a,t.current.lanes=e,Da(t,e),Ht(t),l[Le]=t.current,Xc(l),new Gn(t)},pu.version="19.2.3",pu}var _d;function yy(){if(_d)return sf.exports;_d=1;function E(){if(!(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__>"u"||typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE!="function"))try{__REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE(E)}catch(q){console.error(q)}}return E(),sf.exports=ry(),sf.exports}var vy=yy();const hy=jd(vy);/**
 * @license lucide-react v0.562.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const gy=E=>E.replace(/([a-z0-9])([A-Z])/g,"$1-$2").toLowerCase(),by=E=>E.replace(/^([A-Z])|[\s-_]+(\w)/g,(q,B,m)=>m?m.toUpperCase():B.toLowerCase()),Nd=E=>{const q=by(E);return q.charAt(0).toUpperCase()+q.slice(1)},Ud=(...E)=>E.filter((q,B,m)=>!!q&&q.trim()!==""&&m.indexOf(q)===B).join(" ").trim(),Sy=E=>{for(const q in E)if(q.startsWith("aria-")||q==="role"||q==="title")return!0};/**
 * @license lucide-react v0.562.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */var xy={xmlns:"http://www.w3.org/2000/svg",width:24,height:24,viewBox:"0 0 24 24",fill:"none",stroke:"currentColor",strokeWidth:2,strokeLinecap:"round",strokeLinejoin:"round"};/**
 * @license lucide-react v0.562.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const py=yl.forwardRef(({color:E="currentColor",size:q=24,strokeWidth:B=2,absoluteStrokeWidth:m,className:G="",children:C,iconNode:el,...ol},N)=>yl.createElement("svg",{ref:N,...xy,width:q,height:q,stroke:E,strokeWidth:m?Number(B)*24/Number(q):B,className:Ud("lucide",G),...!C&&!Sy(ol)&&{"aria-hidden":"true"},...ol},[...el.map(([z,L])=>yl.createElement(z,L)),...Array.isArray(C)?C:[C]]));/**
 * @license lucide-react v0.562.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Kl=(E,q)=>{const B=yl.forwardRef(({className:m,...G},C)=>yl.createElement(py,{ref:C,iconNode:q,className:Ud(`lucide-${gy(Nd(E))}`,`lucide-${E}`,m),...G}));return B.displayName=Nd(E),B};/**
 * @license lucide-react v0.562.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const zy=[["path",{d:"M17 7 7 17",key:"15tmo1"}],["path",{d:"M17 17H7V7",key:"1org7z"}]],Md=Kl("arrow-down-left",zy);/**
 * @license lucide-react v0.562.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Ty=[["path",{d:"M7 7h10v10",key:"1tivn9"}],["path",{d:"M7 17 17 7",key:"1vkiza"}]],Od=Kl("arrow-up-right",Ty);/**
 * @license lucide-react v0.562.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Ey=[["path",{d:"M8 2v4",key:"1cmpym"}],["path",{d:"M16 2v4",key:"4m81vk"}],["rect",{width:"18",height:"18",x:"3",y:"4",rx:"2",key:"1hopcy"}],["path",{d:"M3 10h18",key:"8toen8"}]],Ay=Kl("calendar",Ey);/**
 * @license lucide-react v0.562.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const _y=[["path",{d:"m15 18-6-6 6-6",key:"1wnfg3"}]],Ny=Kl("chevron-left",_y);/**
 * @license lucide-react v0.562.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const My=[["path",{d:"m9 18 6-6-6-6",key:"mthhwq"}]],Oy=Kl("chevron-right",My);/**
 * @license lucide-react v0.562.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Dy=[["circle",{cx:"12",cy:"12",r:"10",key:"1mglay"}],["line",{x1:"12",x2:"12",y1:"8",y2:"12",key:"1pkeuh"}],["line",{x1:"12",x2:"12.01",y1:"16",y2:"16",key:"4dfq90"}]],Hd=Kl("circle-alert",Dy);/**
 * @license lucide-react v0.562.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const jy=[["circle",{cx:"12",cy:"12",r:"10",key:"1mglay"}],["path",{d:"m9 12 2 2 4-4",key:"dzmm74"}]],Dd=Kl("circle-check",jy);/**
 * @license lucide-react v0.562.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Uy=[["circle",{cx:"12",cy:"12",r:"10",key:"1mglay"}],["path",{d:"M8 12h8",key:"1wcyev"}],["path",{d:"M12 8v8",key:"napkw2"}]],Hy=Kl("circle-plus",Uy);/**
 * @license lucide-react v0.562.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Cy=[["path",{d:"M10.733 5.076a10.744 10.744 0 0 1 11.205 6.575 1 1 0 0 1 0 .696 10.747 10.747 0 0 1-1.444 2.49",key:"ct8e1f"}],["path",{d:"M14.084 14.158a3 3 0 0 1-4.242-4.242",key:"151rxh"}],["path",{d:"M17.479 17.499a10.75 10.75 0 0 1-15.417-5.151 1 1 0 0 1 0-.696 10.75 10.75 0 0 1 4.446-5.143",key:"13bj9a"}],["path",{d:"m2 2 20 20",key:"1ooewy"}]],Ry=Kl("eye-off",Cy);/**
 * @license lucide-react v0.562.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const qy=[["path",{d:"M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0",key:"1nclc0"}],["circle",{cx:"12",cy:"12",r:"3",key:"1v7zrd"}]],By=Kl("eye",qy);/**
 * @license lucide-react v0.562.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Yy=[["path",{d:"M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8",key:"1357e3"}],["path",{d:"M3 3v5h5",key:"1xhq8a"}],["path",{d:"M12 7v5l4 2",key:"1fdv2h"}]],Gy=Kl("history",Yy);/**
 * @license lucide-react v0.562.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Xy=[["path",{d:"M21 12a9 9 0 1 1-6.219-8.56",key:"13zald"}]],Qn=Kl("loader-circle",Xy);/**
 * @license lucide-react v0.562.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Qy=[["rect",{width:"18",height:"11",x:"3",y:"11",rx:"2",ry:"2",key:"1w4ew1"}],["path",{d:"M7 11V7a5 5 0 0 1 10 0v4",key:"fwvmzm"}]],Zy=Kl("lock",Qy);/**
 * @license lucide-react v0.562.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Ly=[["path",{d:"m16 17 5-5-5-5",key:"1bji2h"}],["path",{d:"M21 12H9",key:"dn1m92"}],["path",{d:"M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4",key:"1uf3rs"}]],Vy=Kl("log-out",Ly);/**
 * @license lucide-react v0.562.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Ky=[["path",{d:"M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2",key:"975kel"}],["circle",{cx:"12",cy:"7",r:"4",key:"17ys0d"}]],Jy=Kl("user",Ky);const wy=[["path",{d:"M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1",key:"18etb6"}],["path",{d:"M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4",key:"xoc0q4"}]],Cd=Kl("wallet",wy);/**
 * @license lucide-react v0.562.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
// ============================================================================
// Group Finance - React 19 Frontend Application
// ============================================================================

const React = yl;
const ReactDOM = hy;
const { useState, useEffect, useCallback, useMemo, useRef, Fragment } = React;
const h = React.createElement;
const rf = window.__API_URL__ || "/api";

// ============================================================================
// Custom High-Aesthetic SVG Icons
// ============================================================================

const GoogleIcon = ({ size = 18, className = "" }) => h("svg", {
  viewBox: "0 0 24 24",
  width: size,
  height: size,
  className: `inline-block shrink-0 ${className}`
},
  h("path", { fill: "#4285F4", d: "M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" }),
  h("path", { fill: "#34A853", d: "M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" }),
  h("path", { fill: "#FBBC05", d: "M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" }),
  h("path", { fill: "#EA4335", d: "M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" })
);

const DatabaseIcon = ({ size = 18, className = "" }) => h("svg", {
  xmlns: "http://www.w3.org/2000/svg",
  width: size,
  height: size,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 2,
  strokeLinecap: "round",
  strokeLinejoin: "round",
  className: `inline-block shrink-0 ${className}`
},
  h("ellipse", { cx: "12", cy: "5", rx: "9", ry: "3" }),
  h("path", { d: "M3 5V19A9 3 0 0 0 21 19V5" }),
  h("path", { d: "M3 12A9 3 0 0 0 21 12" })
);

const SearchIcon = ({ size = 18, className = "" }) => h("svg", {
  xmlns: "http://www.w3.org/2000/svg",
  width: size,
  height: size,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 2,
  strokeLinecap: "round",
  strokeLinejoin: "round",
  className: `inline-block shrink-0 ${className}`
},
  h("circle", { cx: "11", cy: "11", r: "8" }),
  h("path", { d: "m21 21-4.3-4.3" })
);

const RefreshIcon = ({ size = 18, className = "" }) => h("svg", {
  xmlns: "http://www.w3.org/2000/svg",
  width: size,
  height: size,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 2,
  strokeLinecap: "round",
  strokeLinejoin: "round",
  className: `inline-block shrink-0 ${className}`
},
  h("path", { d: "M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8" }),
  h("path", { d: "M21 3v5h-5" }),
  h("path", { d: "M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16" }),
  h("path", { d: "M8 16H3v5" })
);

const EditIcon = ({ size = 16, className = "" }) => h("svg", {
  xmlns: "http://www.w3.org/2000/svg",
  width: size,
  height: size,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 2,
  strokeLinecap: "round",
  strokeLinejoin: "round",
  className: `inline-block shrink-0 ${className}`
},
  h("path", { d: "M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z" }),
  h("path", { d: "m15 5 4 4" })
);

const TrashIcon = ({ size = 16, className = "" }) => h("svg", {
  xmlns: "http://www.w3.org/2000/svg",
  width: size,
  height: size,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 2,
  strokeLinecap: "round",
  strokeLinejoin: "round",
  className: `inline-block shrink-0 ${className}`
},
  h("path", { d: "M3 6h18" }),
  h("path", { d: "M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" }),
  h("path", { d: "M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" }),
  h("line", { x1: "10", x2: "10", y1: "11", y2: "17" }),
  h("line", { x1: "14", x2: "14", y1: "11", y2: "17" })
);

const XIcon = ({ size = 18, className = "" }) => h("svg", {
  xmlns: "http://www.w3.org/2000/svg",
  width: size,
  height: size,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 2,
  strokeLinecap: "round",
  strokeLinejoin: "round",
  className: `inline-block shrink-0 ${className}`
},
  h("path", { d: "M18 6 6 18" }),
  h("path", { d: "m6 6 12 12" })
);

const CheckCircleIcon = ({ size = 18, className = "" }) => h("svg", {
  xmlns: "http://www.w3.org/2000/svg",
  width: size,
  height: size,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 2,
  strokeLinecap: "round",
  strokeLinejoin: "round",
  className: `inline-block shrink-0 ${className}`
},
  h("circle", { cx: "12", cy: "12", r: "10" }),
  h("path", { d: "m9 12 2 2 4-4" })
);

const AlertTriangleIcon = ({ size = 18, className = "" }) => h("svg", {
  xmlns: "http://www.w3.org/2000/svg",
  width: size,
  height: size,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 2,
  strokeLinecap: "round",
  strokeLinejoin: "round",
  className: `inline-block shrink-0 ${className}`
},
  h("path", { d: "m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" }),
  h("line", { x1: "12", x2: "12", y1: "9", y2: "13" }),
  h("line", { x1: "12", x2: "12.01", y1: "17", y2: "17" })
);

const LockIcon = ({ size = 16, className = "" }) => h("svg", {
  xmlns: "http://www.w3.org/2000/svg",
  width: size,
  height: size,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 2,
  strokeLinecap: "round",
  strokeLinejoin: "round",
  className: `inline-block shrink-0 ${className}`
},
  h("rect", { width: "18", height: "11", x: "3", y: "11", rx: "2", ry: "2" }),
  h("path", { d: "M7 11V7a5 5 0 0 1 10 0v4" })
);

const ShieldCheckIcon = ({ size = 18, className = "" }) => h("svg", {
  xmlns: "http://www.w3.org/2000/svg",
  width: size,
  height: size,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 2,
  strokeLinecap: "round",
  strokeLinejoin: "round",
  className: `inline-block shrink-0 ${className}`
},
  h("path", { d: "M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z" }),
  h("path", { d: "m9 12 2 2 4-4" })
);

const BookletIcon = ({ size = 18, className = "" }) => h("svg", {
  xmlns: "http://www.w3.org/2000/svg",
  width: size,
  height: size,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 2,
  strokeLinecap: "round",
  strokeLinejoin: "round",
  className: `inline-block shrink-0 ${className}`
},
  h("path", { d: "M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z" }),
  h("path", { d: "M6 6h10" }),
  h("path", { d: "M6 10h10" })
);

const ArrowUpRightIcon = ({ size = 16, className = "" }) => h("svg", {
  xmlns: "http://www.w3.org/2000/svg",
  width: size,
  height: size,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 2,
  strokeLinecap: "round",
  strokeLinejoin: "round",
  className: `inline-block shrink-0 ${className}`
},
  h("path", { d: "M7 7h10v10" }),
  h("path", { d: "M7 17 17 7" })
);

const ArrowDownLeftIcon = ({ size = 16, className = "" }) => h("svg", {
  xmlns: "http://www.w3.org/2000/svg",
  width: size,
  height: size,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 2,
  strokeLinecap: "round",
  strokeLinejoin: "round",
  className: `inline-block shrink-0 ${className}`
},
  h("path", { d: "M17 7 7 17" }),
  h("path", { d: "M17 17H7V7" })
);

const PlusIcon = ({ size = 16, className = "" }) => h("svg", {
  xmlns: "http://www.w3.org/2000/svg",
  width: size,
  height: size,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 2,
  strokeLinecap: "round",
  strokeLinejoin: "round",
  className: `inline-block shrink-0 ${className}`
},
  h("path", { d: "M5 12h14" }),
  h("path", { d: "M12 5v14" })
);

const PrinterIcon = ({ size = 16, className = "" }) => h("svg", {
  xmlns: "http://www.w3.org/2000/svg",
  width: size,
  height: size,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 2,
  strokeLinecap: "round",
  strokeLinejoin: "round",
  className: `inline-block shrink-0 ${className}`
},
  h("path", { d: "M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2" }),
  h("path", { d: "M6 9V3a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v6" }),
  h("rect", { x: "6", y: "14", width: "12", height: "8", rx: "1" })
);

// ============================================================================
// Default Presets, Accounts, Booklet Metadata & Initial 2026 Ledger Seed
// ============================================================================

const DEFAULT_INCOME_ITEMS = [
  "小组聚会（教会）",
  "小组",
  "特别奉献",
  "主日学",
  "爱宴奉献"
];

const DEFAULT_EXPENSE_ITEMS = [
  "转回给教会",
  "白金",
  "生日蛋糕一月",
  "生日二月",
  "慧芬婚礼",
  "生日蛋糕四月",
  "5月生日",
  "惠芬住院水果",
  "转教会",
  "小组茶点",
  "小组布道会",
  "9月生日",
  "杂支"
];

const DEFAULT_BOOKLET_SETTINGS = {
  group_code: "YA5",
  counters: "Rivaldo, Brendon",
  verify_by: "Brendon",
  verify_name: "Rivaldo",
  opening_balance: 693
};

const DEFAULT_USER_ACCOUNTS = [
  { email: "hengga1007@gmail.com", name: "Brendon", role: "admin" },
  { email: "ejenrivaldo5011@gmail.com", name: "Rivaldo", role: "user" }
];

const INITIAL_SEED_TRANSACTIONS = [
  { id: "seed-2026-01-14", date: "2026-01-14", year: 2026, month: 1, item: "小组聚会（教会）", income: 167, expense: 0, user: "Brendon" },
  { id: "seed-2026-01-16", date: "2026-01-16", year: 2026, month: 1, item: "转回给教会", income: 0, expense: 400, user: "Brendon" },
  { id: "seed-2026-01-17", date: "2026-01-17", year: 2026, month: 1, item: "白金", income: 0, expense: 50, user: "Brendon" },
  { id: "seed-2026-01-21", date: "2026-01-21", year: 2026, month: 1, item: "小组", income: 89, expense: 0, user: "Rivaldo" },
  { id: "seed-2026-01-28", date: "2026-01-28", year: 2026, month: 1, item: "生日蛋糕一月", income: 0, expense: 98, user: "Brendon" },
  { id: "seed-2026-01-29", date: "2026-01-29", year: 2026, month: 1, item: "小组", income: 111, expense: 0, user: "Rivaldo" },
  { id: "seed-2026-02-11", date: "2026-02-11", year: 2026, month: 2, item: "小组", income: 40, expense: 0, user: "Rivaldo" },
  { id: "seed-2026-02-25", date: "2026-02-25", year: 2026, month: 2, item: "生日二月", income: 0, expense: 100, user: "Brendon" },
  { id: "seed-2026-03-11", date: "2026-03-11", year: 2026, month: 3, item: "小组", income: 98, expense: 0, user: "Rivaldo" },
  { id: "seed-2026-03-18", date: "2026-03-18", year: 2026, month: 3, item: "小组", income: 98, expense: 0, user: "Rivaldo" },
  { id: "seed-2026-03-22", date: "2026-03-22", year: 2026, month: 3, item: "慧芬婚礼", income: 0, expense: 50, user: "Brendon" },
  { id: "seed-2026-04-22", date: "2026-04-22", year: 2026, month: 4, item: "小组聚会（教会）", income: 100, expense: 0, user: "Brendon" },
  { id: "seed-2026-04-29", date: "2026-04-29", year: 2026, month: 4, item: "生日蛋糕四月", income: 0, expense: 88, user: "Brendon" },
  { id: "seed-2026-05-13", date: "2026-05-13", year: 2026, month: 5, item: "小组", income: 60, expense: 0, user: "Rivaldo" },
  { id: "seed-2026-05-14", date: "2026-05-14", year: 2026, month: 5, item: "5月生日", income: 0, expense: 100, user: "Brendon" },
  { id: "seed-2026-05-28", date: "2026-05-28", year: 2026, month: 5, item: "小组", income: 90, expense: 0, user: "Rivaldo" },
  { id: "seed-2026-06-10", date: "2026-06-10", year: 2026, month: 6, item: "小组", income: 100, expense: 0, user: "Rivaldo" },
  { id: "seed-2026-06-24", date: "2026-06-24", year: 2026, month: 6, item: "惠芬住院水果", income: 0, expense: 50, user: "Brendon" },
  { id: "seed-2026-07-08", date: "2026-07-08", year: 2026, month: 7, item: "小组", income: 150, expense: 0, user: "Rivaldo" },
  { id: "seed-2026-07-15", date: "2026-07-15", year: 2026, month: 7, item: "转教会", income: 0, expense: 450, user: "Brendon" },
  { id: "seed-2026-07-22", date: "2026-07-22", year: 2026, month: 7, item: "小组", income: 88, expense: 0, user: "Rivaldo" },
  { id: "seed-2026-08-13", date: "2026-08-13", year: 2026, month: 8, item: "小组", income: 90, expense: 0, user: "Rivaldo" },
  { id: "seed-2026-09-07", date: "2026-09-07", year: 2026, month: 9, item: "小组茶点", income: 0, expense: 50, user: "Brendon" },
  { id: "seed-2026-09-09", date: "2026-09-09", year: 2026, month: 9, item: "小组", income: 120, expense: 0, user: "Rivaldo" },
  { id: "seed-2026-09-16", date: "2026-09-16", year: 2026, month: 9, item: "小组布道会", income: 0, expense: 250, user: "Brendon" },
  { id: "seed-2026-09-30", date: "2026-09-30", year: 2026, month: 9, item: "9月生日", income: 0, expense: 89, user: "Brendon" }
];

// --- API Client ---
async function apiPost(action, payload = {}) {
  const token = localStorage.getItem("sessionToken") || localStorage.getItem("authToken");
  const headers = { "Content-Type": "application/json" };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  const body = { action, ...payload };
  const res = await fetch(rf, {
    method: "POST",
    headers,
    body: JSON.stringify(body)
  });
  const data = await res.json().catch(() => ({}));
  if (res.status === 401 && !AUTH_EXEMPT_ACTIONS.has(action) && typeof onSessionExpired === "function") {
    onSessionExpired();
  }
  return { ok: res.ok, status: res.status, data };
}

// Server answered 401 for a signed-in action: the app registers a handler that signs the user out.
const AUTH_EXEMPT_ACTIONS = new Set(["login", "google_login", "logout", "status", "get_settings"]);
let onSessionExpired = null;

// Server refusals (401/403/400/5xx) must not be treated as success. A thrown fetch error (network) is not a refusal.
function refusalMessage(res) {
  if (!res || res.ok) return null;
  if (res.status === 401) return "登录已过期，请重新登录";
  return (res.data && res.data.message) || "操作未能完成，请稍后重试";
}

// --- Normalize Date & Month Helper ---
function normalizeTx(tx, idx = 0) {
  let rawDate = tx.date ? String(tx.date).split("T")[0] : "";
  let year = parseInt(tx.year, 10) || 2026;
  let month = parseInt(tx.month, 10) || 1;
  if (/^\d{4}-\d{2}-\d{2}$/.test(rawDate)) {
    const parts = rawDate.split("-");
    year = parseInt(parts[0], 10);
    month = parseInt(parts[1], 10);
  } else if (/^\d{2}-\d{2}$/.test(rawDate)) {
    const parts = rawDate.split("-");
    month = parseInt(parts[0], 10);
    rawDate = `${year}-${parts[0]}-${parts[1]}`;
  }
  const shortDate = /^\d{4}-\d{2}-\d{2}$/.test(rawDate) ? rawDate.slice(5) : rawDate;
  return {
    ...tx,
    id: tx.id || `tx-${rawDate}-${tx.item || ""}-${idx}`,
    date: rawDate,
    shortDate,
    year,
    month,
    item: tx.item || "",
    income: parseFloat(tx.income || 0),
    expense: parseFloat(tx.expense || 0),
    user: tx.user || "Brendon"
  };
}

// --- Compute Monthly & Yearly Ledger with Balance b/f ---
function computeYearLedger(rawTransactions, year = 2026, initialOpeningBf = 693) {
  const normalized = (rawTransactions || [])
    .map((t, i) => normalizeTx(t, i))
    .filter((t) => t.year === Number(year) && String(t.item).toLowerCase() !== "balance b/f")
    .sort((a, b) => String(a.date).localeCompare(String(b.date)) || String(a.id).localeCompare(String(b.id)));

  const monthsMap = {};
  let runningBf = Number(initialOpeningBf) || 0;

  for (let m = 1; m <= 12; m++) {
    const monthTxs = normalized.filter((t) => t.month === m);
    const openingBf = runningBf;
    let currentBal = openingBf;
    let monthNewIncome = 0;
    let monthExpense = 0;

    const rowsWithBalance = monthTxs.map((t) => {
      const inc = parseFloat(t.income || 0);
      const exp = parseFloat(t.expense || 0);
      monthNewIncome += inc;
      monthExpense += exp;
      currentBal = Number((currentBal + inc - exp).toFixed(2));
      return {
        ...t,
        balance: currentBal
      };
    });

    monthsMap[m] = {
      month: m,
      year: Number(year),
      openingBf: Number(openingBf.toFixed(2)),
      newIncome: Number(monthNewIncome.toFixed(2)),
      totalIncomeWithBf: Number((openingBf + monthNewIncome).toFixed(2)),
      totalExpense: Number(monthExpense.toFixed(2)),
      closingBalance: Number(currentBal.toFixed(2)),
      rows: rowsWithBalance
    };

    runningBf = currentBal;
  }

  // Also compute full-year chronological rows with single opening Balance b/f
  let yearBal = Number(initialOpeningBf) || 0;
  let yearNewIncome = 0;
  let yearExpense = 0;
  const allRowsWithBalance = normalized.map((t) => {
    const inc = parseFloat(t.income || 0);
    const exp = parseFloat(t.expense || 0);
    yearNewIncome += inc;
    yearExpense += exp;
    yearBal = Number((yearBal + inc - exp).toFixed(2));
    return {
      ...t,
      balance: yearBal
    };
  });

  return {
    year: Number(year),
    initialOpeningBf: Number(initialOpeningBf) || 0,
    yearNewIncome: Number(yearNewIncome.toFixed(2)),
    yearTotalIncomeWithBf: Number(((Number(initialOpeningBf) || 0) + yearNewIncome).toFixed(2)),
    yearTotalExpense: Number(yearExpense.toFixed(2)),
    yearClosingBalance: Number(yearBal.toFixed(2)),
    monthsMap,
    allRows: allRowsWithBalance
  };
}

// ============================================================================
// Notification Toast (Disabled per user preference)
// ============================================================================
function ToastBanner() {
  return null;
}

// ============================================================================
// Unified Top Banner Navigation (AppHeader)
// ============================================================================
function AppHeader({
  currentUser,
  canViewDatabase,
  activeTab,
  onNavigateTab,
  onLogout,
  bookletSettings
}) {
  const groupCode = bookletSettings?.group_code || "YA5";

  return h("header", {
    className: "w-full bg-white/90 backdrop-blur-md border-b border-slate-200/80 sticky top-0 z-40 shadow-xs no-print print:hidden"
  },
    h("div", { className: "max-w-7xl mx-auto px-4 py-3 flex flex-wrap items-center justify-between gap-3" },
      // Left: Brand Icon & Title Only
      h("div", { className: "flex items-center gap-3" },
        h("div", {
          onClick: () => onNavigateTab("entry"),
          className: "w-10 h-10 rounded-2xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-blue-700 text-white flex items-center justify-center shadow-md shadow-blue-500/20 cursor-pointer shrink-0"
        },
          h(Cd, { size: 20 })
        ),
        h("span", { className: "font-black text-slate-900 text-base tracking-tight" }, "小组财务系统")
      ),

      // Center: Unified Pill Navigation Bar (Determined by Login Permission: Admin sees 3 buttons, User sees only Record Entry)
      h("nav", {
        className: "flex items-center bg-slate-100/90 p-1.5 rounded-2xl border border-slate-200/80 gap-1.5 shadow-inner"
      },
        // 1. 📝 记账录入 (Accessible by User & Admin)
        h("button", {
          type: "button",
          onClick: () => onNavigateTab("entry"),
          className: `px-4 py-2 rounded-xl text-xs sm:text-sm font-bold transition-all flex items-center gap-1.5 ${
            activeTab === "entry"
              ? "bg-indigo-600 text-white shadow-sm shadow-indigo-500/20"
              : "text-slate-600 hover:text-slate-900 hover:bg-white/70"
          }`
        },
          h("span", null, "📝 记账录入")
        ),

        // 2. 🗄️ 数据库管理 (Admin ONLY)
        canViewDatabase && h("button", {
          type: "button",
          onClick: () => onNavigateTab("database-view"),
          className: `px-4 py-2 rounded-xl text-xs sm:text-sm font-bold transition-all flex items-center gap-1.5 ${
            activeTab === "database-view"
              ? "bg-indigo-600 text-white shadow-sm shadow-indigo-500/20"
              : "text-slate-600 hover:text-slate-900 hover:bg-white/70"
          }`
        },
          h("span", null, "🗄️ 数据库管理")
        ),

        // 3. 📖 奉献记录全册 (User Read-Only / Admin Full)
        h("button", {
          type: "button",
          onClick: () => onNavigateTab("booklet"),
          className: `px-4 py-2 rounded-xl text-xs sm:text-sm font-bold transition-all flex items-center gap-1.5 ${
            activeTab === "booklet"
              ? "bg-indigo-600 text-white shadow-sm shadow-indigo-500/20"
              : "text-slate-600 hover:text-slate-900 hover:bg-white/70"
          }`
        },
          h("span", null, "📖 奉献记录全册")
        )
      ),

      // Right: Logged-in User Email (No Role Label) & Logout Button
      h("div", { className: "flex items-center flex-wrap gap-2.5" },
        h("div", {
          className: "inline-flex items-center gap-2 px-3.5 py-2 bg-slate-50 text-slate-700 rounded-xl text-xs font-semibold border border-slate-200/80"
        },
          h(Jy, { size: 15, className: "text-indigo-600 shrink-0" }),
          h("span", { className: "truncate max-w-[220px]" }, currentUser?.email || "user@group.finance.com")
        ),

        // Logout Button
        h("button", {
          type: "button",
          onClick: onLogout,
          className: "inline-flex items-center gap-1.5 px-3.5 py-2 bg-white hover:bg-rose-50 text-slate-600 hover:text-rose-600 border border-slate-200 hover:border-rose-200 rounded-xl text-xs font-bold transition-all shadow-2xs active:scale-95",
          title: "退出当前登录并返回登录页"
        },
          h(Vy, { size: 14 }),
          h("span", null, "🚪 退出")
        )
      )
    )
  );
}

// ============================================================================
// Official 4-Color Google "G" Logo SVG
// ============================================================================
function GoogleLogoSvg({ size = 18 }) {
  return h("svg", {
    width: size,
    height: size,
    viewBox: "0 0 24 24",
    xmlns: "http://www.w3.org/2000/svg",
    className: "shrink-0"
  },
    h("path", {
      d: "M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z",
      fill: "#4285F4"
    }),
    h("path", {
      d: "M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z",
      fill: "#34A853"
    }),
    h("path", {
      d: "M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z",
      fill: "#FBBC05"
    }),
    h("path", {
      d: "M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z",
      fill: "#EA4335"
    })
  );
}

// ============================================================================
// Full-Page Login Screen (Silently verifies account access in background)
// ============================================================================
const OAUTH_ERROR_MESSAGES = {
  google_oauth_not_configured: "Google OAuth 尚未配置 GOOGLE_CLIENT_ID，请联系管理员或在后台配置 OAuth Client ID。",
  email_not_verified: "该 Google 账号的邮箱尚未验证，请先在 Google 完成邮箱验证后再登录。",
  account_disabled: "该账号已被停用，请联系管理员。",
  not_registered: "该邮箱尚未被授权使用本系统，请联系管理员开通账号。"
};
function describeOauthError(code) {
  return OAUTH_ERROR_MESSAGES[code] || code;
}

function LoginScreen({ onLoginSuccess, userAccounts, googleClientId, initialError }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(() => {
    if (!initialError) return null;
    return describeOauthError(initialError);
  });
  const googleBtnContainerRef = useRef(null);

  useEffect(() => {
    if (initialError) {
      setError(describeOauthError(initialError));
    }
  }, [initialError]);

  // Redirect directly to Backend Google OAuth 2.0 Authorization Code Flow (accounts.google.com)
  const handleGoogleOAuthLogin = () => {
    setLoading(true);
    setError(null);
    const targetState = window.location.pathname + window.location.search;
    window.location.href = `/auth/google/login?state=${encodeURIComponent(targetState)}`;
  };

  return h("div", {
    className: "min-h-screen bg-slate-50 flex flex-col items-center justify-center p-4 relative overflow-hidden"
  },
    // Ambient Background Blurs
    h("div", { className: "fixed top-0 left-0 w-full h-full overflow-hidden pointer-events-none -z-10" },
      h("div", { className: "absolute top-[-5%] left-[-5%] w-96 h-96 bg-blue-500/10 rounded-full blur-3xl" }),
      h("div", { className: "absolute bottom-[-5%] right-[-5%] w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl" })
    ),

    h("div", {
      className: "w-full max-w-lg bg-white/95 backdrop-blur-xl rounded-3xl shadow-2xl shadow-slate-200/70 border border-slate-200/80 p-6 sm:p-9 animate-in fade-in zoom-in-95 duration-200"
    },
      // Brand Header
      h("div", { className: "text-center mb-6" },
        h("div", {
          className: "w-14 h-14 rounded-2xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-blue-700 text-white flex items-center justify-center shadow-lg shadow-indigo-500/25 mx-auto mb-3.5"
        },
          h(Cd, { size: 26 })
        ),
        h("div", { className: "flex items-center justify-center gap-2 mb-1" },
          h("h1", { className: "text-2xl font-black text-slate-900 tracking-tight" }, "小组财务系统")
        ),
        h("p", { className: "text-xs text-slate-500 font-medium" },
          "请使用 Google 账号登录系统"
        )
      ),

      error && h("div", {
        className: "mb-5 p-3.5 bg-rose-50 border border-rose-200 rounded-2xl text-xs text-rose-700 font-semibold flex items-center gap-2"
      },
        h(AlertTriangleIcon, { size: 16 }),
        h("span", null, error)
      ),

      // Primary Action: Google Account Sign-In (Single Button)
      h("div", { className: "space-y-3" },
        h("button", {
          type: "button",
          disabled: loading,
          onClick: handleGoogleOAuthLogin,
          className: "w-full py-3.5 px-5 bg-white hover:bg-slate-50 text-slate-800 font-bold text-sm rounded-2xl border-2 border-slate-200 hover:border-indigo-300 shadow-sm hover:shadow-md transition-all flex items-center justify-center gap-3 active:scale-[0.99] disabled:opacity-50"
        },
          h(GoogleLogoSvg, { size: 20 }),
          h("span", null, "使用 Google 账号登录 (Sign in with Google)")
        )
      )
    )
  );
}

// ============================================================================
// Module 1: 📝 记账录入 (Transaction Entry View - Accessible by User & Admin)
// ============================================================================
function RecordEntryTab({
  currentUser,
  incomeItems,
  expenseItems,
  onRecordAdded,
  recentTransactions
}) {
  const todayStr = new Date().toISOString().split("T")[0];
  const [entryType, setEntryType] = useState("income"); // "income" | "expense"
  const [formData, setFormData] = useState({
    date: todayStr,
    item: "",
    income: "",
    expense: ""
  });
  const [loading, setLoading] = useState(false);
  const [statusMsg, setStatusMsg] = useState({ type: null, text: "" });
  const [localLogs, setLocalLogs] = useState([]);
  const incomeInputRef = useRef(null);
  const expenseInputRef = useRef(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSelectPresetIncome = (itemName) => {
    setEntryType("income");
    setFormData((prev) => ({ ...prev, item: itemName, expense: "" }));
    setTimeout(() => incomeInputRef.current?.focus(), 20);
  };

  const handleSelectPresetExpense = (itemName) => {
    setEntryType("expense");
    setFormData((prev) => ({ ...prev, item: itemName, income: "" }));
    setTimeout(() => expenseInputRef.current?.focus(), 20);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const incVal = parseFloat(formData.income) || 0;
    const expVal = parseFloat(formData.expense) || 0;

    if (incVal > 0 && expVal > 0) {
      setStatusMsg({ type: "error", text: "错误：单笔记录的收入和支出不能同时大于 0，请分开录入。" });
      return;
    }
    if (!formData.item.trim() || (incVal === 0 && expVal === 0)) {
      setStatusMsg({ type: "error", text: "错误：请填写事项说明并输入大于 0 的收入或支出金额。" });
      return;
    }

    setLoading(true);
    setStatusMsg({ type: null, text: "" });

    const newEntry = {
      id: `tx-${Date.now()}`,
      date: formData.date,
      item: formData.item.trim(),
      income: incVal,
      expense: expVal,
      user: currentUser?.name || currentUser?.email || "同工"
    };

    try {
      const res = await apiPost("add_record", {
        date: newEntry.date,
        item: newEntry.item,
        income: newEntry.income,
        expense: newEntry.expense,
        user: newEntry.user
      });
      const refusal = refusalMessage(res);
      if (refusal) {
        setStatusMsg({ type: "error", text: `⚠️ ${refusal}` });
        setLoading(false);
        return;
      }
      if (res && res.ok && res.data) {
        if (res.data.id) {
          newEntry.id = res.data.id;
        } else if (res.data.transaction && res.data.transaction.id) {
          newEntry.id = res.data.transaction.id;
        }
      }
    } catch {
      // Proceed with local state synchronization even if offline (network exception only)
    } finally {
      setLoading(false);
    }

    setLocalLogs((prev) => [newEntry, ...prev.slice(0, 5)]);
    setStatusMsg({ type: "success", text: "✅ 记录已成功保存！数据已实时同步" });
    onRecordAdded(newEntry, "✅ 记录已成功保存！数据已实时同步");
    setFormData({ date: todayStr, item: "", income: "", expense: "" });
  };

  const displayLogs = localLogs.length > 0 ? localLogs : (recentTransactions || []).slice(0, 5);

  return h("div", { className: "max-w-2xl mx-auto space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-300" },
    // Entry Form Card
    h("div", { className: "bg-white/95 backdrop-blur-md rounded-3xl shadow-xl shadow-slate-200/50 border border-slate-200/70 p-6 sm:p-8" },
      // Card Header
      h("div", { className: "flex flex-wrap items-center justify-between gap-3 mb-6 pb-4 border-b border-slate-100" },
        h("div", { className: "flex items-center gap-3" },
          h("div", { className: "w-11 h-11 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold text-xl shadow-2xs" },
            "📝"
          ),
          h("div", null,
            h("h2", { className: "text-base sm:text-lg font-black text-slate-800" }, "新增奉献 / 支出记录 (记账录入)"),
            h("p", { className: "text-xs text-slate-500 mt-0.5" }, "录入后自动计算结存并实时同步至收支流水总账与每月奉献记录")
          )
        ),
        h("div", { className: "px-3 py-1.5 rounded-xl bg-slate-100 border border-slate-200/80 text-xs font-semibold text-slate-600" },
          `经手人: ${currentUser?.name || "同工"} (${currentUser?.email || "user@group.finance.com"})`
        )
      ),

      h("form", { onSubmit: handleSubmit, className: "space-y-5" },
        // Date Input
        h("div", null,
          h("label", { className: "block text-xs font-bold text-slate-600 uppercase tracking-wider mb-1.5 ml-1" },
            "日期 Date"
          ),
          h("input", {
            type: "date",
            name: "date",
            required: true,
            value: formData.date,
            onChange: handleChange,
            className: "w-full px-4 py-3 bg-slate-50/70 border border-slate-200 rounded-2xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none transition-all font-medium text-slate-800"
          })
        ),

        // Item Input + Preset Category Dropdown & Quick-Select Chips
        h("div", { className: "space-y-3" },
          h("div", { className: "flex flex-wrap items-center justify-between gap-2" },
            h("label", { className: "block text-xs font-bold text-slate-600 uppercase tracking-wider ml-1" },
              "事项说明 Item Description"
            ),
            // Preset Category Dropdown Selector
            h("select", {
              value: "",
              onChange: (e) => {
                const val = e.target.value;
                if (!val) return;
                const [type, name] = val.split("::");
                if (type === "inc") handleSelectPresetIncome(name);
                else handleSelectPresetExpense(name);
              },
              className: "px-3 py-1.5 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 rounded-xl text-xs font-bold outline-none cursor-pointer transition-colors"
            },
              h("option", { value: "" }, "📂 从预设事项分类快速选择..."),
              h("optgroup", { label: "🟢 收入事项分类 (Preset Income Items)" },
                (incomeItems || DEFAULT_INCOME_ITEMS).map((item) =>
                  h("option", { key: `inc-${item}`, value: `inc::${item}` }, `🟢 [收入] ${item}`)
                )
              ),
              h("optgroup", { label: "🔴 支出事项分类 (Preset Expense Items)" },
                (expenseItems || DEFAULT_EXPENSE_ITEMS).map((item) =>
                  h("option", { key: `exp-${item}`, value: `exp::${item}` }, `🔴 [支出] ${item}`)
                )
              )
            )
          ),

          h("input", {
            type: "text",
            name: "item",
            list: "item-suggestions",
            required: true,
            placeholder: "点击下方分类标签或直接输入事项，例如：小组聚会（教会）、转回给教会...",
            value: formData.item,
            onChange: handleChange,
            className: "w-full px-4 py-3 bg-slate-50/70 border border-slate-200 rounded-2xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none transition-all font-medium text-slate-800 placeholder:text-slate-400"
          }),

          // Preset Income Items & Expense Items Chips
          h("div", { className: "grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1" },
            // 🟢 Preset Income Chips
            h("div", { className: "p-3 rounded-2xl bg-emerald-50/60 border border-emerald-200/70 space-y-2" },
              h("div", { className: "text-[11px] font-bold text-emerald-800 flex items-center gap-1" },
                "🟢 收入事项分类 (点击自动定位收入栏)"
              ),
              h("div", { className: "flex flex-wrap gap-1.5" },
                (incomeItems || DEFAULT_INCOME_ITEMS).map((item) =>
                  h("button", {
                    type: "button",
                    key: item,
                    onClick: () => handleSelectPresetIncome(item),
                    className: `px-2.5 py-1 text-xs rounded-lg font-bold border transition-all active:scale-95 ${
                      formData.item === item && entryType === "income"
                        ? "bg-emerald-600 text-white border-emerald-600 shadow-xs"
                        : "bg-white hover:bg-emerald-100 text-emerald-700 border-emerald-200"
                    }`
                  }, item)
                )
              )
            ),

            // 🔴 Preset Expense Chips
            h("div", { className: "p-3 rounded-2xl bg-rose-50/60 border border-rose-200/70 space-y-2" },
              h("div", { className: "text-[11px] font-bold text-rose-800 flex items-center gap-1" },
                "🔴 支出事项分类 (点击自动定位支出栏)"
              ),
              h("div", { className: "flex flex-wrap gap-1.5" },
                (expenseItems || DEFAULT_EXPENSE_ITEMS).map((item) =>
                  h("button", {
                    type: "button",
                    key: item,
                    onClick: () => handleSelectPresetExpense(item),
                    className: `px-2.5 py-1 text-xs rounded-lg font-bold border transition-all active:scale-95 ${
                      formData.item === item && entryType === "expense"
                        ? "bg-rose-600 text-white border-rose-600 shadow-xs"
                        : "bg-white hover:bg-rose-100 text-rose-700 border-rose-200"
                    }`
                  }, item)
                )
              )
            )
          )
        ),

        // Income & Expense Inputs
        h("div", { className: "grid grid-cols-1 sm:grid-cols-2 gap-4" },
          // Income
          h("div", null,
            h("label", { className: "block text-xs font-bold text-emerald-700 uppercase tracking-wider mb-1.5 ml-1 flex items-center gap-1" },
              h(ArrowUpRightIcon, { size: 14 }),
              "收入 Income (RM)"
            ),
            h("div", { className: "relative" },
              h("span", { className: "absolute left-3.5 top-1/2 -translate-y-1/2 text-xs font-bold text-emerald-600/80" }, "RM"),
              h("input", {
                ref: incomeInputRef,
                type: "number",
                step: "0.01",
                min: "0",
                name: "income",
                value: formData.income,
                onChange: (e) => {
                  setEntryType("income");
                  handleChange(e);
                },
                placeholder: "0.00",
                className: "w-full pl-11 pr-4 py-3 bg-emerald-50/40 border border-emerald-200 rounded-2xl focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 outline-none transition-all font-bold text-emerald-800 placeholder:text-emerald-700/30"
              })
            )
          ),
          // Expense
          h("div", null,
            h("label", { className: "block text-xs font-bold text-rose-700 uppercase tracking-wider mb-1.5 ml-1 flex items-center gap-1" },
              h(ArrowDownLeftIcon, { size: 14 }),
              "支出 Expense (RM)"
            ),
            h("div", { className: "relative" },
              h("span", { className: "absolute left-3.5 top-1/2 -translate-y-1/2 text-xs font-bold text-rose-600/80" }, "RM"),
              h("input", {
                ref: expenseInputRef,
                type: "number",
                step: "0.01",
                min: "0",
                name: "expense",
                value: formData.expense,
                onChange: (e) => {
                  setEntryType("expense");
                  handleChange(e);
                },
                placeholder: "0.00",
                className: "w-full pl-11 pr-4 py-3 bg-rose-50/40 border border-rose-200 rounded-2xl focus:ring-2 focus:ring-rose-500/20 focus:border-rose-500 outline-none transition-all font-bold text-rose-800 placeholder:text-rose-700/30"
              })
            )
          )
        ),

        // Submit Button
        h("button", {
          type: "submit",
          disabled: loading,
          className: "w-full py-3.5 rounded-2xl font-bold text-white shadow-lg shadow-indigo-500/25 flex items-center justify-center gap-2 bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-700 hover:from-blue-500 hover:to-indigo-500 active:scale-[0.99] transition-all disabled:opacity-60 text-sm"
        },
          loading ? h(Fragment, null,
            h(Qn, { size: 18, className: "animate-spin" }),
            h("span", null, "正在保存记录...")
          ) : h(Fragment, null,
            h(CheckCircleIcon, { size: 18 }),
            h("span", null, "确认提交并保存 (Submit Record)")
          )
        ),

        // Form feedback banner
        statusMsg.text && h("div", {
          className: `p-3 rounded-2xl text-xs font-semibold flex items-center gap-2 ${statusMsg.type === "success" ? "bg-emerald-50 text-emerald-800 border border-emerald-200" : "bg-rose-50 text-rose-800 border border-rose-200"}`
        },
          statusMsg.type === "success" ? h(CheckCircleIcon, { size: 16 }) : h(AlertTriangleIcon, { size: 16 }),
          statusMsg.text
        )
      )
    ),

    // Recent Activity Echo Card
    h("div", { className: "bg-white/90 backdrop-blur-md rounded-3xl border border-slate-200/70 shadow-sm p-6" },
      h("div", { className: "flex items-center justify-between mb-4" },
        h("div", { className: "flex items-center gap-2" },
          h(Gy, { size: 16, className: "text-indigo-600" }),
          h("h3", { className: "text-sm font-bold text-slate-800" }, "最近录入记录")
        ),
        h("span", { className: "text-[10px] text-slate-500 font-bold uppercase tracking-wider bg-slate-100 px-2.5 py-0.5 rounded-full" },
          "Recent Activity"
        )
      ),

      displayLogs.length === 0 ? h("div", { className: "text-center py-7 border-2 border-dashed border-slate-200/80 rounded-2xl" },
        h("p", { className: "text-slate-400 text-xs" }, "暂无新提交记录，上方录入后将即时在此呈现")
      ) : h("div", { className: "space-y-2.5" },
        displayLogs.map((log, idx) => {
          const dateStr = Array.isArray(log) ? log[0] : log.date;
          const itemStr = Array.isArray(log) ? log[1] : log.item;
          const incVal = Array.isArray(log) ? parseFloat(log[2] || 0) : parseFloat(log.income || 0);
          const expVal = Array.isArray(log) ? parseFloat(log[3] || 0) : parseFloat(log.expense || 0);

          return h("div", {
            key: log.id || idx,
            className: "flex items-center justify-between p-3.5 bg-slate-50/70 hover:bg-slate-50 rounded-2xl border border-slate-100 shadow-2xs transition-colors"
          },
            h("div", { className: "flex flex-col gap-0.5" },
              h("span", { className: "text-sm font-bold text-slate-800" }, itemStr),
              h("span", { className: "text-[11px] font-mono text-slate-500" }, dateStr ? String(dateStr).split("T")[0] : "-")
            ),
            h("div", { className: "text-right font-mono" },
              incVal > 0 && h("div", { className: "text-sm font-bold text-emerald-600" }, `+ RM ${incVal.toFixed(2)}`),
              expVal > 0 && h("div", { className: "text-sm font-bold text-rose-600" }, `- RM ${expVal.toFixed(2)}`)
            )
          );
        })
      )
    )
  );
}

// ============================================================================
// Module 2: 🗄️ 数据库管理 (Database Management - Admin Exclusive)
// ============================================================================
function DatabaseViewTab({
  currentUser,
  transactions,
  loadingTransactions,
  onRefreshTransactions,
  onCreateTransaction,
  onUpdateTransaction,
  onDeleteTransaction,
  incomeItems,
  expenseItems,
  onUpdateCategoryPresets,
  userAccounts,
  onUpdateUserAccounts,
  bookletSettings,
  onUpdateBookletSettings,
  googleClientId,
  onUpdateGoogleOAuth,
  showToast
}) {
  const [subTab, setSubTab] = useState("ledger"); // "ledger" | "categories" | "permissions"
  const [yearFilter, setYearFilter] = useState(() => {
    try {
      const p = new URLSearchParams(window.location.search).get("year");
      if (p) return p;
    } catch {}
    return String(new Date().getFullYear() || 2026);
  });
  const [monthFilter, setMonthFilter] = useState(() => {
    try {
      const p = new URLSearchParams(window.location.search).get("month");
      if (p) return p;
    } catch {}
    return String(new Date().getMonth() + 1);
  });
  const [searchQuery, setSearchQuery] = useState("");
  const [createItem, setCreateItem] = useState(null);
  const [editItem, setEditItem] = useState(null);
  const [deleteItem, setDeleteItem] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);

  // Sub-tab 2 state: Preset Income / Expense inputs
  const [newIncomeCategory, setNewIncomeCategory] = useState("");
  const [newExpenseCategory, setNewExpenseCategory] = useState("");

  // Sub-tab 3 state: New User Account & Booklet Settings form
  const [newUserEmail, setNewUserEmail] = useState("");
  const [newUserName, setNewUserName] = useState("");
  const [newUserRole, setNewUserRole] = useState("user");
  const [bookletForm, setBookletForm] = useState(() => ({
    group_code: bookletSettings?.group_code || "YA5",
    counters: bookletSettings?.counters || "Rivaldo, Brendon",
    verify_by: bookletSettings?.verify_by || "Brendon",
    verify_name: bookletSettings?.verify_name || "Rivaldo",
    opening_balance: bookletSettings?.opening_balance ?? 693
  }));
  const [oauthForm, setOauthForm] = useState(() => ({
    google_client_id: googleClientId || "",
    google_client_secret: ""
  }));
  const [oauthSaveStatus, setOauthSaveStatus] = useState("");

  useEffect(() => {
    if (googleClientId) {
      setOauthForm((prev) => ({ ...prev, google_client_id: googleClientId }));
    }
  }, [googleClientId]);

  useEffect(() => {
    if (bookletSettings) {
      setBookletForm({
        group_code: bookletSettings.group_code || "YA5",
        counters: bookletSettings.counters || "Rivaldo, Brendon",
        verify_by: bookletSettings.verify_by || "Brendon",
        verify_name: bookletSettings.verify_name || "Rivaldo",
        opening_balance: bookletSettings.opening_balance ?? 693
      });
    }
  }, [bookletSettings]);

  // Compute Ledger with Balance b/f
  const selectedYearNum = yearFilter === "all" ? 2026 : parseInt(yearFilter, 10) || 2026;
  const yearLedger = useMemo(() => {
    const initialBf = selectedYearNum === 2026 ? (Number(bookletSettings?.opening_balance) || 693) : 0;
    return computeYearLedger(transactions, selectedYearNum, initialBf);
  }, [transactions, selectedYearNum, bookletSettings]);

  // Determine active view metrics & rows (Month vs All Months)
  const ledgerViewData = useMemo(() => {
    let openingBf = yearLedger.initialOpeningBf;
    let newIncome = yearLedger.yearNewIncome;
    let totalIncomeWithBf = yearLedger.yearTotalIncomeWithBf;
    let totalExpense = yearLedger.yearTotalExpense;
    let closingBalance = yearLedger.yearClosingBalance;
    let baseRows = yearLedger.allRows;
    let periodLabel = `${selectedYearNum} 全年`;

    if (monthFilter !== "all") {
      const m = parseInt(monthFilter, 10);
      const mData = yearLedger.monthsMap[m];
      if (mData) {
        openingBf = mData.openingBf;
        newIncome = mData.newIncome;
        totalIncomeWithBf = mData.totalIncomeWithBf;
        totalExpense = mData.totalExpense;
        closingBalance = mData.closingBalance;
        baseRows = mData.rows;
        periodLabel = `${selectedYearNum}年 ${m}月`;
      }
    }

    // Apply keyword search filter to transaction rows
    let filteredRows = baseRows;
    if (searchQuery.trim()) {
      const q = searchQuery.trim().toLowerCase();
      filteredRows = baseRows.filter((t) =>
        (t.item && t.item.toLowerCase().includes(q)) ||
        (t.date && t.date.toLowerCase().includes(q)) ||
        (t.user && t.user.toLowerCase().includes(q))
      );
    }

    return {
      periodLabel,
      openingBf,
      newIncome,
      totalIncomeWithBf,
      totalExpense,
      closingBalance,
      rows: filteredRows
    };
  }, [yearLedger, monthFilter, searchQuery, selectedYearNum]);

  // Handle Create Save
  const handleSaveCreate = async (e) => {
    e.preventDefault();
    if (!createItem) return;
    const inc = parseFloat(createItem.income) || 0;
    const exp = parseFloat(createItem.expense) || 0;
    if (inc > 0 && exp > 0) {
      alert("错误：单笔记录的收入和支出不能同时大于 0。");
      return;
    }
    if (!String(createItem.item || "").trim() || (inc === 0 && exp === 0)) {
      alert("错误：请填写事项说明并输入大于 0 的收入或支出金额。");
      return;
    }
    setActionLoading(true);
    try {
      await onCreateTransaction({
        date: createItem.date,
        item: String(createItem.item).trim(),
        income: inc,
        expense: exp,
        user: String(createItem.user || currentUser?.name || "Brendon").trim() || "Brendon"
      });
      setCreateItem(null);
    } finally {
      setActionLoading(false);
    }
  };

  // Handle Edit Save
  const handleSaveEdit = async (e) => {
    e.preventDefault();
    if (!editItem) return;
    const inc = parseFloat(editItem.income) || 0;
    const exp = parseFloat(editItem.expense) || 0;
    if (inc > 0 && exp > 0) {
      alert("错误：单笔记录的收入和支出不能同时大于 0。");
      return;
    }
    setActionLoading(true);
    try {
      await onUpdateTransaction({
        ...editItem,
        income: inc,
        expense: exp
      });
      setEditItem(null);
    } finally {
      setActionLoading(false);
    }
  };

  // Handle Confirm Delete
  const handleConfirmDelete = async () => {
    if (!deleteItem) return;
    setActionLoading(true);
    try {
      await onDeleteTransaction(deleteItem);
      setDeleteItem(null);
    } finally {
      setActionLoading(false);
    }
  };

  // Handle Preset Category Additions & Deletions
  const handleAddIncomeItem = (e) => {
    e.preventDefault();
    const val = newIncomeCategory.trim();
    if (!val) return;
    if (incomeItems.includes(val)) {
      showToast("⚠️ 该收入事项分类已存在", "warning");
      return;
    }
    const nextIncome = [...incomeItems, val];
    onUpdateCategoryPresets(nextIncome, expenseItems);
    setNewIncomeCategory("");
  };

  const handleRemoveIncomeItem = (item) => {
    const nextIncome = incomeItems.filter((x) => x !== item);
    onUpdateCategoryPresets(nextIncome, expenseItems);
  };

  const handleAddExpenseItem = (e) => {
    e.preventDefault();
    const val = newExpenseCategory.trim();
    if (!val) return;
    if (expenseItems.includes(val)) {
      showToast("⚠️ 该支出事项分类已存在", "warning");
      return;
    }
    const nextExpense = [...expenseItems, val];
    onUpdateCategoryPresets(incomeItems, nextExpense);
    setNewExpenseCategory("");
  };

  const handleRemoveExpenseItem = (item) => {
    const nextExpense = expenseItems.filter((x) => x !== item);
    onUpdateCategoryPresets(incomeItems, nextExpense);
  };

  // Handle User Role Change & Add User
  const handleRoleChange = (email, newRole) => {
    const updated = userAccounts.map((u) =>
      u.email.toLowerCase() === email.toLowerCase() ? { ...u, role: newRole } : u
    );
    const targetUser = updated.find((u) => u.email.toLowerCase() === email.toLowerCase());
    onUpdateUserAccounts(updated, targetUser);
  };

  const handleAddUserAccount = (e) => {
    e.preventDefault();
    const email = newUserEmail.trim().toLowerCase();
    const name = newUserName.trim() || email.split("@")[0];
    if (!email || !email.includes("@")) {
      showToast("⚠️ 请输入有效的邮箱地址", "warning");
      return;
    }
    const exists = userAccounts.some((u) => u.email.toLowerCase() === email);
    const newEntry = { email, name, role: newUserRole };
    const updated = exists
      ? userAccounts.map((u) => (u.email.toLowerCase() === email ? newEntry : u))
      : [...userAccounts, newEntry];
    onUpdateUserAccounts(updated, newEntry);
    setNewUserEmail("");
    setNewUserName("");
  };

  const handleRemoveUserAccount = (email) => {
    const updated = userAccounts.filter((u) => u.email.toLowerCase() !== email.toLowerCase());
    onUpdateUserAccounts(updated, null, email);
  };

  // Handle Save Booklet Metadata
  const handleSaveBookletSettings = (e) => {
    e.preventDefault();
    onUpdateBookletSettings({
      group_code: bookletForm.group_code.trim() || "YA5",
      counters: bookletForm.counters.trim() || "Rivaldo, Brendon",
      verify_by: bookletForm.verify_by.trim() || "Brendon",
      verify_name: bookletForm.verify_name.trim() || "Rivaldo",
      opening_balance: parseFloat(bookletForm.opening_balance) || 693
    });
  };

  return h("div", { className: "space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-300" },
    // Sub-Navigation Bar for Database Management
    h("div", { className: "bg-white/95 backdrop-blur-md rounded-2xl border border-slate-200/80 p-2 shadow-xs flex flex-wrap items-center justify-between gap-2" },
      h("div", { className: "flex flex-wrap items-center gap-1.5" },
        h("button", {
          type: "button",
          onClick: () => setSubTab("ledger"),
          className: `px-4 py-2.5 rounded-xl text-xs sm:text-sm font-bold transition-all flex items-center gap-2 ${
            subTab === "ledger"
              ? "bg-indigo-600 text-white shadow-sm"
              : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
          }`
        }, "📊 收支流水总账管理"),
        h("button", {
          type: "button",
          onClick: () => setSubTab("categories"),
          className: `px-4 py-2.5 rounded-xl text-xs sm:text-sm font-bold transition-all flex items-center gap-2 ${
            subTab === "categories"
              ? "bg-indigo-600 text-white shadow-sm"
              : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
          }`
        }, "⚙️ 收入与支出事项配置"),
        h("button", {
          type: "button",
          onClick: () => setSubTab("permissions"),
          className: `px-4 py-2.5 rounded-xl text-xs sm:text-sm font-bold transition-all flex items-center gap-2 ${
            subTab === "permissions"
              ? "bg-indigo-600 text-white shadow-sm"
              : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
          }`
        }, "👥 权限设定与奉献册子配置")
      ),
      h("div", { className: "px-3 py-1 text-[11px] font-bold text-indigo-700 bg-indigo-50 border border-indigo-100 rounded-xl" },
        "🔒 管理员专属后台 (Admin Only)"
      )
    ),

    // ========================================================================
    // SUB-TAB 1: 📊 收支流水总账管理 (Master Ledger Management)
    // ========================================================================
    subTab === "ledger" && h("div", { className: "space-y-5" },
      // 3 KPI Summary Cards
      h("div", { className: "grid grid-cols-1 md:grid-cols-3 gap-4" },
        // KPI 1: 当月总收入 (Monthly Income, incl. Balance b/f)
        h("div", { className: "rounded-3xl bg-white border border-emerald-200/80 shadow-sm p-6 flex flex-col justify-between" },
          h("div", { className: "flex items-center justify-between mb-2" },
            h("span", { className: "text-xs font-bold text-emerald-700 uppercase tracking-wider" },
              `当月总收入 (${ledgerViewData.periodLabel} · 含 Balance b/f)`
            ),
            h("div", { className: "w-8 h-8 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0" },
              h(ArrowUpRightIcon, { size: 16 })
            )
          ),
          h("div", { className: "text-2xl sm:text-3xl font-black font-mono text-emerald-600 tracking-tight my-1" },
            `RM ${ledgerViewData.totalIncomeWithBf.toFixed(2)}`
          ),
          h("div", { className: "text-[11px] text-slate-500 font-medium flex flex-wrap gap-2 mt-1" },
            h("span", { className: "px-2 py-0.5 bg-amber-50 text-amber-800 border border-amber-200/70 rounded-md font-bold" },
              `Balance b/f: RM ${ledgerViewData.openingBf.toFixed(2)}`
            ),
            h("span", { className: "px-2 py-0.5 bg-emerald-50 text-emerald-700 border border-emerald-200/70 rounded-md font-bold" },
              `本期奉献收入: +RM ${ledgerViewData.newIncome.toFixed(2)}`
            )
          )
        ),

        // KPI 2: 当月总支出 (Monthly Expense)
        h("div", { className: "rounded-3xl bg-white border border-rose-200/80 shadow-sm p-6 flex flex-col justify-between" },
          h("div", { className: "flex items-center justify-between mb-2" },
            h("span", { className: "text-xs font-bold text-rose-700 uppercase tracking-wider" },
              `当月总支出 (${ledgerViewData.periodLabel} Expense)`
            ),
            h("div", { className: "w-8 h-8 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center shrink-0" },
              h(ArrowDownLeftIcon, { size: 16 })
            )
          ),
          h("div", { className: "text-2xl sm:text-3xl font-black font-mono text-rose-600 tracking-tight my-1" },
            `RM ${ledgerViewData.totalExpense.toFixed(2)}`
          ),
          h("div", { className: "text-[11px] text-slate-500 font-medium mt-1" },
            "各项事工报销、教会转交与关怀支出总额"
          )
        ),

        // KPI 3: 当前结余 (Current Balance RM)
        h("div", { className: "relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-900 via-slate-800 to-indigo-950 text-white shadow-xl p-6 flex flex-col justify-between" },
          h("div", { className: "flex items-center justify-between mb-2" },
            h("span", { className: "text-slate-300 text-xs font-bold uppercase tracking-wider" },
              `当前结余 (${ledgerViewData.periodLabel} Balance)`
            ),
            h("span", { className: "px-2.5 py-0.5 text-[10px] font-bold rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30" },
              "实时核算"
            )
          ),
          h("div", { className: "text-2xl sm:text-3xl font-black font-mono text-emerald-400 tracking-tight my-1" },
            `RM ${ledgerViewData.closingBalance.toFixed(2)}`
          ),
          h("div", { className: "text-[11px] text-slate-400 mt-1" },
            `自动结转下月 Balance b/f · 数据已实时同步`
          )
        )
      ),

      // Filter & Action Bar Card
      h("div", { className: "bg-white/95 backdrop-blur-md rounded-3xl border border-slate-200/80 shadow-sm p-5 sm:p-6" },
        h("div", { className: "flex flex-col md:flex-row md:items-center justify-between gap-4 mb-5 pb-4 border-b border-slate-100" },
          h("div", { className: "flex items-center gap-3" },
            h("div", { className: "w-10 h-10 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center shadow-2xs" },
              h(DatabaseIcon, { size: 22 })
            ),
            h("div", null,
              h("h2", { className: "text-base font-black text-slate-800" }, "收支流水总账 (Master Ledger)"),
              h("p", { className: "text-xs text-slate-500 mt-0.5" }, "首行自动展示上期结转 Balance b/f，后续流水按日期排序并实时计算结余")
            )
          ),

          // Action Toolbar
          h("div", { className: "flex items-center flex-wrap gap-2.5" },
            h("span", { className: "px-3 py-1.5 bg-slate-100 text-slate-700 font-bold text-xs rounded-xl border border-slate-200/80" },
              `共 ${ledgerViewData.rows.length} 笔记录 (+1 笔期初 Balance b/f)`
            ),
            h("button", {
              type: "button",
              onClick: () => {
                const defaultDate = monthFilter !== "all"
                  ? `${selectedYearNum}-${String(monthFilter).padStart(2, "0")}-15`
                  : new Date().toISOString().split("T")[0];
                setCreateItem({
                  date: defaultDate,
                  item: "",
                  income: "",
                  expense: "",
                  user: currentUser?.name || "Brendon"
                });
              },
              className: "inline-flex items-center gap-1.5 px-3.5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-xl shadow-xs transition-all active:scale-95"
            },
              h(PlusIcon, { size: 14 }),
              h("span", null, "+ 新增记录")
            ),
            h("button", {
              type: "button",
              onClick: () => onRefreshTransactions(true),
              disabled: loadingTransactions,
              className: "inline-flex items-center gap-1.5 px-3.5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs rounded-xl shadow-xs transition-all active:scale-95 disabled:opacity-50"
            },
              h(RefreshIcon, { size: 14, className: loadingTransactions ? "animate-spin" : "" }),
              h("span", null, loadingTransactions ? "同步中..." : "🔄 刷新数据")
            )
          )
        ),

        // Filters Grid
        h("div", { className: "grid grid-cols-1 sm:grid-cols-12 gap-3" },
          // Year Selector
          h("div", { className: "sm:col-span-3" },
            h("label", { className: "block text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-1 ml-1" }, "年份 Year"),
            h("select", {
              value: yearFilter,
              onChange: (e) => setYearFilter(e.target.value),
              className: "w-full px-3 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-bold text-slate-700 outline-none focus:ring-2 focus:ring-indigo-500/20"
            },
              h("option", { value: "2026" }, "2026 年"),
              h("option", { value: "2025" }, "2025 年"),
              h("option", { value: "2024" }, "2024 年"),
              h("option", { value: "all" }, "全部年份 (All Years)")
            )
          ),

          // Month Selector
          h("div", { className: "sm:col-span-3" },
            h("label", { className: "block text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-1 ml-1" }, "月份 Month"),
            h("select", {
              value: monthFilter,
              onChange: (e) => setMonthFilter(e.target.value),
              className: "w-full px-3 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-bold text-slate-700 outline-none focus:ring-2 focus:ring-indigo-500/20"
            },
              h("option", { value: "all" }, "全部月份 (All Months)"),
              Array.from({ length: 12 }, (_, i) => i + 1).map((m) =>
                h("option", { key: m, value: String(m) }, `${m}月 (${m} / ${selectedYearNum})`)
              )
            )
          ),

          // Keyword Search Input
          h("div", { className: "sm:col-span-6" },
            h("label", { className: "block text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-1 ml-1" }, "关键词检索 Search"),
            h("div", { className: "relative" },
              h("span", { className: "absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" },
                h(SearchIcon, { size: 15 })
              ),
              h("input", {
                type: "text",
                value: searchQuery,
                onChange: (e) => setSearchQuery(e.target.value),
                placeholder: "搜索事项名称、经手人或日期...",
                className: "w-full pl-9 pr-8 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 outline-none focus:ring-2 focus:ring-indigo-500/20"
              }),
              searchQuery && h("button", {
                type: "button",
                onClick: () => setSearchQuery(""),
                className: "absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
              },
                h(XIcon, { size: 14 })
              )
            )
          )
        )
      ),

      // Master Ledger Table Card
      h("div", { className: "bg-white rounded-3xl border border-slate-200/80 shadow-sm overflow-hidden" },
        h("div", { className: "overflow-x-auto" },
          h("table", { className: "w-full text-left border-collapse text-xs" },
            h("thead", { className: "bg-slate-50/90 border-b border-slate-200 text-slate-600 font-bold uppercase tracking-wider text-[11px]" },
              h("tr", null,
                h("th", { className: "py-3.5 px-4 font-bold" }, "日期 (DATE)"),
                h("th", { className: "py-3.5 px-4 font-bold" }, "事项 (ITEM)"),
                h("th", { className: "py-3.5 px-4 font-bold text-right" }, "收入 (INCOME)"),
                h("th", { className: "py-3.5 px-4 font-bold text-right" }, "支出 (EXPENSE)"),
                h("th", { className: "py-3.5 px-4 font-bold text-right" }, "结余 (BALANCE)"),
                h("th", { className: "py-3.5 px-4 font-bold" }, "经手人 (USER)"),
                h("th", { className: "py-3.5 px-4 font-bold text-center" }, "操作 (Edit / Delete)")
              )
            ),
            h("tbody", { className: "divide-y divide-slate-100 font-medium text-slate-700" },
              // Row 1: Carried-forward Balance b/f Row
              h("tr", {
                className: "bg-amber-50/60 hover:bg-amber-50 transition-colors border-b border-amber-200/60"
              },
                h("td", { className: "py-3 px-4 font-mono font-bold text-amber-800 whitespace-nowrap" },
                  monthFilter === "all" ? `${selectedYearNum}-01-01` : `${selectedYearNum}-${String(monthFilter).padStart(2, "0")}-01`
                ),
                h("td", { className: "py-3 px-4 font-black text-slate-900" },
                  h("div", { className: "inline-flex items-center gap-2" },
                    h("span", null, "Balance b/f"),
                    h("span", { className: "px-2 py-0.5 text-[10px] font-bold bg-amber-100 text-amber-800 rounded-md border border-amber-200" },
                      "上期结转"
                    )
                  )
                ),
                h("td", { className: "py-3 px-4 text-right font-mono font-bold text-emerald-700 whitespace-nowrap" },
                  `RM ${ledgerViewData.openingBf.toFixed(2)}`
                ),
                h("td", { className: "py-3 px-4 text-right font-mono text-slate-300 whitespace-nowrap" }, "-"),
                h("td", { className: "py-3 px-4 text-right font-mono font-black text-slate-900 whitespace-nowrap" },
                  `RM ${ledgerViewData.openingBf.toFixed(2)}`
                ),
                h("td", { className: "py-3 px-4 whitespace-nowrap text-slate-500 text-[11px]" }, "系统期初结转"),
                h("td", { className: "py-3 px-4 text-center whitespace-nowrap text-[11px] text-slate-400 font-semibold" }, "期初基准")
              ),

              // Subsequent Chronological Transaction Rows
              ledgerViewData.rows.length === 0 ? h("tr", null,
                h("td", { colSpan: 7, className: "py-12 text-center text-slate-400 text-xs" },
                  "当前筛选周期内暂无新增收支交易记录（仅期初结转 Balance b/f）"
                )
              ) : ledgerViewData.rows.map((tx) => {
                const inc = parseFloat(tx.income || 0);
                const exp = parseFloat(tx.expense || 0);
                const bal = parseFloat(tx.balance ?? 0);

                return h("tr", {
                  key: tx.id,
                  className: "hover:bg-slate-50/90 transition-colors"
                },
                  h("td", { className: "py-3 px-4 font-mono font-semibold text-slate-700 whitespace-nowrap" },
                    tx.date
                  ),
                  h("td", { className: "py-3 px-4 font-bold text-slate-800" },
                    h("span", { className: "inline-block bg-slate-100/90 border border-slate-200/70 px-2.5 py-0.5 rounded-lg text-xs" },
                      tx.item
                    )
                  ),
                  h("td", { className: "py-3 px-4 text-right font-mono font-bold whitespace-nowrap" },
                    inc > 0 ? h("span", { className: "text-emerald-600" }, `+ RM ${inc.toFixed(2)}`) : h("span", { className: "text-slate-300" }, "-")
                  ),
                  h("td", { className: "py-3 px-4 text-right font-mono font-bold whitespace-nowrap" },
                    exp > 0 ? h("span", { className: "text-rose-600" }, `- RM ${exp.toFixed(2)}`) : h("span", { className: "text-slate-300" }, "-")
                  ),
                  h("td", { className: "py-3 px-4 text-right font-mono font-black text-slate-800 whitespace-nowrap" },
                    `RM ${bal.toFixed(2)}`
                  ),
                  h("td", { className: "py-3 px-4 whitespace-nowrap text-slate-600" },
                    h("span", { className: "inline-flex items-center gap-1 text-[11px] font-semibold" },
                      h(Jy, { size: 12, className: "text-indigo-500" }),
                      tx.user || "Brendon"
                    )
                  ),
                  h("td", { className: "py-3 px-4 text-center whitespace-nowrap" },
                    h("div", { className: "inline-flex items-center gap-1.5" },
                      h("button", {
                        type: "button",
                        onClick: () => setEditItem({ ...tx }),
                        className: "inline-flex items-center gap-1 px-2.5 py-1 text-[11px] font-bold text-blue-600 hover:text-blue-700 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors active:scale-95"
                      },
                        h(EditIcon, { size: 13 }),
                        "编辑"
                      ),
                      h("button", {
                        type: "button",
                        onClick: () => setDeleteItem(tx),
                        className: "inline-flex items-center gap-1 px-2.5 py-1 text-[11px] font-bold text-rose-600 hover:text-rose-700 bg-rose-50 hover:bg-rose-100 rounded-lg transition-colors active:scale-95"
                      },
                        h(TrashIcon, { size: 13 }),
                        "删除"
                      )
                    )
                  )
                );
              })
            )
          )
        )
      )
    ),

    // ========================================================================
    // SUB-TAB 2: ⚙️ 收入与支出事项配置 (Income & Expense Item Configuration)
    // ========================================================================
    subTab === "categories" && h("div", { className: "grid grid-cols-1 md:grid-cols-2 gap-6" },
      // 🟢 Preset Income Items Card
      h("div", { className: "bg-white rounded-3xl border border-emerald-200/80 shadow-sm p-6 space-y-5" },
        h("div", { className: "flex items-center justify-between pb-3 border-b border-slate-100" },
          h("div", null,
            h("h3", { className: "text-base font-black text-emerald-800 flex items-center gap-2" },
              "🟢 收入事项分类 (Preset Income Items)"
            ),
            h("p", { className: "text-xs text-slate-500 mt-0.5" },
              "配置【📝 记账录入】表单中的收入事项快速选择按钮与下拉选项"
            )
          ),
          h("span", { className: "px-2.5 py-1 text-xs font-bold bg-emerald-50 text-emerald-700 rounded-xl border border-emerald-200" },
            `${incomeItems.length} 项`
          )
        ),

        // Add Income Item Form
        h("form", { onSubmit: handleAddIncomeItem, className: "flex gap-2" },
          h("input", {
            type: "text",
            value: newIncomeCategory,
            onChange: (e) => setNewIncomeCategory(e.target.value),
            placeholder: "输入新收入事项（如：主日奉献、感恩奉献）...",
            className: "flex-1 px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-semibold outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500"
          }),
          h("button", {
            type: "submit",
            className: "px-4 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold flex items-center gap-1 shadow-xs transition-all active:scale-95 shrink-0"
          },
            h(PlusIcon, { size: 14 }),
            "添加收入事项"
          )
        ),

        // Income Items List
        h("div", { className: "space-y-2" },
          incomeItems.map((item) =>
            h("div", {
              key: item,
              className: "flex items-center justify-between px-4 py-2.5 bg-emerald-50/40 hover:bg-emerald-50/80 border border-emerald-200/60 rounded-xl transition-colors"
            },
              h("div", { className: "flex items-center gap-2" },
                h("span", { className: "w-2 h-2 rounded-full bg-emerald-500" }),
                h("span", { className: "text-xs font-bold text-slate-800" }, item)
              ),
              h("button", {
                type: "button",
                onClick: () => handleRemoveIncomeItem(item),
                className: "inline-flex items-center gap-1 px-2.5 py-1 text-[11px] font-bold text-rose-600 hover:text-white hover:bg-rose-600 bg-rose-50 border border-rose-200 rounded-lg transition-all"
              },
                h(TrashIcon, { size: 12 }),
                "删除"
              )
            )
          )
        )
      ),

      // 🔴 Preset Expense Items Card
      h("div", { className: "bg-white rounded-3xl border border-rose-200/80 shadow-sm p-6 space-y-5" },
        h("div", { className: "flex items-center justify-between pb-3 border-b border-slate-100" },
          h("div", null,
            h("h3", { className: "text-base font-black text-rose-800 flex items-center gap-2" },
              "🔴 支出事项分类 (Preset Expense Items)"
            ),
            h("p", { className: "text-xs text-slate-500 mt-0.5" },
              "配置【📝 记账录入】表单中的支出报销快速选择按钮与下拉选项"
            )
          ),
          h("span", { className: "px-2.5 py-1 text-xs font-bold bg-rose-50 text-rose-700 rounded-xl border border-rose-200" },
            `${expenseItems.length} 项`
          )
        ),

        // Add Expense Item Form
        h("form", { onSubmit: handleAddExpenseItem, className: "flex gap-2" },
          h("input", {
            type: "text",
            value: newExpenseCategory,
            onChange: (e) => setNewExpenseCategory(e.target.value),
            placeholder: "输入新支出事项（如：转回给教会、生日蛋糕）...",
            className: "flex-1 px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-semibold outline-none focus:ring-2 focus:ring-rose-500/20 focus:border-rose-500"
          }),
          h("button", {
            type: "submit",
            className: "px-4 py-2.5 bg-rose-600 hover:bg-rose-700 text-white rounded-xl text-xs font-bold flex items-center gap-1 shadow-xs transition-all active:scale-95 shrink-0"
          },
            h(PlusIcon, { size: 14 }),
            "添加支出事项"
          )
        ),

        // Expense Items List
        h("div", { className: "space-y-2 max-h-96 overflow-y-auto pr-1" },
          expenseItems.map((item) =>
            h("div", {
              key: item,
              className: "flex items-center justify-between px-4 py-2.5 bg-rose-50/40 hover:bg-rose-50/80 border border-rose-200/60 rounded-xl transition-colors"
            },
              h("div", { className: "flex items-center gap-2" },
                h("span", { className: "w-2 h-2 rounded-full bg-rose-500" }),
                h("span", { className: "text-xs font-bold text-slate-800" }, item)
              ),
              h("button", {
                type: "button",
                onClick: () => handleRemoveExpenseItem(item),
                className: "inline-flex items-center gap-1 px-2.5 py-1 text-[11px] font-bold text-rose-600 hover:text-white hover:bg-rose-600 bg-rose-50 border border-rose-200 rounded-lg transition-all"
              },
                h(TrashIcon, { size: 12 }),
                "删除"
              )
            )
          )
        )
      )
    ),

    // ========================================================================
    // SUB-TAB 3: 👥 权限设定与奉献册子配置 (User/Admin Role & Booklet Settings)
    // ========================================================================
    subTab === "permissions" && h("div", { className: "space-y-6" },
      // Section A: User Role Management Table
      h("div", { className: "bg-white rounded-3xl border border-slate-200/80 shadow-sm p-6 space-y-5" },
        h("div", { className: "flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-100" },
          h("div", null,
            h("h3", { className: "text-base font-black text-slate-800" }, "👥 用户与管理员权限设定 (User / Admin Role Management)"),
            h("p", { className: "text-xs text-slate-500 mt-0.5" },
              "设定同工账号角色：普通同工 (User) 可访问【📝 记账录入】与查看【📖 奉献记录全册（只读，不可编辑/删除）】，不可访问【🗄️ 数据库管理】；管理员 (Admin) 拥有完整权限"
            )
          ),
          h("span", { className: "px-3 py-1 bg-indigo-50 text-indigo-700 rounded-xl text-xs font-bold border border-indigo-200" },
            `共 ${userAccounts.length} 个已授权账号`
          )
        ),

        // Add User Account Form
        h("form", { onSubmit: handleAddUserAccount, className: "grid grid-cols-1 sm:grid-cols-12 gap-3 bg-slate-50 p-4 rounded-2xl border border-slate-200/70" },
          h("div", { className: "sm:col-span-4" },
            h("label", { className: "block text-[11px] font-bold text-slate-500 uppercase mb-1" }, "同工邮箱 Email"),
            h("input", {
              type: "email",
              required: true,
              value: newUserEmail,
              onChange: (e) => setNewUserEmail(e.target.value),
              placeholder: "coworker@group.finance.com",
              className: "w-full px-3 py-2 bg-white border border-slate-200 rounded-xl text-xs font-semibold outline-none focus:ring-2 focus:ring-indigo-500/20"
            })
          ),
          h("div", { className: "sm:col-span-3" },
            h("label", { className: "block text-[11px] font-bold text-slate-500 uppercase mb-1" }, "同工姓名 Name"),
            h("input", {
              type: "text",
              value: newUserName,
              onChange: (e) => setNewUserName(e.target.value),
              placeholder: "例如：Rivaldo",
              className: "w-full px-3 py-2 bg-white border border-slate-200 rounded-xl text-xs font-semibold outline-none focus:ring-2 focus:ring-indigo-500/20"
            })
          ),
          h("div", { className: "sm:col-span-3" },
            h("label", { className: "block text-[11px] font-bold text-slate-500 uppercase mb-1" }, "分配角色 Role"),
            h("select", {
              value: newUserRole,
              onChange: (e) => setNewUserRole(e.target.value),
              className: "w-full px-3 py-2 bg-white border border-slate-200 rounded-xl text-xs font-bold text-slate-700 outline-none focus:ring-2 focus:ring-indigo-500/20"
            },
              h("option", { value: "user" }, "User (普通同工)"),
              h("option", { value: "admin" }, "Admin (管理员)")
            )
          ),
          h("div", { className: "sm:col-span-2 flex items-end" },
            h("button", {
              type: "submit",
              className: "w-full py-2 px-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold flex items-center justify-center gap-1 shadow-xs transition-all active:scale-95"
            },
              h(PlusIcon, { size: 14 }),
              "新增账号"
            )
          )
        ),

        // User Role Table
        h("div", { className: "overflow-x-auto" },
          h("table", { className: "w-full text-left border-collapse text-xs" },
            h("thead", { className: "bg-slate-50 border-b border-slate-200 text-slate-500 font-bold uppercase text-[11px]" },
              h("tr", null,
                h("th", { className: "py-3 px-4" }, "邮箱 (Email)"),
                h("th", { className: "py-3 px-4" }, "姓名 (Name)"),
                h("th", { className: "py-3 px-4" }, "角色选择 (Role Dropdown)"),
                h("th", { className: "py-3 px-4" }, "访问权限说明 (Access Scope Description)"),
                h("th", { className: "py-3 px-4 text-center" }, "操作")
              )
            ),
            h("tbody", { className: "divide-y divide-slate-100" },
              userAccounts.map((u) => {
                const isRoleAdmin = u.role === "admin";
                return h("tr", { key: u.email, className: "hover:bg-slate-50/80 transition-colors" },
                  h("td", { className: "py-3 px-4 font-mono font-bold text-slate-800 whitespace-nowrap" }, u.email),
                  h("td", { className: "py-3 px-4 font-bold text-slate-700 whitespace-nowrap" }, u.name),
                  h("td", { className: "py-3 px-4 whitespace-nowrap" },
                    h("select", {
                      value: u.role,
                      onChange: (e) => handleRoleChange(u.email, e.target.value),
                      className: `px-3 py-1.5 rounded-xl text-xs font-bold border outline-none cursor-pointer transition-colors ${
                        isRoleAdmin
                          ? "bg-indigo-50 text-indigo-700 border-indigo-200"
                          : "bg-blue-50 text-blue-700 border-blue-200"
                      }`
                    },
                      h("option", { value: "admin" }, "Admin (管理员)"),
                      h("option", { value: "user" }, "User (普通同工)")
                    )
                  ),
                  h("td", { className: "py-3 px-4 text-xs text-slate-600 leading-relaxed" },
                    isRoleAdmin
                      ? h("span", { className: "text-indigo-700 font-semibold" },
                          "完整权限：可访问【记账录入】、【数据库管理】、【奉献记录全册】，支持编辑/删除流水、配置分类及管理同工权限"
                        )
                      : h("span", { className: "text-slate-600 font-medium" },
                          "基础权限：可访问【📝 记账录入】与查看【📖 奉献记录全册（只读，不可编辑/删除记录）】，禁止访问【🗄️ 数据库管理】"
                        )
                  ),
                  h("td", { className: "py-3 px-4 text-center whitespace-nowrap" },
                    h("button", {
                      type: "button",
                      onClick: () => handleRemoveUserAccount(u.email),
                      className: "px-2.5 py-1 text-[11px] font-bold text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"
                    }, "移除")
                  )
                );
              })
            )
          )
        )
      ),

      // Section B: Booklet Header & Signature Metadata Configuration
      h("div", { className: "bg-white rounded-3xl border border-slate-200/80 shadow-sm p-6 space-y-5" },
        h("div", { className: "pb-3 border-b border-slate-100" },
          h("h3", { className: "text-base font-black text-slate-800" }, "📖 奉献册子表头与签名配置 (Booklet Header & Signature Metadata)"),
          h("p", { className: "text-xs text-slate-500 mt-0.5" },
            "自定义【📖 奉献记录全册】纸质表格顶部的小组编号、点算同工及底部审核签名信息，保存后立即生效"
          )
        ),

        h("form", { onSubmit: handleSaveBookletSettings, className: "space-y-4" },
          h("div", { className: "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4" },
            h("div", null,
              h("label", { className: "block text-xs font-bold text-slate-600 mb-1" }, "小组编号 (Group Code)"),
              h("input", {
                type: "text",
                required: true,
                value: bookletForm.group_code,
                onChange: (e) => setBookletForm({ ...bookletForm, group_code: e.target.value }),
                placeholder: "YA5",
                className: "w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-bold text-slate-800 outline-none focus:ring-2 focus:ring-indigo-500/20"
              })
            ),
            h("div", null,
              h("label", { className: "block text-xs font-bold text-slate-600 mb-1" }, "点算同工 (Counters)"),
              h("input", {
                type: "text",
                required: true,
                value: bookletForm.counters,
                onChange: (e) => setBookletForm({ ...bookletForm, counters: e.target.value }),
                placeholder: "Rivaldo, Brendon",
                className: "w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-bold text-slate-800 outline-none focus:ring-2 focus:ring-indigo-500/20"
              })
            ),
            h("div", null,
              h("label", { className: "block text-xs font-bold text-slate-600 mb-1" }, "审核人签名 (Verify by)"),
              h("input", {
                type: "text",
                required: true,
                value: bookletForm.verify_by,
                onChange: (e) => setBookletForm({ ...bookletForm, verify_by: e.target.value }),
                placeholder: "Brendon",
                className: "w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-bold text-slate-800 outline-none focus:ring-2 focus:ring-indigo-500/20"
              })
            ),
            h("div", null,
              h("label", { className: "block text-xs font-bold text-slate-600 mb-1" }, "复核人姓名 (Name)"),
              h("input", {
                type: "text",
                required: true,
                value: bookletForm.verify_name,
                onChange: (e) => setBookletForm({ ...bookletForm, verify_name: e.target.value }),
                placeholder: "Rivaldo",
                className: "w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-bold text-slate-800 outline-none focus:ring-2 focus:ring-indigo-500/20"
              })
            ),
            h("div", null,
              h("label", { className: "block text-xs font-bold text-slate-600 mb-1" }, "年初结转 Balance b/f (RM)"),
              h("input", {
                type: "number",
                step: "0.01",
                required: true,
                value: bookletForm.opening_balance,
                onChange: (e) => setBookletForm({ ...bookletForm, opening_balance: e.target.value }),
                className: "w-full px-3.5 py-2.5 bg-amber-50/60 border border-amber-200 rounded-xl text-xs font-bold text-amber-900 outline-none focus:ring-2 focus:ring-amber-500/20"
              })
            )
          ),

          h("div", { className: "flex justify-end pt-2" },
            h("button", {
              type: "submit",
              className: "px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold shadow-md shadow-indigo-500/20 transition-all active:scale-95 flex items-center gap-2"
            },
              h(CheckCircleIcon, { size: 15 }),
              "💾 保存册子配置"
            )
          )
        )
      ),

      // Section C: Google OAuth 2.0 Login Configuration
      h("div", { className: "bg-white rounded-3xl border border-slate-200/80 shadow-sm p-6 space-y-5" },
        h("div", { className: "flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-100" },
          h("div", null,
            h("h3", { className: "text-base font-black text-slate-800 flex items-center gap-2" },
              h(GoogleLogoSvg, { size: 18 }),
              "🔑 Google OAuth 2.0 账号登录配置 (Google Sign-In Config)"
            ),
            h("p", { className: "text-xs text-slate-500 mt-0.5" },
              "配置 Google Cloud Console 的 OAuth 2.0 客户端 ID 与密钥，允许同工使用 Google 账号一键安全登录"
            )
          ),
          h("span", {
            className: `px-3 py-1 rounded-xl text-xs font-bold border ${
              googleClientId
                ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                : "bg-blue-50 text-blue-700 border-blue-200"
            }`
          }, googleClientId ? "✅ OAuth Client ID 已启用" : "⚡ 内置 Google 账号选择器已启用")
        ),

        h("form", {
          onSubmit: async (e) => {
            e.preventDefault();
            if (onUpdateGoogleOAuth) {
              await onUpdateGoogleOAuth(oauthForm.google_client_id.trim(), oauthForm.google_client_secret.trim());
              setOauthSaveStatus("✅ Google OAuth 2.0 配置已保存并实时生效！");
              setTimeout(() => setOauthSaveStatus(""), 4000);
            }
          },
          className: "space-y-4"
        },
          h("div", { className: "grid grid-cols-1 md:grid-cols-2 gap-4" },
            h("div", null,
              h("label", { className: "block text-xs font-bold text-slate-600 mb-1" }, "Google OAuth Client ID"),
              h("input", {
                type: "text",
                value: oauthForm.google_client_id,
                onChange: (e) => setOauthForm({ ...oauthForm, google_client_id: e.target.value }),
                placeholder: "例如：1234567890-abc.apps.googleusercontent.com",
                className: "w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-mono text-slate-800 outline-none focus:ring-2 focus:ring-indigo-500/20"
              })
            ),
            h("div", null,
              h("label", { className: "block text-xs font-bold text-slate-600 mb-1" }, "Google OAuth Client Secret (可选)"),
              h("input", {
                type: "password",
                value: oauthForm.google_client_secret,
                onChange: (e) => setOauthForm({ ...oauthForm, google_client_secret: e.target.value }),
                placeholder: "GOCSPX-••••••••••••••••••••",
                className: "w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-mono text-slate-800 outline-none focus:ring-2 focus:ring-indigo-500/20"
              })
            )
          ),

          h("div", { className: "p-3.5 rounded-2xl bg-slate-50 border border-slate-200/80 text-xs text-slate-600 flex flex-wrap items-center justify-between gap-2" },
            h("div", null,
              h("span", { className: "font-bold text-slate-700" }, "已授权的重定向 URI (Authorized Redirect URI): "),
              h("code", { className: "px-2 py-0.5 bg-white border border-slate-200 rounded-md font-mono text-indigo-700" },
                `${typeof window !== "undefined" ? window.location.origin : ""}/auth/google/callback`
              )
            ),
            oauthSaveStatus && h("span", { className: "font-bold text-emerald-600" }, oauthSaveStatus)
          ),

          h("div", { className: "flex justify-end" },
            h("button", {
              type: "submit",
              className: "px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold shadow-md shadow-indigo-500/20 transition-all active:scale-95 flex items-center gap-2"
            },
              h(CheckCircleIcon, { size: 15 }),
              "💾 保存 Google 登录配置"
            )
          )
        )
      )
    ),

    // ========================================================================
    // Create Record Modal Dialog
    // ========================================================================
    createItem && h("div", { className: "fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm animate-in fade-in duration-200" },
      h("div", { className: "bg-white rounded-3xl shadow-2xl border border-slate-100 max-w-md w-full p-6 animate-in zoom-in-95 duration-200" },
        h("div", { className: "flex items-center justify-between pb-3 border-b border-slate-100 mb-4" },
          h("div", { className: "flex items-center gap-2" },
            h("div", { className: "w-8 h-8 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold" },
              h(PlusIcon, { size: 16 })
            ),
            h("h3", { className: "text-base font-black text-slate-800" }, "新增收支记录 (Create Record)")
          ),
          h("button", {
            type: "button",
            onClick: () => setCreateItem(null),
            className: "text-slate-400 hover:text-slate-600 p-1 rounded-lg"
          },
            h(XIcon, { size: 18 })
          )
        ),

        h("form", { onSubmit: handleSaveCreate, className: "space-y-4" },
          h("div", null,
            h("label", { className: "block text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-1" }, "日期 Date"),
            h("input", {
              type: "date",
              required: true,
              value: createItem.date ? String(createItem.date).split("T")[0] : "",
              onChange: (e) => setCreateItem({ ...createItem, date: e.target.value }),
              className: "w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-semibold outline-none focus:ring-2 focus:ring-emerald-500/20"
            })
          ),

          h("div", { className: "space-y-2" },
            h("div", { className: "flex items-center justify-between gap-2" },
              h("label", { className: "block text-[11px] font-bold text-slate-500 uppercase tracking-wider" }, "事项说明 Item"),
              h("select", {
                value: "",
                onChange: (e) => {
                  const val = e.target.value;
                  if (!val) return;
                  const [type, name] = val.split("::");
                  if (type === "inc") {
                    setCreateItem({ ...createItem, item: name, expense: "" });
                  } else {
                    setCreateItem({ ...createItem, item: name, income: "" });
                  }
                },
                className: "px-2.5 py-1 bg-indigo-50 text-indigo-700 border border-indigo-200 rounded-lg text-[11px] font-bold outline-none cursor-pointer"
              },
                h("option", { value: "" }, "📂 从预设事项选择..."),
                h("optgroup", { label: "🟢 收入事项分类" },
                  (incomeItems || DEFAULT_INCOME_ITEMS).map((item) =>
                    h("option", { key: `c-inc-${item}`, value: `inc::${item}` }, `🟢 [收入] ${item}`)
                  )
                ),
                h("optgroup", { label: "🔴 支出事项分类" },
                  (expenseItems || DEFAULT_EXPENSE_ITEMS).map((item) =>
                    h("option", { key: `c-exp-${item}`, value: `exp::${item}` }, `🔴 [支出] ${item}`)
                  )
                )
              )
            ),
            h("input", {
              type: "text",
              required: true,
              placeholder: "请输入或选择事项说明...",
              value: createItem.item || "",
              onChange: (e) => setCreateItem({ ...createItem, item: e.target.value }),
              className: "w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-semibold outline-none focus:ring-2 focus:ring-emerald-500/20"
            })
          ),

          h("div", { className: "grid grid-cols-2 gap-3" },
            h("div", null,
              h("label", { className: "block text-[11px] font-bold text-emerald-600 uppercase tracking-wider mb-1" }, "收入 (RM)"),
              h("input", {
                type: "number",
                step: "0.01",
                min: "0",
                value: createItem.income ?? "",
                onChange: (e) => setCreateItem({ ...createItem, income: e.target.value, expense: "" }),
                placeholder: "0.00",
                className: "w-full px-3.5 py-2.5 bg-emerald-50/40 border border-emerald-200 rounded-xl text-xs font-bold text-emerald-700 outline-none"
              })
            ),
            h("div", null,
              h("label", { className: "block text-[11px] font-bold text-rose-600 uppercase tracking-wider mb-1" }, "支出 (RM)"),
              h("input", {
                type: "number",
                step: "0.01",
                min: "0",
                value: createItem.expense ?? "",
                onChange: (e) => setCreateItem({ ...createItem, expense: e.target.value, income: "" }),
                placeholder: "0.00",
                className: "w-full px-3.5 py-2.5 bg-rose-50/40 border border-rose-200 rounded-xl text-xs font-bold text-rose-700 outline-none"
              })
            )
          ),

          h("div", null,
            h("label", { className: "block text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-1" }, "经手同工 User"),
            h("input", {
              type: "text",
              value: createItem.user || "",
              onChange: (e) => setCreateItem({ ...createItem, user: e.target.value }),
              className: "w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-semibold outline-none"
            })
          ),

          h("div", { className: "pt-2 flex gap-2" },
            h("button", {
              type: "button",
              onClick: () => setCreateItem(null),
              className: "flex-1 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-bold transition-all"
            }, "取消"),
            h("button", {
              type: "submit",
              disabled: actionLoading,
              className: "flex-1 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold transition-all shadow-md shadow-emerald-500/20 disabled:opacity-50"
            }, "确认新增")
          )
        )
      )
    ),

    // ========================================================================
    // Edit Record Modal Dialog
    // ========================================================================
    editItem && h("div", { className: "fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm animate-in fade-in duration-200" },
      h("div", { className: "bg-white rounded-3xl shadow-2xl border border-slate-100 max-w-md w-full p-6 animate-in zoom-in-95 duration-200" },
        h("div", { className: "flex items-center justify-between pb-3 border-b border-slate-100 mb-4" },
          h("div", { className: "flex items-center gap-2" },
            h("div", { className: "w-8 h-8 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center font-bold" },
              h(EditIcon, { size: 16 })
            ),
            h("h3", { className: "text-base font-black text-slate-800" }, "编辑收支流水记录")
          ),
          h("button", {
            type: "button",
            onClick: () => setEditItem(null),
            className: "text-slate-400 hover:text-slate-600 p-1 rounded-lg"
          },
            h(XIcon, { size: 18 })
          )
        ),

        h("form", { onSubmit: handleSaveEdit, className: "space-y-4" },
          h("div", null,
            h("label", { className: "block text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-1" }, "日期 Date"),
            h("input", {
              type: "date",
              required: true,
              value: editItem.date ? String(editItem.date).split("T")[0] : "",
              onChange: (e) => setEditItem({ ...editItem, date: e.target.value }),
              className: "w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-semibold outline-none focus:ring-2 focus:ring-blue-500/20"
            })
          ),

          h("div", null,
            h("label", { className: "block text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-1" }, "事项说明 Item"),
            h("input", {
              type: "text",
              required: true,
              value: editItem.item || "",
              onChange: (e) => setEditItem({ ...editItem, item: e.target.value }),
              className: "w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-semibold outline-none focus:ring-2 focus:ring-blue-500/20"
            })
          ),

          h("div", { className: "grid grid-cols-2 gap-3" },
            h("div", null,
              h("label", { className: "block text-[11px] font-bold text-emerald-600 uppercase tracking-wider mb-1" }, "收入 (RM)"),
              h("input", {
                type: "number",
                step: "0.01",
                min: "0",
                value: editItem.income ?? "",
                onChange: (e) => setEditItem({ ...editItem, income: e.target.value }),
                placeholder: "0.00",
                className: "w-full px-3.5 py-2.5 bg-emerald-50/40 border border-emerald-200 rounded-xl text-xs font-bold text-emerald-700 outline-none"
              })
            ),
            h("div", null,
              h("label", { className: "block text-[11px] font-bold text-rose-600 uppercase tracking-wider mb-1" }, "支出 (RM)"),
              h("input", {
                type: "number",
                step: "0.01",
                min: "0",
                value: editItem.expense ?? "",
                onChange: (e) => setEditItem({ ...editItem, expense: e.target.value }),
                placeholder: "0.00",
                className: "w-full px-3.5 py-2.5 bg-rose-50/40 border border-rose-200 rounded-xl text-xs font-bold text-rose-700 outline-none"
              })
            )
          ),

          h("div", null,
            h("label", { className: "block text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-1" }, "经手人 User"),
            h("input", {
              type: "text",
              value: editItem.user || "",
              onChange: (e) => setEditItem({ ...editItem, user: e.target.value }),
              className: "w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-semibold outline-none"
            })
          ),

          h("div", { className: "pt-2 flex gap-2" },
            h("button", {
              type: "button",
              onClick: () => setEditItem(null),
              className: "flex-1 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-bold transition-all"
            }, "取消"),
            h("button", {
              type: "submit",
              disabled: actionLoading,
              className: "flex-1 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold transition-all shadow-md shadow-indigo-500/20 disabled:opacity-50"
            }, "保存修改")
          )
        )
      )
    ),

    // ========================================================================
    // Delete Record Confirmation Modal Dialog
    // ========================================================================
    deleteItem && h("div", { className: "fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm animate-in fade-in duration-200" },
      h("div", { className: "bg-white rounded-3xl shadow-2xl border border-slate-100 max-w-sm w-full p-6 animate-in zoom-in-95 duration-200" },
        h("div", { className: "w-12 h-12 rounded-2xl bg-rose-100 text-rose-600 flex items-center justify-center mx-auto mb-4" },
          h(TrashIcon, { size: 24 })
        ),
        h("h3", { className: "text-base font-black text-slate-800 text-center mb-1" }, "确认删除此笔流水记录？"),
        h("p", { className: "text-xs text-slate-500 text-center mb-4 leading-relaxed" },
          "删除后，当月及后续月份的结存 (Balance) 将自动重新计算并实时同步至奉献记录全册。"
        ),

        h("div", { className: "bg-slate-50 border border-slate-200/70 rounded-2xl p-3.5 mb-5 space-y-1.5 text-xs" },
          h("div", { className: "flex justify-between text-slate-500" },
            h("span", null, "日期:"),
            h("span", { className: "font-mono font-bold text-slate-800" }, deleteItem.date)
          ),
          h("div", { className: "flex justify-between text-slate-500" },
            h("span", null, "事项:"),
            h("span", { className: "font-bold text-slate-800" }, deleteItem.item)
          ),
          h("div", { className: "flex justify-between text-slate-500" },
            h("span", null, "金额:"),
            h("span", { className: `font-mono font-bold ${deleteItem.income > 0 ? "text-emerald-600" : "text-rose-600"}` },
              deleteItem.income > 0
                ? `+ RM ${parseFloat(deleteItem.income).toFixed(2)}`
                : `- RM ${parseFloat(deleteItem.expense).toFixed(2)}`
            )
          )
        ),

        h("div", { className: "flex gap-2" },
          h("button", {
            type: "button",
            onClick: () => setDeleteItem(null),
            className: "flex-1 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-bold transition-all"
          }, "取消"),
          h("button", {
            type: "button",
            disabled: actionLoading,
            onClick: handleConfirmDelete,
            className: "flex-1 py-2.5 bg-rose-600 hover:bg-rose-700 text-white rounded-xl text-xs font-bold transition-all shadow-md shadow-rose-500/20"
          }, "确认删除")
        )
      )
    )
  );
}

// ============================================================================
// Module 3: 📖 奉献记录全册 (Monthly Offering Booklet View - User Read-Only / Admin Editable)
// ============================================================================
function BookletViewTab({
  canViewDatabase,
  canDelete,
  transactions,
  bookletSettings,
  onDeleteTransaction,
  onNavigateTab,
  onLogout
}) {
  const [selectedMonth, setSelectedMonth] = useState(() => new Date().getMonth() + 1); // 1..12 or "all"
  const [selectedYear, setSelectedYear] = useState(() => new Date().getFullYear() || 2026);

  const yearLedger = useMemo(() => {
    const initialBf = selectedYear === 2026 ? (Number(bookletSettings?.opening_balance) || 693) : 0;
    return computeYearLedger(transactions, selectedYear, initialBf);
  }, [transactions, selectedYear, bookletSettings]);

  const monthsToRender = useMemo(() => {
    if (selectedMonth === "all") {
      return [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
    }
    return [Number(selectedMonth)];
  }, [selectedMonth]);

  const groupCode = bookletSettings?.group_code || "YA5";
  const counters = bookletSettings?.counters || "Rivaldo, Brendon";
  const verifyBy = bookletSettings?.verify_by || "Brendon";
  const verifyName = bookletSettings?.verify_name || "Rivaldo";

  const handleInlineDelete = async (tx) => {
    if (!canDelete) return;
    const amtStr = tx.income > 0 ? `收入: RM ${tx.income}` : `支出: RM ${tx.expense}`;
    const confirmed = window.confirm(
      `确定要从奉献记录册中删除这条记录吗？\n\n• 日期: ${tx.shortDate || tx.date}\n• 事项: ${tx.item}\n• 金额: ${amtStr}\n\n删除后，本月及后续月份的结存将自动重新计算。`
    );
    if (!confirmed) return;
    await onDeleteTransaction(tx);
  };

  return h("div", { className: "space-y-6 animate-in fade-in duration-300" },
    // Top Booklet Control Bar (Hidden when printing)
    h("div", {
      className: "bg-white/95 backdrop-blur-md rounded-3xl border border-slate-200/80 shadow-sm p-4 sm:p-5 no-print print:hidden space-y-4"
    },
      // Row 1: Quick Module Switcher & Right Actions (Print / Logout)
      h("div", { className: "flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-100" },
        h("div", { className: "flex items-center flex-wrap gap-2" },
          h("button", {
            type: "button",
            onClick: () => onNavigateTab("entry"),
            className: "px-3.5 py-2 rounded-xl text-xs font-bold bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 transition-all"
          }, "📝 记账录入"),
          canViewDatabase && h("button", {
            type: "button",
            onClick: () => onNavigateTab("database-view"),
            className: "px-3.5 py-2 rounded-xl text-xs font-bold bg-sky-50 hover:bg-sky-100 text-sky-700 border border-sky-200 transition-all"
          }, "🗄️ 数据库管理"),
          h("button", {
            type: "button",
            onClick: () => onNavigateTab("booklet"),
            className: "px-3.5 py-2 rounded-xl text-xs font-bold bg-slate-900 text-white shadow-xs"
          }, "📖 奉献记录全册 (当前)")
        ),

        // Right Action Buttons: Print / Export PDF & Logout
        h("div", { className: "flex items-center gap-2" },
          h("button", {
            type: "button",
            onClick: () => window.print(),
            className: "inline-flex items-center gap-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-xl shadow-sm shadow-blue-500/20 transition-all active:scale-95"
          },
            h(PrinterIcon, { size: 15 }),
            h("span", null, "🖨️ 打印 / 导出 PDF")
          ),
          h("button", {
            type: "button",
            onClick: onLogout,
            className: "inline-flex items-center gap-1 px-3.5 py-2 bg-slate-100 hover:bg-rose-50 text-slate-700 hover:text-rose-600 border border-slate-200 rounded-xl text-xs font-bold transition-all"
          },
            "🚪 退出"
          )
        )
      ),

      // Row 2: Month Selector Buttons (1月 - 12月 + 全部月份)
      h("div", { className: "flex items-center flex-wrap gap-1.5" },
        h("span", { className: "text-xs font-bold text-slate-500 mr-1" }, "选择月份:"),
        Array.from({ length: 12 }, (_, i) => i + 1).map((m) =>
          h("button", {
            key: m,
            type: "button",
            onClick: () => setSelectedMonth(m),
            className: `px-3 py-1.5 rounded-xl text-xs font-bold border transition-all ${
              selectedMonth === m
                ? "bg-slate-900 text-white border-slate-900 shadow-xs"
                : "bg-white hover:bg-slate-100 text-slate-700 border-slate-200"
            }`
          }, `${m}月`)
        ),
        h("button", {
          type: "button",
          onClick: () => setSelectedMonth("all"),
          className: `px-3.5 py-1.5 rounded-xl text-xs font-bold border transition-all ml-1 ${
            selectedMonth === "all"
              ? "bg-indigo-600 text-white border-indigo-600 shadow-xs"
              : "bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border-indigo-200"
          }`
        }, "📚 全部月份 (1-12月连排)")
      )
    ),

    // Paper-Style Offering Sheets
    h("div", { className: "space-y-8 pb-12" },
      monthsToRender.map((m) => {
        const mData = yearLedger.monthsMap[m] || {
          openingBf: 0,
          rows: [],
          closingBalance: 0
        };
        const txRows = mData.rows || [];
        const blankCount = Math.max(2, 7 - txRows.length);
        const lastDay = new Date(selectedYear, m, 0).getDate();
        const endOfMonthDateStr = `${lastDay}/${m}/${selectedYear}`;

        return h("div", {
          key: m,
          id: `month-${selectedYear}-${String(m).padStart(2, "0")}`,
          className: "booklet-sheet"
        },
          // Paper Sheet Title
          h("h1", null, "小组每月奉献记录"),

          // Paper Sheet Header Metadata
          h("div", { className: "hdr" },
            h("span", null,
              "小组编号：",
              h("u", null, `__${groupCode}___`)
            ),
            h("span", null,
              "点算同工：",
              h("u", null, counters)
            ),
            h("span", null,
              `月份：_${m} / ${selectedYear}`
            )
          ),

          // Strictly Bordered Paper Table
          h("table", { className: "paper-table" },
            h("colgroup", null,
              h("col", { style: { width: "62px" } }),
              h("col", { style: { width: "210px" } }),
              h("col", { style: { width: "86px" } }),
              h("col", { style: { width: "86px" } }),
              h("col", { style: { width: "88px" } }),
              h("col", { style: { width: "68px" } }),
              h("col", { style: { width: "68px" } }),
              canDelete && h("col", { className: "col-act" })
            ),
            h("thead", null,
              h("tr", null,
                h("th", null, "日期"),
                h("th", null, "事项"),
                h("th", null, "数目-收入"),
                h("th", null, "数目-支出"),
                h("th", null, "结存"),
                h("th", null, "签名"),
                h("th", null, "签名"),
                canDelete && h("th", { className: "col-act" })
              )
            ),
            h("tbody", null,
              // Row 1: Opening Balance b/f
              h("tr", null,
                h("td", { className: "d" }, ""),
                h("td", { className: "i", style: { fontWeight: 600 } }, "Balance b/f"),
                h("td", { className: "n" }, Number.isInteger(mData.openingBf) ? String(mData.openingBf) : mData.openingBf.toFixed(2)),
                h("td", { className: "n" }, ""),
                h("td", { className: "b", style: { fontWeight: 600 } }, Number.isInteger(mData.openingBf) ? String(mData.openingBf) : mData.openingBf.toFixed(2)),
                h("td", null, ""),
                h("td", null, ""),
                canDelete && h("td", { className: "col-act" })
              ),

              // Subsequent Chronological Transaction Rows
              txRows.map((tx) => {
                const incStr = tx.income > 0 ? (Number.isInteger(tx.income) ? String(tx.income) : tx.income.toFixed(2)) : "";
                const expStr = tx.expense > 0 ? (Number.isInteger(tx.expense) ? String(tx.expense) : tx.expense.toFixed(2)) : "";
                const balStr = Number.isInteger(tx.balance) ? String(tx.balance) : tx.balance.toFixed(2);

                return h("tr", { key: tx.id },
                  h("td", { className: "d" }, tx.shortDate || tx.date),
                  h("td", { className: "i" }, tx.item),
                  h("td", { className: "n" }, incStr),
                  h("td", { className: "n" }, expStr),
                  h("td", { className: "b" }, balStr),
                  h("td", null, ""),
                  h("td", null, ""),
                  canDelete && h("td", { className: "col-act no-print print:hidden" },
                    h("button", {
                      type: "button",
                      className: "btn-del",
                      onClick: () => handleInlineDelete(tx),
                      title: "删除此行记录"
                    }, "🗑️ 删除")
                  )
                );
              }),

              // Blank Padding Rows for Traditional Printed Ledger Form
              Array.from({ length: blankCount }, (_, idx) =>
                h("tr", { key: `blank-${m}-${idx}` },
                  h("td", { className: "x" }, ""),
                  h("td", { className: "x" }, ""),
                  h("td", { className: "x" }, ""),
                  h("td", { className: "x" }, ""),
                  h("td", { className: "x" }, ""),
                  h("td", { className: "x" }, ""),
                  h("td", { className: "x" }, ""),
                  canDelete && h("td", { className: "col-act" })
                )
              )
            )
          ),

          // Paper Sheet Footer Signatures
          h("div", { className: "foot" },
            h("div", { className: "row" },
              h("div", { className: "left-col" }, `Verify by: ________${verifyBy}__________`),
              h("div", { className: "right-col" }, `Name     :  _______${verifyName}___________`)
            ),
            h("div", { className: "row row-date" },
              h("div", { className: "left-col" }, `Date:  _______${endOfMonthDateStr}_______`)
            )
          )
        );
      })
    )
  );
}

// ============================================================================
// Main Application Container with RBAC & Unified Routing
// ============================================================================
function normalizeServerUser(u) {
  const role = u.role === "admin" ? "admin" : "user";
  const out = {
    email: u.email,
    name: u.name || String(u.email).split("@")[0],
    role
  };
  if (u.permissions && typeof u.permissions === "object") out.permissions = u.permissions;
  return out;
}

function GroupFinanceApp() {
  // 1. User Accounts & Role Configuration State
  const [userAccounts, setUserAccounts] = useState(() => DEFAULT_USER_ACCOUNTS);

  // 2. Current Logged-in User State (Null until logged in, or restored from active session)
  // The server is the source of truth for identity. localStorage only tells us whether to show a loading
  // state while `whoami` answers; the cached role is never used to render admin-only UI.
  const [currentUser, setCurrentUser] = useState(null);
  const [sessionChecking, setSessionChecking] = useState(() => {
    try {
      return !!(localStorage.getItem("sessionToken") || localStorage.getItem("authToken"));
    } catch {
      return false;
    }
  });
  const [notice, setNotice] = useState(null);

  // 3. Preset Income & Expense Items State
  const [incomeItems, setIncomeItems] = useState(() => {
    try {
      const saved = localStorage.getItem("gf_income_items");
      return saved ? JSON.parse(saved) : DEFAULT_INCOME_ITEMS;
    } catch {
      return DEFAULT_INCOME_ITEMS;
    }
  });

  const [expenseItems, setExpenseItems] = useState(() => {
    try {
      const saved = localStorage.getItem("gf_expense_items");
      return saved ? JSON.parse(saved) : DEFAULT_EXPENSE_ITEMS;
    } catch {
      return DEFAULT_EXPENSE_ITEMS;
    }
  });

  // 4. Booklet Header & Signature Metadata State
  const [bookletSettings, setBookletSettings] = useState(() => {
    try {
      const saved = localStorage.getItem("gf_booklet_settings");
      return saved ? { ...DEFAULT_BOOKLET_SETTINGS, ...JSON.parse(saved) } : DEFAULT_BOOKLET_SETTINGS;
    } catch {
      return DEFAULT_BOOKLET_SETTINGS;
    }
  });

  // 5. Master Ledger Transactions State
  const [transactions, setTransactions] = useState(() => {
    try {
      const saved = localStorage.getItem("gf_transactions");
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0) return parsed;
      }
    } catch {
      // Fallback to seed
    }
    return INITIAL_SEED_TRANSACTIONS;
  });
  const [loadingTransactions, setLoadingTransactions] = useState(false);

  // 6. Google OAuth Client ID & OAuth Error State
  const [googleClientId, setGoogleClientId] = useState("");
  const [oauthError, setOauthError] = useState(() => {
    try {
      const params = new URLSearchParams(window.location.search);
      return params.get("oauth_error") || null;
    } catch {
      return null;
    }
  });

  // 7. Toast Callback (No-op per user preference to disable floating banner)
  // Success toasts stay disabled; warnings and errors (refusals, redirects) are shown in a small banner.
  const showToast = useCallback((msg, type) => {
    if (type !== "warning" && type !== "error") return;
    setNotice({ msg, type });
  }, []);
  useEffect(() => {
    if (!notice) return undefined;
    const t = setTimeout(() => setNotice(null), 6000);
    return () => clearTimeout(t);
  }, [notice]);

  // Permissions come from the server's user object; fall back to role only if `permissions` is missing.
  const perms = currentUser?.permissions;
  const isAdminRole = currentUser?.role === "admin";
  const canViewDatabase = !!currentUser && (perms ? perms.can_view_database === true : isAdminRole);
  const canEditRecord = !!currentUser && (perms ? perms.can_edit_record === true : isAdminRole);
  const canDeleteRecord = !!currentUser && (perms ? perms.can_delete_record === true : isAdminRole);

  // Cache the server-provided identity (hint only)
  useEffect(() => {
    if (!currentUser) return;
    localStorage.setItem("currentUser", JSON.stringify(currentUser));
  }, [currentUser]);

  const clearSession = useCallback(() => {
    localStorage.removeItem("sessionToken");
    localStorage.removeItem("authToken");
    localStorage.removeItem("currentUser");
    localStorage.removeItem("gf_user_accounts");
    setCurrentUser(null);
    setSessionChecking(false);
  }, []);

  // Central 401 handling: any signed-in action answered 401 signs the user out.
  useEffect(() => {
    onSessionExpired = () => {
      if (!localStorage.getItem("sessionToken") && !localStorage.getItem("authToken")) return;
      clearSession();
      window.history.replaceState(null, "", "/app?tab=entry");
      setActiveTab("entry");
      setNotice({ msg: "登录已过期，请重新登录", type: "warning" });
    };
    return () => { onSessionExpired = null; };
  }, [clearSession]);

  // Verify the stored session with the server on load.
  useEffect(() => {
    const token = localStorage.getItem("sessionToken") || localStorage.getItem("authToken");
    if (!token) {
      setSessionChecking(false);
      return;
    }
    let cancelled = false;
    (async () => {
      try {
        const { ok, status, data } = await apiPost("whoami");
        if (cancelled) return;
        if (ok && data && data.user && data.user.email) {
          if (!localStorage.getItem("sessionToken")) localStorage.setItem("sessionToken", token);
          setCurrentUser(normalizeServerUser(data.user));
        } else if (status === 401 || status === 403) {
          clearSession();
        } else {
          // Unexpected server answer: do not trust the cached role.
          clearSession();
        }
      } catch {
        // Network failure: identity cannot be verified, so show the login screen without trusting the cached
        // role. The token is kept so a reload can retry.
        if (!cancelled) setCurrentUser(null);
      } finally {
        if (!cancelled) setSessionChecking(false);
      }
    })();
    return () => { cancelled = true; };
  }, [clearSession]);

  // Determine Initial Tab from URL (/booklet, /app?tab=database-view, /app?tab=entry)
  const resolveTabFromUrl = useCallback(() => {
    const path = window.location.pathname;
    const params = new URLSearchParams(window.location.search);
    const tabParam = params.get("tab");
    if (path.startsWith("/booklet") || tabParam === "booklet") {
      return "booklet";
    }
    if (tabParam === "database-view") {
      return "database-view";
    }
    return "entry";
  }, []);

  const [activeTab, setActiveTab] = useState(() => resolveTabFromUrl());

  // Enforce RBAC on Route / Tab changes once logged in
  useEffect(() => {
    if (!currentUser) return;
    const checkAndEnforceRbac = () => {
      const targetTab = resolveTabFromUrl();
      if (!canViewDatabase && (targetTab === "database-view" || activeTab === "database-view")) {
        window.history.replaceState(null, "", "/app?tab=entry");
        setActiveTab("entry");
        showToast("⚠️ 已为您自动跳转至【记账录入】页面", "warning");
      } else {
        setActiveTab(targetTab);
      }
    };

    checkAndEnforceRbac();
    window.addEventListener("popstate", checkAndEnforceRbac);
    return () => window.removeEventListener("popstate", checkAndEnforceRbac);
  }, [currentUser, canViewDatabase, activeTab, resolveTabFromUrl, showToast]);

  // Navigate between tabs with RBAC guard
  const handleNavigateTab = useCallback((targetTab) => {
    if (!canViewDatabase && targetTab === "database-view") {
      window.history.replaceState(null, "", "/app?tab=entry");
      setActiveTab("entry");
      showToast("⚠️ 已为您自动跳转至【记账录入】页面", "warning");
      return;
    }
    setActiveTab(targetTab);
    if (targetTab === "booklet") {
      window.history.pushState(null, "", "/booklet");
    } else if (targetTab === "database-view") {
      window.history.pushState(null, "", "/app?tab=database-view");
    } else {
      window.history.pushState(null, "", "/app?tab=entry");
    }
  }, [canViewDatabase, showToast]);

  // Fetch Transactions from Backend API & Merge/Sync
  const fetchTransactionsFromApi = useCallback(async (showFeedback = false) => {
    setLoadingTransactions(true);
    try {
      const { ok, data } = await apiPost("list_transactions", { limit: 500 });
      if (!ok && data && data.message && showFeedback) {
        showToast(`⚠️ ${data.message}`, "warning");
        return;
      }
      if (ok && data.status === "success" && Array.isArray(data.transactions) && data.transactions.length > 0) {
        const normalized = data.transactions.map((t, i) => normalizeTx(t, i));
        setTransactions(normalized);
        localStorage.setItem("gf_transactions", JSON.stringify(normalized));
      }
      if (showFeedback) {
        showToast("✅ 数据已刷新并与总账同步");
      }
    } catch {
      if (showFeedback) {
        showToast("✅ 数据已刷新并与总账同步");
      }
    } finally {
      setLoadingTransactions(false);
    }
  }, [showToast]);

  useEffect(() => {
    try {
      const params = new URLSearchParams(window.location.search);
      const errParam = params.get("oauth_error");
      if (errParam) {
        setOauthError(errParam);
        params.delete("oauth_error");
        const cleanQuery = params.toString();
        window.history.replaceState(null, "", window.location.pathname + (cleanQuery ? `?${cleanQuery}` : ""));
      }
    } catch {
      // Ignore URL parse error
    }

    (async () => {
      try {
        const { ok, data } = await apiPost("get_settings", {});
        if (ok && data && data.status === "success") {
          if (data.google_client_id || data.settings?.google_client_id) {
            setGoogleClientId(data.google_client_id || data.settings.google_client_id);
          }
          if (data.settings?.income_items?.length) {
            setIncomeItems(data.settings.income_items);
            localStorage.setItem("gf_income_items", JSON.stringify(data.settings.income_items));
          }
          if (data.settings?.expense_items?.length) {
            setExpenseItems(data.settings.expense_items);
            localStorage.setItem("gf_expense_items", JSON.stringify(data.settings.expense_items));
          }
          if (data.settings?.booklet) {
            setBookletSettings((prev) => {
              const merged = { ...prev, ...data.settings.booklet };
              localStorage.setItem("gf_booklet_settings", JSON.stringify(merged));
              return merged;
            });
          }
          if (Array.isArray(data.users) && data.users.length) {
            setUserAccounts(data.users);
            localStorage.setItem("gf_user_accounts", JSON.stringify(data.users));
          }
        }
      } catch {
        // Fallback to localStorage defaults
      }
    })();
  }, [currentUser?.email]);

  // Load the ledger only once the server has confirmed who is signed in.
  useEffect(() => {
    if (!currentUser) return;
    fetchTransactionsFromApi(false);
  }, [currentUser?.email, fetchTransactionsFromApi]);

  // Handlers for CRUD & Settings
  const handleRecordAdded = useCallback((newEntry, msg) => {
    setTransactions((prev) => {
      const next = [...prev, normalizeTx(newEntry, prev.length)];
      localStorage.setItem("gf_transactions", JSON.stringify(next));
      return next;
    });
    fetchTransactionsFromApi(false);
    showToast(msg || "✅ 记录已成功保存！数据已实时同步");
  }, [fetchTransactionsFromApi, showToast]);

  const handleCreateTransaction = useCallback(async ({ date, item, income, expense, user }) => {
    let realId = "tx-" + Date.now();
    try {
      const res = await apiPost("add_record", { date, item, income, expense, user });
      const refusal = refusalMessage(res);
      if (refusal) {
        if (res.status !== 401) showToast(`⚠️ ${refusal}`, "warning");
        return;
      }
      if (res && res.ok && res.data) {
        realId = res.data.id || res.data.transaction?.id || realId;
      }
    } catch {
      // Fallback to local ID
    }
    const createdTx = { id: realId, date, item, income, expense, user };
    setTransactions((prev) => {
      const next = [...prev, normalizeTx(createdTx, prev.length)];
      localStorage.setItem("gf_transactions", JSON.stringify(next));
      return next;
    });
    await fetchTransactionsFromApi(false);
    showToast("✅ 记录已成功新增！收支总账与奉献册子已实时同步");
  }, [fetchTransactionsFromApi, showToast]);

  const handleUpdateTransaction = useCallback(async (updatedTx) => {
    if (!canEditRecord) return;
    try {
      const res = await apiPost("update_record", {
        id: updatedTx.id,
        date: updatedTx.date,
        item: updatedTx.item,
        income: updatedTx.income,
        expense: updatedTx.expense,
        user: updatedTx.user
      });
      const refusal = refusalMessage(res);
      if (refusal) {
        if (res.status !== 401) showToast(`⚠️ ${refusal}`, "warning");
        return;
      }
    } catch {
      // Network exception only: continue with local state update (offline fallback)
    }
    setTransactions((prev) => {
      const next = prev.map((t) => (t.id === updatedTx.id ? normalizeTx(updatedTx) : t));
      localStorage.setItem("gf_transactions", JSON.stringify(next));
      return next;
    });
    await fetchTransactionsFromApi(false);
    showToast("✅ 记录已成功修改！收支总账与奉献册子已实时同步");
  }, [canEditRecord, fetchTransactionsFromApi, showToast]);

  const handleDeleteTransaction = useCallback(async (targetTx) => {
    if (!canDeleteRecord) return;
    try {
      const res = await apiPost("delete_record", {
        id: targetTx.id,
        year: targetTx.year,
        month: targetTx.month,
        date: targetTx.shortDate || targetTx.date,
        item: targetTx.item,
        income: targetTx.income,
        expense: targetTx.expense
      });
      const refusal = refusalMessage(res);
      if (refusal) {
        if (res.status !== 401) showToast(`⚠️ ${refusal}`, "warning");
        return;
      }
    } catch {
      // Network exception only: continue with local state update (offline fallback)
    }
    setTransactions((prev) => {
      const next = prev.filter((t) => t.id !== targetTx.id);
      localStorage.setItem("gf_transactions", JSON.stringify(next));
      return next;
    });
    await fetchTransactionsFromApi(false);
    showToast("✅ 记录已成功删除！结余已重新计算并实时同步");
  }, [canDeleteRecord, fetchTransactionsFromApi, showToast]);

  const handleUpdateCategoryPresets = useCallback(async (nextIncome, nextExpense) => {
    try {
      const res = await apiPost("update_settings", {
        income_items: nextIncome,
        expense_items: nextExpense
      });
      const refusal = refusalMessage(res);
      if (refusal) {
        if (res.status !== 401) showToast(`⚠️ ${refusal}`, "warning");
        return;
      }
    } catch {
      // Network exception only: keep local copy (offline fallback)
    }
    setIncomeItems(nextIncome);
    setExpenseItems(nextExpense);
    localStorage.setItem("gf_income_items", JSON.stringify(nextIncome));
    localStorage.setItem("gf_expense_items", JSON.stringify(nextExpense));
    showToast("✅ 收入与支出事项分类已更新并同步至记账录入！");
  }, [showToast]);

  const handleUpdateUserAccounts = useCallback(async (nextAccounts, changedAccount, removedEmail) => {
    try {
      if (removedEmail) {
        const res = await apiPost("delete_user", { email: removedEmail });
        const refusal = refusalMessage(res);
        if (refusal) {
          if (res.status !== 401) showToast(`⚠️ ${refusal}`, "warning");
          return;
        }
      }
      if (changedAccount) {
        const res = await apiPost("update_user_role", {
          email: changedAccount.email,
          name: changedAccount.name,
          role: changedAccount.role
        });
        const refusal = refusalMessage(res);
        if (refusal) {
          if (res.status !== 401) showToast(`⚠️ ${refusal}`, "warning");
          return;
        }
      }
    } catch {
      // Network exception only: keep local copy (offline fallback)
    }
    setUserAccounts(nextAccounts);
    localStorage.setItem("gf_user_accounts", JSON.stringify(nextAccounts));
    if (changedAccount && currentUser && currentUser.email.toLowerCase() === changedAccount.email.toLowerCase()) {
      // Own role changed: re-read identity from the server rather than trusting the edit.
      try {
        const who = await apiPost("whoami");
        if (who.ok && who.data && who.data.user) setCurrentUser(normalizeServerUser(who.data.user));
      } catch {
        // ignore
      }
    }
    showToast("✅ 同工权限设定已保存并实时生效！");
  }, [currentUser, showToast]);

  const handleUpdateBookletSettings = useCallback(async (nextBooklet) => {
    try {
      const res = await apiPost("update_settings", { booklet: nextBooklet });
      const refusal = refusalMessage(res);
      if (refusal) {
        if (res.status !== 401) showToast(`⚠️ ${refusal}`, "warning");
        return;
      }
    } catch {
      // Network exception only: keep local copy (offline fallback)
    }
    setBookletSettings(nextBooklet);
    localStorage.setItem("gf_booklet_settings", JSON.stringify(nextBooklet));
    showToast("✅ 奉献册子表头与签名配置已保存并实时同步！");
  }, [showToast]);

  const handleUpdateGoogleOAuth = useCallback(async (clientId, clientSecret) => {
    try {
      const payload = { google_client_id: clientId };
      if (clientSecret) payload.google_client_secret = clientSecret;
      const res = await apiPost("update_settings", payload);
      const refusal = refusalMessage(res);
      if (refusal) {
        if (res.status !== 401) showToast(`⚠️ ${refusal}`, "warning");
        return;
      }
    } catch {
      // Network exception only (offline fallback)
    }
    setGoogleClientId(clientId);
    showToast("✅ Google OAuth 登录配置已保存！");
  }, [showToast]);

  // Login Handler: Check role permission & route to appropriate workspace
  const handleLoginSuccess = useCallback((token, userObj) => {
    localStorage.setItem("sessionToken", token);
    // Role and permissions come from the server's user object; the client never infers them.
    const normalizedUser = normalizeServerUser(userObj);
    localStorage.setItem("currentUser", JSON.stringify(normalizedUser));
    setCurrentUser(normalizedUser);
    setOauthError(null);

    const targetTab = resolveTabFromUrl();
    const allowDb = normalizedUser.permissions
      ? normalizedUser.permissions.can_view_database === true
      : normalizedUser.role === "admin";
    if (!allowDb && targetTab === "database-view") {
      window.history.replaceState(null, "", "/app?tab=entry");
      setActiveTab("entry");
    } else {
      setActiveTab(targetTab);
    }
    showToast(`✅ 登录成功 (${normalizedUser.email})`);
  }, [resolveTabFromUrl, showToast]);

  // Logout Handler: tell the server (clears the HttpOnly session cookie), then clear local state
  const handleLogout = useCallback(async () => {
    try {
      await apiPost("logout");
    } catch {
      // Ignore failure: local sign-out proceeds regardless
    }
    clearSession();
    window.history.replaceState(null, "", "/app?tab=entry");
    setActiveTab("entry");
    showToast("已安全退出登录");
  }, [clearSession, showToast]);

  // Step 1: If not logged in, render Full-Page Login & Role Verification Screen
  const noticeEl = notice && h("div", {
    role: "alert",
    "data-testid": "notice",
    className: "fixed top-4 left-1/2 -translate-x-1/2 z-50 px-4 py-2.5 rounded-xl bg-amber-50 border border-amber-200 text-amber-800 text-sm font-semibold shadow-lg no-print print:hidden"
  }, notice.msg);

  if (sessionChecking) {
    return h("div", { className: "min-h-screen bg-slate-50 flex items-center justify-center text-slate-500 text-sm font-semibold", "data-testid": "session-loading" },
      "正在验证登录状态…"
    );
  }

  if (!currentUser) {
    return h("div", { className: "min-h-screen bg-slate-50 font-sans text-slate-900 relative" },
      noticeEl,
      h(LoginScreen, {
        userAccounts,
        googleClientId,
        initialError: oauthError,
        onLoginSuccess: handleLoginSuccess
      })
    );
  }

  // Step 2: Authenticated Workspace (Role-checked Header & Modules)
  return h("div", { className: "min-h-screen bg-slate-50 font-sans text-slate-900 pb-16 relative" },
    // Ambient Background Blurs (Hidden when printing)
    h("div", { className: "fixed top-0 left-0 w-full h-full overflow-hidden pointer-events-none -z-10 no-print print:hidden" },
      h("div", { className: "absolute top-[-5%] left-[-5%] w-96 h-96 bg-blue-500/10 rounded-full blur-3xl" }),
      h("div", { className: "absolute top-[30%] right-[-5%] w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl" })
    ),

    noticeEl,
    // Unified Top Banner Navigation (Displays modules based on server-provided permissions)
    h(AppHeader, {
      currentUser,
      canViewDatabase,
      activeTab,
      onNavigateTab: handleNavigateTab,
      onLogout: handleLogout,
      bookletSettings
    }),

    // Main Content Area
    h("main", { className: "max-w-7xl mx-auto px-4 pt-6" },
      // Module 1: 📝 记账录入 (Accessible by User & Admin)
      activeTab === "entry" && h(RecordEntryTab, {
        currentUser,
        incomeItems,
        expenseItems,
        onRecordAdded: handleRecordAdded,
        recentTransactions: transactions.slice().reverse()
      }),

      // Module 2: 🗄️ 数据库管理 (Admin Exclusive)
      activeTab === "database-view" && canViewDatabase && h(DatabaseViewTab, {
        currentUser,
        transactions,
        loadingTransactions,
        onRefreshTransactions: fetchTransactionsFromApi,
        onCreateTransaction: handleCreateTransaction,
        onUpdateTransaction: handleUpdateTransaction,
        onDeleteTransaction: handleDeleteTransaction,
        incomeItems,
        expenseItems,
        onUpdateCategoryPresets: handleUpdateCategoryPresets,
        userAccounts,
        onUpdateUserAccounts: handleUpdateUserAccounts,
        bookletSettings,
        onUpdateBookletSettings: handleUpdateBookletSettings,
        googleClientId,
        onUpdateGoogleOAuth: handleUpdateGoogleOAuth,
        showToast
      }),

      // Module 3: 📖 奉献记录全册 (User Read-Only / Admin Editable)
      activeTab === "booklet" && h(BookletViewTab, {
        canViewDatabase,
        canDelete: canDeleteRecord,
        transactions,
        bookletSettings,
        onDeleteTransaction: handleDeleteTransaction,
        onNavigateTab: handleNavigateTab,
        onLogout: handleLogout
      })
    )
  );
}

// ============================================================================
// Mount Root
// ============================================================================
const rootEl = document.getElementById("root");
if (rootEl) {
  const root = hy.createRoot(rootEl);
  root.render(h(fy.StrictMode, null, h(GroupFinanceApp)));
}
