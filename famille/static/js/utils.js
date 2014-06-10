function djangoUriParts() {
    return window.location.pathname.split("/");
}

// http://stackoverflow.com/questions/979975/how-to-get-the-value-from-url-parameter
function queryString () {
    // This function is anonymous, is executed immediately and
    // the return value is assigned to QueryString!
    var query_string = {};
    var query = window.location.search.substring(1);
    if (!query) {
        return query_string;
    }
    var vars = query.split("&");
    for (var i=0;i<vars.length;i++) {
        var pair = vars[i].split("=");
        // If first entry with this name
        if (typeof query_string[pair[0]] === "undefined") {
            query_string[pair[0]] = pair[1];
            // If second entry with this name
        } else if (typeof query_string[pair[0]] === "string") {
            var arr = [query_string[pair[0]], pair[1]];
            query_string[pair[0]] = arr;
            // If third or later entry with this name
        } else {
            query_string[pair[0]].push(pair[1]);
        }
    }
    return query_string;
}

// requires moment
function dateIsGreaterThan(d1, d2) {
    d2 = (d2) ? moment(d2, "DD/MM/YYYY") : moment();
    d1 = moment(d1, "DD/MM/YYYY");
    return d1.isAfter(d2);
}


module.exports = {
    djangoUriParts: djangoUriParts,
    queryString: queryString(),
    dateIsGreaterThan: dateIsGreaterThan
}
