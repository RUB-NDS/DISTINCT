/**
 * This background script fixes the browser's CORS implementation which we disabled with the
 * startup flag "--disable-web-security". This flag causes the browser to not send the "Origin"
 * header in CORS requests. This breaks some websites. Thus, if we have a CORS request, we manually
 * add the "Origin" header to the request.
 */

chrome.webRequest.onBeforeSendHeaders.addListener((details) => {
    let headers = details.requestHeaders;
    if (
        details.initiator // origin where the request was initiated
    ) {
        for (let header of headers) {
            if (
                header.name.toLowerCase() == "sec-fetch-mode"
                && header.value.toLowerCase() == "cors"
            ) {
                // This is a cors request -> include origin header
                headers.push({
                    "name": "Origin",
                    "value": details.initiator
                });
            }
        }
    }
    
    return {requestHeaders: headers};
}, {
    urls: ["http://*/*", "https://*/*"]
}, [
    "blocking",
    "requestHeaders",
    "extraHeaders"
]);

console.info("background_cors.js initialized");
