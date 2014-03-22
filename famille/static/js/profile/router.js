
module.exports = Backbone.Router.extend({
    serverRoutes: {
        submitRating: "/submit-rating/"
    },

    submitRating: function (data) {
        var self = this;
        $.ajax({
            type: "post",
            data: data,
            url: this.serverRoutes.submitRating,
            headers: {'X-CSRFToken': $.cookie('csrftoken')}
        }).done(function(){
            self.trigger("rating:success");
        }).fail(function(){
            self.trigger("rating:fail");
        });
    }
});
