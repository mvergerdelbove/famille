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
        this.userType = options.userType || uriParts[2];
        this.userId = options.pk || uriParts[3];
        this.popover = options.popover;
    },

    submit: function (e) {
        e.preventDefault();
        var self = this;
        Rating({
            userType: this.userType,
            pk: this.userId,
            rate: this.getData()
        }).done(function () {
            self.popover.popover("hide");
            if (!self.popover.hasClass("popover-rating-search")) {
                self.popover.remove();
            }
            else {
                self.popover.addClass("disabled");
            }
        });
    },

    getData: function () {
        return _.object(_.map(this.$("input"), function (el) {
            var $el = $(el);
            return [$el.attr("name"), $el.val()];
        }));
    }
});
