module.exports = Backbone.View.extend({

    events: {
        "click .profile-pic": "onClickProfilePic",
        "click .save": "onClickSave"
    },

    initialize: function (options) {
        this.router = options.router;
        this.$(".profile-pic").tooltip({
            title: "Cliquez pour éditer"
        });
        this.modal = this.$("#modal-pic");
        this.modal.modal({
            show: false
        });
        // router events
        this.listenTo(this.router, "profilePic:success", this.onSuccess);
        this.listenTo(this.router, "profilePic:fail", this.onFail);
    },

    onClickProfilePic: function (e) {
        e.preventDefault();
        this.modal.modal("show");
    },

    onClickSave: function (e) {
        var error = false;
        _.each(this.$("[required]"), function (el) {
            var $el = $(el);
            if (!$el.val()) {
                $el.addClass("field-has-error");
                error = true;
            }
        });
        if (!error) {
            var data = new FormData();
            data.append("profile_pic", this.$("#picFile")[0].files[0]);
            this.router.saveProfilePic(data);
        }
    },

    onSuccess: function (data) {
        this.$(".errorblock").html();
        this.modal.modal("hide");
        this.$("img").attr("src", Settings.urls.media + data.profile_pic);
    },

    onFail: function (data) {
        this.$(".errorblock").html(data.profile_pic.join(", "));
    }
});
