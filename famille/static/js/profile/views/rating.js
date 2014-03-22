var ScoreView = require("./score");


module.exports = Backbone.View.extend({
    events: {
        "click .submit-rating": "submit"
    },

    initialize: function (options) {
        _.extend(this, options);
        this.views = _.map(this.$(".form-group:has(.star-control)"), function (el) {
            return new ScoreView({
                el: el
            });
        });
        this.listenTo("rating:success", this.router, this.onSuccess);
        this.listenTo("rating:fail", this.router, this.onFailure);
    },

    submit: function (e) {
        e.preventDefault();
        this.router.submitRating(this.getData());
    },

    getData: function () {
        return _.object(_.map(this.$("input"), function (el) {
            var $el = $(el);
            return [$el.attr("name"), $el.val()];
        }));
    },

    onSuccess: function () {
        // TODO:
        // - close popover
        // - trigger event that will remove the button from the DOM
        // - this event will also update the notation of the user
    },

    onFailure: function () {
        console.log(arguments);
    }
});
