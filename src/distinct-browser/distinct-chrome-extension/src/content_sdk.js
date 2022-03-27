/**
 * This content script detects certain SSO SDKs provided by Apple, Facebook, and Google.
 * Following SDKs are detected:
 *      - Sign in with Apple SDK
 *      - Sign in with Google SDK
 *      - Google Sign-In SDK
 *      - Google One Tap SDK
 *      - Facebook Login SDK
 */

let content_sdk = () => {

    /* Sign in with Apple SDK */
    /* Docs: https://developer.apple.com/documentation/sign_in_with_apple/sign_in_with_apple_js/configuring_your_webpage_for_sign_in_with_apple */
    if (
        location.host === "appleid.apple.com"
        && location.pathname === "/auth/authorize"
        && "m" in _sso._qparams
        && "v" in _sso._qparams
        && "frame_id" in _sso._qparams
    ) {
        _sso._event("statement", {key: "sdk", val: "siwa"});
        _sso._event("statement", {key: "sdk-idp", val: "apple"});
        _sso._event("statement", {key: "sdk-loginrequrl", val: location.href});
        _sso._event("statement", {key: "sdk-loginreqframe", val: _sso._hierarchy(window)});
    }

    /* Facebook Login SDK */
    /* Docs: https://developers.facebook.com/docs/facebook-login/web */
    if (
        location.host.endsWith("facebook.com") // www.facebook.com, web.facebook.com, ...
        && location.pathname.endsWith("/dialog/oauth") // /v11.0/dialog/oauth
        && "app_id" in _sso._qparams
        && "display" in _sso._qparams
        && _sso._qparams["display"] === "popup"
        && "channel_url" in _sso._qparams
    ) {
        _sso._event("statement", {key: "sdk", val: "fl"});
        _sso._event("statement", {key: "sdk-idp", val: "facebook"});
        _sso._event("statement", {key: "sdk-loginrequrl", val: location.href});
        _sso._event("statement", {key: "sdk-loginreqframe", val: _sso._hierarchy(window)});
    }

    /* Google Sign-In SDK (Legacy) */
    /* https://developers.google.com/identity/sign-in/web/sign-in */
    if (
        location.host === "accounts.google.com"
        && location.pathname === "/o/oauth2/auth"
        && "redirect_uri" in _sso._qparams
        && _sso._qparams["redirect_uri"].startsWith("storagerelay://")
    ) {
        _sso._event("statement", {key: "sdk", val: "gsi"});
        _sso._event("statement", {key: "sdk-idp", val: "google"});
        _sso._event("statement", {key: "sdk-loginrequrl", val: location.href});
        _sso._event("statement", {key: "sdk-loginreqframe", val: _sso._hierarchy(window)});
    }

    /* Sign in with Google Button SDK */
    /* Docs: https://developers.google.com/identity/gsi/web/guides/personalized-button */
    if (
        location.host === "accounts.google.com"
        && location.pathname === "/gsi/select"
        && "ux_mode" in _sso._qparams
        && "ui_mode" in _sso._qparams
        && "channel_id" in _sso._qparams
        && "as" in _sso._qparams
        && "origin" in _sso._qparams
    ) {
        _sso._event("statement", {key: "sdk", val: "siwg"});
        _sso._event("statement", {key: "sdk-idp", val: "google"});
        _sso._event("statement", {key: "sdk-loginrequrl", val: location.href});
        _sso._event("statement", {key: "sdk-loginreqframe", val: _sso._hierarchy(window)});
    }

    /* Google One Tap SDK */
    /* Docs: https://developers.google.com/identity/gsi/web/guides/features */
    window.XMLHttpRequest.prototype.open = function open() {
        let url = arguments[1] || undefined;
        if (
            url
            && url.startsWith("/gsi/issue")
            && url.includes("select_by=user_1ta")
        ) {
            _sso._event("statement", {key: "sdk", val: "got"});
            _sso._event("statement", {key: "sdk-idp", val: "google"});
            _sso._event("statement", {key: "sdk-loginrequrl", val: url});
            _sso._event("statement", {key: "sdk-loginreqframe", val: _sso._hierarchy(window)});
        }
        return _sso._xmlhttprequest_open.apply(this, arguments);
    };

    console.info("content_sdk.js initialized");
}

let content_sdk_script = document.createElement("script");
content_sdk_script.classList.add("chromeextension");
content_sdk_script.textContent = "(" + content_sdk.toString() + ")()";
document.documentElement.prepend(content_sdk_script);
