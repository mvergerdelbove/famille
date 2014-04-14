function Notifier () {
    this.initialize();
}

_.extend(Notifier.prototype, {
    initialize: function () {
        this.notify = $.growl;
        this.error = _.partial(this.wrapper, "error", {duration: 10000});
        this.warning = _.partial(this.wrapper, "warning", null);
        this.success = _.partial(this.wrapper, "notice", null);
    },

    wrapper: function (methodName, defaults, msg, options) {
        defaults = defaults || {};
        options = options || {};
        if (_.isObject(msg)) options = msg;
        else if (_.isString(msg)) options.message = msg;

        options.title = options.title || "";
        options.message = options.message || "";
        _.extend(defaults, options);
        return this.notify[methodName](defaults);
    }
});


module.exports = (function ($) {
    window.notifier = window.notifier || new Notifier();
    return window.notifier;
})(jQuery);
