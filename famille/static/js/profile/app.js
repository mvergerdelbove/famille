var RatingView = require("./views/rating");
var UserScoreView = require("./views/user_score");


(function($){
    function App () {
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
    }

    window.famille = new App();

})(jQuery);
