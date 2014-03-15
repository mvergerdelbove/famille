var Router = require("./router.js");
var FavoriteView = require("./views/favorites");
var PlanningView = require("./views/planning");

(function($){
    function App () {
        this.router = new Router();
        this.favorites = new FavoriteView({
            el: $(".favorite-panel"),
            modalEl: $("#modal-contact-favorite"),
            router: this.router
        });
        this.plannings = new PlanningView({
            el: $("#planning"),
            router: this.router
        });
    }

    window.famille = new App();

})(jQuery);