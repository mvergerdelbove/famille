var Shared = require("./shared.js");
var Router = require("./router.js");
var PlanningView = require("./views/planning.js");
var ProfilePic = require("./views/picture.js");
var ReferenceView = require("./views/references.js");

var templateExistingReference = '\
    <div class="col-md-8">\
        <h4>Famille <%= referenced_user %></h4>\
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
        <h4>Famille <%= name %></h4>\
        <small><%= (email) ? email : phone %></small>\
        <p>Missions: <%= missions %></p>\
    </div>\
    <div class="col-md-4">\
        <div class="btn-group">\
            <button type="button" class="btn btn-default btn-xs edit">Modifier</button>\
            <button type="button" class="btn btn-default btn-xs remove">Supprimer</button>\
        </div>\
    </div>';

(function($){
    Shared();
    window.famille = window.famille || {};

    var $otherTypeContainer = $(".other-type"), $typeSelect = $("#id_type");
    $typeSelect.change(function () {
        var val = $(this).val();
        if (val == "other") $otherTypeContainer.removeClass("hide");
        else $otherTypeContainer.addClass("hide");
    });
    var $hiddenFormEl = $(".empty-real-form .reference-form");
    var settings = {
        templates: {
            templateExistingReference: _.template(templateExistingReference),
            templateOutsideReference: _.template(templateOutsideReference)
        },
        hiddenFormEl: $hiddenFormEl
    };

    function App () {
        this.router = new Router();
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
