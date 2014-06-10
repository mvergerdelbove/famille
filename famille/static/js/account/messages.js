var utils = require("../utils.js");


module.exports = (function ($) {
    // init select2
    var $recipients = $("#id_recipients");
    var emptyTerm = "________";
    var __initSelection = {};

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
        },
        initSelection: function (element, callback) {
            var ids = element.val().split(",");
            callback(_.map(ids, function (id) {
                return {id: id, text: __initSelection[id]};
            }));
        }
    });

    // write to recipients
    if (utils.queryString.r) {
        $.ajax({
            url: "/get-recipients/" + utils.queryString.r,
            dataType: "json",
            headers: {'X-CSRFToken': $.cookie('csrftoken')}
        }).done(function (data) {
            _.each(data.users, function (user) {
                __initSelection[user.id] = user.text;
            });
            $recipients.select2("val", _.pluck(data.users, "id"));
        });
    }

})(jQuery);
