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
        if (options.totalNbSearchResults > this.limit)
            this.next = this.searchApi + "offset=" + this.limit + "&limit=" + this.limit;
        this.previous = null;
        this.total_count = 0;
    },

    doSearch: function(url, options){
        var url = (url.indexOf(this.searchApi) == 0) ? url : this.searchApi + url,
            that = this;

        url = this.addMetaToUrl(url);

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

    addMetaToUrl: function (url) {
        if (url.indexOf("limit") === -1) url += "&limit=" + this.limit;

        return url;
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