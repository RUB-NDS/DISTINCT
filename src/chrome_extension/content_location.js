/**
 * This content script monitors the use of the window.location API.
 * Each time a new location is set using JavaScript, an event is generated.
 * Following properties and functions are available on window.location:
 *      - location.href
 *      - location.origin (read only)
 * 
 *      - location.protocol
 *      - location.host
 *      - location.hostname
 *      - location.port
 *      - location.pathname
 *      - location.search
 *      - location.hash
 * 
 *      - location.assign()
 *      - location.replace()
 *      - location.reload()
 * 
 * Note: If we set location = "...", it internally sets location.href = "...". There is not need
 * to overwrite the location setter.
 * 
 * Note: Browsers do not allow to reconfigure the location API, since its property descriptor is
 * not configurable. We provide a patched Chromium that allows the reconfiguration of the location
 * property. Use this brower if you want to receive events related to the use of the location API.
 * 
 */

let content_location = () => {

    if (Object.getOwnPropertyDescriptor(window, "location").configurable == false) {
        console.warn(
            "This browser does not allow the reconfiguration of the location API. " +
            "Use a patched browser if you want to receive location events."
        );
        return;
    }

    let _href_descriptor = Object.getOwnPropertyDescriptor(location, "href");
    Object.defineProperty(window.location, "href", {
        configurable: true,
        enumerable: true,
        get: () => {
            return _href_descriptor.get.call(window.location);
        },
        set: (val) => {
            if (
                "_sso._type" in document.documentElement.attributes
            ) {
                // This is our http redirect which we transformed into a location redirect.
                // We do not want to log this location being set.
                return _href_descriptor.set.call(window.location, val);
            }

            window._sso._event("locationset", {
                prop: "href",
                target: val
            }).finally(() => {
                return _href_descriptor.set.call(window.location, val);
            });
        }
    });

    let _origin_descriptor = Object.getOwnPropertyDescriptor(location, "origin");
    Object.defineProperty(window.location, "origin", {
        configurable: true,
        enumerable: true,
        get: () => {
            return _origin_descriptor.get.call(window.location);
        }
        // location.origin is read only
    });

    let _protocol_descriptor = Object.getOwnPropertyDescriptor(location, "protocol");
    Object.defineProperty(window.location, "protocol", {
        configurable: true,
        enumerable: true,
        get: () => {
            return _protocol_descriptor.get.call(window.location);
        },
        set: (val) => {
            window._sso._event("locationset", {
                prop: "protocol",
                target: val
            }).finally(() => {
                return _protocol_descriptor.set.call(window.location, val);
            });
        }
    });

    let _host_descriptor = Object.getOwnPropertyDescriptor(location, "host");
    Object.defineProperty(window.location, "host", {
        configurable: true,
        enumerable: true,
        get: () => {
            return _host_descriptor.get.call(window.location);
        },
        set: (val) => {
            window._sso._event("locationset", {
                prop: "host",
                target: val
            }).finally(() => {
                return _host_descriptor.set.call(window.location, val);
            });
        }
    });

    let _hostname_descriptor = Object.getOwnPropertyDescriptor(location, "hostname");
    Object.defineProperty(window.location, "hostname", {
        configurable: true,
        enumerable: true,
        get: () => {
            return _hostname_descriptor.get.call(window.location);
        },
        set: (val) => {
            window._sso._event("locationset", {
                prop: "hostname",
                target: val
            }).finally(() => {
                return _hostname_descriptor.set.call(window.location, val);
            });
        }
    });

    let _port_descriptor = Object.getOwnPropertyDescriptor(location, "port");
    Object.defineProperty(window.location, "port", {
        configurable: true,
        enumerable: true,
        get: () => {
            return _port_descriptor.get.call(window.location);
        },
        set: (val) => {
            window._sso._event("locationset", {
                prop: "port",
                target: val
            }).finally(() => {
                return _port_descriptor.set.call(window.location, val);
            });
        }
    });

    let _pathname_descriptor = Object.getOwnPropertyDescriptor(location, "pathname");
    Object.defineProperty(window.location, "pathname", {
        configurable: true,
        enumerable: true,
        get: () => {
            return _pathname_descriptor.get.call(window.location);
        },
        set: (val) => {
            window._sso._event("locationset", {
                prop: "pathname",
                target: val
            }).finally(() => {
                return _pathname_descriptor.set.call(window.location, val);
            });
        }
    });

    let _search_descriptor = Object.getOwnPropertyDescriptor(location, "search");
    Object.defineProperty(window.location, "search", {
        configurable: true,
        enumerable: true,
        get: () => {
            return _search_descriptor.get.call(window.location);
        },
        set: (val) => {
            window._sso._event("locationset", {
                prop: "search",
                target: val
            }).finally(() => {
                return _search_descriptor.set.call(window.location, val);
            });
        }
    });

    let _hash_descriptor = Object.getOwnPropertyDescriptor(location, "hash");
    Object.defineProperty(window.location, "hash", {
        configurable: true,
        enumerable: true,
        get: () => {
            return _hash_descriptor.get.call(window.location);
        },
        set: (val) => {
            window._sso._event("locationset", {
                prop: "hash",
                target: val
            }).finally(() => {
                return _hash_descriptor.set.call(window.location, val);
            });
        }
    });

    let _reload_descriptor = Object.getOwnPropertyDescriptor(location, "reload");
    Object.defineProperty(window.location, "reload", {
        configurable: true,
        enumerable: true,
        value: (...args) => {
            window._sso._event("locationset", {
                prop: "reload",
                target: ""
            }).finally(() => {
                return _reload_descriptor.value.call(window.location, ...args);
            });
        }
    });

    let _assign_descriptor = Object.getOwnPropertyDescriptor(location, "assign");
    Object.defineProperty(window.location, "assign", {
        configurable: true,
        enumerable: true,
        value: (...args) => {
            let url = args[0];
            window._sso._event("locationset", {
                prop: "assign",
                target: url
            }).finally(() => {
                return _assign_descriptor.value.call(window.location, ...args);
            });
        }
    });

    let _replace_descriptor = Object.getOwnPropertyDescriptor(location, "replace");
    Object.defineProperty(window.location, "replace", {
        configurable: true,
        enumerable: true,
        value: (...args) => {
            let url = args[0];
            window._sso._event("locationset", {
                prop: "replace",
                target: url
            }).finally(() => {
                return _replace_descriptor.value.call(window.location, ...args);
            });
        }
    });

    console.info("content_location.js initialized");
}

let content_location_script = document.createElement("script");
content_location_script.classList.add("chromeextension");
content_location_script.textContent = "(" + content_location.toString() + ")()";
document.documentElement.prepend(content_location_script);
