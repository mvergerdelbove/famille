var Router = require("./router.js");
var FavoriteView = require("./views/favorites.js");
var PlanningView = require("./views/planning.js");
var ProfilePic = require("./views/picture.js");
var Shared = require("./shared.js");


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
        this.profilePic = new ProfilePic({
            el: $("#profile-pic-container"),
            router: this.router
        });
    }

    Shared();
    window.famille = new App();

})(jQuery);