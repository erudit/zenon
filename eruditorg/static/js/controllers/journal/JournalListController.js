export default {

  init: function() {
    this.smoothScroll();
    this.stickyElements();
  },

  smoothScroll: function() {
    $('#journal_list_per_names .alpha-nav').on('click', 'a', function(e) {
      e.preventDefault();
      e.stopPropagation();
      var target = $(this).attr('href').replace('#', '');
      $('html, body').animate( { scrollTop: $('ul[id="'+target+'"]').offset().top - 137 }, 750);
      return false;
    });
    $('#journal_list_per_disciplines .discipline-nav').on('click', 'a', function(e) {
      e.preventDefault();
      e.stopPropagation();
      var target = $(this).attr('href').replace('#', '');
      $('html, body').animate( { scrollTop: $('a[id="'+target+'"]').offset().top - 100 }, 750);
      return false;
    });
  },

  stickyElements: function() {

    function stickyItemsMenu(offset) {
      let menu = $('.list-header');

      if ($(window).scrollTop() >= offset) {
        menu.addClass('sticky');
      } else {
        menu.removeClass('sticky');
      }
    }

    var listPerNames = $('#journal_list_per_names');

    if (listPerNames.length) {

      $(window).scroll(function () {
        var origOffsetY = $('#journal_list_per_names').offset().top + 390;
        stickyItemsMenu(origOffsetY);
      });

    }

  },

};
