//(function($){
    window.famille = window.famille || {};

    var searchApi = location.origin + "/api/v1/prestataires/?",
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

    var Router = Backbone.Router.extend({
        initialize: function(options){
            this.limit = options.limit;
            this.next = null;
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
            return _.compact(filters).join("&") + "&limit=" + this.limit;
        },

        doSearch: function($els, options){
            var url = searchApi + this.buildQuery($els),
                that = this;
            options.success = options.success || $.noop;
            options.error = options.error || $.noop;
            $.ajax({
                url: url,
                headers: {'X-CSRFToken': $.cookie('csrftoken')},
                dataType: "json",
                success: _.partial(that.processResults, options.success),
                error: options.error
            });
        },

        processResults: function(callback, data){
            this.next = data.meta.next;
            this.previous = data.meta.previous;
            this.total = data.meta.total_count;
            callback(data.objects);
        }
    });

    var View = Backbone.View.extend({
        events: {
            "click .do-search": "doSearch"
        },

        initialize: function(options){
            this.resultTemplate = options.resultTemplate;
            _.bindAll(this, "displayResults", "formatResult");
        },

        doSearch: function(){
            var $els = this.$(".form-search .form-control,[type=checkbox]");
            famille.router.doSearch($els, {
                success: this.displayResults,
                error: this.error
            });
        },

        displayResults: function(data){
            var $container = this.$(".search-results");
            $container.html("");
            $container.append(_.map(data, this.formatResult));
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

    //})(jQuery);
