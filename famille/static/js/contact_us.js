var notifier = require("./notifier.js");

(function ($) {
    var nameInput = $("#contact-name");
    var msgInput = $("#contact-messageContent");
    var emailInput = $("#contact-email");

    $(".send-contact-message").click(function () {
        var name = nameInput.val();
        var msg = msgInput.val();
        var email = emailInput.val();

        $.ajax({
            url: "/contact-us/",
            type: "POST",
            data: {name: name, message: msg, email: email},
            headers: {'X-CSRFToken': $.cookie('csrftoken')}
        }).done(function () {
            notifier.success("Merci ! Nous ferons en sorte de vous répondre au plus vite.");
        }).fail(function () {
            notifier.error("Une erreur est survenue, veuillez réessayer ultérieurement.");
        });
    });
})(jQuery);
