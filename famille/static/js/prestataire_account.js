(function($){
    window.famille = window.famille || {};

    // FIXME: factorize
    var templateExistingReference = '\
        <div class="col-md-8">\
            <h4>Famille <%= referenced_user %></h4>\
            <p>Missions: <%= missions %></p>\
        </div>\
        <div class="col-md-4">\
            <div class="btn-group">\
                <button type="button" class="btn btn-default btn-xs edit">Modifier</button>\
                <button type="button" class="btn btn-default btn-xs remove">Supprimer</button>\
            </div>\
        </div>';
    var templateOutsideReference = '\
        <div class="col-md-8">\
            <h4>Famille <%= name %></h4>\
            <small><%= (email) ? email : phone %></small>\
            <p>Missions: <%= missions %></p>\
        </div>\
        <div class="col-md-4">\
            <div class="btn-group">\
                <button type="button" class="btn btn-default btn-xs edit">Modifier</button>\
                <button type="button" class="btn btn-default btn-xs remove">Supprimer</button>\
            </div>\
        </div>';

    var $hiddenFormEl = $(".empty-real-form .reference-form");

    function getDataFromEl(form){
        form = $(form);
        return _.object(_.map(form.find(".form-control"), function(el){
            return [el.name, $(el).val()];
        }));
    }


    var ReferenceView = Backbone.View.extend({
        className: "row reference",
        templateExistingReference: _.template(templateExistingReference),
        templateOutsideReference: _.template(templateOutsideReference),

        initialize: function(data){
            this.data = data;
        },

        render: function(data){
            if (data) this.data = data;
            var template = (this.data.referenced_user) ? this.templateExistingReference : this.templateOutsideReference;

            this.cleanData();
            this.$el.html(template(this.data));
            this.renderFormEl();

            return this;
        },

        renderFormEl: function(){
            var self = this;
            if (this.$formEl) this.$formEl.remove();
            
            this.$formEl = $hiddenFormEl.clone();
            _.each(this.formData, function(value, key){
                $("[name="+ key +"]", self.$formEl).val(value);
            });
        },

        cleanData: function(){
            this.formData = _.clone(this.data);
            if (this.data.referenced_user){
                this.data.referenced_user = famille.mainView.getReferencedUserName(this.data.referenced_user);
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
            "change [data-collapse]": "handleCollapse"
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
            // TODO: validate date on save
            var data = this.getData();
            if (this.currentRef) this.currentRef.render(data);
            else famille.mainView.addReference(data);
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

            _.each(reference.data, function(value, key){
                self.$(".form-control[name=" + key + "]").val(value);
            });
        },

        handleCollapse: function(){
            this.$(".choice-collapse").toggleClass("hidden");
        }
    });

    var PrestataireAccountView = Backbone.View.extend({
        events: {
            "click .reference .edit": "editReference",
            "click .reference .remove": "removeReference"
        },

        initialize: function(options){
            Backbone.View.prototype.initialize.call(this, options);
            this.views = [];
        },

        initializeFromHTML: function(){
            var self = this;
            _.each(this.$(".real-forms .reference-form"), function(el){
                var data = getDataFromEl(el);
                self.addReference(data, true);
            });
        },

        addReference: function(data, hasFormEl){
            var view = new ReferenceView(data);
            this.views.push(view);
            this.$(".reference-list").append(view.render().el);
            if (!hasFormEl) this.$(".real-forms").append(view.$formEl);
        },

        editReference: function(e){
            var idx = this.getReferenceIdx(e.target);
            famille.modalView.fill(this.views[idx]);
            famille.modalView.render();
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

    famille.mainView = new PrestataireAccountView({
        el: $("#compte")
    });
    famille.mainView.initializeFromHTML();
    famille.modalView = new ReferenceEditionView({
        el: $("#referenceModal")
    });

    // TODO: find a smart way for initialization

})(jQuery);