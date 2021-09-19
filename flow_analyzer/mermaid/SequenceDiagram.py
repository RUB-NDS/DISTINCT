import base64
import json
import webbrowser

class SequenceDiagram:

    def __init__(self):
        self.statements = ["sequenceDiagram"]

    def __str__(self):
        return "\n".join(self.statements)

    def plot(self):
        template = {
            "code": str(self),
            "mermaid": {"theme": "default"}
        }
        template_bytes = json.dumps(template).encode("utf8")
        base64_bytes = base64.b64encode(template_bytes)
        base64_string = base64_bytes.decode("utf8")
        webbrowser.open("https://mermaid-js.github.io/mermaid-live-editor/view/#" + base64_string)

    """ TOPFRAME """

    def add_topframe(self):
        self.statements.append(f"participant top")
    
    """ IFRAME """

    def add_iframe(self, iframe, parent):
        self.statements.append(f"participant {iframe}")
        self.statements.append(f"{parent}-->>{iframe}: IFrame embedded.")
    
    def close_iframe(self, iframe, parent):
        self.statements.append(f"{iframe}-->>{parent}: IFrame destroyed.")

    """ POPUPS """

    def add_popup(self, popup, opener):
        self.statements.append(f"participant {popup}")
        self.statements.append(f"{opener}-->>{popup}: Popup opened.")

    def close_popup(self, popup, opener):
        self.statements.append(f"{popup}-->>{opener}: Popup closed.")

    """ ACTIONS """

    def url_get(self, frame, url):
        self.statements.append(f"Note over {frame}: GET \"{url}\"")

    def url_post(self, frame, url, postbody):
        self.statements.append(f"Note over {frame}: POST \"{url}\"\n\n{json.dumps(postbody)}")

    def js_action(self, source, target, action):
        self.statements.append(f"{source}->>{target}: {action}")
