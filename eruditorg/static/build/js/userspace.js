!function(t){function e(e){for(var r,a,c=e[0],u=e[1],s=e[2],f=0,d=[];f<c.length;f++)a=c[f],Object.prototype.hasOwnProperty.call(o,a)&&o[a]&&d.push(o[a][0]),o[a]=0;for(r in u)Object.prototype.hasOwnProperty.call(u,r)&&(t[r]=u[r]);for(l&&l(e);d.length;)d.shift()();return i.push.apply(i,s||[]),n()}function n(){for(var t,e=0;e<i.length;e++){for(var n=i[e],r=!0,c=1;c<n.length;c++){var u=n[c];0!==o[u]&&(r=!1)}r&&(i.splice(e--,1),t=a(a.s=n[0]))}return t}var r={},o={3:0},i=[];function a(e){if(r[e])return r[e].exports;var n=r[e]={i:e,l:!1,exports:{}};return t[e].call(n.exports,n,n.exports,a),n.l=!0,n.exports}a.m=t,a.c=r,a.d=function(t,e,n){a.o(t,e)||Object.defineProperty(t,e,{enumerable:!0,get:n})},a.r=function(t){"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(t,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(t,"__esModule",{value:!0})},a.t=function(t,e){if(1&e&&(t=a(t)),8&e)return t;if(4&e&&"object"==typeof t&&t&&t.__esModule)return t;var n=Object.create(null);if(a.r(n),Object.defineProperty(n,"default",{enumerable:!0,value:t}),2&e&&"string"!=typeof t)for(var r in t)a.d(n,r,function(e){return t[e]}.bind(null,r));return n},a.n=function(t){var e=t&&t.__esModule?function(){return t.default}:function(){return t};return a.d(e,"a",e),e},a.o=function(t,e){return Object.prototype.hasOwnProperty.call(t,e)},a.p="";var c=window.webpackJsonp=window.webpackJsonp||[],u=c.push.bind(c);c.push=e,c=c.slice();for(var s=0;s<c.length;s++)e(c[s]);var l=u;i.push([335,0]),n()}({135:function(t,e){t.exports=jQuery},335:function(t,e,n){n(352),t.exports=n(338)},336:function(t,e,n){n(11)(n(337))},337:function(t,e){t.exports='!function(t,e){"object"==typeof exports&&"undefined"!=typeof module?e(exports):"function"==typeof define&&define.amd?define(["exports"],e):e((t=t||self).clipboard={})}(this,function(t){"use strict";function e(t,e,n,r){return new(n||(n=Promise))(function(o,i){function a(t){try{c(r.next(t))}catch(t){i(t)}}function u(t){try{c(r.throw(t))}catch(t){i(t)}}function c(t){t.done?o(t.value):new n(function(e){e(t.value)}).then(a,u)}c((r=r.apply(t,e||[])).next())})}function n(t,e){var n,r,o,i,a={label:0,sent:function(){if(1&o[0])throw o[1];return o[1]},trys:[],ops:[]};return i={next:u(0),throw:u(1),return:u(2)},"function"==typeof Symbol&&(i[Symbol.iterator]=function(){return this}),i;function u(i){return function(u){return function(i){if(n)throw new TypeError("Generator is already executing.");for(;a;)try{if(n=1,r&&(o=2&i[0]?r.return:i[0]?r.throw||((o=r.return)&&o.call(r),0):r.next)&&!(o=o.call(r,i[1])).done)return o;switch(r=0,o&&(i=[2&i[0],o.value]),i[0]){case 0:case 1:o=i;break;case 4:return a.label++,{value:i[1],done:!1};case 5:a.label++,r=i[1],i=[0];continue;case 7:i=a.ops.pop(),a.trys.pop();continue;default:if(!(o=(o=a.trys).length>0&&o[o.length-1])&&(6===i[0]||2===i[0])){a=0;continue}if(3===i[0]&&(!o||i[1]>o[0]&&i[1]<o[3])){a.label=i[1];break}if(6===i[0]&&a.label<o[1]){a.label=o[1],o=i;break}if(o&&a.label<o[2]){a.label=o[2],a.ops.push(i);break}o[2]&&a.ops.pop(),a.trys.pop();continue}i=e.call(t,a)}catch(t){i=[6,t],r=0}finally{n=o=0}if(5&i[0])throw i[1];return{value:i[0]?i[1]:void 0,done:!0}}([i,u])}}}var r=["text/plain","text/html"];var o=function(){(console.warn||console.log).call(arguments)}.bind(console,"[clipboard-polyfill]"),i=!0;var a=function(){function t(){this.m={}}return t.prototype.setData=function(t,e){i&&-1===r.indexOf(t)&&o("Unknown data type: "+t,"Call clipboard.suppressWarnings() to suppress this warning."),this.m[t]=e},t.prototype.getData=function(t){return this.m[t]},t.prototype.forEach=function(t){for(var e in this.m)t(this.m[e],e)},t}(),u=function(t){},c=!0;var s=function(){(console.warn||console.log).apply(console,arguments)}.bind("[clipboard-polyfill]"),d="text/plain";function l(t){u=t}function f(){c=!1,i=!1}function p(t){return e(this,void 0,void 0,function(){var e;return n(this,function(n){if(c&&!t.getData(d)&&s("clipboard.write() was called without a `text/plain` data type. On some platforms, this may result in an empty clipboard. Call clipboard.suppressWarnings() to suppress this warning."),k()){if(function(t){var e=t.getData(d);if(void 0!==e)return window.clipboardData.setData("Text",e);throw new Error("No `text/plain` value was specified.")}(t))return[2];throw new Error("Copying failed, possibly because the user rejected it.")}if(x(t))return u("regular execCopy worked"),[2];if(navigator.userAgent.indexOf("Edge")>-1)return u(\'UA "Edge" => assuming success\'),[2];if(D(document.body,t))return u("copyUsingTempSelection worked"),[2];if(function(t){var e=document.createElement("div");e.setAttribute("style","-webkit-user-select: text !important"),e.textContent="temporary element",document.body.appendChild(e);var n=D(e,t);return document.body.removeChild(e),n}(t))return u("copyUsingTempElem worked"),[2];if(void 0!==(e=t.getData(d))&&function(t){u("copyTextUsingDOM");var e=document.createElement("div");e.setAttribute("style","-webkit-user-select: text !important");var n=e;e.attachShadow&&(u("Using shadow DOM."),n=e.attachShadow({mode:"open"}));var r=document.createElement("span");r.innerText=t,n.appendChild(r),document.body.appendChild(e),T(r);var o=document.execCommand("copy");return E(),document.body.removeChild(e),o}(e))return u("copyTextUsingDOM worked"),[2];throw new Error("Copy command failed.")})})}function v(t){return e(this,void 0,void 0,function(){return n(this,function(e){return navigator.clipboard&&navigator.clipboard.writeText?(u("Using `navigator.clipboard.writeText()`."),[2,navigator.clipboard.writeText(t)]):[2,p(C(t))]})})}function h(){return e(this,void 0,void 0,function(){var t;return n(this,function(e){switch(e.label){case 0:return t=C,[4,b()];case 1:return[2,t.apply(void 0,[e.sent()])]}})})}function b(){return e(this,void 0,void 0,function(){return n(this,function(t){if(navigator.clipboard&&navigator.clipboard.readText)return u("Using `navigator.clipboard.readText()`."),[2,navigator.clipboard.readText()];if(k())return u("Reading text using IE strategy."),[2,U()];throw new Error("Read is not supported in your browser.")})})}var m=!1;function w(){m||(c&&s(\'The deprecated default object of `clipboard-polyfill` was called. Please switch to `import * as clipboard from "clipboard-polyfill"` and see https://github.com/lgarron/clipboard-polyfill/issues/101 for more info.\'),m=!0)}var y={DT:a,setDebugLog:function(t){return w(),l(t)},suppressWarnings:function(){return w(),f()},write:function(t){return e(this,void 0,void 0,function(){return n(this,function(e){return w(),[2,p(t)]})})},writeText:function(t){return e(this,void 0,void 0,function(){return n(this,function(e){return w(),[2,v(t)]})})},read:function(){return e(this,void 0,void 0,function(){return n(this,function(t){return w(),[2,h()]})})},readText:function(){return e(this,void 0,void 0,function(){return n(this,function(t){return w(),[2,b()]})})}},g=function(){this.success=!1};function x(t){var e=new g,n=function(t,e,n){u("listener called"),t.success=!0,e.forEach(function(e,r){var o=n.clipboardData;o.setData(r,e),r===d&&o.getData(r)!==e&&(u("setting text/plain failed"),t.success=!1)}),n.preventDefault()}.bind(this,e,t);document.addEventListener("copy",n);try{document.execCommand("copy")}finally{document.removeEventListener("copy",n)}return e.success}function D(t,e){T(t);var n=x(e);return E(),n}function T(t){var e=document.getSelection();if(e){var n=document.createRange();n.selectNodeContents(t),e.removeAllRanges(),e.addRange(n)}}function E(){var t=document.getSelection();t&&t.removeAllRanges()}function C(t){var e=new a;return e.setData(d,t),e}function k(){return"undefined"==typeof ClipboardEvent&&void 0!==window.clipboardData&&void 0!==window.clipboardData.setData}function U(){return e(this,void 0,void 0,function(){var t;return n(this,function(e){if(""===(t=window.clipboardData.getData("Text")))throw new Error("Empty clipboard or could not read plain text from clipboard");return[2,t]})})}t.DT=a,t.default=y,t.read=h,t.readText=b,t.setDebugLog=l,t.suppressWarnings=f,t.write=p,t.writeText=v,Object.defineProperty(t,"__esModule",{value:!0})});\n//# sourceMappingURL=clipboard-polyfill.js.map\n'},338:function(t,e,n){},352:function(t,e,n){"use strict";n.r(e);n(92);var r=n(50),o={init:function(){$("#id_contact").select2();var t=!1;function e(e){if(!t){var n=$("#id_submissions").data("files-added"),r=$("#id_submissions").data("files-uploading");if(n||r){if(n)1==confirm(gettext("Certains de vos fichiers n'ont pas étés téléversés. Voulez-vous poursuivre l'enregistrement ?"))&&(t=!0);if(r)1==confirm(gettext("Certains de vos fichiers ne sont pas complètement téléversés. Êtes-vous sûr ?"))&&(t=!0);t||e.preventDefault()}else t=!0}}$("form").submit(e),$("a:not(form a)").click(e),window.onbeforeunload=e}},i=(n(91),{init:function(){var t=function(t){var e="#"+t+"-year",n="#"+t+"-format",r=["#"+t+"-year_start","#"+t+"-year_end","#"+t+"-month_start","#"+t+"-month_end"];for(var o in r)$(r[o]).change((function(){$(e).val("")}));$(e).change((function(){for(var t in r)$(r[t]).val("")})),$(n).change((function(){var t=$(n).val(),r=2011;"csv"==t&&(r=2009),$(e+" > option").show(),$(e+" > option").filter((function(){return $(this).val()<r&&""!=$(this).val()})).hide(),""!=$(e).val()&&$(e).val()<r&&$(e).val(r)}))};t("id_counter_jr1"),t("id_counter_jr1_goa")}});n(336);function a(t,e){for(var n=0;n<e.length;n++){var r=e[n];r.enumerable=r.enumerable||!1,r.configurable=!0,"value"in r&&(r.writable=!0),Object.defineProperty(t,r.key,r)}}var c={"userspace:editor:form":o,"userspace:library:stats:legacy:landing":i,"userspace:library:connection:landing":{init:function(){this.landing=$("#connection"),this.clipboard()},clipboard:function(t){function e(){return t.apply(this,arguments)}return e.toString=function(){return t.toString()},e}((function(){this.landing.find(".clipboard-data").on("click",(function(t){return t&&(t.preventDefault(),t.stopPropagation()),clipboard.writeText($(t.currentTarget).attr("data-clipboard-text")).then((function(){$(t.currentTarget).addClass("success"),setTimeout((function(){$(t.currentTarget).removeClass("success error")}),3e3)}),(function(){$(t.currentTarget).addClass("error"),setTimeout((function(){$(t.currentTarget).removeClass("success error")}),3e3)})),!1}))}))},"userspace:journalinformation:update":new(function(){function t(){!function(t,e){if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t)}var e,n,r;return e=t,(n=[{key:"init",value:function(){$("#id_languages").select2(),this.contributor_fieldset=$('fieldset[name="contributors"]'),this.set_formset_state()}},{key:"set_formset_state",value:function(){var t=this;$("#button-add-contributor").off("click").on("click",(function(e){e.stopPropagation(),t.add_contributor(),t.set_formset_state()})),$("button[data-action='delete']").off("click").on("click",(function(e){e.stopPropagation();var n=$(this).parent().parent().data("object");t.delete_contributor($("div[data-object='"+n+"']")),t.set_formset_state()}));var e=$(this.contributor_fieldset).children('div[class="row"][id]');$(e).each((function(e){$(this).attr("data-object",e),$(t.get_inputs($(this))).each((function(t){var n=$(this).attr("id").replace(/\d+/,e),r=$(this).attr("name").replace(/\d/,e);$(this).attr("id",n),$(this).attr("name",r)}))}));var n=$(this.contributor_fieldset).children('div[class="row"][id]').length,r=$('input[type="hidden"][name$="id"][value]').length;$("#id_contributor_set-TOTAL_FORMS").val(n),$("#id_contributor_set-INITIAL_FORMS").val(r)}},{key:"clear_inputs",value:function(t){var e=this.get_inputs(t);$(e).not('[id$="journal_information"]').not('[id$="id"]').val("")}},{key:"get_inputs",value:function(t){return $(t).find("input").add($(t).find("select"))}},{key:"add_contributor",value:function(){var t=$('fieldset[name="contributors"] > div[class="row"]:last'),e=$(t).clone();this.clear_inputs(e),$(t).after(e)}},{key:"delete_contributor",value:function(t){var e=$(t).find('[id$="name"]').val(),n=window.confirm("Êtes-vous certain de vouloir retirer "+e+" de la liste des collaborateurs?"),r=$(this.contributor_fieldset).data("form-url");if(n){var o=$(t).find('[id$="id"]').val();if(""!==o){var i=this;$.ajax({type:"POST",url:r,data:{contributor_id:o},success:function(){i.clear_inputs(t),$(this.contributor_fieldset).children('div[class="row"][id]').length>1&&$(t).hide()}})}1==$(this.contributor_fieldset).children('div[class="row"][id]').length?this.clear_inputs(t):$(t).remove()}}}])&&a(e.prototype,n),r&&a(e,r),t}())},u=new r.a(c);$(document).ready((function(t){u.init(),$("#id_scope_chooser").select2()}))},39:function(t,e,n){"use strict";n.d(e,"a",(function(){return i}));n(133),n(134);function r(t,e){for(var n=0;n<e.length;n++){var r=e[n];r.enumerable=r.enumerable||!1,r.configurable=!0,"value"in r&&(r.writable=!0),Object.defineProperty(t,r.key,r)}}var o="form#id-login-form";function i(){$(o).validate({rules:{username:{required:!0},password:{required:!0}}})}var a=function(){function t(){!function(t,e){if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t),this.previousURL=null,this.modalSelector="#login-modal, #article-login-modal, #journal-login-modal",this.init()}var e,n,o;return e=t,(n=[{key:"init",value:function(){this.modal()}},{key:"modal",value:function(){var t=this;$(this.modalSelector).magnificPopup({mainClass:"mfp-fade",removalDelay:750,type:"ajax",closeOnBgClick:!1,closeBtnInside:!0,ajax:{settings:{beforeSend:function(t){t.setRequestHeader("X-PJAX","true")}}},callbacks:{beforeOpen:function(){t.previousURL=window.location.pathname},open:function(){history.replaceState(null,null,$($.magnificPopup.instance.currItem.el).attr("href")),$("body").addClass("modal-open")},ajaxContentAdded:function(){i()},close:function(){history.replaceState(null,null,t.previousURL),$("body").removeClass("modal-open")}}})}}])&&r(e.prototype,n),o&&r(e,o),t}();e.b=a},50:function(t,e,n){"use strict";function r(t,e){for(var n=0;n<e.length;n++){var r=e[n];r.enumerable=r.enumerable||!1,r.configurable=!0,"value"in r&&(r.writable=!0),Object.defineProperty(t,r.key,r)}}var o=function(){function t(e){!function(t,e){if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t),this.controllers=void 0===e?{}:e}var e,n,o;return e=t,(n=[{key:"execAction",value:function(t,e){""!==t&&this.controllers[t]&&"function"==typeof this.controllers[t][e]&&this.controllers[t][e]()}},{key:"init",value:function(){if(document.body){var t=document.body,e=t.getAttribute("data-controller"),n=t.getAttribute("data-action");e&&(this.execAction(e,"init"),this.execAction(e,n))}}}])&&r(e.prototype,n),o&&r(e,o),t}();e.a=o},92:function(t,e,n){"use strict";n(93),n(127),n(128),n(129),n(130),n(131),n(132);function r(t,e){for(var n=0;n<e.length;n++){var r=e[n];r.enumerable=r.enumerable||!1,r.configurable=!0,"value"in r&&(r.writable=!0),Object.defineProperty(t,r.key,r)}}var o=function(){function t(){!function(t,e){if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t),this.init()}var e,n,o;return e=t,(n=[{key:"init",value:function(){this.scrollToTop(),this.randomImage()}},{key:"scrollToTop",value:function(){$(".scroll-top").on("click",(function(t){return t&&(t.preventDefault(),t.stopPropagation()),$("html,body").animate({scrollTop:0},450),!1}))}},{key:"randomImage",value:function(){var t=Math.floor(5*Math.random())+1;$("#campaign-banner, #campaign-sidebar").addClass("image"+t)}}])&&r(e.prototype,n),o&&r(e,o),t}();function i(t,e){for(var n=0;n<e.length;n++){var r=e[n];r.enumerable=r.enumerable||!1,r.configurable=!0,"value"in r&&(r.writable=!0),Object.defineProperty(t,r.key,r)}}var a=function(){function t(){!function(t,e){if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t),this.init()}var e,n,r;return e=t,(n=[{key:"init",value:function(){this.svg()}},{key:"svg",value:function(){inlineSVG.init({svgSelector:"img.inline-svg",initClass:"js-inlinesvg"})}}])&&i(e.prototype,n),r&&i(e,r),t}(),c=n(39);function u(t,e){for(var n=0;n<e.length;n++){var r=e[n];r.enumerable=r.enumerable||!1,r.configurable=!0,"value"in r&&(r.writable=!0),Object.defineProperty(t,r.key,r)}}var s=function(){function t(){!function(t,e){if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t),this.init()}var e,n,r;return e=t,(n=[{key:"init",value:function(){this.subNavs(),this.stickyHeader(),this.searchBar()}},{key:"subNavs",value:function(){$("[data-sub-nav]").on("click",(function(t){t.preventDefault();var e=$(this),n=$(e.data("sub-nav"));n.eq(0)&&(e.toggleClass("selected"),n.toggleClass("visible"))}))}},{key:"stickyHeader",value:function(){$(window).on("scroll",(function(t){$(window).scrollTop()>=100?$("header#site-header").addClass("site-header__scrolled"):$("header#site-header").removeClass("site-header__scrolled")}))}},{key:"searchBar",value:function(){$("[data-trigger-search-bar]").on("click",(function(t){var e;t.preventDefault(),e=$("#search-form").hasClass("visible"),$("#search-form").toggleClass("visible"),$("header#site-header").toggleClass("inverted-search-bar"),e||$("#search-form input.search-terms").focus()})),$(document).keyup((function(t){27===t.keyCode&&$(".nav-search-triggers__close").click()}))}}])&&u(e.prototype,n),r&&u(e,r),t}();new o,new a,new c.b,new s;n(91);function l(){return function(t){var e=null;if(document.cookie&&""!=document.cookie)for(var n=document.cookie.split(";"),r=0;r<n.length;r++){var o=jQuery.trim(n[r]);if(o.substring(0,t.length+1)==t+"="){e=decodeURIComponent(o.substring(t.length+1));break}}return e}("csrftoken")}$.ajaxSetup({beforeSend:function(t,e){var n;n=e.type,/^(GET|HEAD|OPTIONS|TRACE)$/.test(n)||this.crossDomain||t.setRequestHeader("X-CSRFToken",l())},data:{csrfmiddlewaretoken:l()}})}});