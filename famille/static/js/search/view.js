var notifier = require("../notifier.js");
var SignalUser = require("../signal.js");
var RatingView = require("../profile/views/rating.js");
var Favorite = require("../favorite.js");


var constructFilterForString = function(name, query, value){
    return name + "__" + query + "=" + value;
};

var constructFilter = function(name, query, value){
    if (_.isString(value)) return constructFilterForString(name, query, value);
    if (_.isArray(value)) return _.map(value, _.partial(constructFilterForString, name, query)).join("&");
};

var constructTarifFilter = function (name, value) {
    return "tarif__in="+ value[0] +"," + value[1];
};


var constructAgeFilter = function(name, value) {
    var birhdayField = "birthday";
    var today = new Date();
    var birthDate;
    switch(value) {
        case "16-":
            birthDate = new Date(today.setYear(today.getYear() - 16));
            return birhdayField + "__gte="+ birthDate.toISOString().split('T')[0];
        case "18-":
            birthDate = new Date(today.setYear(today.getYear() - 18));
            return birhdayField + "__gte="+ birthDate.toISOString().split('T')[0];
        case "18+":
            birthDate = new Date(today.setYear(today.getYear() - 18));
            return birhdayField + "__lte="+ birthDate.toISOString().split('T')[0];
        default:
            return "";
    }
};

var dateToIso = function (date) {
    var parts = date.split("/");
    return parts[2] + "-" + parts[1] + "-" + parts[0];
};

