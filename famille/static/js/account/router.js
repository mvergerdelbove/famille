
module.exports = Backbone.Router.extend({
    serverRoutes: {
        toggleFavorite: "/favorite/",
        contactFavorite: "/contact-favorites/",
        plannings: "/plannings/"
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
    },

    savePlannings: function (data) {
        var self = this;
        $.ajax({
            type: "post",
            data: JSON.stringify({"plannings": data}),
            contentType: "application/json",
            url: this.serverRoutes.plannings,
            headers: {'X-CSRFToken': $.cookie('csrftoken')}
        }).done(function(){
            self.trigger("plannings:success");
        }).fail(function(error){
            var data;
            try {
                data = JSON.parse(error.responseText);
                self.trigger("plannings:fail", data);
            }
            catch (e) {
                console.log(error);
            }
        });
    }
});
