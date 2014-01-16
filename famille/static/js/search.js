(function($){
    var initSlider = function($el){
        var value = $el.val();
		$el.slider({value: value});
    };

    var showTab = function(){
	$('.nav-tabs a:first').tab('show');
		if (document.location.hash){
			$('.nav-tabs a[href="' + document.location.hash + '"]').tab('show');
		}
    };

    // init
    $('[data-toggle="tooltip"]').tooltip();
    initSlider($("#id_tarif"));
    $(".slider").removeAttr("style").css("width", "100%");
    $(".has-success").removeClass("has-success");

})(jQuery);
