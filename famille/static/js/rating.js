var notifier = require("./notifier.js");

module.exports = function (data){
    var url = "/submit-rating/" + data.userType + "/" + data.pk + "/";
    var promise = $.ajax({
        type: "post",
        data: data.rate,
        url: url,
        headers: {'X-CSRFToken': $.cookie('csrftoken')}
    }).done(function(data){
        notifier.success("Votre note a bien été prise en compte !");
        $("body").trigger("rating:success", data);
    }).fail(function(){
        notifier.error("Une erreur est survenue, veuillez réessayer ultérieurement.");
    });

    return promise.promise();
};
