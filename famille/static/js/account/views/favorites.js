var notifier = require("../../notifier");

var modalSubtitleTemplate = _.template("Ce formulaire sera envoyé à <em><%= names.join(', ') %></em>.");
var modalBodyTemplate = _.template("\
    <form class='form-horizontal'>\
        <div class='form-group'>\
            <label for='subject' class='sr-only'>Sujet du message</label>\
            <div class='col-sm-12'>\
                <input type='text' class='form-control' id='subject' placeholder='Sujet du message'>\
            </div>\
        </div>\
        <textarea class='form-control' rows='3' id='content' placeholder='Contenu du message'></textarea>\
    </form>");

var FavoriteView = Backbone.View.extend({
    events: {
        "click .contact": "contactFavorite",
        "click .remove": "removeFavorite"
    },

    initialize: function (options) {
        this.router = options.router;
    },

    getFavoriteData: function(){
        return {
            object_type: this.$(".favorite-type").text(),
            object_id: this.$(".favorite-pk").text(),
            resource_uri: this.$(".favorite-uri").text(),
            name: this.$(".favorite-name").text()
        };
    },

    // TODO: undo favorite removal
    removeFavorite: function(e){
        var data = this.getFavoriteData()
        this.router.removeFavorite({
            data: _.pick(data, "resource_uri")
        });
        this.trigger("remove", this);
        this.remove();
    }
});

var MainView = Backbone.View.extend({
    events: {
        "click .contact-all": "contactAll"
    },

    initialize: function(options){
        var self = this;
        this.router = options.router;
        this.views = _.map(this.$(".favorite-row"), function(el){
            var view = new FavoriteView({
                el: el,
                router: options.router
            });
            self.listenTo(view, "remove", self.removeFavorite);
            self.listenTo(view, "fav:contact", self.fireModal);
            return view;
        });
        this.listenTo(this.router, "contact:success", this.contactSuccess);
        this.listenTo(this.router, "contact:error", this.contactError);
    },

    removeFavorite: function(view){
        this.views = _.without(this.views, view);
        notifier.info("Favori supprimé avec succès.");
    },

    contactAll: function (e) {
        e.preventDefault();
        e.stopPropagation();
        var favType = $(e.target).data("fav-type");
        var favs = _.map(
            this.$(".fav-container-"+ favType +" .favorite-encoded"),
            function (el) {return $(el).text();}
        );
        var uri = "/messages/write/?r=" + favs.join("---");
        window.open(uri, "_blank");
    }
});

module.exports = MainView;
