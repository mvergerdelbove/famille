var Shared = require("./shared.js");
var Router = require("./router.js");
var FavoriteView = require("./views/favorites.js");
var PlanningView = require("./views/planning.js");
var ProfilePic = require("./views/picture.js");
var ReferenceView = require("./views/references.js");

var templateExistingReference = '\
    <div class="col-md-8">\
        <h4>Famille <%= referenced_user %></h4>\
        <p>Du <%= date_from %> <%= (typeof current !== "undefined" && current) ? "à Aujourd\'hui" : "au " + date_to %></p>\
        <p>Type de garde: <%= garde %></p>\
        <p>Missions: <%= missions %></p>\
    </div>\
    <div class="col-md-4">\
        <div class="btn-group">\
            <button type="button" class="btn btn-default btn-xs edit">Modifier</button>\
            <button type="button" class="btn btn-default btn-xs remove">Supprimer</button>\
        </div>\
    </div>';

var templateOutsideReference = '\
    <div class="col-md-8">\
        <h4>Famille <%= name %> <small><%= (email) ? email : phone %></small></h4>\
        <p>Du <%= date_from %> <%= (typeof current !== "undefined" && current) ? "à Aujourd\'hui" : "au " + date_to %></p>\
        <p>Type de garde: <%= garde %></p>\
        <p>Missions: <%= missions %></p>\
    </div>\
    <div class="col-md-4">\
        <div class="btn-group">\
            <button type="button" class="btn btn-default btn-xs edit">Modifier</button>\
            <button type="button" class="btn btn-default btn-xs remove">Supprimer</button>\
        </div>\
    </div>';

(function($){
    window.famille = window.famille || {};

    var $otherTypeContainer = $(".other-type"), $typeSelect = $("#id_type");
    $typeSelect.change(function () {
        var val = $(this).val();
        if (val == "other") $otherTypeContainer.removeClass("hide");
        else $otherTypeContainer.addClass("hide");
    });
    var $hiddenFormEl = $(".empty-real-form").html();
    var settings = {
        templates: {
            templateExistingReference: _.template(templateExistingReference),
            templateOutsideReference: _.template(templateOutsideReference)
        },
        hiddenFormEl: $hiddenFormEl
    };

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
        this.referenceView = new ReferenceView({
            el: $("#compte"),
            settings: settings
        });
        this.referenceView.initializeFromHTML();
    }
    Shared();
    window.famille = new App();

})(jQuery);
