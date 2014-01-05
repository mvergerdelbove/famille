(function($){
    var childContainer = $(".child-container"),
	childForm = $(".child-form").first();

    var addChild = function(){
	getChildForm().appendTo(childContainer);
    };

    var getChildForm = function(){
	var $clone = childForm.clone(true);
	$("input", $clone).val("");
	return $clone;
    };

    var removeChild = function(e){
	$(e.target).parent(".child-form").remove();
    };

    // event handling
    $('.nav-tabs a:first').tab('show');
    $(".add-child").on("click", addChild);
    $(".remove-child").on("click", removeChild);

})(jQuery);
