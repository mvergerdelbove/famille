var notifier = require("./notifier.js");


module.exports = function(data) {
    var $target = $(data.event.target),
    $star = $(".glyphicon", $target),
    resource_uri = $("[data-field=resource_uri]", $target.parents(data.container)).html(),
    action = ($star.hasClass("favorited")) ? "remove": "add";

    $star.toggleClass("favorited");
    if (data.userData) {
        if (action == "add") data.userData.favorites.push(resource_uri);
        else data.userData.favorites = _.without(data.userData.favorites, resource_uri);
    }

    return toggleFavorite({
        resource_uri: resource_uri,
        action: action
    });
};

function toggleFavorite (data) {
    var promise = $.ajax({
        data: data,
        url: "/favorite/",
        type: "post",
        headers: {'X-CSRFToken': $.cookie('csrftoken')}
    }).fail(function () {
        notifier.error("Une erreur est survenue, veuillez réessayer ultérieurement.");
    });

    return promise.promise();
}
