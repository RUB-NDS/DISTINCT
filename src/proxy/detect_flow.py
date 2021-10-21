import requests

def _event(key, val):
    requests.post(
        "http://localhost:20200",
        json={"event": {"key": key, "val": val}}
    )

def request(flow):
    method = flow.request.method # GET, POST, ...
    scheme = flow.request.scheme # http or https
    host = flow.request.host
    path = flow.request.path.split("?")[0]
    query = flow.request.query # {"key": "val", ...}
    url = flow.request.url # full url

    print(f"{method}: {scheme}://{host}{path}")

    # Apple AuthnReq
    if (
        host == "appleid.apple.com"
        and path == "/auth/authorize"
    ):
        _event("result", {"key": "idp", "val": "apple"})
        _event("result", {"key": "authnrequrl", "val": url})

    # Facebook AuthnReq
    if (
        host.endswith("facebook.com")
        and path.endswith("/dialog/oauth")
    ):
        _event("result", {"key": "idp", "val": "facebook"})
        _event("result", {"key": "authnrequrl", "val": url})

    # Google AuthnReq
    if (
        host == "accounts.google.com"
        and path == "/o/oauth2/v2/auth"
    ):
        _event("result", {"key": "idp", "val": "google"})
        _event("result", {"key": "authnrequrl", "val": url})

    # AuthnResp
    if (
        "code" in query
    ):
        _event("result", {"key": "authnrespurl", "val": url})
