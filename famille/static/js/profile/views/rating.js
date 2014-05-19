var Utils = require("../../utils");
var ScoreView = require("./score");
var Rating = require("../../rating");


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
        var uriParts = Utils.djangoUriParts();
        this.userType = uriParts[2];
        this.userId = uriParts[3];
    },

    submit: function (e) {
        e.preventDefault();
        Rating({
            userType: this.userType,
            pk: this.userId,
            rate: this.getData()
        });
    },

    getData: function () {
        return _.object(_.map(this.$("input"), function (el) {
            var $el = $(el);
            return [$el.attr("name"), $el.val()];
        }));
    }
});
