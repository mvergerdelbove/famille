function Notifier () {
    this.initialize();
}

_.extend(Notifier.prototype, {
    initialize: function () {
        this.notify = $.notify;
        this.info = _.partial(this.wrapper, "info");
        this.error = _.partial(this.wrapper, "error");
        this.warning = _.partial(this.wrapper, "warning");
        this.success = _.partial(this.wrapper, "success");
    },

    wrapper: function (className, msg, options) {
        options = options || {};
        options.className = className;
        this.notify(msg, options);
    }
});


module.exports = (function ($) {
    window.notifier = window.notifier || new Notifier();
})(jQuery);
