var notifier = require("./notifier.js");

function displaySuccessNotification (msg) {
    if (document.location.search.indexOf("success") !== -1) {
        notifier.success(msg);
    }
};

module.exports = displaySuccessNotification;
