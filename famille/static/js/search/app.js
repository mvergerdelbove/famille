var Router = require("./router");
var View = require("./view");


function App(){
    this.initEvents();
    this.baseUrl = location.origin;
    this.nbSearchResults = parseInt($(".nb-search-results").val(), 10);
    this.emptyResultTemplate = $(".empty-result-template").html();
    this.searchType = $(".search-type").val();
    this.searchApi = "/api/v1/{type}s/?".replace("{type}", this.searchType);
    this.cache = {};
    this.userData = {};
}

App.prototype.initialize = function(){
    this.router = new Router({
        limit: this.nbSearchResults,
        baseUrl: this.baseUrl,
        searchApi: this.searchApi,
        searchType: this.searchType
    });
    this.view = new View({
        el: $(".search-view"),
        resultTemplate: this.emptyResultTemplate
    });
    this.view.initFavorites(); // FIXME : it's bugging here ??
};

App.prototype.initEvents = function(){
    $("select").select2();
    $('[data-toggle="tooltip"]').tooltip();
    if ($("#id_tarif").length){
        this.initSlider($("#id_tarif"));
        $(".slider").removeAttr("style").css("width", "70%");
    }
    $(".has-success").removeClass("has-success");
};

App.prototype.initSlider = function($el){
    var value = $el.val();
	$el.slider({value: value});
};

window.famille = new App();
window.famille.initialize();