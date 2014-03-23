var RatingView = require("./views/rating");
var UserScoreView = require("./views/user_score");
var Router = require("./router");


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
                router: self.router
            });
        });
        this.router = new Router();
        this.userScoreView = new UserScoreView({
            router: this.router,
            el: $(".user-score")
        });
        this.router.on("rating:success", function () {
            $(".popover-rating").popover("hide").remove();
        })
    }

    window.famille = new App();

})(jQuery);
