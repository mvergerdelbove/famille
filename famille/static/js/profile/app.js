var RatingView = require("./views/rating");
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
    }

    window.famille = new App();

})(jQuery);
