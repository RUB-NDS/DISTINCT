/**
 * This content script checks if the current HTTP/200 document is an HTTP/3** redirect transformed
 * by the mitmproxy. If it is a redirect, mitmproxy returns a special document that looks like this:
 * 
 * <html
 *      _sso._type="redirect"
 *      _sso._status_code="3**"
 *      _sso._location="https://target.com/redirected.html?1=2#3=4">
 * </html>
 * 
 * If these attributes are set, the content script redirects to the location by setting the
 * window.location with JavaScript. Also, the "httpredirect" event is logged.
 * 
 * This script also checks whether the current document contains any redirects using
 * the <meta http-equiv="refresh" content="0; url=https://target.com"> tag.
 */

let content_redirects = () => {

    window.onload = () => {

        /**
         * Check for Meta Redirects
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
         * Check for HTTP Redirects
         * once the page is fully loaded.
         */

        let html = document.documentElement;
        if (
            "_sso._type" in html.attributes
            && html.attributes["_sso._type"].value === "redirect" // this is an http redirect
            && "_sso._status_code" in html.attributes // status code of the http redirect
            && "_sso._location" in html.attributes // target of the http redirect
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
    }

    console.info("content_redirects.js initialized");
}

let content_redirects_script = document.createElement("script");
content_redirects_script.classList.add("chromeextension");
content_redirects_script.textContent = "(" + content_redirects.toString() + ")()";
document.documentElement.prepend(content_redirects_script);
