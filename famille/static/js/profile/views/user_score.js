
module.exports = Backbone.View.extend({
    initialize: function (options) {
        _.extend(this, options);
        this.listenTo(this.router, "rating:success", this.updateScore);
    },

    updateScore: function (data) {
        var score = parseFloat(data.total_rating);
        this.$(".rating-score").html(score.toFixed(2));
        _.each(this.$(".score-star"), function (el, idx) {
            if (idx + 1 <= score) {
                $(el).removeClass("glyphicon-star-empty").addClass("glyphicon-star");
            }
            else {
                $(el).addClass("glyphicon-star-empty").removeClass("glyphicon-star");
            }
        });
    }
});