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
                
                window._sso._onmessage = cb;
            },
            get: () => window._sso._onmessage
        },
        addEventListener: {
            value: (...args) => {
                let [type, callback, options] = args;
                if (type == "message") {
                    let cbstring = callback ? callback.toString() : JSON.stringify(callback);
                    console.info(`window.addEventListener("message", ${cbstring}, ${options})`);
                    
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
                    let cbstring = callback ? callback.toString() : JSON.stringify(callback);
                    console.info(`window.removeEventListener("message", ${cbstring}, ${options})`);

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
                if (item instanceof MessagePort)
                    ports.push(item);
            }
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
                "transfer": (transfer ? transfer.toString() : "N/A"),
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
            pm.log.source_origin_accessed = "yes";
        } else {
            pm.log.source_origin_accessed = "no";
        }
        
        // Filter out postMessage from/to blacklisted origins
        
        for (let blacklisted of window._sso._pmblacklist) {
            if (new URL(pm.log.source_origin).host.includes(blacklisted))
                return;
            if (new URL(pm.log.target_origin).host.includes(blacklisted))
                return;
        }

        // Logging

        if (pm.log["target_origin_check"] == "*")
            console.warn(`PostMessage sent: ${JSON.stringify(pm.log)}`);
        else
            console.info(`PostMessage sent: ${JSON.stringify(pm.log)}`);

        // Report

        _sso._event("postmessagereceived", {
            "receiver":pm.log.target_frame,
            "sender": pm.log.source_frame,
            "data": pm.log.message_payload,
            "datatype": pm.log.message_type,
            "targetorigincheck": pm.log.target_origin_check,
            "sourceoriginaccessed": pm.log.source_origin_accessed
        });
        
    }

    console.info("content_pm.js initialized");
}

let content_messaging_script = document.createElement("script");
content_messaging_script.classList.add("chromeextension");
content_messaging_script.textContent = "(" + content_messaging.toString() + ")()";
document.documentElement.prepend(content_messaging_script);
