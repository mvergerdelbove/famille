var notifier = require("../notifier.js");

$(function () {
    var action = $("#paypal-action").val();
    if (action == "valider") {
        notifier.success({
            title: "Félicitations !",
            message:"Vous êtes maintenant un membre premium d'Une vie de famille"
        });
    }
});
