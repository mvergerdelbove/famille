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

    contactFavorite: function(e){
        this.trigger("fav:contact", [this.getFavoriteData()]);
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
        this.trigger("remove");
        this.remove();
    }
});

var MainView = Backbone.View.extend({
    events: {
        "click .contact-all": "contactFavorites"
    },

    initialize: function(options){
        var self = this;
        this.router = options.router;
        this.modal = new ModalView({
            el: options.modalEl,
            router: this.router
        });
        this.views = _.map(this.$(".favorite-row"), function(el){
            var view = new FavoriteView({
                el: el,
                router: options.router
            });
            self.listenTo(view, "remove", self.removeFavorite(view));
            self.listenTo(view, "fav:contact", self.fireModal);
            return view;
        });
    },

    contactFavorites: function(e){
        var data = _.map(this.views, function (view) {
            return view.getFavoriteData();
        });
        this.fireModal(data);
    },

    fireModal: function (data) {
        this.modal.render(data);
    },

    removeFavorite: function(view){
        this.views = _.without(this.views, view);
    }
});

var ModalView = Backbone.View.extend({
    events: {
        "click .send-contact": "sendContact"
    },
    subtitleTemplate: modalSubtitleTemplate,
    bodyTemplate: modalBodyTemplate,

    initialize: function (options) {
        this.router = options.router;
    },

    render: function(data){
        this.data = data;
        var names = _.map(data, function(d){return d.name;});
        var subtitle = this.subtitleTemplate({
            data: data,
            names: names
        });
        var body = this.bodyTemplate({});

        this.$(".modal-body").html(body);
        this.$(".modal-subtitle").html(subtitle);
        this.$el.modal("toggle");
    },

    sendContact: function(e){
        this.router.sendContact({
            favorites: this.data,
            message: this.getContactData()
        });
    },

    getContactData: function(){
        return {
            subject: this.$("#subject").val(),
            content: this.$("#content").val()
        };
    }
});

module.exports = MainView;
