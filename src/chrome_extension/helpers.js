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

    /* Get the HTML markup of the current window */
    function html() {
        let docelement = document.documentElement.cloneNode(true);
        
        // Remove all inline scripts of chrome extension
        let extensionscripts = docelement.getElementsByClassName("chromeextension");
        while (extensionscripts[0]) {
            extensionscripts[0].parentNode.removeChild(extensionscripts[0]);
        }

        // Remove all inline CSS stylesheets
        let stylesheets = docelement.getElementsByTagName("style");
        while(stylesheets[0]) {
            stylesheets[0].parentNode.removeChild(stylesheets[0]);
        }

        return docelement.outerHTML;
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

    /* Get target window's hierarchy, i.e., top.popups[0].frames[0] */
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

    /* Send in-browser events to python backend */
    function event(key, val) {
        // Where did this event trigger?
        val["hierarchy"] = _hierarchy(self);
        val["href"] = location.href;

        // We are working with a promise
        // This allows us to either send event and don't care of whether it was
        // received by the event server or we can send the event and wait for it
        // to be acknowledged by the event server
        return new Promise((resolve, reject) => {
            
            // Send request to event server and check response
            // Event format: {"event": {"key": "...", "val": {...}}}
            fetch("http://localhost:20200", {
                method: "POST",
                mode: "cors",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({"event": {"key": key, "val": val}}, (key, val) => {
                    return typeof val === "undefined" ? null : val;
                })
            }).then(r => r.json()).then(r => {
                
                // Resolve if event was successfully received by event server
                // and reject if event server failed to receive event
                if (r.success) {
                    console.info(
                        `%c[sso-context-switching]%c\nkey=${key}\nval=${JSON.stringify(val)}`,
                        "color:green;", ""
                    );
                    resolve();
                } else {
                    console.info(
                        `%c[sso-context-switching]%c\nkey=${key}\nval=${JSON.stringify(val)}`,
                        "color:red;", ""
                    );
                    reject("Event server failed to receive event");
                }

            }).catch(e => {
                console.info(
                    `%c[sso-context-switching]%c\nkey=${key}\nval=${JSON.stringify(val)}`,
                    "color:red;", ""
                );
                reject(e);
            });

        });
        
    }

    /* Global access */
    window._qparams = query_params();
    window._hparams = hash_params();
    window._html = html;
    window._form2json = form2json;
    window._hierarchy = hierarchy;
    window._postMessageAll = postMessageAll;
    window._event = event;

}

let helpers_script = document.createElement("script");
helpers_script.classList.add("chromeextension");
helpers_script.textContent = "(" + helpers.toString() + ")()";
document.documentElement.prepend(helpers_script);
