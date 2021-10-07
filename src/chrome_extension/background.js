/*
    Disable CSP header such that our requests to localhost:20200
    do not get blocked by website's CSP policy.
*/

chrome.webRequest.onHeadersReceived.addListener((details) => {
    let headers = details.responseHeaders;
    for (let header of headers) {
        if (header.name.toLowerCase() == "content-security-policy") {
            header.value = "";
        }
    }
    return {responseHeaders: headers}
}, {
    urls: ["*://*/*"],
    types: ["main_frame", "sub_frame", "object"],
}, [
    "blocking",
    "responseHeaders"
]);
