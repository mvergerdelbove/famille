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

var sortedQueryString = function(uri){
    return uri.substring(uri.indexOf('?') + 1).split("&").sort().join("&");
};


module.exports = Backbone.Router.extend({

    serverRoutes: {
        toggleFavorite: "/favorite/",
        switchSearch: "/recherche/",
    },

    initialize: function(options){
        _.bindAll(this, "processResults");
        this.limit = options.limit;
        this.baseUrl = options.baseUrl;
        this.searchType = options.searchType;
        this.searchApi = options.searchApi;
        this.next = this.searchApi + "offset=" + this.limit + "&limit=" + this.limit;
        this.previous = null;
        this.total_count = 0;
    },

    buildQuery: function($els){
        var filters = $els.map(function(){
            var $this = $(this),
                name = $this.attr("name"),
                value = $this.val(),
                query = $this.data("api");
            if (value && query) return constructFilter(name, query, value);
            if (value && name == "language") return constructLanguageFilter(name, value);
        });
        return _.compact(filters).join("&") + "&limit=" + this.limit + "&offset=0";
    },

    doSearch: function(url_or_$els, options){
        var url = _.isString(url_or_$els) ? url_or_$els : this.searchApi + this.buildQuery(url_or_$els),
            that = this;

        options.success = options.success || $.noop;
        options.error = options.error || $.noop;

        this.currentUri = sortedQueryString(url);
        if (_.has(famille.cache, this.currentUri)) {
            this.processResults(options.success, famille.cache[this.currentUri])
        }
        else {
            url = this.baseUrl + url;
            $.ajax({
                url: url,
                headers: {'X-CSRFToken': $.cookie('csrftoken')},
                dataType: "json",
                success: _.partial(that.processResults, options.success),
                error: options.error
            });
        }
    },

    processResults: function(callback, data){
        this.next = data.meta.next;
        this.previous = data.meta.previous;
        this.total = data.meta.total_count;
        // storing in cache to avoid duplicate requests
        famille.cache[this.currentUri] = data;
        callback(data.objects);
    },

    toggleFavorite: function(options){
        options.success = options.success || $.noop;
        options.error = options.error || $.noop;
        _.extend(options, {
            url: this.serverRoutes.toggleFavorite,
            type: "post",
            headers: {'X-CSRFToken': $.cookie('csrftoken')}
        });
        $.ajax(options);
    },

    switchSearch: function(searchType){
        var url = window.location.origin + window.location.pathname + "?type=" + searchType;
        window.location.href = url;
    }
});