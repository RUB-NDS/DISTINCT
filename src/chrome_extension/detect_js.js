let detect_js = () => {

    /* CROSS-FRAME COMMUNICATION */

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

    /* Report when properties are set on global window object */

    let blacklistedprops = [
        "_postMessage", "_addEventListener", "_open", "_close",
        "_popups", "_xmlhttprequest_open", "_localStorage", "_sessionStorage",
        "_qparams", "_hparams", "_html", "_form2json", "_hierarchy",
        "_postMessageAll", "_event", "_defaultprops", "_customprops"
    ];

    // At this time when the extension runs, no custom properties should be set
    // with exception of custom properties defined in the extension itself (see blacklist)
    window._customprops = {};
    window._defaultprops = Object.keys(window).filter((item) => {
        return !blacklistedprops.includes(item);
    });

    function check_props() {
        Object.keys(window).filter((item) => {
            return (!_defaultprops.includes(item)) && (!blacklistedprops.includes(item));
        }).forEach((item) => {
            
            if (!(item in _customprops)) {
                // This is an entirely new property on global window object
                let value = window[item];
                _customprops[item] = value;
                
                _event("windowpropnew", {
                    key: item,
                    val: (typeof value == "function" ? value.toString() : value),
                    valtype: typeof value
                });
            } else if (item in _customprops && _customprops[item] !== window[item]) {
                // The value of the property changed
                let value = window[item];
                _customprops[item] = value;

                _event("windowpropchanged", {
                    key: item,
                    val: (typeof value == "function" ? value.toString() : value),
                    valtype: typeof value
                });
            }

        });
    }

    setInterval(check_props, 500);

    /* BROWSER STORAGE */

    /* LocalStorage, SessionStorage, IndexedDB, ~WebSQL~, Cookies, ~Trust Tokens~
       - We cannot store data in trust tokens
       - The Web SQL Database specification is no longer being maintained
       and support may be dropped in future versions. (https://caniuse.com/sql-storage)
     */

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

    /* Report when data is written to cookies */
    let cookieDescriptor = Object.getOwnPropertyDescriptor(Document.prototype, "cookie");
    Object.defineProperty(document, "cookie", {
        configurable: true,
        enumerable: true,
        get: () => {
            return cookieDescriptor.get.call(document);
        },
        set: (val) => {
            _event("cookieset", {val: val});
            cookieDescriptor.set.call(document, val);
        }
    });

    /* Report when data is written to IndexedDB */
    let _add = IDBObjectStore.prototype.add;
    let _put = IDBObjectStore.prototype.put;
    IDBObjectStore.prototype.add = function add(value, ...args) { // (value, [key])
        _event("idbadd", {
            db: this.transaction.db.name,
            objectstore: this.name,
            keypath: this.keyPath,
            key: args[0] || "",
            val: value
        });
        return _add.call(this, value, ...args);
    }
    IDBObjectStore.prototype.put = function put(value, ...args) { // (value, [key])
        _event("idbput", {
            db: this.transaction.db.name,
            objectstore: this.name,
            keypath: this.keyPath,
            key: args[0] || "",
            val: value
        });
        return _put.call(this, value, ...args);
    }

}

let detect_js_script = document.createElement("script");
detect_js_script.classList.add("chromeextension");
detect_js_script.textContent = "(" + detect_js.toString() + ")()";
document.documentElement.prepend(detect_js_script);
