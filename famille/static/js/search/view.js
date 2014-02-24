module.exports = Backbone.View.extend({
    events: {
        "click .next": "displayNext",
        "click .previous": "displayPrevious",
        "click .favorite": "toggleFavorite",
        "click .choose-search": "switchSearch",
        "change .form-control": "doSearch",
        "click [type=checkbox]": "doSearch",
        "onkeyup [type=text]": "doSearch"
    },

    initialize: function(options){
        this.resultTemplate = options.resultTemplate;
        _.bindAll(this, "displayResults", "formatResult", "displayNext", "displayPrevious", "toggleFavorite");
    },

    doSearch: function(){
        var $els = this.$(".form-search .form-control,[type=checkbox]:checked");
        famille.router.doSearch($els, {
            success: this.displayResults,
            error: this.error
        });
    },

    displayNext: function(e){
        e.preventDefault();
        if (famille.router.next)
        famille.router.doSearch(famille.router.next, {
            success: this.displayResults,
            error: this.error
        });
    },

    displayPrevious: function(e){
        e.preventDefault();
        if (famille.router.previous)
        famille.router.doSearch(famille.router.previous, {
            success: this.displayResults,
            error: this.error
        });
    },

    displayResults: function(data){
        var $container = this.$(".search-results");
        $container.html("");
        $container.append(_.map(data, this.formatResult));
        this.displayPagination();
        this.markFavoritedItems();
    },

    displayPagination: function(){
        if (!famille.router.next) this.$(".next").addClass("disabled");
        else this.$(".next").removeClass("disabled");
        if (!famille.router.previous) this.$(".previous").addClass("disabled");
        else this.$(".previous").removeClass("disabled");
    },

    formatResult: function(object){
        var $el = $(this.resultTemplate);
        $("[data-field]", $el).each(function(){
            var $this = $(this),
            field = $this.data("field");
            $this.html(object[field]);
        });
        return $el;
    },

    error: function(jqXHR){
        console.log(jqXHR);
    },

    initFavorites: function(){
        if (!this.isAuthenticated()) return;
        famille.userData.favorites = this.$(".favorited-item").map(function(idx, el){
            var $el = $(el);
            return "/api/v1/" + $el.data("type").toLowerCase() + "s/" + $el.data("id") + "/";
        }).get();
        this.markFavoritedItems();
    },

    markFavoritedItems: function(){
        if (!this.isAuthenticated()) return;
        var self = this;
        _.each(famille.userData.favorites, function(uri){
            self.$(".one-search-result:contains("+ uri +") .favorite")
            .addClass("glyphicon-star")
            .removeClass("glyphicon-star-empty");
        });
    },

    toggleFavorite: function(e){
        if (!this.isAuthenticated()) return;
        var $target = $(e.target),
        resource_uri = $("[data-field=resource_uri]", $target.parent().parent()).html(),
        action = ($target.hasClass("glyphicon-star-empty")) ? "add": "remove";

        $target.toggleClass("glyphicon-star").toggleClass("glyphicon-star-empty");
        if (action == "add") famille.userData.favorites.push(resource_uri);
        else famille.userData.favorites = _.without(famille.userData.favorites, resource_uri);

        famille.router.toggleFavorite({
            data: {
                resource_uri: resource_uri,
                action: action
            },
            error: this.error
        });
    },

    isAuthenticated: function(){
        return (this.$("[data-authenticated]").length == 1);
    },

    switchSearch: function(e){
        famille.router.switchSearch($(e.target).data("search"));
    }
});
