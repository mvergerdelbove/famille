(function ($){
    $(".social-link").click(function (e) {
        var type = $("[name=social_type]:checked").val();
        var href = this.href;
        this.href = href.replace(/next=\/([^\/]+)\/([^\/]+)\/([^\/]+)\//, function (all, action, backend, old_type) {
           return "next=/{action}/{backend}/{type}/"
               .replace("{action}", action)
               .replace("{backend}", backend)
               .replace("{type}", type);
        });
    });

    $(".cgu-checkbox").click(function () {
        var toggable = $(this).data("toggle");
        $(toggable).toggleClass("hide");
    });

    $(".btn-register").click(function (e) {
        var checkbox = $(this).data("checkbox");
        if (!$(checkbox).is(':checked')) {
            e.preventDefault();
            e.stopPropagation();
        }
    });
})(jQuery);