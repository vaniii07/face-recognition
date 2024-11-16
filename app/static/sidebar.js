$(".menu > ul > li > a").click(function (e) {
  var $li = $(this).parent("li");
  const emptyHref = $(this).attr('href') === '';
    if (emptyHref) {
        e.preventDefault();
    }
  // Close any open submenus
  $(".menu > ul > li")
    .not($li)
    .removeClass("active")
    .find(".sub-menu")
    .removeClass("show");

  // Toggle the current submenu
  if ($li.hasClass("active")) {
    $li.removeClass("active");
    $li.find(".sub-menu").removeClass("show");
  } else {
    $li.addClass("active");
    $li.find(".sub-menu").addClass("show");
  }
});

$(".menu-btn").click(function () {
  $(".sidebar-container").toggleClass("active");
});
