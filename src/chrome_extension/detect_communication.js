let detect_communication = () => {

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

}

let detect_communication_script = document.createElement("script");
detect_communication_script.classList.add("chromeextension");
detect_communication_script.textContent = "(" + detect_communication.toString() + ")()";
document.documentElement.prepend(detect_communication_script);
