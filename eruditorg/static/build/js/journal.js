!function(t){var e={};function n(r){if(e[r])return e[r].exports;var o=e[r]={i:r,l:!1,exports:{}};return t[r].call(o.exports,o,o.exports,n),o.l=!0,o.exports}n.m=t,n.c=e,n.d=function(t,e,r){n.o(t,e)||Object.defineProperty(t,e,{enumerable:!0,get:r})},n.r=function(t){"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(t,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(t,"__esModule",{value:!0})},n.t=function(t,e){if(1&e&&(t=n(t)),8&e)return t;if(4&e&&"object"==typeof t&&t&&t.__esModule)return t;var r=Object.create(null);if(n.r(r),Object.defineProperty(r,"default",{enumerable:!0,value:t}),2&e&&"string"!=typeof t)for(var o in t)n.d(r,o,function(e){return t[e]}.bind(null,o));return r},n.n=function(t){var e=t&&t.__esModule?function(){return t.default}:function(){return t};return n.d(e,"a",e),e},n.o=function(t,e){return Object.prototype.hasOwnProperty.call(t,e)},n.p="",n(n.s=378)}({1:function(t,e,n){"use strict";function r(t,e){for(var n=0;n<e.length;n++){var r=e[n];r.enumerable=r.enumerable||!1,r.configurable=!0,"value"in r&&(r.writable=!0),Object.defineProperty(t,r.key,r)}}var o=function(){function t(e){!function(t,e){if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t),this.controllers=void 0===e?{}:e}var e,n,o;return e=t,(n=[{key:"execAction",value:function(t,e){""!==t&&this.controllers[t]&&"function"==typeof this.controllers[t][e]&&this.controllers[t][e]()}},{key:"init",value:function(){if(document.body){var t=document.body,e=t.getAttribute("data-controller"),n=t.getAttribute("data-action");e&&(this.execAction(e,"init"),this.execAction(e,n))}}}])&&r(e.prototype,n),o&&r(e,o),t}();e.a=o},378:function(t,e,n){n(398),t.exports=n(379)},379:function(t,e,n){},398:function(t,e,n){"use strict";n.r(e);var r=n(1),o={init:function(){var t=this.find_url_fragment();this.set_active_fragment(t[0],t[1])},find_url_fragment:function(){var t=null,e=null;if(window.location.hash){var n=window.location.hash.substring(1);t=$("#"+(n+"-li")),e=$("#"+n)}return[t,e]},set_active_fragment:function(t,e){t||(t=$('[role="presentation"]').first()),e||(e=$('[role="tabpanel"]').first()),$(t).addClass("active"),$(e).addClass("active")}};$(document).ready((function(){new r.a({"public:journal:journal_detail":o}).init()}))}});