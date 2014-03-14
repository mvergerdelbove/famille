
module.exports = Backbone.Router.extend({
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
