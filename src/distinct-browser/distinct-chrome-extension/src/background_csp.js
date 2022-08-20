/**
 * This background script disables the Content Security Policy header of all websites such that the
 * POST requests to the event server (localhost:20200) are not blocked by the website's CSP policy.
 */

chrome.webRequest.onHeadersReceived.addListener((details) => {
    let headers = details.responseHeaders;
    for (let header of headers) {
        if (
            header.name.toLowerCase() == "content-security-policy"
            || header.name.toLowerCase() == "content-security-policy-report-only"
        ) {
            header.value = "";
        }
    }
    return {responseHeaders: headers};
}, {
    urls: ["http://*/*", "https://*/*"],
    types: ["main_frame", "sub_frame", "object"],
}, [
    "blocking",
    "responseHeaders"
]);

console.info("background_csp.js initialized");
