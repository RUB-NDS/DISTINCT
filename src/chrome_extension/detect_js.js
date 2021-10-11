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

}

let detect_js_script = document.createElement("script");
detect_js_script.classList.add("chromeextension");
detect_js_script.textContent = "(" + detect_js.toString() + ")()";
document.documentElement.prepend(detect_js_script);
