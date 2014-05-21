var RatingView = require("./views/rating");
var UserScoreView = require("./views/user_score");
var SignalUser = require("../signal.js");
var Favorite = require("../favorite.js");


(function($){
    function App () {
        var userPk = $("[data-field=pk]").html();
        var userType = $("[data-field=type]").html();

        var $formEl = $(".rating-form"), self = this;
        $(".popover-rating").popover({
            content: function () {
                return $formEl.html();
            }
        }).on("shown.bs.popover", function () {
            self.ratingView = new RatingView({
                $el: $(".popover-rating-container .form-rating"),
                popover: $(".popover-rating")
            });
        });
        this.userScoreView = new UserScoreView({
            el: $(".user-score")
        });

        // signal user
        $(".confirm-signal").click(function () {
            var reason = $("input[name=reason]:checked").val();
            SignalUser({
                reason: reason,
                userType: userType,
                pk: userPk
            });
        });

        // favorite
        $(".favorite").click(function (e) {
            Favorite({
                event: e,
                container: ".profile-container"
            });
        })
    }

    window.famille = new App();

})(jQuery);