module.exports = Backbone.View.extend({
    events: {
        "click .next": "displayNext",
        "click .previous": "displayPrevious",
        "click .favorite": "toggleFavorite",
        "click .favorite i": "toggleFavorite",
        "click .choose-search": "switchSearch",
        "change .form-search .form-control": "doSearch",
        "click .form-search [type=checkbox]": "doSearch",
        "onkeyup .form-search [type=text]": "doSearch",
        "slideStop #id_tarif": "doSearch",
        "click .form-search [data-distance]": "doDistanceSearch",
        "change #search-sort": "doSearch",
        "change #id_age": "doSearch",
        "click .contact-result": "checkRights",
        "click .signal-result": "signalUser",
        "click .rate-result": "rateUser",
    },

    initialize: function(options){
        this.resultTemplate = options.resultTemplate;
        this.userPlan = options.userPlan;
        _.bindAll(this, "displayResults", "formatResult", "displayNext", "displayPrevious", "toggleFavorite");
        this.$distanceButton = this.$(".control-distance");
        this.$distanceInput = this.$("#id_distance");
        this.$distanceButtonGroup = this.$(".btn-group-distance");
        this.$sortSelect = this.$("#search-sort");
        // disable popovers on click outside of them
        $('body').on('click', function (e) {
            $('[data-toggle=popover]').each(function () {
                var $el = $(this)
                $el = $el.attr("data-trigger") ? $el : $el.parent();

                if (!$el.is(e.target) && $el.has(e.target).length === 0 && $('.popover').has(e.target).length === 0) {
                    if ($el.data('bs.popover') && $el.data('bs.popover').tip().hasClass('in')) {
                        $el.popover('toggle');
                    }
                }
            });
        });
        if (!this.isAuthenticated()) {
            this.disableForm();
        }
    },

    buildQuery: function($els){
        var filters = $els.map(function(){
            var $this = $(this),
                name = $this.attr("name"),
                value = $this.val(),
                query = $this.data("api");
            if (value && name == "age") return constructAgeFilter(name, value);
            if (value && name == "plannings__start_date") {
                return constructFilter(name, query, dateToIso(value));
            }
            if (value && query) return constructFilter(name, query, value);
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
        var $container = this.$(".search-results"), $noResults = this.$(".no-results");
        $container.html("");
        if (!data.length) {
            $noResults.show();
            this.views = [];
            this.$(".total-search-results").html("0");
            this.$(".plural-search-result").html("s");
        }
        else {
            $noResults.hide();
            this.views = _.map(data, this.formatResult);
            $container.append(_.map(this.views, function(view) {
                return view.el;
            }));
            _.invoke(this.views, "initRating");
            $("[data-toggle=popover]", $container).popover();
            $("[data-toggle=tooltip]", $container).tooltip();
            this.displayPagination();
            this.markFavoritedItems();
        }
    },

    displayPagination: function(){
        var nbResults = famille.router.total;
        this.$(".total-search-results").html(nbResults);
        this.$(".plural-search-result").html(nbResults > 1 ? "s": "");
        if (!famille.router.next) this.$(".next").addClass("disabled");
        else this.$(".next").removeClass("disabled");
        if (!famille.router.previous) this.$(".previous").addClass("disabled");
        else this.$(".previous").removeClass("disabled");
    },

    formatResult: function(object){
        return new ResultView({
            el: object.template,
            data: object
        });
    },

    error: function(jqXHR){
        notifier.error("Une erreur est survenue, veuillez réessayer ultérieurement.");
    },

    disableForm: function () {
        var postalCode = this.$(".form-control[name=pc]")[0];
        this.$("#id_tarif").slider('disable');
        this.attachDisabledPopover(this.$(".slider-disabled"));
        var $els = this.$(".form-control,[type=checkbox]", ".form-search");
        $els.add(this.$sortSelect);
        _.each($els, function (el) {
            if (el === postalCode) return;
            if ($(el).attr("name") === "tarif") return;

            var $el = $(el);
            $el.prop("disabled", "disabled");
            this.attachDisabledPopover($el);
        }, this);
    },
    /**
     * Attach the popover to the elements that are disabled.
     * in order to notify the user that he can create an account.
     */
    attachDisabledPopover: function ($el) {
        $el.attr("data-toggle", "popover");
        $el = $el.parent();
        $el.popover({
            placement: "bottom",
            trigger: "click",
            title: "Fonctionalité indisponible",
            html: true,
            content: this.$(".disabled-popover-content-not-logged").html()
        });
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
            self.$(".one-search-result:contains("+ uri +") .favorite .glyphicon")
            .addClass("favorited");
        });
    },

    toggleFavorite: function(e){
        if (!this.isAuthenticated()) return;

        Favorite({
            event: e,
            container: ".one-search-result",
            userData: famille.userData
        });
    },

    isAuthenticated: function(){
        return window._auth;
    },

    switchSearch: function(e){
        famille.router.switchSearch($(e.target).data("search"));
    },

    /****************************************/
    /*************   Actions   **************/
    /****************************************/

    initResultViews: function(objects) {
        this.views = _.map($(".one-search-result-outer"), function (el) {
            var resource_uri = $(el).find('[data-field=resource_uri]').text();
            var data = {
                resource_uri: resource_uri,
                id: resource_uri.split("/")[4]
            };
            return new ResultView({
                el: el,
                data: data
            });
        });
        _.invoke(this.views, "initRating");
    },

    /**
     * Verify that the user as the right to perform actions
     */
    checkRights: function (e) {
        if (this.userPlan !== "premium") {
            var $target = $(e.target);
            e.preventDefault();
            e.stopPropagation();
            $target.popover("show");
            return false;
        }
        return true;
    },

    rateUser: function (e) {
        this.checkRights(e);
    }
});

var ResultView = Backbone.View.extend({
    events: {
        "click .confirm-signal": "signalUser"
    },

    initialize: function (options) {
        this.data = options.data;
        this.userType = (this.data.resource_uri.indexOf("prestataires") === -1) ? "famille" : "prestataire";
    },

    initRating: function () {
        var $formEl = $(".rating-form"), self = this;
        this.$(".popover-rating").attr("data-content", $formEl.html());
        this.$(".popover-rating").popover().on("shown.bs.popover", function () {
            self.ratingView = new RatingView({
                $el: self.$(".popover-rating-container-"+ self.data.id +" .form-rating"),
                userType: self.userType,
                pk: self.data.id,
                popover: self.$(".popover-rating")
            });
        });
    },

    signalUser: function () {
        var reason = this.$("input[name=reason]:checked").val();
        SignalUser({
            reason: reason,
            userType: this.userType,
            pk: this.data.id
        });
    }
});
