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
        this.ui = {
            referenced_user: this.$("[name=referenced_user]"),
            current: this.$("[name=current]"),
            name: this.$("[name=name]"),
            date_from: this.$("[name=date_from]"),
            date_to: this.$("[name=date_to]"),
            phone: this.$("[name=phone]"),
            email: this.$("[name=email]"),
            missions: this.$("[name=missions]"),
            garde: this.$("[name=garde]")
        };
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
        var data = this.getData();
        if (this.validate(data)) {
            this.cleanInvalid();
            if (this.currentRef) {
                this.currentRef.render(data);
                this.trigger("reference:changed", this.currentRef);
            }
            else this.trigger("reference:add", data);
            this.$el.modal("hide");
        }
    },

    empty: function(e){
        _.each(this.$(".form-control"), function(el){
            $(el).val("");
        });
        this.currentRef = null;
        this.cleanInvalid();
    },

    fill: function(reference){
        var self = this;
        this.currentRef = reference;

        // TODO: use filter
        var values = _.omit(reference.data, "referenced_user", "current", "date_from", "date_to", "garde");
        _.each(values, function(value, key){
            self.ui[key].val(value);
        });
        if (reference.data.current) {
            this.ui.current.prop("checked", true);
        }
        else {
            this.ui.current.prop("checked", false);
        }
        this.ui.garde.select2("val", reference.data.garde);
        this.$date_from.data("DateTimePicker").setDate(moment(reference.data.date_from, "DD/MM/YYYY"));
        this.handleCurrent();
        this.$date_to.data("DateTimePicker").setDate(moment(reference.data.date_to, "DD/MM/YYYY"));

        if (reference.data.referenced_user) {
            $("[value=#exists]").click();
            var value = $(
                "option:contains("+ reference.data.referenced_user +")",
                this.ui.referenced_user
            ).attr("value");
            this.ui.referenced_user.select2("val", value);
        }
        else {
            $("[value=#doesnt-exists]").click();
        }
    },

    handleCollapse: function(){
        this.$(".choice-collapse").toggleClass("hidden");
    },

    handleCurrent: function (e) {
        if (this.ui.current.is(":checked")) {
            this.ui.date_to.val("");
            this.$date_to.data("DateTimePicker").disable();
        }
        else {
            this.$date_to.data("DateTimePicker").enable();
        }
    },

    validate: function (data) {
        var valid = true, msg;
        // referenced_user or famille name + (tel or mail)
        if (!data.referenced_user && !(data.name && (data.phone || data.email))) {
            if (!data.name) {
                msg = "Ce champs est requis.";
                this.markInvalid(this.ui.name, msg);
                valid = false;
            }
            if (!data.phone && !data.email) {
                msg = "Au moins un champs de contact est requis.";
                this.markInvalid(this.ui.phone, msg);
                this.markInvalid(this.ui.email, msg);
                valid = false;
            }
        }
        if (!data.date_from) {
            msg = "Ce champs est requis";
            this.markInvalid(this.ui.date_from, msg);
            valid = false;
        }
        if (!data.current && !data.date_to) {
            msg = "Ce champs est requis.";
            this.markInvalid(this.ui.date_to, msg);
            valid = false;
        }
        if (!data.missions) {
            msg = "Ce champs est requis.";
            this.markInvalid(this.ui.missions, msg);
            valid = false;
        }

        if (valid) this.cleanInvalid();

        return valid;
    },

    markInvalid: function ($field, msg) {
        var el = "<span class='invalid-field text-danger'>{msg}</span>".replace("{msg}", msg);
        var $parent = $field.parents(".form-group");

        if (!$parent.hasClass("has-error")) {
            $parent.addClass("has-error").append(el);
        }
    },

    cleanInvalid: function () {
        this.$(".form-group").removeClass("has-error");
        this.$(".invalid-field").remove();
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