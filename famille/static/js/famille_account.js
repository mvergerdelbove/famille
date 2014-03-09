(function($){

    var modalSubtitleTemplate = _.template("Ce formulaire sera envoyé à <em><%= names.join(', ') %></em>."); //TODO
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

    var Router = Backbone.Router.extend({
        serverRoutes: {
            toggleFavorite: "/favorite/",
            contactFavorite: "/contact-favorites/",
        },

        removeFavorite: function(options){
            options.success = options.success || $.noop;
            options.error = options.error || $.noop;
            options.data.action = "remove";
            _.extend(options, {
                url: this.serverRoutes.toggleFavorite,
                type: "post",
                headers: {'X-CSRFToken': $.cookie('csrftoken')}
            });
            $.ajax(options);
        },

        sendContact: function(data){
            var self = this;
            $.ajax({
                type: "post",
                data: JSON.stringify(data),
                contentType: "application/json",
                url: this.serverRoutes.contactFavorite,
                headers: {'X-CSRFToken': $.cookie('csrftoken')}
            }).done(function(){
                self.trigger("contact:success");
            }).fail(function(){
                self.trigger("contact:fail");
            });
        }
    });

    var FavoriteView = Backbone.View.extend({
        events: {
            "click .contact": "contactFavorite",
            "click .remove": "removeFavorite"
        },

        contactFavorite: function(e){
            famille.modal.render([_.pick(this.getFavoriteData(), "object_type", "object_id")]);
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
            famille.router.removeFavorite({
                data: _.pick(data, "resource_uri")
            });
            this.trigger("remove");
            this.remove();
        }
    });

    var View = Backbone.View.extend({
        events: {
            "click .contact-all": "contactFavorites"
        },

        initialize: function(options){
            var self = this;
            this.views = _.map(this.$(".favorite-row"), function(el){
                var view = new FavoriteView({
                    el: el
                });
                self.listenTo(view, "remove", self.removeFavorite(view));
                return view;
            });
        },

        contactFavorites: function(e){
            
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
            famille.router.sendContact({
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

    window.famille = {};
    window.famille.router = new Router();
    window.famille.view = new View({
       el: $(".favorite-panel") 
    });
    window.famille.modal = new ModalView({
        el: $("#modal-contact-favorite")
    });
})(jQuery);