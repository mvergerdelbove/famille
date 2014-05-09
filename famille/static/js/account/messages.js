module.exports = (function ($) {
    var path = location.pathname.match(/\/messages\/([a-z]+)\//)[1];
    $("#" + path + "Link").addClass("active");

    var $recipients = $("#id_recipients");
    var emptyTerm = "________";
    if ($recipients.length) {
        $recipients.select2({
            multiple: true,
            query: function (options) {
                var termCache = options.term || emptyTerm;
                var cache = this.__cache = this.__cache || {};

                if (cache[termCache]) {
                    return options.callback(cache[termCache]);
                }
                $.ajax({
                    url: "/autocomplete/",
                    dataType: "json",
                    data: {
                        query: options.term
                    },
                    success: function (data) {
                        cache[termCache] = {results: data.objects || []};
                        return options.callback(cache[termCache]);
                    },
                    headers: {'X-CSRFToken': $.cookie('csrftoken')}
                });
            }
        });
    }

})(jQuery);
