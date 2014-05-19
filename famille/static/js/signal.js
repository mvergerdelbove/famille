var notifier = require("./notifier.js");

module.exports = function (data) {
    var url = "/signal-user/";
    url += data.userType + "/" + data.pk + "/";
    var promise = $.ajax(url, {
        data: {
            reason: data.reason
        },
        type: "POST",
        headers: {'X-CSRFToken': $.cookie('csrftoken')}
    }).done(function () {
        notifier.success("Cet utilisateur a été signalé avec succès, merci de votre aide.");
    }).fail(function () {
        notifier.error("Une erreur est survenue, veuillez réessayer ultérieurement.");
    });

    return promise.promise();
};
