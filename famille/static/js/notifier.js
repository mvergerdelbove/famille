function Notifier () {
    this.initialize();
}

_.extend(Notifier.prototype, {
    initialize: function () {
        this.notify = $.growl;
        this.error = _.partial(this.wrapper, "error");
        this.warning = _.partial(this.wrapper, "warning");
        this.success = _.partial(this.wrapper, "notice");
    },

    wrapper: function (methodName, msg, options) {
        options = options || {};
        if (_.isObject(msg)) options = msg;
        else if (_.isString(msg)) options.message = msg;

        options.title = options.title || "";
        options.message = options.message || "";
        return this.notify[methodName](options);
    }
});


module.exports = (function ($) {
    window.notifier = window.notifier || new Notifier();
})(jQuery);
