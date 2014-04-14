function Notifier () {
    this.initialize();
}

_.extend(Notifier.prototype, {
    initialize: function () {
        this.notify = $.growl;
        this.error = _.partial(this.wrapper, "error", {duration: 10000});
        this.warning = _.partial(this.wrapper, "warning", null);
        this.success = _.partial(this.wrapper, "notice", {clean: ["error"]});
        this._notifications = {
            error: [],
            warning: [],
            notice: []
        }
    },

    wrapper: function (methodName, defaults, msg, options) {
        defaults = defaults || {};
        if (defaults.clean) _.each(defaults.clean, function (method) {
            this.cleanPrevious(method);
        }, this);
        options = options || {};
        if (_.isObject(msg)) options = msg;
        else if (_.isString(msg)) options.message = msg;

        options.title = options.title || "";
        options.message = options.message || "";
        _.extend(defaults, options);

        var notification = this.notify[methodName](defaults);
        this._notifications[methodName].push(notification);
        return notification;
    },

    cleanPrevious: function (methodName) {
        _.each(this._notifications[methodName], function (notif) {
            notif.remove($.noop);
        });
    }
});


module.exports = (function ($) {
    window.notifier = window.notifier || new Notifier();
    return window.notifier;
})(jQuery);
