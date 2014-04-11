var MainView = Backbone.View.extend({
    events: {
        "click .add-planning": "addPlanning",
        "click .submit-planning": "submit"
    },

    initialize: function(options) {
        var self = this;
        this.router = options.router;
        this.emptyView = this.$(".no-planning");
        this.planningTemplate = this.$(".empty-planning-form").html();
        this.$container = this.$(".planning-container");
        this.views = _.map($(".planning-form", this.$container), function (el) {
            var view = new PlanningView({
                el: el,
            });
            self.listenTo(view, "remove", function () {
                self.removePlanning(view);
            });
            return view;
        });
        if (this.views.length) this.emptyView.hide();

        // router events
        this.listenTo(this.router, "plannings:success", this.onSuccess);
        this.listenTo(this.router, "plannings:fail", this.onError);
    },

    addPlanning: function() {
        this.emptyView.hide();
        var view = new PlanningView({
            template: this.planningTemplate
        });
        this.views.push(view);
        this.$container.append(view.render().el);
    },

    removePlanning: function (view) {
        this.views = _.without(this.views, view);
        if (!this.views.length) this.emptyView.show();
    },

    submit: function (e) {
        e.preventDefault();
        var data = _.map(this.views, function (view) {
            return view.getValue();
        });
        this.router.savePlannings(data);
    },

    onSuccess: function () {
        _.invoke(this.views, "onSuccess");
    },

    onError: function (errors) {
        var views = this.views;
        _.each(errors, function (errs, idx) {
            views[idx].onError(errs);
        });
    }
});

var PlanningView = Backbone.View.extend({
    events: {
        "click .remove-planning": "remove"
    },

    initialize: function (options) {
        options = options || {};
        if (options.template) {
            this.template = _.template(options.template);
        }
        else {
            this.renderDatetime();
        }
    },

    render: function () {
        this.setElement(this.template({}));
        this.$("select").select2();
        this.renderDatetime();
        return this;
    },

    renderDatetime: function () {
        this.$(".date").datetimepicker({
            language: 'fr',
            format: "DD/MM/YYYY",
            startDate: moment().startOf("day")
        });
    },

    getValue: function () {
        return _.object(_.map(this.$(".form-control"), function (el) {
            var $el = $(el);
            return [el.name, $el.val()];
        }));
    },

    remove: function () {
        this.trigger("remove");
        Backbone.View.prototype.remove.call(this);
    },

    onSuccess: function () {
        this.$(".form-group").removeClass("has-error").addClass("has-success");
    },

    onError: function (errors) {
        if (!_.isEmpty(errors)) {
            var self = this;
            _.each(errors, function (msg, name) {
                msg = "<span class=help-block>{msg}</span>".replace("{msg}", msg);
                var $el = self.$(".form-control[name={name}]".replace("{name}", name));
                $el.closest(".form-group").addClass("has-error");
                $el.after(msg);
            });
        }
    }
});

module.exports = MainView;
