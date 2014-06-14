(function ($){
    $(".social-link").click(function (e) {
        var type = $("[name=social_type]:checked").val();
        if (!type) return;
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
        var $el = $(toggable);
        if ($el.attr("disabled")) $el.removeAttr("disabled");
        else $el.attr("disabled", "disabled");
    });

    $(".btn-register").click(function (e) {
        var checkbox = $(this).data("checkbox");
        var name = ($(this).hasClass("btn-register-social")) ? "social_type" : "type";
        function abort () {
            e.preventDefault();
            e.stopPropagation();
        }

        if (!assertTypeChecked(name)) {
            abort();
            var $container = $("[name="+ name +"]").parents(".form-group");
            if (!$(".text-danger", $container).length) {
                $container.append("<span class='text-danger'>Veuillez sélectionner une valeur.</span>");
            }
        }
        else if (!$(checkbox).is(':checked')) abort();
    });

    function assertTypeChecked(name) {
        // TODO: verify that this works on home page
        if (!$("[type=checkbox][name="+ name +"]").length) return true;
        return $("[name="+ name +"]:checked").length !== 0;
    }

})(jQuery);
