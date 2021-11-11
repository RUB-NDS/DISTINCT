/**
 * This content script monitors the use of client-side storage mechanisms.
 * Following storage mechanisms are available in Chromium:
 *      - LocalStorage
 *      - SessionStorage
 *      - IndexedDB
 *      - Cookies
 *      - ~WebSQL~ -> the Web SQL Database specification is no longer being maintained 
 *        and support may be dropped in future versions (https://caniuse.com/sql-storage)
 *      - ~Trust Tokens~ -> we cannot store data in trust tokens
 */

let content_storage = () => {

    /* Report when data is written to localStorage */
    /* LocalStorage items can be set in two different ways:
        - using window.localStorage.setItem("foo", "faa")
        - using window.localStorage["foo"] = "faa"
       Thus, we need a proxy to catch all property accesses
       and additionally overwrite the setItem, getItem, ... methods.
     */
    window._sso._localStorage = window.localStorage;
    let localStorageHandler = {
        set: function(target, prop, value) {
            _sso._event("localstorageset", {key: prop, val: value});
            return Reflect.set(...arguments);
        },
        get: function(target, prop, receiver) {
            if (prop == "setItem") {
                return (key, val) => {
                    _sso._event("localstorageset", {key: key, val: val});
                    return window._sso._localStorage.setItem(key, val);
                }
            } else if (prop == "getItem") {
                return (key) => {
                    return window._sso._localStorage.getItem(key);
                }
            } else if (prop == "removeItem") {
                return (key) => {
                    return window._sso._localStorage.removeItem(key);
                }
            } else if (prop == "key") {
                return (key) => {
                    return window._sso._localStorage.key(key);
                }
            } else if (prop == "clear") {
                return () => {
                    return window._sso._localStorage.clear();
                }
            } else if (prop == "length") {
                return window._sso._localStorage.length;
            } else {
                if (typeof window._sso._localStorage[prop] == "function") {
                    return (...args) => {
                        return window._sso._localStorage[prop](...args);
                    }
                } else if (typeof window._sso._localStorage[prop] == "string") {
                    return window._sso._localStorage[prop];
                }
            }
        }
    }
    let localStorageProxy = new Proxy(
        window._sso._localStorage, localStorageHandler
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
    window._sso._sessionStorage = window.sessionStorage;
    let sessionStorageHandler = {
        set: function(target, prop, value) {
            _sso._event("sessionstorageset", {key: prop, val: value});
            return Reflect.set(...arguments);
        },
        get: function(target, prop, receiver) {
            if (prop == "setItem") {
                return (key, val) => {
                    _sso._event("sessionstorageset", {key: key, val: val});
                    return window._sso._sessionStorage.setItem(key, val);
                }
            } else if (prop == "getItem") {
                return (key) => {
                    return window._sso._sessionStorage.getItem(key);
                }
            } else if (prop == "removeItem") {
                return (key) => {
                    return window._sso._sessionStorage.removeItem(key);
                }
            } else if (prop == "key") {
                return (key) => {
                    return window._sso._sessionStorage.key(key);
                }
            } else if (prop == "clear") {
                return () => {
                    return window._sso._sessionStorage.clear();
                }
            } else if (prop == "length") {
                return window._sso._sessionStorage.length;
            } else {
                if (typeof window._sso._sessionStorage[prop] == "function") {
                    return (...args) => {
                        return window._sso._sessionStorage[prop](...args);
                    }
                } else if (typeof window._sso._sessionStorage[prop] == "string") {
                    return window._sso._sessionStorage[prop];
                }
            }
        }
    }
    let sessionStorageProxy = new Proxy(
        window._sso._sessionStorage, sessionStorageHandler
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
            _sso._event("cookieset", {val: val});
            cookieDescriptor.set.call(document, val);
        }
    });

    /* Report when data is written to IndexedDB */
    let _add = IDBObjectStore.prototype.add;
    let _put = IDBObjectStore.prototype.put;
    IDBObjectStore.prototype.add = function add(value, ...args) { // (value, [key])
        _sso._event("idbadd", {
            db: this.transaction.db.name,
            objectstore: this.name,
            keypath: this.keyPath,
            key: args[0] || "",
            val: value
        });
        return _add.call(this, value, ...args);
    }
    IDBObjectStore.prototype.put = function put(value, ...args) { // (value, [key])
        _sso._event("idbput", {
            db: this.transaction.db.name,
            objectstore: this.name,
            keypath: this.keyPath,
            key: args[0] || "",
            val: value
        });
        return _put.call(this, value, ...args);
    }

    console.info("content_storage.js initialized");
}

let content_storage_script = document.createElement("script");
content_storage_script.classList.add("chromeextension");
content_storage_script.textContent = "(" + content_storage.toString() + ")()";
document.documentElement.prepend(content_storage_script);
