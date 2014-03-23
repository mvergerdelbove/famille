function djangoUriParts() {
    return window.location.pathname.split("/");
}

module.exports = {
    djangoUriParts: djangoUriParts
}
