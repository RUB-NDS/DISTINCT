let detect_js = () => {

    /* Report when postMessage is received */
    window.addEventListener("message", (e) => {
        let receiver = _hierarchy(self);
        let sender = _hierarchy(e.source);
        let data = typeof e.data == "string" ? e.data : JSON.stringify(e.data);

        _event("postmessagereceived", {
            "receiver": receiver,
            "sender": sender,
            "data": data,
            "datatype": typeof data
        });

    });

    /* Report when data is written to localStorage */
    /* LocalStorage items can be set in two different ways:
        - using window.localStorage.setItem("foo", "faa")
        - using window.localStorage["foo"] = "faa"
       Thus, we need a proxy to catch all property accesses
       and additionally overwrite the setItem, getItem, ... methods.
     */
    window._localStorage = window.localStorage;
    let localStorageHandler = {
        set: function(target, prop, value) {
            _event("localstorageset", {key: prop, val: value});
            return Reflect.set(...arguments);
        },
        get: function(target, prop, receiver) {
            if (prop == "setItem") {
                return (key, val) => {
                    _event("localstorageset", {key: key, val: val});
                    return window._localStorage.setItem(key, val);
                }
            } else if (prop == "getItem") {
                return (key) => {
                    return window._localStorage.getItem(key);
                }
            } else if (prop == "removeItem") {
                return (key) => {
                    return window._localStorage.removeItem(key);
                }
            } else if (prop == "key") {
                return (key) => {
                    return window._localStorage.key(key);
                }
            } else if (prop == "clear") {
                return () => {
                    return window._localStorage.clear();
                }
            } else if (prop == "length") {
                return window._localStorage.length;
            } else {
                if (typeof window._localStorage[prop] == "function") {
                    return (...args) => {
                        return window._localStorage[prop](...args);
                    }
                } else if (typeof window._localStorage[prop] == "string") {
                    return window._localStorage[prop];
                }
            }
        }
    }
    let localStorageProxy = new Proxy(
        window._localStorage, localStorageHandler
    );
    Object.defineProperty(window, "localStorage", {
        value: localStorageProxy,
        configurable: true,
        enumerable: true,
        writable: false
    });

    /* Report when data is written to sessionStorage */
    /* SessionStorage items can be set in two different ways:
        - using window.sessionStorage.setItem("foo", "faa")
        - using window.sessionStorage["foo"] = "faa"
       Thus, we need a proxy to catch all property accesses
       and additionally overwrite the setItem, getItem, ... methods.
     */
    window._sessionStorage = window.sessionStorage;
    let sessionStorageHandler = {
        set: function(target, prop, value) {
            _event("sessionstorageset", {key: prop, val: value});
            return Reflect.set(...arguments);
        },
        get: function(target, prop, receiver) {
            if (prop == "setItem") {
                return (key, val) => {
                    _event("sessionstorageset", {key: key, val: val});
                    return window._sessionStorage.setItem(key, val);
                }
            } else if (prop == "getItem") {
                return (key) => {
                    return window._sessionStorage.getItem(key);
                }
            } else if (prop == "removeItem") {
                return (key) => {
                    return window._sessionStorage.removeItem(key);
                }
            } else if (prop == "key") {
                return (key) => {
                    return window._sessionStorage.key(key);
                }
            } else if (prop == "clear") {
                return () => {
                    return window._sessionStorage.clear();
                }
            } else if (prop == "length") {
                return window._sessionStorage.length;
            } else {
                if (typeof window._sessionStorage[prop] == "function") {
                    return (...args) => {
                        return window._sessionStorage[prop](...args);
                    }
                } else if (typeof window._sessionStorage[prop] == "string") {
                    return window._sessionStorage[prop];
                }
            }
        }
    }
    let sessionStorageProxy = new Proxy(
        window._sessionStorage, sessionStorageHandler
    );
    Object.defineProperty(window, "sessionStorage", {
        value: sessionStorageProxy,
        configurable: true,
        enumerable: true,
        writable: false
    });

    /* TODO: Report when properties are set on global window object */
    /* Note: These properties are commonly used as JS callbacks in SSO flows */

}

let detect_js_script = document.createElement("script");
detect_js_script.classList.add("chromeextension");
detect_js_script.textContent = "(" + detect_js.toString() + ")()";
document.documentElement.prepend(detect_js_script);
