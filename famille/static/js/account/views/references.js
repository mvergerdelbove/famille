function getDataFromEl(form){
    form = $(form);
    return _.object(_.compact(_.map(form.find(".form-control,[type=checkbox]:checked"), function(el){
        var $el = $(el), name = $el.attr("name");
        if (name)
            return [name, $el.val()];
    })));
}

var ReferenceView = Backbone.View.extend({
    className: "row reference",

    initialize: function(data, formEl, settings){
        _.extend(this, settings);
        this.data = data;
        if (formEl) {
            this.$formEl = $(formEl);
            this.renderFormEl();
        }
    },

    render: function(data){
        if (data) this.data = data;
        var template = (this.data.referenced_user) ? this.templates.templateExistingReference : this.templates.templateOutsideReference;

        this.cleanData();
        this.$el.html(template(this.data));
        this.renderFormEl();

        return this;
    },

    renderFormEl: function(){
        var self = this;
        if (this.$formEl) this.$formEl.remove();

        this.$formEl = $(this.hiddenFormEl);
        _.each(this.formData, function(value, key){
            $("[name="+ key +"]", self.$formEl).val(value);
        });
    },

    cleanData: function(){
        this.formData = _.clone(this.data);
        if (this.data.referenced_user){
            this.data.referenced_user = this.main.getReferencedUserName(this.data.referenced_user);
        }
    },

    remove: function(){
        Backbone.View.prototype.remove.call(this);
        if (this.$formEl) this.$formEl.remove();
    }
});

var ReferenceEditionView = Backbone.View.extend({
    events: {
        "click .save-reference": "save",
        "hidden.bs.modal": "empty",
        "change [data-collapse]": "handleCollapse",
        "click [name=current]": "handleCurrent"
    },

    initialize: function (options) {
        this.$date_from = this.$(".date:has([name=date_from])");
        this.$date_to = this.$(".date:has([name=date_to])");
    },

    render: function(){
        this.$el.modal('show');
        return this;
    },

    getData: function(){
        var id = this.$("[data-collapse]:checked").val();
        return getDataFromEl(this.$(id + ", .no-collapse"));
    },

    save: function(e){
        // TODO: validate data on save
        var data = this.getData();
        if (this.currentRef) {
            this.currentRef.render(data);
            this.trigger("reference:changed", this.currentRef);
        }
        else this.trigger("reference:add", data);
    },

    empty: function(e){
        _.each(this.$(".form-control"), function(el){
            $(el).val("");
        });
        this.currentRef = null;
    },

    fill: function(reference){
        var self = this;
        this.currentRef = reference;

        var values = _.omit(reference.data, "referenced_user", "current", "date_from", "date_to");
        _.each(values, function(value, key){
            self.$("[name=" + key + "]").val(value);
        });
        if (reference.data.current) {
            this.$("[name=current]").attr("checked", true);
        }
        else {
            this.$("[name=current]").attr("checked", false);
        }
        this.$date_from.data("DateTimePicker").setDate(moment(reference.data.date_from, "DD/MM/YYYY"));
        this.handleCurrent();
        this.$date_to.data("DateTimePicker").setDate(moment(reference.data.date_to, "DD/MM/YYYY"));

        if (reference.data.referenced_user) {
            $("[value=#exists]").click();
            var referenceSelect = this.$("[name=referenced_user]");
            var value = $("option:contains("+ reference.data.referenced_user +")", referenceSelect).attr("value");
            referenceSelect.select2("val", value);
        }
        else {
            $("[value=#doesnt-exists]").click();
        }
    },

    handleCollapse: function(){
        this.$(".choice-collapse").toggleClass("hidden");
    },

    handleCurrent: function (e) {
        if (this.$("[name=current]").is(":checked")) {
            this.$("[name=date_to]").val("");
            this.$date_to.data("DateTimePicker").disable();
        }
        else {
            this.$date_to.data("DateTimePicker").enable();
        }
    },

    validate: function (data) {

    }
});

var PrestataireAccountView = Backbone.View.extend({
    events: {
        "click .reference .edit": "editReference",
        "click .reference .remove": "removeReference"
    },

    initialize: function(options){
        Backbone.View.prototype.initialize.call(this, options);
        this.settings = options.settings;
        this.settings.main = this;
        this.views = [];
        this.modalView = new ReferenceEditionView({
            el: this.$("#referenceModal")
        });
        this.listenTo(this.modalView, "reference:add", this.addReference);
        this.listenTo(this.modalView, "reference:changed", this.appendReferenceForm);
    },

    initializeFromHTML: function(){
        var self = this;
        _.each(this.$(".real-forms .reference-form"), function(el){
            var data = getDataFromEl(el);
            self.addReference(data, el);
        });
    },

    addReference: function(data, formEl){
        var view = new ReferenceView(data, formEl, this.settings);
        this.views.push(view);
        this.$(".reference-list").append(view.render().el);
        this.appendReferenceForm(view);
    },

    appendReferenceForm: function (view) {
        this.$(".real-forms").append(view.$formEl);
    },

    editReference: function(e){
        var idx = this.getReferenceIdx(e.target);
        this.modalView.fill(this.views[idx]);
        this.modalView.render();
    },

    removeReference: function(e){
        var idx = this.getReferenceIdx(e.target);
        this.views[idx].remove();
        this.views.splice(idx, 1);
    },

    getReferenceIdx: function(el){
        return this.$(".reference").index($(el).closest(".reference"));
    },

    getReferencedUserName: function(uid){
        return this.$("select[name=referenced_user] option[value="+ uid +"]").html();
    }
});

module.exports = PrestataireAccountView;