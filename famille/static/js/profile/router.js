var Utils = require("../utils");


module.exports = Backbone.Router.extend({
    serverRoutes: {
        submitRating: "/submit-rating/"
    },

    initialize: function (options) {
        var uriParts = Utils.djangoUriParts();
        this.serverRoutes.submitRating += uriParts[2] + "/" + uriParts[3] + "/";
    },

    submitRating: function (data) {
        var self = this;
        $.ajax({
            type: "post",
            data: data,
            url: this.serverRoutes.submitRating,
            headers: {'X-CSRFToken': $.cookie('csrftoken')}
        }).done(function(data){
            self.trigger("rating:success", data);
        }).fail(function(){
            self.trigger("rating:fail");
        });
    }
});
