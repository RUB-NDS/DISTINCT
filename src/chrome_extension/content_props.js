/**
 * This content script monitors all properties that are set on the global window object.
 * Each time a new property is set or an existing property is modified, it reports an event.
 */

let content_props = () => {

    // Ignore all properties that are set by the chrome extension
    let blacklistedprops = ["_sso"];

    // At this time when the extension runs, no custom properties should be set
    // with exception of custom properties defined in the extension itself
    window._sso._customprops = {};
    window._sso._defaultprops = Object.keys(window).filter((item) => {
        return !blacklistedprops.includes(item);
    });

    function check_props() {
        Object.keys(window).filter((item) => {
            // Filter out all default and blacklisted properties
            return (!_sso._defaultprops.includes(item)) && (!blacklistedprops.includes(item));
        }).forEach((item) => {
            
            if (!(item in _sso._customprops)) {
                // This is an entirely new property on global window object
                let value = window[item];
                _sso._customprops[item] = value;
                
                _sso._event("windowpropnew", {
                    key: item,
                    val: (typeof value == "function" ? value.toString() : value),
                    valtype: typeof value
                });
            } else if (item in _sso._customprops && _sso._customprops[item] !== window[item]) {
                // The value of the property changed
                let value = window[item];
                _sso._customprops[item] = value;

                _sso._event("windowpropchanged", {
                    key: item,
                    val: (typeof value == "function" ? value.toString() : value),
                    valtype: typeof value
                });
            }

        });
    }

    setInterval(check_props, 500);

    console.info("content_props.js initialized");
}

let content_props_script = document.createElement("script");
content_props_script.classList.add("chromeextension");
content_props_script.textContent = "(" + content_props.toString() + ")()";
document.documentElement.prepend(content_props_script);
