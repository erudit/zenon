!function(t){var e={};function n(r){if(e[r])return e[r].exports;var o=e[r]={i:r,l:!1,exports:{}};return t[r].call(o.exports,o,o.exports,n),o.l=!0,o.exports}n.m=t,n.c=e,n.d=function(t,e,r){n.o(t,e)||Object.defineProperty(t,e,{enumerable:!0,get:r})},n.r=function(t){"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(t,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(t,"__esModule",{value:!0})},n.t=function(t,e){if(1&e&&(t=n(t)),8&e)return t;if(4&e&&"object"==typeof t&&t&&t.__esModule)return t;var r=Object.create(null);if(n.r(r),Object.defineProperty(r,"default",{enumerable:!0,value:t}),2&e&&"string"!=typeof t)for(var o in t)n.d(r,o,function(e){return t[e]}.bind(null,o));return r},n.n=function(t){var e=t&&t.__esModule?function(){return t.default}:function(){return t};return n.d(e,"a",e),e},n.o=function(t,e){return Object.prototype.hasOwnProperty.call(t,e)},n.p="",n(n.s=79)}({0:function(t,e,n){"use strict";e.a=class{constructor(t){this.controllers=void 0===t?{}:t}execAction(t,e){""!==t&&this.controllers[t]&&"function"==typeof this.controllers[t][e]&&this.controllers[t][e]()}init(){if(document.body){var t=document.body,e=t.getAttribute("data-controller"),n=t.getAttribute("data-action");e&&(this.execAction(e,"init"),this.execAction(e,n))}}}},79:function(t,e,n){n(90),t.exports=n(80)},80:function(t,e,n){},90:function(t,e,n){"use strict";n.r(e);var r=n(0),o={init:function(){var t=this.find_url_fragment();this.set_active_fragment(t[0],t[1])},find_url_fragment:function(){var t=null,e=null;if(window.location.hash){var n=window.location.hash.substring(1);t=$("#"+(n+"-li")),e=$("#"+n)}return[t,e]},set_active_fragment:function(t,e){t||(t=$('[role="presentation"]').first()),e||(e=$('[role="tabpanel"]').first()),$(t).addClass("active"),$(e).addClass("active")}};$(document).ready((function(){new r.a({"public:journal:journal_detail":o}).init()}))}});