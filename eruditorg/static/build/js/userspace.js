!function(e){function t(t){for(var r,a,c=t[0],s=t[1],u=t[2],f=0,d=[];f<c.length;f++)a=c[f],Object.prototype.hasOwnProperty.call(i,a)&&i[a]&&d.push(i[a][0]),i[a]=0;for(r in s)Object.prototype.hasOwnProperty.call(s,r)&&(e[r]=s[r]);for(l&&l(t);d.length;)d.shift()();return o.push.apply(o,u||[]),n()}function n(){for(var e,t=0;t<o.length;t++){for(var n=o[t],r=!0,c=1;c<n.length;c++){var s=n[c];0!==i[s]&&(r=!1)}r&&(o.splice(t--,1),e=a(a.s=n[0]))}return e}var r={},i={3:0},o=[];function a(t){if(r[t])return r[t].exports;var n=r[t]={i:t,l:!1,exports:{}};return e[t].call(n.exports,n,n.exports,a),n.l=!0,n.exports}a.m=e,a.c=r,a.d=function(e,t,n){a.o(e,t)||Object.defineProperty(e,t,{enumerable:!0,get:n})},a.r=function(e){"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(e,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(e,"__esModule",{value:!0})},a.t=function(e,t){if(1&t&&(e=a(e)),8&t)return e;if(4&t&&"object"==typeof e&&e&&e.__esModule)return e;var n=Object.create(null);if(a.r(n),Object.defineProperty(n,"default",{enumerable:!0,value:e}),2&t&&"string"!=typeof e)for(var r in e)a.d(n,r,function(t){return e[t]}.bind(null,r));return n},a.n=function(e){var t=e&&e.__esModule?function(){return e.default}:function(){return e};return a.d(t,"a",t),t},a.o=function(e,t){return Object.prototype.hasOwnProperty.call(e,t)},a.p="";var c=window.webpackJsonp=window.webpackJsonp||[],s=c.push.bind(c);c.push=t,c=c.slice();for(var u=0;u<c.length;u++)t(c[u]);var l=s;o.push([339,0]),n()}({137:function(e,t){e.exports=jQuery},339:function(e,t,n){n(354),e.exports=n(340)},340:function(e,t,n){},354:function(e,t,n){"use strict";n.r(t);n(91);var r=n(50);function i(e,t){for(var n=0;n<t.length;n++){var r=t[n];r.enumerable=r.enumerable||!1,r.configurable=!0,"value"in r&&(r.writable=!0),Object.defineProperty(e,r.key,r)}}var o={"userspace:editor:form":{init:function(){$("#id_contact").select2();var e=!1;function t(t){if(!e){var n=$("#id_submissions").data("files-uploading");if(n){if(n)1==confirm(gettext("Certains de vos fichiers ne sont pas complètement téléversés. Êtes-vous sûr ?"))&&(e=!0);e||t.preventDefault()}else e=!0}}$("form").submit(t),$("a:not(form a)").click(t),window.onbeforeunload=t}},"userspace:library:connection:landing":{init:function(){this.landing=$("#connection"),this.clipboard()},clipboard:function(e){function t(){return e.apply(this,arguments)}return t.toString=function(){return e.toString()},t}((function(){this.landing.find(".clipboard-data").on("click",(function(e){return e&&(e.preventDefault(),e.stopPropagation()),clipboard.writeText($(e.currentTarget).attr("data-clipboard-text")).then((function(){$(e.currentTarget).addClass("success"),setTimeout((function(){$(e.currentTarget).removeClass("success error")}),3e3)}),(function(){$(e.currentTarget).addClass("error"),setTimeout((function(){$(e.currentTarget).removeClass("success error")}),3e3)})),!1}))}))},"userspace:journalinformation:update":new(function(){function e(){!function(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}(this,e)}var t,n,r;return t=e,(n=[{key:"init",value:function(){$("#id_languages").select2(),this.contributor_fieldset=$('fieldset[name="contributors"]'),this.set_formset_state()}},{key:"set_formset_state",value:function(){var e=this;$("#button-add-contributor").off("click").on("click",(function(t){t.stopPropagation(),e.add_contributor(),e.set_formset_state()})),$("button[data-action='delete']").off("click").on("click",(function(t){t.stopPropagation();var n=$(this).parent().parent().data("object");e.delete_contributor($("div[data-object='"+n+"']")),e.set_formset_state()}));var t=$(this.contributor_fieldset).children('div[class="row"][id]');$(t).each((function(t){$(this).attr("data-object",t),$(e.get_inputs($(this))).each((function(e){var n=$(this).attr("id").replace(/\d+/,t),r=$(this).attr("name").replace(/\d/,t);$(this).attr("id",n),$(this).attr("name",r)}))}));var n=$(this.contributor_fieldset).children('div[class="row"][id]').length,r=$('input[type="hidden"][name$="id"][value]').length;$("#id_contributor_set-TOTAL_FORMS").val(n),$("#id_contributor_set-INITIAL_FORMS").val(r)}},{key:"clear_inputs",value:function(e){var t=this.get_inputs(e);$(t).not('[id$="journal_information"]').not('[id$="id"]').val("")}},{key:"get_inputs",value:function(e){return $(e).find("input").add($(e).find("select"))}},{key:"add_contributor",value:function(){var e=$('fieldset[name="contributors"] > div[class="row"]:last'),t=$(e).clone();this.clear_inputs(t),$(e).after(t)}},{key:"delete_contributor",value:function(e){var t=$(e).find('[id$="name"]').val(),n=window.confirm("Êtes-vous certain de vouloir retirer "+t+" de la liste des collaborateurs?"),r=$(this.contributor_fieldset).data("form-url");if(n){var i=$(e).find('[id$="id"]').val();if(""!==i){var o=this;$.ajax({type:"POST",url:r,data:{contributor_id:i},success:function(){o.clear_inputs(e),$(this.contributor_fieldset).children('div[class="row"][id]').length>1&&$(e).hide()}})}1==$(this.contributor_fieldset).children('div[class="row"][id]').length?this.clear_inputs(e):$(e).remove()}}}])&&i(t.prototype,n),r&&i(t,r),e}())},a=new r.a(o);$(document).ready((function(e){a.init(),$("#id_scope_chooser").select2()}))},39:function(e,t,n){"use strict";n.d(t,"a",(function(){return i}));n(134),n(135);function r(e,t){for(var n=0;n<t.length;n++){var r=t[n];r.enumerable=r.enumerable||!1,r.configurable=!0,"value"in r&&(r.writable=!0),Object.defineProperty(e,r.key,r)}}function i(){$("form#id-login-form").validate({rules:{username:{required:!0},password:{required:!0}},messages:{username:gettext("Ce champ est obligatoire."),password:gettext("Ce champ est obligatoire.")}})}var o=function(){function e(){!function(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}(this,e),this.previousURL=null,this.modalSelector="#login-modal, #article-login-modal, #journal-login-modal",this.init()}var t,n,o;return t=e,(n=[{key:"init",value:function(){this.modal()}},{key:"modal",value:function(){var e=this;$(this.modalSelector).magnificPopup({mainClass:"mfp-fade",removalDelay:750,type:"ajax",closeOnBgClick:!1,closeBtnInside:!0,ajax:{settings:{beforeSend:function(e){e.setRequestHeader("X-PJAX","true")}}},callbacks:{beforeOpen:function(){e.previousURL=window.location.pathname},open:function(){history.replaceState(null,null,$($.magnificPopup.instance.currItem.el).attr("href")),$("body").addClass("modal-open")},ajaxContentAdded:function(){i()},close:function(){history.replaceState(null,null,e.previousURL),$("body").removeClass("modal-open")}}})}}])&&r(t.prototype,n),o&&r(t,o),e}();t.b=o},50:function(e,t,n){"use strict";function r(e,t){for(var n=0;n<t.length;n++){var r=t[n];r.enumerable=r.enumerable||!1,r.configurable=!0,"value"in r&&(r.writable=!0),Object.defineProperty(e,r.key,r)}}var i=function(){function e(t){!function(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}(this,e),this.controllers=void 0===t?{}:t}var t,n,i;return t=e,(n=[{key:"execAction",value:function(e,t){""!==e&&this.controllers[e]&&"function"==typeof this.controllers[e][t]&&this.controllers[e][t]()}},{key:"init",value:function(){if(document.body){var e=document.body,t=e.getAttribute("data-controller"),n=e.getAttribute("data-action");t&&(this.execAction(t,"init"),this.execAction(t,n))}}}])&&r(t.prototype,n),i&&r(t,i),e}();t.a=i},91:function(e,t,n){"use strict";n(92),n(126),n(127),n(128),n(129),n(130),n(131),n(132),n(133);function r(e,t){for(var n=0;n<t.length;n++){var r=t[n];r.enumerable=r.enumerable||!1,r.configurable=!0,"value"in r&&(r.writable=!0),Object.defineProperty(e,r.key,r)}}var i=function(){function e(){!function(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}(this,e),this.init()}var t,n,i;return t=e,(n=[{key:"init",value:function(){this.scrollToTop()}},{key:"scrollToTop",value:function(){$(".scroll-top").on("click",(function(e){return e&&(e.preventDefault(),e.stopPropagation()),$("html,body").animate({scrollTop:0},450),!1}))}}])&&r(t.prototype,n),i&&r(t,i),e}();function o(e,t){for(var n=0;n<t.length;n++){var r=t[n];r.enumerable=r.enumerable||!1,r.configurable=!0,"value"in r&&(r.writable=!0),Object.defineProperty(e,r.key,r)}}var a=function(){function e(){!function(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}(this,e),this.init()}var t,n,r;return t=e,(n=[{key:"init",value:function(){this.svg()}},{key:"svg",value:function(){inlineSVG.init({svgSelector:"img.inline-svg",initClass:"js-inlinesvg"})}}])&&o(t.prototype,n),r&&o(t,r),e}(),c=n(39);function s(e,t){for(var n=0;n<t.length;n++){var r=t[n];r.enumerable=r.enumerable||!1,r.configurable=!0,"value"in r&&(r.writable=!0),Object.defineProperty(e,r.key,r)}}var u=function(){function e(){!function(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}(this,e),this.init()}var t,n,r;return t=e,(n=[{key:"init",value:function(){this.stickyHeader(),this.searchBar()}},{key:"stickyHeader",value:function(){$(window).on("scroll",(function(e){$(window).scrollTop()>=100?$("header#site-header").addClass("site-header__scrolled"):$("header#site-header").removeClass("site-header__scrolled")}))}},{key:"searchBar",value:function(){$("[data-trigger-search-bar]").on("click",(function(e){var t;e.preventDefault(),t=$("#search-form").hasClass("visible"),$("#search-form").toggleClass("visible"),$("header#site-header").toggleClass("inverted-search-bar"),t||$("#search-form input.search-terms").focus()})),$(document).keyup((function(e){27===e.keyCode&&$(".nav-search-triggers__close").click()}))}}])&&s(t.prototype,n),r&&s(t,r),e}();new i,new a,new c.b,new u;n(136);function l(){return function(e){var t=null;if(document.cookie&&""!=document.cookie)for(var n=document.cookie.split(";"),r=0;r<n.length;r++){var i=jQuery.trim(n[r]);if(i.substring(0,e.length+1)==e+"="){t=decodeURIComponent(i.substring(e.length+1));break}}return t}("csrftoken")}$.ajaxSetup({beforeSend:function(e,t){var n;n=t.type,/^(GET|HEAD|OPTIONS|TRACE)$/.test(n)||this.crossDomain||e.setRequestHeader("X-CSRFToken",l())},data:{csrfmiddlewaretoken:l()}})}});