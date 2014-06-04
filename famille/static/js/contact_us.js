var notifier = require("./notifier.js");

(function ($) {
    function validateEmail(email) {
        var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return re.test(email);
    }

    function validatePhone(phone) {
        var re = /^0\d{9}$/;
        return re.test(phone);
    }


    var nameInput = $("#contact-name");
    var msgInput = $("#contact-messageContent");
    var emailInput = $("#contact-email");
    var modal = $("#contactModal");

    $(".send-contact-message").click(function () {
        var name = nameInput.val();
        var msg = msgInput.val();
        var email = emailInput.val();
        var errors = [];
        var err_msg = "";

        // errors
        if (!name.trim()) errors.push("Nom ou raison sociale");
        if (!msg.trim()) errors.push("Message");
        if (!email.trim()) errors.push("Email / contact");

        if (errors.length) {
            if (errors.lengts === 1) err_msg = "Le champs '" + errors[0] + "' est requis.";
            else err_msg = "Les champs '" + errors.join("', '") + "' sont requis.";
        }
        else if (!validateEmail(email.trim()) && !validatePhone(email.trim())) {
            err_msg = (
                "Le champs 'Email / contact' doit être un mail valide ou un " +
                "numéro de téléphone valide (sans espace ni points ou tirets)."
            );
        }

        if (err_msg.length) {
            notifier.error(err_msg);
            return;
        }

        modal.modal("hide");
        $.ajax({
            url: "/contact-us/",
            type: "POST",
            data: {name: name, message: msg, email: email},
            headers: {'X-CSRFToken': $.cookie('csrftoken')}
        }).done(function () {
            notifier.success("Votre message a bien été envoyé, nous vous répondrons dans les plus brefs délais.");
        }).fail(function () {
            notifier.error("Une erreur est survenue, veuillez réessayer ultérieurement.");
        });
    });
})(jQuery);
