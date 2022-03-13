/**
 * This content script checks if the current HTTP/200 document is a redirect using "Location"
 * transformed by the mitmproxy. If it is a redirect, mitmproxy returns a document like this:
 *
 * <html
 *      _sso._type="location"
 *      _sso._status_code="3**"
 *      _sso._location="https://target.com/redirected">
 * </html>
 *
 * If these attributes are set, the content script redirects to the location by setting the
 * window.location with JavaScript. Also, the "httpredirect" event is logged.
 *
 * This script also checks whether the current document contains any redirects using
 * "Refresh" either as HTTP header or as <meta> tag.
 */

let content_redirects = () => {

    window.addEventListener("load", () => {

        /**
         * Check for Refresh Redirects in Meta
         * <meta http-equiv="refresh" content="0; url=https://target.com">
         */

        let meta_redirect = document.querySelector('meta[http-equiv="refresh"]');

        if (meta_redirect) {
            let [secs, target] = meta_redirect.content.split(";");

            if (target) {
                // This is a redirect using <meta>
                _sso._event("metaredirect", {
                    wait_seconds: secs,
                    location: target.replace(/^(.*url=)/i, "")
                });
            } else {
                // This is a reload using <meta>
                _sso._event("metareload", {
                    wait_seconds: secs
                });
            }
        }

        /**
         * Check for HTTP redirects using the "Location" header
         */

        let html = document.documentElement;

        if (
            "_sso._type" in html.attributes
            && html.attributes["_sso._type"].value === "location"
            && "_sso._status_code" in html.attributes
            && "_sso._location" in html.attributes
        ) {
            let status_code = html.attributes["_sso._status_code"].value;
            let target = html.attributes["_sso._location"].value;

            window._sso._event("httpredirect", {
                status_code: status_code,
                location: target
            }).then(() => {
                window.location = target; // redirect if event was received on backend
            });
        }

        /**
         * Check for HTTP response using the "Refresh" header
         */

         if (
            "_sso._type" in html.attributes
            && html.attributes["_sso._type"].value === "refresh"
            && "_sso._status_code" in html.attributes
            && "_sso._refresh" in html.attributes
        ) {
            let status_code = html.attributes["_sso._status_code"].value;
            let refresh = html.attributes["_sso._refresh"].value;

            let [secs, target] = refresh.split(";");

            if (target) {
                // This is a redirect using "Refresh"
                _sso._event("refreshredirect", {
                    wait_seconds: secs,
                    location: target.replace(/^(.*url=)/i, ""),
                    status_code: status_code
                });
            } else {
                // This is a reload using "Refresh"
                _sso._event("refreshreload", {
                    wait_seconds: secs,
                    status_code: status_code
                });
            }
        }

    });

    console.info("content_redirects.js initialized");
}

let content_redirects_script = document.createElement("script");
content_redirects_script.classList.add("chromeextension");
content_redirects_script.textContent = "(" + content_redirects.toString() + ")()";
document.documentElement.prepend(content_redirects_script);
