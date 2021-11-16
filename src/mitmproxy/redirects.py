""" 1) Transform HTTP redirects using the "Location" header to HTTP/200 documents.
    This is necessary because content scripts should be injected in redirects as well.

    Therefore, redirects using "Location" return a simple HTTP/200 document that looks like this:
    <html
        _sso._type="location"
        _sso._status_code="302"
        _sso._location="https://target.com/redirected" />
    </html>

    2) Add information about the "Refresh" header as <html> attributes.
    This is necessary because the content scripts should detect the "Refresh" header.

    Therefore, responses using "Refresh" return an HTTP/200 document that looks like this:
    <html
        _sso._type="refresh"
        _sso._status_code="200"
        _sso._refresh="0; url=https://target.com/redirected">

        <original response ...>
    </html>

    The content scripts are checking in each document if these <html> attributes are set.
"""

from mitmproxy.http import HTTPFlow
from bs4 import BeautifulSoup

def make_location_document(status_code: int, location: str) -> str:
    """ Returns an HTTP/200 document that represents HTTP redirects using "Location" """
    return f'''<html
        _sso._type="location"
        _sso._status_code="{status_code}"
        _sso._location="{location}">
    </html>
    '''

def response(flow: HTTPFlow) -> None:
    status_code = flow.response.status_code
    
    # Transform HTTP redirects using the "Location" header to HTTP/200 documents
    if "Location" in flow.response.headers:
        location = flow.response.headers["Location"]

        flow.response.status_code = 200
        del flow.response.headers["Location"]
        flow.response.headers["Content-Type"] = "text/html"
        flow.response.set_content(bytes(
            make_location_document(status_code, location),
            "utf-8"
        ))
    
    # Add information about the "Refresh" header as <html> attributes
    elif (
        "Refresh" in flow.response.headers
        and "Content-Type" in flow.response.headers
        and "text/html" in flow.response.headers["Content-Type"]
    ):
        refresh = flow.response.headers["Refresh"]

        doc = BeautifulSoup(flow.response.text)
        html = doc.find("html")
        if html:
            html["_sso._type"] = "refresh"
            html["_sso._status_code"] = status_code
            html["_sso._refresh"] = refresh
            flow.response.set_content(bytes(
                str(doc),
                "utf-8"
            ))
