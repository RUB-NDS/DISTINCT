let detect_flow = () => {

    window.addEventListener("load", (e) => {

        /* Apple AuthnReq opened in popup */
        /* Docs: https://developer.apple.com/documentation/sign_in_with_apple/sign_in_with_apple_js/incorporating_sign_in_with_apple_into_other_platforms */
        if (
            window.opener
            && location.host === "appleid.apple.com"
            && location.pathname === "/auth/authorize"
            && "client_id" in _qparams
            && "redirect_uri" in _qparams
            && _qparams["redirect_uri"].startsWith("http")
            && "response_type" in _qparams
            && (
                !("response_mode" in _qparams)
                || (_qparams["response_mode"] !== "web_message")
            )
            // TODO: and not SDK
        ) {
            _event("result", {key: "idp", val: "apple"});
            _event("result", {key: "sourceframe", val: "popup"});
            _event("result", {key: "authnrequrl", val: location.href});
        }

        /* Facebook AuthnReq opened in popup */
        /* Docs: https://developers.facebook.com/docs/facebook-login/manually-build-a-login-flow */
        if (
            window.opener
            && location.host === "www.facebook.com"
            && location.pathname.endsWith("/dialog/oauth") // /v11.0/dialog/oauth
            && "client_id" in _qparams
            && "redirect_uri" in _qparams
            && _qparams["redirect_uri"].startsWith("http")
            // TODO: and not SDK
        ) {
            _event("result", {key: "idp", val: "facebook"});
            _event("result", {key: "sourceframe", val: "popup"});
            _event("result", {key: "authnrequrl", val: location.href});
        }

        /* Google AuthnReq opened in popup */
        /* Docs: https://developers.google.com/identity/protocols/oauth2/web-server */
        if (
            window.opener
            && location.host === "accounts.google.com"
            && location.pathname === "/o/oauth2/v2/auth"
            && "client_id" in _qparams
            && "redirect_uri" in _qparams
            && _qparams["redirect_uri"].startsWith("http")
            && "response_type" in _qparams
            && "scope" in _qparams
            // TODO: and not SDK
        ) {
            _event("result", {key: "idp", val: "google"});
            _event("result", {key: "sourceframe", val: "popup"});
            _event("result", {key: "authnrequrl", val: location.href});
        }

        /* response_type = code &| token &| id_token */
        /* response_mode = query | fragment */
        if (
            window.opener
            && (
                "code" in _qparams
                || "code" in _hparams
                || "access_token" in _hparams
                || "id_token" in _hparams
            )
        ) {
            _event("result", {key: "sourceframe", val: "popup"});
            _event("result", {key: "sourceframehierarchy", val: _hierarchy(self)});
            _event("result", {key: "initiator", val: "sp"});
            _event("result", {key: "authnrespurl", val: location.href});

            // _postMessageAll({cmd: "dumpframe"});
            window.postMessage({cmd: "dumpframe"}, "*");
        }

    });

    /* response_type = code &| token &| id_token */
    /* response_mode = form_post */

    function formsubmit(e) {
        let target = e ? e.target : this;
        let jsonform = _form2json(target);
        _event("formsubmit", {action: target.action, form: jsonform});

        if (
            Object.keys(jsonform).includes("code")
            || Object.keys(jsonform).includes("state")
            || Object.keys(jsonform).includes("access_token")
            || Object.keys(jsonform).includes("id_token")
        ) {
            _event("formpost", {action: target.action, form: jsonform});
        }

        target._submit();
    }
    window.addEventListener("submit", formsubmit, true); // Submission with click
    HTMLFormElement.prototype._submit = HTMLFormElement.prototype.submit;
    HTMLFormElement.prototype.submit = formsubmit; // Submission with .submit() call

}

let detect_flow_script = document.createElement("script");
detect_flow_script.classList.add("chromeextension");
detect_flow_script.textContent = "(" + detect_flow.toString() + ")()";
document.documentElement.prepend(detect_flow_script);
