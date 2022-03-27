/**
 * This content script monitors the use of web messaging:
 *      - PostMessage API
 *      - Channel Messaging API
 *      - Broadcast Channel API
 *      - Custom Events
 *
 * The postMessage API is emulated.
 * We use it to intercept the registration of message event listeners and for the analysis of
 * postMessages. We get automatic access to the postMessage receiver origin check.
 * That is, we can extract the content of the postMessage function's second parameter.
 *
 * Syntax: window.postMessage(data, receiver_origin, ...)
 */

let content_messaging = () => {

    // Blacklisted origins from/to which we want to ignore postMessages
    // Reason: Ads and analytics are agressively sending a huge amount of postMessages
    // which we are not interested in.

    window._sso._pmblacklist = [
        "safeframe.googlesyndication.com"
    ]

    // Default events that can be dispatched on the window
    // If we want to detect the listening for / dispatching of custom events, we need to know
    // all default window events such that we exclude them from being classified as custom events.
    // Source: https://developer.mozilla.org/en-US/docs/Web/Events (list under "Window")
    window._sso._default_window_events = [
        "afterprint", "animationcancel", "animationend", "animationiteration",
        "animationstart", "appinstalled", "beforeprint", "beforeunload", "blur", "copy", "cut",
        "devicemotion", "deviceorientation", "DOMContentLoaded", "error", "focus",
        "gamepadconnected", "gamepaddisconnected", "hashchange", "languagechange", "load",
        "messageerror", "message", "offline", "online", "orientationchange", "pagehide",
        "pageshow", "paste", "popstate", "rejectionhandled", "resize", "storage",
        "transitioncancel", "transitionend", "transitionrun", "transitionstart",
        "unhandledrejection", "unload", "vrdisplayactivate", "vrdisplayblur", "vrdisplayconnect",
        "vrdisplaydeactivate", "vrdisplaydisconnect", "vrdisplayfocus",
        "vrdisplaypointerrestricted", "vrdisplaypointerunrestricted", "vrdisplaypresentchange",
        "scroll", "touchmove", "keydown"
    ]

    // If executed in frame X, this function sets the window._sso._source_frame property
    // in all other frames that can be reached by frame X.
    // This property holds a reference to frame X.
    // If a sender sends a postMessage to a receiver, the sender executes this function to indicate
    // that the postMessage was sent by itself.

    window._sso._advertise = function() {
        function go_down(current) {
            for (let i = 0; i < current.frames.length; i++) {
                // Child
                current.frames[i]._sso._source_frame = window.self;
                go_down(current.frames[i]);
            }
            for (let i = 0; i < current._sso._popups.length, current._sso._popups[i] != undefined; i++) {
                // Popup
                current._sso._popups[i]._sso._source_frame = window.self;
                go_down(current._sso._popups[i]);
            }
        }
        function go_up(current) {
            if (current.parent !== current) {
                // Parent
                current.parent._sso._source_frame = window.self;
                // Enumerate Popups
                for (let i = 0; i < current.parent._sso._popups.length, current.parent._sso._popups[i] != undefined; i++) {
                    current.parent._sso._popups[i]._sso._source_frame = window.self;
                    go_down(current.parent._sso._popups[i]);
                }
                // Enumerate Frames
                for (let i = 0; i < current.parent.frames.length; i++) {
                    if (current.parent.frames[i] !== current) {
                        // Sibling
                        current.parent.frames[i]._sso._source_frame = window.self;
                        go_down(current.parent.frames[i]);
                    }
                }
                go_up(current.parent);
            } else {
                // We reached the top
                if (current.opener) {
                    // Opener
                    current.opener._sso._source_frame = window.self;
                    for (let i = 0; i < current.opener._sso._popups.length, current.opener._sso._popups[i] != undefined; i++) {
                        current.opener._sso._popups[i]._sso._source_frame = window.self;
                        go_down(current.opener._sso._popups[i]);
                    }
                    go_up(current.opener);
                }
            }
        }
        window._sso._source_frame = window.self;
        go_down(window);
        go_up(window);
    }

    // PostMessage Callbacks

    window._sso._callbacks = [];
    window._sso._onmessage = null;

    // Wrappers of window.onmessage and window.addEventListener

    Object.defineProperties(window, {
        onmessage: {
            set: (cb) => {
                let cbstring = cb ? cb.toString() : JSON.stringify(cb);

                console.info(`window.onmessage = ${cbstring}`);
                _sso._event("addeventlistener", {
                    type: "message",
                    method: "onmessage",
                    callback: cbstring
                });

                window._sso._onmessage = cb;
            },
            get: () => window._sso._onmessage
        },
        addEventListener: {
            value: (...args) => {
                let [type, callback, options] = args;
                let cbstring = callback ? callback.toString() : JSON.stringify(callback);

                if (type == "message") {
                    console.info(`window.addEventListener("message", ${cbstring}, ${options})`);
                    _sso._event("addeventlistener", {
                        type: type,
                        method: "window.addEventListener",
                        callback: cbstring
                    });

                    window._sso._callbacks.push(callback);
                } else {
                    if (!_sso._default_window_events.includes(type)) {
                        // This event listener listens for a custom event
                        _sso._event("addeventlistener", {
                            type: type,
                            method: "window.addEventListener",
                            callback: cbstring
                        });
                    }

                    window._sso._addEventListener(...args);
                }
            }
        },
        removeEventListener: {
            value: (...args) => {
                let [type, callback, options] = args;
                let cbstring = callback ? callback.toString() : JSON.stringify(callback);

                if (type == "message") {
                    console.info(`window.removeEventListener("message", ${cbstring}, ${options})`);
                    _sso._event("removeeventlistener", {
                        type: type,
                        method: "window.removeEventListener",
                        callback: cbstring
                    });

                    for (let i = 0; i < window._sso._callbacks.length; i++) {
                        if (window._sso._callbacks[i] === callback)
                            window._sso._callbacks.splice(i, 1);
                    }
                } else {
                    if (!_sso._default_window_events.includes(type)) {
                        // This event listener listened for a custom event
                        _sso._event("removeeventlistener", {
                            type: type,
                            method: "window.removeEventListener",
                            callback: cbstring
                        });
                    }

                    window._sso._removeEventListener(...args);
                }
            }
        }
    });

    // Wrapper of window.postMessage

    window.postMessage = function postMessage(...args) {

        // Halt execution to get access to source information
        debugger;
        // Now we can access _sso._source_frame, _sso._source_hierarchy, and _sso._source_origin vars

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
                if ("_channel_id" in item)
                    ports.push(item);
            }
        }

        let ports_log = [];
        for (let port of ports) {
            ports_log.push({
                channel_id: port._channel_id,
                port_id: port._port_id
            });
        }

        // If this frame receives a port, then this frame is the target frame of all messages
        // that are sent to this port.
        // If this frame receives a port, then this frame is the source frame of all messages
        // that are sent to the other port entangled to the received port.
        for (let port of ports) {
            port._target_frame = _sso._hierarchy(window);
            port._other_port._source_frame = _sso._hierarchy(window);
        }

        // Dispatch Message

        let pm = {
            "log": {
                "source_frame": _sso._source_hierarchy,
                "source_origin": _sso._source_origin,
                "target_frame": _sso._hierarchy(window),
                "target_origin": window.location.href,
                "target_origin_check": (typeof targetOrigin == "string") ? targetOrigin : JSON.stringify(targetOrigin),
                "message_type": message_type,
                "message_payload": message_string,
                "ports": ports_log
            },
            "event": {
                "data": message,
                "origin": (new URL(_sso._source_origin)).origin,
                "source": _sso._source_frame,
                "lastEventId": "",
                "ports": ports
            }
        };

        // Proxy postMessage

        let proxyhandler = {
            get: function(target, prop, receiver) {
                if (prop == "origin") {
                    target._origin_accessed = true;
                }
                return Reflect.get(...arguments);
            }
        };
        let target = pm.event;
        let proxy = new Proxy(target, proxyhandler);

        // Invoke message event handlers

        for (let cb of window._sso._callbacks)
            cb(proxy);

        if (window._sso._onmessage)
            window._sso._onmessage(proxy);

        if (proxy._origin_accessed) {
            pm.log.source_origin_accessed = true;
        } else {
            pm.log.source_origin_accessed = false;
        }

        // Filter out postMessage from/to blacklisted origins

        for (let blacklisted of window._sso._pmblacklist) {
            if (new URL(pm.log.source_origin).host.includes(blacklisted))
                return;
            if (new URL(pm.log.target_origin).host.includes(blacklisted))
                return;
        }

        // Report

        _sso._event("postmessagereceived", {
            "target_frame":pm.log.target_frame,
            "source_frame": pm.log.source_frame,
            "data": pm.log.message_payload,
            "data_type": pm.log.message_type,
            "ports": pm.log.ports,
            "target_origin_check": pm.log.target_origin_check,
            "source_origin_accessed": pm.log.source_origin_accessed
        });

    }

    // Wrapper of CustomEvent constructor

    window.CustomEvent = function CustomEvent(...args) {
        let type = args[0];
        let data = undefined;
        let data_type = typeof undefined;

        if (args[1] && args[1]["detail"]) {
            data = args[1]["detail"];
            data_type = typeof data;
        }

        _sso._event("customeventnew", {
            type: type,
            data: data,
            data_type: data_type
        });

        let custom_event = new window._sso._CustomEvent(...args);
        custom_event._source_frame = _sso._hierarchy(window);

        return custom_event;
    }

    // Wrapper of window.dispatchEvent

    window.dispatchEvent = function dispatchEvent(...args) {
        let event = args[0];
        let type = event.type;
        let data = event.detail || undefined;
        let data_type = typeof data;

        if (!_sso._default_window_events.includes(type)) {
            // This is a custom event
            _sso._event("customeventreceived", {
                type: type,
                data: data,
                data_type: data_type,
                source_frame: event._source_frame,
                target_frame: _sso._hierarchy(window)
            });
        }

        return window._sso._dispatchEvent(...args);
    }

    // Wrapper of MessageChannel constructor

    window.MessageChannel = function MessageChannel(...args) {

        let channel = new window._sso._MessageChannel(...args);
        let channel_id = Math.floor(Math.random() * 1000);

        // Ports are identified by a pair of (Channel ID, Port ID)
        channel.port1._channel_id = channel_id;
        channel.port2._channel_id = channel_id;
        channel.port1._port_id = "port1";
        channel.port2._port_id = "port2";

        // Save a reference to port2 on port1 and port1 on port2
        channel.port1._other_port = channel.port2;
        channel.port2._other_port = channel.port1;

        // If we receive a message on port1 or port2, it was sent *from* this frame because port2
        // and port1 are currently owned by this frame.
        // We change that property once port1 or port2 are sent to another frame.
        channel.port1._source_frame = _sso._hierarchy(window);
        channel.port2._source_frame = _sso._hierarchy(window);

        // If we receive a message on port1 or port2, it was sent *to* this frame because port1
        // and port2 are currently owned by this frame.
        // We change that property once port1 or port2 are sent to another frame.
        channel.port1._target_frame = _sso._hierarchy(window);
        channel.port2._target_frame = _sso._hierarchy(window);

        channel.port1.addEventListener("message", (e) => {
            _sso._event("channelmessagereceived", {
                channel_id: e.target._channel_id,
                port_id: e.target._port_id,
                source_frame: e.target._source_frame,
                target_frame: e.target._target_frame,
                data: e.data,
                data_type: typeof e.data
            });
        });

        channel.port2.addEventListener("message", (e) => {
            _sso._event("channelmessagereceived", {
                channel_id: e.target._channel_id,
                port_id: e.target._port_id,
                source_frame: e.target._source_frame,
                target_frame: e.target._target_frame,
                data: e.data,
                data_type: typeof e.data
            });
        });

        _sso._event("messagechannelnew", {
            channel_id: channel_id
        });

        return channel;
    }

    // Wrapper of BroadcastChannel constructor

    window.BroadcastChannel = function BroadcastChannel(...args) {

        let channel_name = args[0];
        let channel = new window._sso._BroadcastChannel(...args);

        channel._postMessage = channel.postMessage;
        channel.postMessage = function postMessage(...args) {
            _sso._event("broadcastmessagesent", {
                channel_name: this.name,
                source_frame: _sso._hierarchy(window),
                data: args[0],
                data_type: typeof args[0]
            });
            return this._postMessage(...args);
        }

        channel.addEventListener("message", (e) => {
            _sso._event("broadcastmessagereceived", {
                channel_name: channel_name,
                target_frame: _sso._hierarchy(self),
                data: e.data,
                data_type: typeof e.data
            });
        });

        _sso._event("broadcastchannelnew", {
            channel_name: channel_name
        });

        return channel;
    }

    console.info("content_messaging.js initialized");
}

let content_messaging_script = document.createElement("script");
content_messaging_script.classList.add("chromeextension");
content_messaging_script.textContent = "(" + content_messaging.toString() + ")()";
document.documentElement.prepend(content_messaging_script);
