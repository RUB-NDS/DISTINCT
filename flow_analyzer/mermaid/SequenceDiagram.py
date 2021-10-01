import webbrowser
import plantuml

class SequenceDiagram:

    def __init__(self):
        self.statements = ["@startuml"]

    def __str__(self):
        stm = self.statements.copy()
        stm.append("@enduml")
        return "\n".join(stm)

    def plot(self):
        # template = {
        #     "code": str(self),
        #     "mermaid": {"theme": "default"}
        # }
        # template_bytes = json.dumps(template).encode("utf8')
        # base64_bytes = base64.b64encode(template_bytes)
        # base64_string = base64_bytes.decode("utf8')
        # webbrowser.open("https://mermaid-js.github.io/mermaid-live-editor/view/#" + base64_string)
        code = plantuml.deflate_and_encode(str(self))
        webbrowser.open("https://plantuml-server.kkeisuke.dev/svg/" + code)

    """ REPORTS """

    def documentinteractive(self, frame):
        if frame.parent:
            self.statements.append(f'participant "{frame.hierarchy()}"')
            self.statements.append(f'participant "{frame.parent.hierarchy()}"')
            self.statements.append(f'"{frame.parent.hierarchy()}" -> "{frame.hierarchy()}" : Document Interactive')
        elif frame.opener:
            self.statements.append(f'participant "{frame.hierarchy()}"')
            self.statements.append(f'participant "{frame.opener.hierarchy()}"')
            self.statements.append(f'"{frame.opener.hierarchy()}" -> "{frame.hierarchy()}" : Document Interactive')
        else:
            self.statements.append(f'participant "{frame.hierarchy()}"')
        
        self.statements.append(f'note right of "{frame.hierarchy()}": URL: "{frame.href}"')

    def documentbeforeunload(self, frame):
        if frame.parent:
            self.statements.append(f'participant "{frame.hierarchy()}"')
            self.statements.append(f'participant "{frame.parent.hierarchy()}"')
            self.statements.append(f'"{frame.hierarchy()}" -> "{frame.parent.hierarchy()}" : Document Unload')
        elif frame.opener:
            self.statements.append(f'participant "{frame.hierarchy()}"')
            self.statements.append(f'participant "{frame.opener.hierarchy()}"')
            self.statements.append(f'"{frame.hierarchy()}" -> "{frame.opener.hierarchy()}" : Document Unload')

    def formsubmit(self, frame, formbody):
        self.statements.append(
            f'note right of "{frame.hierarchy()}"\n'
            f'POST "{frame.href}"\n'
            f'{formbody}\n'
            f'end note'
        )

    def dumpframe(self, hierarchy, html):
        self.statements.append(
            f'note right of "{hierarchy}"\n'
            f'HTML:\n'
            f'{html}\n'
            f'end note'
        )
