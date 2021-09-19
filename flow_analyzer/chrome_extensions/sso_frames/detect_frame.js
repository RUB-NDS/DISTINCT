let detect_frame = () => {

    /* Function wrappers */
    window._postMessage = window.postMessage;
    window._addEventListener = window.addEventListener;
    window._open = window.open;
    window._close = window.close;
    
    /* FRAME CREATED / DESTROYED */

    document.onreadystatechange = () => {
        switch(document.readyState) {
            case "loading":
                _report("documentloading")
            case "interactive":
                _report("documentinteractive")
            case "complete":
                _report("documentcomplete", {html: document.documentElement.outerHTML})
        }
    };

    /* Report when new frame is created */
    window._addEventListener("load", () => {
        let html = document.documentElement.outerHTML;
        _report("framecreated", {html: html});
    });

    /* Report when frame is destroyed */
    window._addEventListener("beforeunload", () => {
        _report("framedestroyed");
    });

    /* POPUPS */

    window._popups = []; // Save popups in list similar to window.frames

    /* Wrapper of window.open function */
    window.open = function open(...args) {
        let popup = window._open(...args);
        _report("popupopened", {url: args[0]});
        window._popups.push(popup);
        return popup;
    }

    /* Wrapper of window.close function */
    window.close = function close(...args) {
        _report("popupclosed");
        // Wait a second to give event time to be sent to handler
        self.setTimeout(() => {
            window._close(...args);
        }, 1000);
    }

    /* OTHERS */

    /* Dump the current frame, i.e., href, hierarchy, source code */
    function dump_frame() {
        let html = document.documentElement.outerHTML;
        _report("dumpframe", {html: html});
    }
    
    /* Report when dumpframes event is received */
    window._addEventListener("message", (e) => {
        if (e.data.cmd === "dumpframe") {
            _dump_frame();
        }
    });

    /* Global access */
    window._dump_frame = dump_frame;

}

let detect_frame_script = document.createElement("script");
detect_frame_script.textContent = "(" + detect_frame.toString() + ")()";
document.documentElement.prepend(detect_frame_script);
