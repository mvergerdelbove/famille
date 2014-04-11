var constructFilterForString = function(name, query, value){
    return name + "__" + query + "=" + value;
};

var constructFilter = function(name, query, value){
    if (_.isString(value)) return constructFilterForString(name, query, value);
    if (_.isArray(value)) return _.map(value, _.partial(constructFilterForString, name, query)).join("&");
};

var constructLanguageFilter = function(name, value){
    return _.map(value, function(val){
        return constructFilterForString("level_" + val, "isnull", "False")
    }).join("&");
};

var constructTarifFilter = function (name, value) {
    var min = value[0];
    var max = value[1];
    if(min !== max) {
        return "tarif__gte="+ min +"&tarif__lte=" + max;
    }
};

module.exports = Backbone.View.extend({
    events: {
        "click .next": "displayNext",
        "click .previous": "displayPrevious",
        "click .favorite": "toggleFavorite",
        "click .choose-search": "switchSearch",
        "change .form-search .form-control": "doSearch",
        "click .form-search [type=checkbox]": "doSearch",
        "onkeyup .form-search [type=text]": "doSearch",
        "slideStop #id_tarif": "doSearch",
        "click .form-search [data-distance]": "doDistanceSearch",
        "change #search-sort": "doSearch"
    },

    initialize: function(options){
        this.resultTemplate = options.resultTemplate;
        _.bindAll(this, "displayResults", "formatResult", "displayNext", "displayPrevious", "toggleFavorite");
        this.$distanceButton = this.$(".control-distance");
        this.$distanceInput = this.$("#id_distance");
        this.$distanceButtonGroup = this.$(".btn-group-distance");
        this.$sortSelect = this.$("#search-sort");
    },

    buildQuery: function($els){
        var filters = $els.map(function(){
            var $this = $(this),
                name = $this.attr("name"),
                value = $this.val(),
                query = $this.data("api");
            if (value && query) return constructFilter(name, query, value);
            if (value && name == "language") return constructLanguageFilter(name, value);
            if (value && name == "tarif") return constructTarifFilter(name, $this.slider("getValue"));
        });
        filters.push(this.getSortQuery());
        return _.compact(filters).join("&");
    },

    doSearch: function(){
        var $els = this.$(".form-control,[type=checkbox]:checked,#id_distance", ".form-search");
        famille.router.doSearch(this.buildQuery($els), {
            success: this.displayResults,
            error: this.error
        });
    },

    doDistanceSearch: function (e) {
        e.preventDefault();
        var $target = $(e.target),
            distance = $target.data("distance");

        if ($target.is(this.$distanceButton) && this.$distanceButton.hasClass("active")) {
            this.$distanceInput.val("");
            this.$distanceButton.removeClass("active");
            this.$distanceButtonGroup.tooltip("destroy");
            this.$distanceButton.blur();
        }
        else {
            this.$distanceInput.val(distance);
            this.$distanceButton.addClass("active");
            this.$distanceButtonGroup.tooltip({
                placement: "right",
                title: "La recherche par géolocation est active."
            });
        }
        this.doSearch();
    },

    displayNext: function(e){
        e.preventDefault();
        if (famille.router.next) {
            famille.router.doSearch(famille.router.next, {
                success: this.displayResults,
                error: this.error
            });
        }
    },

    displayPrevious: function(e){
        e.preventDefault();
        if (famille.router.previous) {
            famille.router.doSearch(famille.router.previous, {
                success: this.displayResults,
                error: this.error
            });
        }
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

    /****************************************/
    /************      Sort     *************/
    /****************************************/

    getSortQuery: function () {
        var sort = this.$sortSelect.val();
        return "order_by=" + sort;
    },

    /****************************************/
    /************   Favorites   *************/
    /****************************************/

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
        resource_uri = $("[data-field=resource_uri]", $target.parents(".panel-heading")).html(),
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
