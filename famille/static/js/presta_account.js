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

    // event handling
    $('[data-toggle="tooltip"]').tooltip();
    // init
    showTab();
    $('.nav-tabs a').click(function (e) {
	$(this).tab('show');
	var scrollmem = $('body').scrollTop();
	window.location.hash = this.hash;
	$('html,body').scrollTop(scrollmem);
    });

})(jQuery);
