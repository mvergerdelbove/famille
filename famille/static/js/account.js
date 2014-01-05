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

    // event handling
    $('.nav-tabs a:first').tab('show');
    $('[data-toggle="tooltip"]').tooltip();
    $(".add-child").on("click", addChild);
    $(".remove-child").on("click", removeChild);
    // init
    if (hasChildren()) noChild.hide();

})(jQuery);
