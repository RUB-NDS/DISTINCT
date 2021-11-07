let detect_frame = () => {

    /* DOCUMENT */

    /* Report when this extension is executed */
    _sso._event("extensioninit", {});

    /* Report when document finished loading */
    document.onreadystatechange = () => {
        switch(document.readyState) {
            case "loading":
                _sso._event("documentloading", {})
            case "interactive":
                _sso._event("documentinteractive", {html: _sso._html()})
            case "complete":
                _sso._event("documentcomplete", {})
        }
    };

    /* Report when document is unloaded */
    window._sso._addEventListener("beforeunload", () => {
        _sso._event("documentbeforeunload", {});
    });

    /* POPUPS */

    window._sso._popups = []; // Save popups in list similar to window.frames

    /* Wrapper of window.open function */
    window.open = function open(...args) {
        let popup = window._sso._open(...args);
        window._sso._popups.push(popup);
        _sso._event("windowopen", {url: args[0], popup_hierarchy: _sso._hierarchy(popup)});
        return popup;
    }

    /* Wrapper of window.close function */
    window.close = function close(...args) {
        _sso._event("windowclose", {}).finally(() => {
            window._sso._close(...args); // Close window once event is acknowledged
        });
    }

    /* Report when window.closed property is accessed */
    Object.defineProperty(window, "closed", {
        get: () => {
            _sso._event("closedaccessed", {closed: window._sso._closed_get()});
            return window._sso._closed_get();
        }
    });

    /* SOURCE CODE */

    /* Dump the current frame (href, hierarchy, html) when dumpframe event is received */
    window._sso._addEventListener("message", (e) => {
        if (e.data.cmd === "dumpframe") {
            _sso._event("dumpframe", {html: _sso._html()});
        }
    });

    console.info("detect_frame.js initialized");
}

let detect_frame_script = document.createElement("script");
detect_frame_script.classList.add("chromeextension");
detect_frame_script.textContent = "(" + detect_frame.toString() + ")()";
document.documentElement.prepend(detect_frame_script);
