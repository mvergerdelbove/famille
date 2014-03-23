
module.exports = Backbone.View.extend({
    events: {
        "click .star-control": "compute"
    },

    initialize: function (options) {
        this.stars = this.$("i.glyphicon");
        this.$input = this.$(".rating-score");
    },

    compute: function (e) {
        var $el = $(e.target),
            ticked = this.isTicked($el),
            idx = this.getStarIndex($el),
            score = this.$input.val();

        if (!ticked) {
            _.each(this.stars, function (star, i) {
                if (i <= idx) this._on(star);
                else this._off(star);
            }, this);
        }
        else {
            var lasts = (idx == 0 && score == 1) ? this.stars.length : this.stars.length - idx - 1;
            _.each(_.last(this.stars, lasts), function (star) {
                this._off(star);
            }, this);
        }
        this.$input.val(idx + 1);
    },

    _on: function (star) {
        $(star).removeClass("glyphicon-star-empty").addClass("glyphicon-star");
    },

    _off: function (star) {
        $(star).addClass("glyphicon-star-empty").removeClass("glyphicon-star");
    },

    isTicked: function ($el) {
        return $el.hasClass("glyphicon-star");
    },

    getStarIndex: function ($el) {
        return this.$("i.glyphicon").index($el);
    }
});
