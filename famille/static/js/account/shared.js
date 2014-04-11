function App (){
    var containers = {child: $(".child-container"), planning: $(".planning-container")},
	forms = {child: $(".empty-child-form .child-form"), planning: $(".empty-planning-form .planning-form")},
	no = {child: $(".no-child"), planning: $(".no-planning")};

    var datePickerOptions = {
        planning: {
            language: 'fr',
            format: "DD/MM/YYYY",
            startDate: moment().startOf("day"),
            pickTime: false
        },
        references: {
            language: 'fr',
            format: "DD/MM/YYYY",
            pickTime: false,
            defaultDate: ""
        }
    };

    var addSubForm = function(key){
        no[key].hide();
        var $form = forms[key].clone(true);
        $form.appendTo(containers[key]);
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
        var hash = document.location.hash || $(".url-hash").val();
        if (hash){
            $('.nav-tabs a[href="' + hash + '"]').tab('show');
        }
    };

    var initSubForms = function(key){
        $(".add-" + key).on("click", function(e){addSubForm(key, e);});
        $(".remove-" + key).on("click", function(e){removeSubForm(key, e);});
        if (hasSubForm(key)) no[key].hide();
    };

    var initDatepicker = function($els, options){
        $els.datetimepicker(options);
    };

    // event handling
    $('[data-toggle="tooltip"]').tooltip();
	if (forms.child && forms.planning){
        initSubForms("child");
	}
    initSlider($("#id_tarif"));
    $(".slider").removeAttr("style");
    $("select:not(.empty-planning-form select)").select2();

    // init
    showTab();
    initDatepicker($("#planning .date"), datePickerOptions.planning);
    initDatepicker($("#compte .date"), datePickerOptions.references);
    initDatepicker($("#profil .date"), datePickerOptions.references);
    $('.nav-tabs a').click(function (e) {
		$(this).tab('show');
		var scrollmem = $('body').scrollTop();
		window.location.hash = this.hash;
		$('html,body').scrollTop(scrollmem);
    });

}

module.exports = App;
