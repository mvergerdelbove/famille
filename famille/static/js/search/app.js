var Router = require("./router");
var View = require("./view");


function App(){
    this.initEvents();
    this.baseUrl = location.origin;
    this.maxNbSearchResults = parseInt($(".max-nb-search-results").val(), 10);
    this.totalNbSearchResults = parseInt($(".total-nb-search-results").val(), 10);
    this.emptyResultTemplate = $(".empty-result-template").html();
    this.searchType = $(".search-type").val();
    this.searchApi = "/api/v1/{type}s/?".replace("{type}", this.searchType);
    this.userPlan = $(".p-type").val();
    this.cache = {};
    this.userData = {};
}

App.prototype.initialize = function(){
    this.router = new Router({
        limit: this.maxNbSearchResults,
        totalNbSearchResults: this.totalNbSearchResults,
        baseUrl: this.baseUrl,
        searchApi: this.searchApi,
        searchType: this.searchType
    });
    this.view = new View({
        el: $(".search-view"),
        resultTemplate: this.emptyResultTemplate,
        userPlan: this.userPlan
    });
    this.view.initFavorites();
    this.view.initResultViews();
};

App.prototype.initEvents = function(){
    $("select").select2();
    $('[data-toggle="tooltip"]').tooltip();
    $('[data-toggle="popover"]').popover();
    if ($("#id_tarif").length) {
        this.initSlider($("#id_tarif"));
        $(".slider").removeAttr("style").css("width", "70%");
    }
    $(".has-success").removeClass("has-success");
    $("#id_plannings__start_date").datetimepicker({
        language: 'fr',
        format: "DD/MM/YYYY",
        startDate: moment().startOf("day"),
        pickTime: false
    });

    // FIXME : this engender problems : the popover is just hidden but
    //         covers the possibly underlying buttons

    // $('body').on('click', function (e) {
//         if ($(e.target).data('toggle') !== 'popover'
//             && $(e.target).parents('.popover.in').length === 0) {
//             $('[data-toggle="popover"]').popover('hide');
//         }
//     });
};

App.prototype.initSlider = function($el){
    var value = $el.val();
	$el.slider({value: value});
};

window.famille = new App();
window.famille.initialize();