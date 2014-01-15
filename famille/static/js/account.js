(function($){
    var childContainer = $(".child-container"),
	childForm = $(".empty-child-form .child-form"),
	noChild = $(".no-child");

    var addChild = function(){
		noChild.hide();
		getChildForm().appendTo(childContainer);
    };

    var getChildForm = function(){
		return childForm.clone(true);
    };

    var hasChildren = function(){
		return $(".child-form", childContainer).length > 0;
    };

    var removeChild = function(e){
	$(e.target).parent(".child-form").remove();
		if (!hasChildren()) noChild.show();
    };

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
	if (childForm){
		$(".add-child").on("click", addChild);
		$(".remove-child").on("click", removeChild);
		if (hasChildren()) noChild.hide();
	}
    initSlider($("#id_tarif"));
    $(".slider").removeAttr("style");

    // init
    showTab();
    $('.nav-tabs a').click(function (e) {
		$(this).tab('show');
		var scrollmem = $('body').scrollTop();
		window.location.hash = this.hash;
		$('html,body').scrollTop(scrollmem);
    });

})(jQuery);
