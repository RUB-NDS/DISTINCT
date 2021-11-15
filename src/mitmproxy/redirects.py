""" Transform HTTP/3** redirects to HTTP/200 documents.
    This is necessary because content scripts should be injected in redirects as well.

    Therefore, redirects return a simple HTTP/200 document that looks like this:
    <html
        _sso._type="redirect"
        _sso._status_code="302"
        _sso._location="https://target.com/redirected" />
    </html>

    The content scripts are checking in each document if these attributes are set and if they are,
    they manually trigger the redirect by setting the location.href.

    Transform responses that contain the "Refresh" header into HTTP/200 documents containing the
    <meta http-equiv="refresh" content="..."> directive. This is necessary because the content
    scripts would otherwise be not injected.
"""

from mitmproxy.http import HTTPFlow

def make_redirect_document(status_code: int, location: str) -> str:
    """ Returns an HTTP/200 document that represents HTTP/3** redirects """
    return f'''<html
        _sso._type="redirect"
        _sso._status_code="{status_code}"
        _sso._location="{location}">
    </html>
    '''

def make_meta_document(meta_content: str) -> str:
    """ Returns an HTTP/200 document that represents the "Refresh" header """
    return f'''<html _sso._type="meta">
        <head>
            <meta http-equiv="refresh" content="{meta_content}">
        </head>
        <body></body>
    </html>
    '''

def response(flow: HTTPFlow) -> None:
    status_code = flow.response.status_code
    
    # Transform HTTP/3** redirects to HTTP/200 documents
    if "Location" in flow.response.headers:
        location : str = flow.response.headers["Location"]

        # Transform HTTP/3** response to HTTP/200 response
        flow.response.status_code = 200
        del flow.response.headers["Location"]
        flow.response.headers["Content-Type"] = "text/html"
        flow.response.set_content(bytes(
            make_redirect_document(status_code, location),
            "utf-8"
        ))
    
    # Transform response with "Refresh" header to <meta http-equiv="refresh" ...>
    elif "Refresh" in flow.response.headers:
        refresh : str = flow.response.headers["Refresh"]

        flow.response.status_code = 200
        del flow.response.headers["Refresh"]
        flow.response.headers["Content-Type"] = "text/html"
        flow.response.set_content(bytes(
            make_meta_document(refresh),
            "utf-8"
        ))
