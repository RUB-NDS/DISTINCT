let helpers = () => {

    /* Parse and return URL query parameters */
    function query_params() {
        let params = {};
        location.search.substr(1).split("&").forEach((keyval) => {
            let keyvalsplitted = keyval.split("=");
            let key = decodeURIComponent(keyvalsplitted[0]);
            let val = decodeURIComponent(keyvalsplitted[1]);
            params[key] = val;
        });
        return params;
    }
    
    /* Parse and return URL hash parameters */
    function hash_params() {
        let params = {};
        location.hash.substr(1).split("&").forEach((keyval) => {
            let keyvalsplitted = keyval.split("=");
            let key = decodeURIComponent(keyvalsplitted[0]);
            let val = decodeURIComponent(keyvalsplitted[1]);
            params[key] = val;
        });
        return params;
    }

    /* Creates a json object including fields in the form */
    /* Source: https://jordanfinners.dev/blogs/how-to-easily-convert-html-form-to-json */
    function form2json(form) {
        const data = new FormData(form);
        return Array.from(data.keys()).reduce((result, key) => {
            if (result[key]) {
                result[key] = data.getAll(key);
                return result;
            }
            result[key] = data.get(key);
            return result;
        }, {});
    };

    /* Get target window's hierarchy, i.e., top.popup.top.frames[0] */
    function hierarchy(target) {
		var path = "";
		function go_up(current) {
			if (current.parent !== current) {
				// Which child am I?
				for (let i = 0; i < current.parent.frames.length; i++) {
					if (current.parent.frames[i] === current) {
						path = `frames[${i}]` + (path.length ? "." : "") + path;
					}
				}
				go_up(current.parent, path);
			} else {
				// We reached the top
				// If opener is set, go up in opener context
				if (current.opener) {
                    // Which popup am I?
                    for (let i = 0; i < current.opener._popups.length; i++) {
                        if (current.opener._popups[i] === current) {
                            path = `popups[${i}]` + (path.length ? "." : "") + path;
                        }
                    }
					go_up(current.opener, path)
				} else {
                    path = "top" + (path.length ? "." : "") + path;
                }
			}
		}
		go_up(target);
		return path;
	}

    /* Send a postMessage to all frames in current execution context */
    function postMessageAll(message) {
		function go_down(current) {
			for (let i = 0; i < current.frames.length; i++) {
				// Child
				current.frames[i].postMessage(message, "*");
				go_down(current.frames[i]);
			}
			for (let i = 0; i < current._popups.length, current._popups[i].closed === false; i++) {
				// Popup
				current._popups[i].postMessage(message, "*");
				go_down(current._popups[i]);
			}
		}
		function go_up(current) {
			if (current.parent !== current) {
				// Parent
				current.parent.postMessage(message, "*");
				// Enumerate Popups
				for (let i = 0; i < current.parent._popups.length, current.parent._popups[i].closed === false; i++) {
					current.parent._popups[i].postMessage(message, "*");
					go_down(current.parent._popups[i]);
				}
				// Enumerate Frames
				for (let i = 0; i < current.parent.frames.length; i++) {
					if (current.parent.frames[i] !== current) {
						// Sibling Frame
						current.parent.frames[i].postMessage(message, "*");
						go_down(current.parent.frames[i]);
					}
				}
				go_up(current.parent);
			} else {
				// We reached the top
				if (current.opener) {
					// Opener
					current.opener.postMessage(message, "*");
                    // Enumerate Popups
					for (let i = 0; i < current.opener._popups.length, current.opener._popups[i].closed === false; i++) {
						if (current.opener._popups[i] !== current) {
                            // Sibling Popup
                            current.opener._popups[i].postMessage(message, "*");
						    go_down(current.opener._popups[i]);
                        }
					}
                    // Enumerate Frames
                    for (let i = 0; i < current.opener.frames.length; i++) {
                        current.opener.frames[i].postMessage(message, "*");
                        go_down(current.opener.frames[i]);
                    }
					go_up(current.opener);
				}
			}
		}
		window.postMessage(message, "*");
		go_down(window);
		go_up(window);
	}

    /* Dump the current frame, i.e., href, hierarchy, source code */
    function dump_frame() {
        let html = document.documentElement.outerHTML;
        _report("html", {html: html});
    }
    
    /* Simple logger that logs to console */
    function log(message) {
        console.info(`%c[sso-context-switching]%c ${message}`, "color:green;", "");
    }

    /* Send signals back to python script */
    function report(key, val) {
        let obj = val || {};
        obj["hierarchy"] = _hierarchy(self);
        obj["href"] = location.href;

        // Format: {"report": {"key": ..., "val": ...}}
        fetch("http://localhost:7777", {
            method: "POST",
            mode: "cors",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({"report": {"key": key, "val": obj}})
        }).then(r => r.json()).then(r => {
            if (r.success) {
                console.info(
                    `%c[sso-context-switching]%c\nkey=${key}\nval=${JSON.stringify(obj)}`,
                    "color:green;", ""
                );
            } else {
                console.info(
                    `%c[sso-context-switching]%c\nkey=${key}\nval=${JSON.stringify(obj)}`,
                    "color:red;", ""
                );
            }
        }).catch(e => {
            console.info(
                `%c[sso-context-switching]%c\nkey=${key}\nval=${JSON.stringify(obj)}`,
                "color:red;", ""
            );
        });
    }

    /* Function wrappers */
    window._postMessage = window.postMessage;
    window._addEventListener = window.addEventListener;
    window._open = window.open;
    window._close = window.close;

    /* Global access */
    window._qparams = query_params();
    window._hparams = hash_params();
    window._form2json = form2json;
    window._hierarchy = hierarchy;
    window._postMessageAll = postMessageAll;
    window._dump_frame = dump_frame;
    window._log = log;
    window._report = report;
    window._popups = [];

    /* Report when new frame is created */
    window._addEventListener("load", () => {
        let html = document.documentElement.outerHTML;
        _report("framecreated");
    });

    /* Report when frame is destroyed */
    window._addEventListener("beforeunload", () => {
        _report("framedestroyed");
    });

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
        self.setTimeout(() => {
            window._close(...args);
        }, 1000);
    }

    /* Report when dumpframes event is received */
    window._addEventListener("message", (e) => {
        if (e.data.cmd === "dumpframe") {
            _report("dumpframe");
            _dump_frame();
        }
    });

}

let helpers_script = document.createElement("script");
helpers_script.textContent = "(" + helpers.toString() + ")()";
document.documentElement.prepend(helpers_script);
