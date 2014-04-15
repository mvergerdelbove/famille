var notifier = require("../../notifier.js");
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
        this.listenTo(this.router, "rating:success", this.onSuccess);
        this.listenTo(this.router, "rating:error", this.onError);
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

    onError: function () {
        notifier.error("Une erreur est survenue, veuillez réessayer ultérieurement.");
    },

    onSuccess: function () {
        notifier.success("Votre note a bien été prise en compte !");
    }
});
