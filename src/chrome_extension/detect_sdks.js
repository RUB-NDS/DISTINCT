let detect_sdks = () => {

    window.addEventListener("load", (e) => {

        /* Sign in with Apple SDK */
        /* Docs: https://developer.apple.com/documentation/sign_in_with_apple/sign_in_with_apple_js/configuring_your_webpage_for_sign_in_with_apple */
        if (
            window.opener
            && location.host === "appleid.apple.com"
            && location.pathname === "/auth/authorize"
            && "response_mode" in _qparams
            && _qparams["response_mode"] === "web_message"
            && "m" in _qparams
            && "v" in _qparams
            && "frame_id" in _qparams
        ) {
            _event("result", {key: "idp", val: "apple"});
            _event("result", {key: "sdk", val: "siwa"});
            _event("result", {key: "initiator", val: "idp"});
        }

        /* Facebook Login SDK */
        /* Docs: https://developers.facebook.com/docs/facebook-login/web */
        if (
            window.opener
            && location.host.endsWith("facebook.com") // Found www.facebook.com and web.facebook.com
            && location.pathname.endsWith("/dialog/oauth") // /v11.0/dialog/oauth
            && "app_id" in _qparams
            && "display" in _qparams
            && _qparams["display"] === "popup"
            && "channel_url" in _qparams
            && "ref" in _qparams
            && _qparams["ref"] === "LoginButton"
        ) {
            _event("result", {key: "idp", val: "facebook"});
            _event("result", {key: "sdk", val: "fl"});
            _event("result", {key: "initiator", val: "idp"});
        }

        /* Facebook Login Button SDK */
        /* Docs: https://developers.facebook.com/docs/facebook-login/web */
        // if (
        //     window.parent
        //     && location.host.includes("facebook.com")
        //     && location.pathname.endsWith("/plugins/login_button.php")
        //     && "app_id" in _qparams
        //     && "channel" in _qparams
        //     && "sdk" in _qparams
        //     && _qparams["sdk"] === "joey"
        //     && "use_continue_as" in _qparams
        //     && _qparams["use_continue_as"] === "true"
        // ) {
        // 
        // }

        /* Google Sign-In SDK (Legacy) */
        /* https://developers.google.com/identity/sign-in/web/sign-in */
        if (
            window.opener
            && location.host === "accounts.google.com"
            && location.pathname === "/o/oauth2/auth"
            && "redirect_uri" in _qparams
            && _qparams["redirect_uri"].startsWith("storagerelay://")
        ) {
            _event("result", {key: "idp", val: "google"});
            _event("result", {key: "sdk", val: "gsi"});
            _event("result", {key: "initiator", val: "idp"});
        }

        /* Sign in with Google Button SDK */
        /* Docs: https://developers.google.com/identity/gsi/web/guides/personalized-button */
        if (
            window.opener
            && location.host === "accounts.google.com"
            && location.pathname === "/gsi/select"
            && "ux_mode" in _qparams
            && "ui_mode" in _qparams
            && "channel_id" in _qparams
            && "as" in _qparams
            && "origin" in _qparams
        ) {
            _event("result", {key: "idp", val: "google"});
            _event("result", {key: "sdk", val: "siwg"});
            _event("result", {key: "initiator", val: "idp"});
        }

    });

    /* Google One Tap SDK */
    /* Docs: https://developers.google.com/identity/gsi/web/guides/features */
    window._xmlhttprequest_open = window.XMLHttpRequest.prototype.open;
    window.XMLHttpRequest.prototype.open = function open() {
        let url = arguments[1] || undefined;
        if (
            url 
            && url.startsWith("/gsi/issue")
            && url.includes("select_by=user_1ta")
        ) {
            _event("result", {key: "idp", val: "google"});
            _event("result", {key: "sdk", val: "got"});
            _event("result", {key: "initiator", val: "idp"});
        }
        return window._xmlhttprequest_open.apply(this, arguments);
    };

}

let detect_sdks_script = document.createElement("script");
detect_sdks_script.classList.add("chromeextension");
detect_sdks_script.textContent = "(" + detect_sdks.toString() + ")()";
document.documentElement.prepend(detect_sdks_script);
