!function(t){var e={};function n(i){if(e[i])return e[i].exports;var o=e[i]={i:i,l:!1,exports:{}};return t[i].call(o.exports,o,o.exports,n),o.l=!0,o.exports}n.m=t,n.c=e,n.d=function(t,e,i){n.o(t,e)||Object.defineProperty(t,e,{enumerable:!0,get:i})},n.r=function(t){"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(t,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(t,"__esModule",{value:!0})},n.t=function(t,e){if(1&e&&(t=n(t)),8&e)return t;if(4&e&&"object"==typeof t&&t&&t.__esModule)return t;var i=Object.create(null);if(n.r(i),Object.defineProperty(i,"default",{enumerable:!0,value:t}),2&e&&"string"!=typeof t)for(var o in t)n.d(i,o,function(e){return t[e]}.bind(null,o));return i},n.n=function(t){var e=t&&t.__esModule?function(){return t.default}:function(){return t};return n.d(e,"a",e),e},n.o=function(t,e){return Object.prototype.hasOwnProperty.call(t,e)},n.p="",n(n.s=68)}({0:function(t,e,n){"use strict";function i(t,e){for(var n=0;n<e.length;n++){var i=e[n];i.enumerable=i.enumerable||!1,i.configurable=!0,"value"in i&&(i.writable=!0),Object.defineProperty(t,i.key,i)}}var o=function(){function t(e){!function(t,e){if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t),this.controllers=void 0===e?{}:e}var e,n,o;return e=t,(n=[{key:"execAction",value:function(t,e){""!==t&&this.controllers[t]&&"function"==typeof this.controllers[t][e]&&this.controllers[t][e]()}},{key:"init",value:function(){if(document.body){var t=document.body,e=t.getAttribute("data-controller"),n=t.getAttribute("data-action");e&&(this.execAction(e,"init"),this.execAction(e,n))}}}])&&i(e.prototype,n),o&&i(e,o),t}();e.a=o},3:function(t,e,n){"use strict";function i(t,e){if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}function o(t,e){for(var n=0;n<e.length;n++){var i=e[n];i.enumerable=i.enumerable||!1,i.configurable=!0,"value"in i&&(i.writable=!0),Object.defineProperty(t,i.key,i)}}var a=function(){function t(){var e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:{};i(this,t);var n={documentAddDataAttribute:"citation-save",documentRemoveDataAttribute:"citation-remove",documentButtonSelector:"[data-citation-list-button]",documentIdDataAttribute:"document-id",documentIsSavedDataAttribute:"is-in-citation-list"};this.options=Object.assign(n,e),this.addButtonSelector="[data-"+this.options.documentAddDataAttribute+"]",this.removeButtonSelector="[data-"+this.options.documentRemoveDataAttribute+"]"}var e,n,a;return e=t,(n=[{key:"save",value:function(t){var e=this,n=t.data(this.options.documentIdDataAttribute),i=t.attr("id");$.ajax({type:"POST",url:Urls["public:citations:add_citation"](),data:{document_id:n}}).done((function(){t.data(e.options.documentIsSavedDataAttribute,!0),$("[data-"+e.options.documentAddDataAttribute+'="#'+i+'"]').hide(),$("[data-"+e.options.documentRemoveDataAttribute+'="#'+i+'"]').show()}))}},{key:"remove",value:function(t){var e=this,n=t.data(this.options.documentIdDataAttribute),i=t.attr("id");$.ajax({type:"POST",url:Urls["public:citations:remove_citation"](),data:{document_id:n}}).done((function(){t.data(e.options.documentIsSavedDataAttribute,!1),$("[data-"+e.options.documentAddDataAttribute+'="#'+i+'"]').show(),$("[data-"+e.options.documentRemoveDataAttribute+'="#'+i+'"]').hide()}))}},{key:"init",value:function(){var t=this;$(this.addButtonSelector).on("click",(function(e){var n=$($(e.currentTarget).data(t.options.documentAddDataAttribute));t.save(n),e.preventDefault()})),$(this.removeButtonSelector).on("click",(function(e){var n=$($(e.currentTarget).data(t.options.documentRemoveDataAttribute));t.remove(n),e.preventDefault()})),$("[data-"+this.options.documentIdDataAttribute+"]").each((function(e,n){var i=$(n).attr("id");1==$(n).data(t.options.documentIsSavedDataAttribute)?($("[data-"+t.options.documentAddDataAttribute+'="#'+i+'"]').hide(),$("[data-"+t.options.documentRemoveDataAttribute+'="#'+i+'"]').show()):($("[data-"+t.options.documentAddDataAttribute+'="#'+i+'"]').show(),$("[data-"+t.options.documentRemoveDataAttribute+'="#'+i+'"]').hide())}))}}])&&o(e.prototype,n),a&&o(e,a),t}();e.a=a},4:function(t,e,n){"use strict";e.a=function t(e){!function(t,e){if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t),e.magnificPopup({mainClass:"mfp-fade",removalDelay:750,type:"ajax",closeOnBgClick:!0,closeBtnInside:!0,items:{src:e.data("modal-id"),type:"inline"}})}},68:function(t,e,n){n(89),t.exports=n(69)},69:function(t,e,n){},7:function(t,e,n){"use strict";var i=n(4),o={facebook:function(t,e){var n={t:e,u:encodeURI(t)},i="https://www.facebook.com/sharer/sharer.php?"+$.param(n),o=($(window).width()-575)/2,a="status=1,width=575,height=400,top="+($(window).height()-400)/2+",left="+o;window.open(i,"facebook",a)},twitter:function(t,e){var n={text:e,url:encodeURI(t)},i="https://twitter.com/intent/tweet?"+$.param(n),o=($(window).width()-575)/2,a="status=1,width=575,height=400,top="+($(window).height()-400)/2+",left="+o;window.open(i,"twitter",a)},linkedin:function(t,e){var n={mini:!0,title:e,url:encodeURI(t),summary:"",source:""},i="https://www.linkedin.com/shareArticle?"+$.param(n),o=($(window).width()-575)/2,a="status=1,width=575,height=400,top="+($(window).height()-400)/2+",left="+o;window.open(i,"linkedin",a)},email:function(t,e,n){var i="mailto:?subject=Érudit%20–%20"+encodeURIComponent(e.replace(/^\s+|\s+$/g,""))+"&body="+encodeURIComponent((n.replace(/^\s+|\s+$/g,"")||"")+"\n\n"+t);document.location.href=i}};function a(t,e){for(var n=0;n<e.length;n++){var i=e[n];i.enumerable=i.enumerable||!1,i.configurable=!0,"value"in i&&(i.writable=!0),Object.defineProperty(t,i.key,i)}}var r=function(){function t(e){!function(t,e){if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t),this.el=e,this.title=e.data("title")||document.title,this.title=this.title.replace(/\s+/g," "),this.url=e.data("share-url")||window.location.href,this.citation_text=$(e.data("cite")).text().replace(/\s+/g," "),this.init()}var e,n,i;return e=t,(n=[{key:"init",value:function(){var t=this;this.el.magnificPopup({mainClass:"mfp-fade",removalDelay:750,closeOnBgClick:!0,closeBtnInside:!0,showCloseBtn:!1,items:{src:'<div class="modal share-modal col-lg-3 col-md-5 col-sm-6 col-xs-12 col-centered">                <div class="panel">                  <header class="panel-heading">                    <h2 class="h4 panel-title text-center">'+gettext("Partager ce document")+'</h2>                  </header>                  <div class="panel-body share-modal--body">                    <ul class="unstyled">                      <li><button id="share-email" class="btn btn-primary btn-block"><i class="icon ion-ios-mail"></i> '+gettext("Courriel")+'</button></li>                      <li><button id="share-twitter" class="btn btn-primary btn-block"><i class="icon ion-logo-twitter"></i> Twitter</button></li>                      <li><button id="share-facebook" class="btn btn-primary btn-block"><i class="icon ion-logo-facebook"></i> Facebook</button></li>                      <li><button id="share-linkedin" class="btn btn-primary btn-block"><i class="icon ion-logo-linkedin"></i> LinkedIn</button></li>                    </ul>                  </div>                </div>              </div>',type:"inline"},callbacks:{open:function(){var e=$($.magnificPopup.instance.content);e.on("click","#share-email",(function(e){return e.preventDefault(),o.email(t.url,t.title,t.citation_text.replace(/(\r\n|\n|\r)/gm,"")),!1})),e.on("click","#share-twitter",(function(e){return e.preventDefault(),o.twitter(t.url),!1})),e.on("click","#share-facebook",(function(e){return e.preventDefault(),o.facebook(t.url,t.title),!1})),e.on("click","#share-linkedin",(function(e){return e.preventDefault(),o.linkedin(t.url,t.title),!1}))},close:function(){$($.magnificPopup.instance.content).off("click")}}})}}])&&a(e.prototype,n),i&&a(e,i),t}();function c(t,e){for(var n=0;n<e.length;n++){var i=e[n];i.enumerable=i.enumerable||!1,i.configurable=!0,"value"in i&&(i.writable=!0),Object.defineProperty(t,i.key,i)}}var s=function(){function t(e){!function(t,e){if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t),this.el=e,this.init()}var e,n,o;return e=t,(n=[{key:"init",value:function(){this.el.on("click",".tool-download",this.download),this.citation=new i.a(this.el.find(".tool-cite")),this.share=new r(this.el.find(".tool-share"))}},{key:"download",value:function(t){return t.preventDefault(),window.open($(this).data("href")),!1}}])&&c(e.prototype,n),o&&c(e,o),t}();e.a=s},89:function(t,e,n){"use strict";n.r(e);var i=n(0),o=n(3),a=n(7),r={init:function(){var t=$("#id_search_results_metadata");this.toolbox(),this.saved_citations=new o.a,this.saved_citations.init(),$("#id_save_search").click((function(e){var n=$("form#id-search");$.ajax({type:"POST",url:Urls["public:search:add_search"](),data:{querystring:n.serialize(),results_count:t.data("results-count")}}).done((function(){$("#id_save_search").addClass("disabled"),$("#id_save_search").text(gettext("Résultats sauvegardés !"))})),e.preventDefault()})),$("#id_page_size,#id_sort_by").change((function(t){var e=$("form#id-search");window.location.href="?"+e.serialize()}))},toolbox:function(){$("#search-results .result .toolbox").each((function(){new a.a($(this))}))}};$(document).ready((function(){new i.a({"public:search:results":r}).init()}))}});