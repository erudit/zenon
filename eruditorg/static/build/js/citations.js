!function(t){var e={};function n(c){if(e[c])return e[c].exports;var i=e[c]={i:c,l:!1,exports:{}};return t[c].call(i.exports,i,i.exports,n),i.l=!0,i.exports}n.m=t,n.c=e,n.d=function(t,e,c){n.o(t,e)||Object.defineProperty(t,e,{enumerable:!0,get:c})},n.r=function(t){"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(t,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(t,"__esModule",{value:!0})},n.t=function(t,e){if(1&e&&(t=n(t)),8&e)return t;if(4&e&&"object"==typeof t&&t&&t.__esModule)return t;var c=Object.create(null);if(n.r(c),Object.defineProperty(c,"default",{enumerable:!0,value:t}),2&e&&"string"!=typeof t)for(var i in t)n.d(c,i,function(e){return t[e]}.bind(null,i));return c},n.n=function(t){var e=t&&t.__esModule?function(){return t.default}:function(){return t};return n.d(e,"a",e),e},n.o=function(t,e){return Object.prototype.hasOwnProperty.call(t,e)},n.p="",n(n.s=85)}({0:function(t,e,n){"use strict";e.a=class{constructor(t){this.controllers=void 0===t?{}:t}execAction(t,e){""!==t&&this.controllers[t]&&"function"==typeof this.controllers[t][e]&&this.controllers[t][e]()}init(){if(document.body){var t=document.body,e=t.getAttribute("data-controller"),n=t.getAttribute("data-action");e&&(this.execAction(e,"init"),this.execAction(e,n))}}}},4:function(t,e,n){"use strict";e.a=class{constructor(t){t.magnificPopup({mainClass:"mfp-fade",removalDelay:750,type:"ajax",closeOnBgClick:!0,closeBtnInside:!0,items:{src:t.data("modal-id"),type:"inline"}})}}},85:function(t,e,n){n(95),t.exports=n(86)},86:function(t,e,n){},95:function(t,e,n){"use strict";n.r(e);var c=n(0),i=n(4),o={init(){function t(){let t=$("#citations_list .bib-records .checkbox input[type=checkbox]:checked").length,e={count:t},n=ngettext("%(count)s document sélectionné","%(count)s documents sélectionnés",e.count),c=interpolate(n,e,!0);$(".saved-citations strong").text(c),t?$("#id_selection_tools").show():$("#id_selection_tools").hide()}function e(t){let e=t.data("document-type"),n=$("[data-"+e+"-count]"),c=parseInt(n.data(e+"-count"));if(c-=1,c){let t={count:c},i=void 0;"scientific-article"===e?i=ngettext("%(count)s article savant","%(count)s articles savants",t.count):"cultural-article"===e?i=ngettext("%(count)s article culturel","%(count)s articles culturels",t.count):"thesis"===e&&(i=ngettext("%(count)s thèse","%(count)s thèses",t.count));let o=interpolate(i,t,!0);n.text(o),n.data(e+"-count",c)}else n.remove()}function n(){var t=new Array;return $("#citations_list .bib-records .checkbox input[type=checkbox]:checked").each((function(){let e=$(this).parents("li.bib-record");t.push(e.data("document-id"))})),t}$(".documents-head input[type=checkbox]").on("change",(function(t){$(this).is(":checked")?$("#citations_list .bib-records .checkbox input[type=checkbox]").each((function(){$(this).prop("checked",!0)})):$("#citations_list .bib-records .checkbox input[type=checkbox]").each((function(){$(this).prop("checked",!1)})),$("#citations_list .bib-records .checkbox input[type=checkbox]").change()})),$("#citations_list .bib-records .checkbox input[type=checkbox]").on("change",t),$("a[data-remove]").click((function(n){n.preventDefault(),function(n){let c=n.data("document-id");$.ajax({type:"POST",url:Urls["public:citations:remove_citation"](),data:{document_id:c}}).done((function(){n.remove(),t(),e(n)}))}($(this).parents("li.bib-record"))})),$("#id_selection_tools a.remove-selection").click((function(c){if(c.preventDefault(),0!=confirm(gettext("Voulez-vous vraiment supprimer votre sélection ?"))){var i=n();$.ajax({type:"POST",url:Urls["public:citations:remove_citation_batch"](),data:{document_ids:i},traditional:!0}).done((function(){$("#citations_list .bib-records .checkbox input[type=checkbox]:checked").each((function(){let n=$(this).parents("li.bib-record");e(n),n.remove(),t()}))}))}})),$("#export_citation_enw").click((function(t){t.preventDefault();var e=n(),c=Urls["public:citations:citation_enw"]()+"?"+$.param({document_ids:e},!0);window.location.href=c})),$("#export_citation_ris").click((function(t){t.preventDefault();var e=n(),c=Urls["public:citations:citation_ris"]()+"?"+$.param({document_ids:e},!0);window.location.href=c})),$("#export_citation_bib").click((function(t){t.preventDefault();var e=n(),c=Urls["public:citations:citation_bib"]()+"?"+$.param({document_ids:e},!0);window.location.href=c})),$("a[data-cite]").each((function(){new i.a($(this))}))}};$(document).ready((function(){new c.a({"public:citations:list":o}).init()}))}});