(function($){
    var containers = {child: $(".child-container"), planning: $(".planning-container")},
	forms = {child: $(".empty-child-form .child-form"), planning: $(".empty-planning-form .planning-form")},
	no = {child: $(".no-child"), planning: $(".no-planning")};

    var addSubForm = function(key){
        no[key].hide();
        var $form = forms[key].clone(true);
        $form.appendTo(containers[key]);
        if (key == "planning") initDatepicker($(".date", $form));
    };

    var hasSubForm = function(key){
		return $("."+ key +"-form", containers[key]).length > 0;
    };

    var removeSubForm = function(key, e){
        $(e.target).parent("."+ key +"-form").remove();
        if (!hasSubForm(key)) no[key].show();
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

    var initSubForms = function(key){
        $(".add-" + key).on("click", function(e){addSubForm(key, e);});
        $(".remove-" + key).on("click", function(e){removeSubForm(key, e);});
        if (hasSubForm(key)) no[key].hide();
    };

    var initDatepicker = function($els){
        $els.datetimepicker({
            language: 'fr',
            format: "DD/MM/YYYY HH:mm:ss",
            minuteStepping: 10,
            startDate: moment().startOf("day")
        });
    };

    // event handling
    $('[data-toggle="tooltip"]').tooltip();
    initDatepicker($('.initial-date'));
	if (forms.child && forms.planning){
        initSubForms("child");
        initSubForms("planning");
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
