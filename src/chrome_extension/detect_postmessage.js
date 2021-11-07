let detect_postmessage = () => {

	// Blacklist

	window._sso._pmblacklist = [
		"safeframe.googlesyndication.com"
	]

	// Helpers

	window._sso._advertise = function() {
		function go_down(current) {
			for (let i = 0; i < current.frames.length; i++) {
				// Child
				current.frames[i].source_frame = window.self;
				go_down(current.frames[i]);
			}
			for (let i = 0; i < current._sso._popups.length, current._sso._popups[i] != undefined; i++) {
				// Popup
				current._sso._popups[i].source_frame = window.self;
				go_down(current._sso._popups[i]);
			}
		}
		function go_up(current) {
			if (current.parent !== current) {
				// Parent
				current.parent.source_frame = window.self;
				// Enumerate Popups
				for (let i = 0; i < current.parent._sso._popups.length, current.parent._sso._popups[i] != undefined; i++) {
					current.parent._sso._popups[i].source_frame = window.self;
					go_down(current.parent._sso._popups[i]);
				}
				// Enumerate Frames
				for (let i = 0; i < current.parent.frames.length; i++) {
					if (current.parent.frames[i] !== current) {
						// Sibling
						current.parent.frames[i].source_frame = window.self;
						go_down(current.parent.frames[i]);
					}
				}
				go_up(current.parent);
			} else {
				// We reached the top
				if (current.opener) {
					// Opener
					current.opener.source_frame = window.self;
					for (let i = 0; i < current.opener._sso._popups.length, current.opener._sso._popups[i] != undefined; i++) {
						current.opener._sso._popups[i].source_frame = window.self;
						go_down(current.opener._sso._popups[i]);
					}
					go_up(current.opener);
				}
			}
		}
		window.source_frame = window.self;
		go_down(window);
		go_up(window);
	}

	// Custom PostMessage Receiver and Callbacks

	window._sso._callbacks = [];

	window._sso._addEventListener("messagesent", (event) => {

		// Proxy message event

		const proxyhandler = {
			get: function(target, prop, receiver) {
				if (prop == "origin") {
					target._origin_accessed = true;
				}
				return Reflect.get(...arguments);
			}
		};
		let target = event.detail.event;
		const proxy = new Proxy(target, proxyhandler);

		// Invoke message event handlers

		for (let cb of window._sso._callbacks)
			cb(proxy);

		if (window._sso._onmessage)
			window._sso._onmessage(proxy);

		if (proxy._origin_accessed) {
			event.detail.log.source_origin_accessed = "TRUE";
		} else {
			event.detail.log.source_origin_accessed = "FALSE";
		}
		
		// Filter out messages from sources in blacklist
		
		for (let blacklisted of window._sso._pmblacklist) {
			if (new URL(event.detail.log.source_origin).host.includes(blacklisted))
				return;
			if (new URL(event.detail.log.target_origin).host.includes(blacklisted))
				return;
		}

		// Logging

		if (event.detail.log["target_origin_check"] == "*")
			console.warn(`[PM Callalyzer] Message sent: ${JSON.stringify(event.detail.log)}`);
		else
			console.info(`[PM Callalyzer] Message sent: ${JSON.stringify(event.detail.log)}`);

        // Report

        _sso._event("postmessagereceived", {
            "receiver": event.detail.log.target_frame,
            "sender": event.detail.log.source_frame,
            "data": event.detail.log.message_payload,
            "datatype": event.detail.log.message_type,
            "targetorigincheck": event.detail.log.target_origin_check,
            "sourceoriginaccessed": event.detail.log.source_origin_accessed
        });

	});

	// Wrap window.onmessage and window.addEventListener function
	
	Object.defineProperties(window, {
		onmessage: {
			set: (cb) => {
				console.info(`[PM Callalyzer] window.onmessage = ${cb ? cb.toString() : JSON.stringify(cb)}`);
				window._sso._onmessage = cb;
			},
			get: () => window._sso._onmessage
		},
		addEventListener: {
			value: (...args) => {
				let [type, callback, options] = args;
				if (type == "message") {
					console.info(`[PM Callalyzer] window.addEventListener("message", ${callback ? callback.toString() : JSON.stringify(callback)}, ${options})`);
					window._sso._callbacks.push(callback);
				} else {
					window._sso._addEventListener(...args);
				}
			}
		},
		removeEventListener: {
			value: (...args) => {
				let [type, callback, options] = args;
				if (type == "message") {
					console.info(`[PM Callalyzer] window.removeEventListener("message", ${callback ? callback.toString() : JSON.stringify(callback)}, ${options})`);
					for (let i = 0; i < window._sso._callbacks.length; i++) {
						if (window._sso._callbacks[i] === callback)
                            window._sso._callbacks.splice(i, 1);
					}
				} else {
					window._sso._removeEventListener(...args);
				}
			}
		}
	});

	// Wrap window.postMessage function

	window.postMessage = function postMessage(...args) {

		// Halt execution such that we get access to source information
		debugger; // Now we can access source_frame, source_hierarchy, and source_origin variables
		
		let [message, targetOrigin, transfer] = args;

		// Serialize Message

		let message_type = typeof message;
		let message_string = "";
		switch(message_type) {
			case "number": message_string = message.toString(); break;
			case "boolean": message_string = message.toString(); break;
			case "string": message_string = message; break;
			default: message_string = JSON.stringify(message); break;
		}

		// Transfer
		let ports = [];
		if (transfer) {
			for (let item of transfer) {
				if (item instanceof MessagePort) ports.push(item);
			}
		}

		// Dispatch Message

		let messagesent = new CustomEvent("messagesent", {
			detail: {
				"log": {
					"source_frame": source_hierarchy,
					"source_origin": source_origin,
					"target_frame": _sso._hierarchy(window),
					"target_origin": window.location.href,
					"target_origin_check": (typeof targetOrigin == "string") ? targetOrigin : JSON.stringify(targetOrigin),
					"message_type": message_type,
					"message_payload": message_string,
					"transfer": (transfer ? transfer.toString() : "N/A"),
				},
				"event": {
					"data": message,
					"origin": (new URL(source_origin)).origin,
					"source": source_frame,
					"lastEventId": "",
					"ports": ports
				}
			}
		});
		
		window._sso._dispatchEvent(messagesent);
	}

	console.info("detect_postmessage.js initialized");
}

let detect_postmessage_script = document.createElement("script");
detect_postmessage_script.classList.add("chromeextension");
detect_postmessage_script.textContent = "(" + detect_postmessage.toString() + ")()";
document.documentElement.prepend(detect_postmessage_script);
