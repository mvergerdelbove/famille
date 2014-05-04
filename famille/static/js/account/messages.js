module.exports = (function ($) {
    var path = location.pathname.match(/\/messages\/([a-z]+)\//)[1];
    $("#" + path + "Link").addClass("active");
})(jQuery);
