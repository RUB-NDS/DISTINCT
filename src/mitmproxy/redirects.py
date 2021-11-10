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
"""

from mitmproxy.http import HTTPFlow

def make_document(status_code: int, location: str) -> str:
    """ Returns an HTTP/200 document that represents HTTP/3** redirects """
    return f'''<html
        _sso._type="redirect"
        _sso._status_code="{status_code}"
        _sso._location="{location}">
    </html>
    '''

def response(flow: HTTPFlow) -> None:
    """ Transform HTTP/3** redirects to HTTP/200 documents """

    status_code = flow.response.status_code
    if status_code in [302]:
        location : str = flow.response.headers["Location"]

        # Transform HTTP/3** response to HTTP/200 response
        flow.response.status_code = 200
        del flow.response.headers["Location"]
        flow.response.headers["Content-Type"] = "text/html"
        flow.response.set_content(bytes(
            make_document(status_code, location),
            "utf-8"
        ))
