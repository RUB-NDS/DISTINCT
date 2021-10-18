import requests

def _event(key, val):
    requests.post(
        "http://localhost:20200",
        json={"event": {"key": key, "val": val}}
    )

def request(flow):
    # Apple AuthnReq
    if (
        flow.request.host == "appleid.apple.com"
        and flow.request.path == "/auth/authorize"
    ):
        _event("result", {"key": "idp", "val": "apple"})

    # Facebook AuthnReq
    if (
        flow.request.host == "www.facebook.com"
        and flow.request.path.endswith("/dialog/oauth")
    ):
        _event("result", {"key": "idp", "val": "facebook"})

    # Google AuthnReq
    if (
        flow.request.host == "accounts.google.com"
        and flow.request.path == "/o/oauth2/v2/auth"
    ):
        _event("result", {"key": "idp", "val": "google"})
