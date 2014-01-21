(function($){
    window.famille = window.famille || {};

    var baseUrl = location.origin,
        searchApi = "/api/v1/prestataires/?",
        nbSearchResults = parseInt($(".nb-search-results").val(), 10),
        emptyResultTemplate = $(".empty-result-template").html();

    var initSlider = function($el){
        var value = $el.val();
		$el.slider({value: value});
    };

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

    var Router = Backbone.Router.extend({
        initialize: function(options){
            _.bindAll(this, "processResults");
            this.limit = options.limit;
            this.next = "/api/v1/prestataires/?offset="+ this.limit +"&limit="+ this.limit;
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
            var url = _.isString(url_or_$els) ? url_or_$els : searchApi + this.buildQuery(url_or_$els),
                that = this;

            options.success = options.success || $.noop;
            options.error = options.error || $.noop;

            this.currentUri = sortedQueryString(url);
            if (_.has(famille.cache, this.currentUri)) {
                this.processResults(options.success, famille.cache[this.currentUri])
            }
            else {
                url = baseUrl + url;
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
        }
    });

    var View = Backbone.View.extend({
        events: {
            "click .do-search": "doSearch",
            "click .next": "displayNext",
            "click .previous": "displayPrevious",
        },

        initialize: function(options){
            this.resultTemplate = options.resultTemplate;
            _.bindAll(this, "displayResults", "formatResult", "displayNext", "displayPrevious");
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
        }
    });

    // init
    $('[data-toggle="tooltip"]').tooltip();
    initSlider($("#id_tarif"));
    $(".slider").removeAttr("style").css("width", "100%");
    $(".has-success").removeClass("has-success");
    famille.router = new Router({limit: nbSearchResults}),
    famille.view = new View({
        el: $(".search-view"),
        resultTemplate: emptyResultTemplate
    });
    famille.cache = {};

})(jQuery);
