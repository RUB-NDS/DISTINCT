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
                _report("documentloading")
            case "interactive":
                _report("documentinteractive", {html: _html()})
            case "complete":
                _report("documentcomplete")
        }
    };

    /* Report when document is unloaded */
    window._addEventListener("beforeunload", () => {
        _report("documentbeforeunload");
    });

    /* POPUPS */

    window._popups = []; // Save popups in list similar to window.frames

    /* Wrapper of window.open function */
    window.open = function open(...args) {
        let popup = window._open(...args);
        window._popups.push(popup);
        _report("windowopen", {url: args[0], popup_hierarchy: _hierarchy(popup)});
        return popup;
    }

    /* Wrapper of window.close function */
    window.close = function close(...args) {
        _report("windowclose");
        // Wait a second to give event time to be sent to handler
        self.setTimeout(() => {
            window._close(...args);
        }, 1000);
    }

    /* OTHERS */

    /* Dump the current frame, i.e., href, hierarchy, source code */
    function dump_frame() {
        _report("dumpframe", {html: _html()});
    }
    
    /* Report when dumpframe event is received */
    window._addEventListener("message", (e) => {
        if (e.data.cmd === "dumpframe") {
            _dump_frame();
        }
    });

    /* Global access */
    window._dump_frame = dump_frame;

}

let detect_frame_script = document.createElement("script");
detect_frame_script.classList.add("chromeextension");
detect_frame_script.textContent = "(" + detect_frame.toString() + ")()";
document.documentElement.prepend(detect_frame_script);
