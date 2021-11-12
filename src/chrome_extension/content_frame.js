/**
 * This content script reports on events related to basic frame operations.
 * These include the reporting of different document loading stages and the handling with popups.
 */

let content_frame = () => {

    /* Report when the document is initialized / when this extension is executed */
    _sso._event("documentinit", {});

    /* Report the different document loading stages */
    document.onreadystatechange = () => {
        switch(document.readyState) {
            case "loading":
                _sso._event("documentloading", {});
            case "interactive":
                _sso._event("documentinteractive", {html: _sso._html()});
            case "complete":
                _sso._event("documentcomplete", {});
        }
    };

    /* Report when the document is unloaded */
    window._sso._addEventListener("beforeunload", () => {
        _sso._event("documentbeforeunload", {});
    });

    /* Save popup references in list similar to window.frames */
    window._sso._popups = [];

    /* Wrapper of window.open function: save popup references in list when opened */
    window.open = function open(...args) {
        let popup = window._sso._open(...args);
        window._sso._popups.push(popup);
        _sso._event("windowopen", {url: args[0], popup_hierarchy: _sso._hierarchy(popup)});
        return popup;
    }

    /* Wrapper of window.close function: report when popup is closed */
    window.close = function close(...args) {
        _sso._event("windowclose", {opener_hierarchy: _sso._hierarchy(opener)}).finally(() => {
            window._sso._close(...args); // Close window once backend acknowledges event received
        });
    }

    /* Report when window.closed property is accessed */
    Object.defineProperty(window, "closed", {
        get: () => {
            _sso._event("closedaccessed", {closed: window._sso._closed_get()});
            return window._sso._closed_get();
        }
    });

    console.info("content_frame.js initialized");
}

let content_frame_script = document.createElement("script");
content_frame_script.classList.add("chromeextension");
content_frame_script.textContent = "(" + content_frame.toString() + ")()";
document.documentElement.prepend(content_frame_script);
