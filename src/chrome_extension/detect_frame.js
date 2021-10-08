let detect_frame = () => {

    /* Function wrappers */
    window._postMessage = window.postMessage;
    window._addEventListener = window.addEventListener;
    window._open = window.open;
    window._close = window.close;
    
    /* DOCUMENT */

    /* Report when document is loaded */
    document.onreadystatechange = () => {
        switch(document.readyState) {
            case "loading":
                _event("documentloading", {})
            case "interactive":
                _event("documentinteractive", {html: _html()})
            case "complete":
                _event("documentcomplete", {})
        }
    };

    /* Report when document is unloaded */
    window._addEventListener("beforeunload", () => {
        _event("documentbeforeunload", {});
    });

    /* POPUPS */

    window._popups = []; // Save popups in list similar to window.frames

    /* Wrapper of window.open function */
    window.open = function open(...args) {
        let popup = window._open(...args);
        window._popups.push(popup);
        _event("windowopen", {url: args[0], popup_hierarchy: _hierarchy(popup)});
        return popup;
    }

    /* Wrapper of window.close function */
    window.close = function close(...args) {
        _event("windowclose", {});
        // Wait a second to give the event time to be sent to python backend
        self.setTimeout(() => {
            window._close(...args);
        }, 1000);
    }

    /* DUMP FRAME */

    /* Dump the current frame (href, hierarchy, html) when dumpframe event is received */
    window._addEventListener("message", (e) => {
        if (e.data.cmd === "dumpframe") {
            _event("dumpframe", {html: _html()});
        }
    });

}

let detect_frame_script = document.createElement("script");
detect_frame_script.classList.add("chromeextension");
detect_frame_script.textContent = "(" + detect_frame.toString() + ")()";
document.documentElement.prepend(detect_frame_script);
