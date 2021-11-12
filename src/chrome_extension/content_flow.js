/**
 * This content script automatically determines which flow type is started.
 * It detects SSO-related messages and maps them to the frames in which they are issued.
 * Based on this information, it decides whether the textbook, popup, or iframe flows are started.
 */

let content_flow = () => {

    /* Apple LoginReq */
    /* Docs: https://developer.apple.com/documentation/sign_in_with_apple/sign_in_with_apple_js/incorporating_sign_in_with_apple_into_other_platforms */
    if (
        location.host === "appleid.apple.com"
        && location.pathname === "/auth/authorize"
        && "client_id" in _sso._qparams
        && "redirect_uri" in _sso._qparams
        && "response_type" in _sso._qparams
    ) {
        _sso._event("report", {"key": "idp", "val": "apple"});
        _sso._event("report", {"key": "loginrequrl", "val": location.href});
        _sso._event("report", {"key": "loginreqframe", "val": _sso._hierarchy(window)});

        if (window.parent === self && window.opener == null) {
            _sso._event("report", {"key": "flow", "val": "textbook"});
        } else if (window.opener) {
            _sso._event("report", {"key": "flow", "val": "popup"});
        } else if (window.parent !== self) {
            _sso._event("report", {"key": "flow", "val": "iframe"});
        }
    }

    /* Facebook LoginReq */
    /* Docs: https://developers.facebook.com/docs/facebook-login/manually-build-a-login-flow */
    if (
        location.host.endsWith("facebook.com") // www.facebook.com
        && location.pathname.endsWith("/dialog/oauth") // /v11.0/dialog/oauth
        && ("client_id" in _sso._qparams || "app_id" in _sso._qparams)
    ) {
        _sso._event("report", {"key": "idp", "val": "facebook"});
        _sso._event("report", {"key": "loginrequrl", "val": location.href});
        _sso._event("report", {"key": "loginreqframe", "val": _sso._hierarchy(window)});

        if (window.parent === self && window.opener == null) {
            _sso._event("report", {"key": "flow", "val": "textbook"});
        } else if (window.opener) {
            _sso._event("report", {"key": "flow", "val": "popup"});
        } else if (window.parent !== self) {
            _sso._event("report", {"key": "flow", "val": "iframe"});
        }
    }

    /* Google LoginReq */
    /* Docs: https://developers.google.com/identity/protocols/oauth2/web-server */
    if (
        location.host === "accounts.google.com"
        && location.pathname === "/o/oauth2/v2/auth"
        && "client_id" in _sso._qparams
        && "redirect_uri" in _sso._qparams
        && "response_type" in _sso._qparams
    ) {
        _sso._event("report", {"key": "idp", "val": "google"});
        _sso._event("report", {"key": "loginrequrl", "val": location.href});
        _sso._event("report", {"key": "loginreqframe", "val": _sso._hierarchy(window)});

        if (window.parent === self && window.opener == null) {
            _sso._event("report", {"key": "flow", "val": "textbook"});
        } else if (window.opener) {
            _sso._event("report", {"key": "flow", "val": "popup"});
        } else if (window.parent !== self) {
            _sso._event("report", {"key": "flow", "val": "iframe"});
        }
    }

    /* LoginResp */
    /* response_type = code &| token &| id_token */
    /* response_mode = query | fragment */
    if (
        "code" in _sso._qparams
        || "access_token" in _sso._qparams
        || "id_token" in _sso._qparams
        || "code" in _sso._hparams
        || "access_token" in _sso._hparams
        || "id_token" in _sso._hparams
        // state is optional
    ) {
        _sso._event("report", {"key": "loginrespurl", "val": location.href});
        _sso._event("report", {"key": "loginrespframe", "val": _sso._hierarchy(window)});
        _sso._event("report", {"key": "loginresptype", "val": "GET"});

        if (window.opener) {
            _sso._event("dumpframe", {html: _sso._html()});
        }
    }

    /* LoginResp */
    /* response_type = code &| token &| id_token */
    /* response_mode = form_post */

    function formsubmit(e) {
        let target = e ? e.target : this;
        let jsonform = _sso._form2json(target);
        _sso._event("formsubmit", {action: target.action, form: jsonform});

        if (
            Object.keys(jsonform).includes("code")
            || Object.keys(jsonform).includes("access_token")
            || Object.keys(jsonform).includes("id_token")
        ) {
            _sso._event("report", {"key": "loginrespurl", "val": target.action});
            _sso._event("report", {"key": "loginrespframe", "val": _sso._hierarchy(window)});
            _sso._event("report", {"key": "loginresptype", "val": "POST"});
        }

        target._submit();
    }
    
    window._sso._addEventListener("submit", formsubmit, true); // Submission with click
    HTMLFormElement.prototype._submit = HTMLFormElement.prototype.submit;
    HTMLFormElement.prototype.submit = formsubmit; // Submission with .submit() call

    console.info("content_flow.js initialized");
}

let content_flow_script = document.createElement("script");
content_flow_script.classList.add("chromeextension");
content_flow_script.textContent = "(" + content_flow.toString() + ")()";
document.documentElement.prepend(content_flow_script);
