import webbrowser
import plantuml
import os

class SequenceDiagram:

    def __init__(self):
        outputdir = os.environ.get("OUTPUTDIR")
        self.sequencefile = f"{outputdir}/sequencediagram.txt"
        
        self.statements = []
        self.statement("@startuml")

    def __str__(self):
        stm = self.statements.copy()
        stm.append("@enduml")
        return "\n".join(stm)

    def statement(self, stm):
        self.statements.append(stm)
        with open(f"{self.sequencefile}", "a+") as f:
            f.write(stm + "\n")

    def plot(self):
        code = plantuml.deflate_and_encode(str(self))
        webbrowser.open("https://plantuml-server.kkeisuke.dev/svg/" + code)

    def compile(self):
        with open(f"{self.sequencefile}", "a+") as f:
            f.write("@enduml") # last line to end uml plot
        os.system(f"java -jar ../plantuml/plantuml.jar -svg {self.sequencefile}") # compile
        os.system(f"sed -i '' -e '$ d' {self.sequencefile}") # delete last line (works only on macos!)

    def show(self):
        sequencefilesvg = self.sequencefile.replace(".txt", ".svg")
        print(sequencefilesvg)

    """ REPORTS """

    def extensioninit(self, frame):
        self.statement(f'participant "{frame.hierarchy()}"')
        self.statement(
            f'note right of "{frame.hierarchy()}"\n'
            f'Event: Extension Init\n'
            f'URL: {frame.href}\n'
            f'end note'
        )

    def documentinteractive(self, frame):
        self.statement(f'participant "{frame.hierarchy()}"')
        self.statement(
            f'note right of "{frame.hierarchy()}"\n'
            f'Event: Document Interactive\n'
            f'URL: {frame.href}\n'
            f'end note'
        )

    def documentbeforeunload(self, frame):
        self.statement(f'participant "{frame.hierarchy()}"')
        self.statement(f'note right of "{frame.hierarchy()}": Event: Document Before Unload')

    def formsubmit(self, frame, formbody):
        self.statement(f'participant "{frame.hierarchy()}"')
        self.statement(
            f'note right of "{frame.hierarchy()}"\n'
            f'Event: Form Submit\n'
            f'URL: {frame.href}\n'
            f'{formbody}\n'
            f'end note'
        )

    def dumpframe(self, hierarchy, html):
        self.statement(f'participant "{hierarchy}"')
        self.statement(
            f'note right of "{hierarchy}"\n'
            f'HTML:\n'
            f'{html}\n'
            f'end note'
        )

    def windowopen(self, frame):
        self.statement(f'participant "{frame.hierarchy()}"')
        self.statement(f'participant "{frame.opener.hierarchy()}"')
        self.statement(f'"{frame.opener.hierarchy()}" -> "{frame.hierarchy()}": window.open("{frame.href}")')

    def windowclose(self, frame):
        self.statement(f'participant "{frame.hierarchy()}"')
        self.statement(f'participant "{frame.opener.hierarchy()}"')
        self.statement(f'"{frame.hierarchy()}" -> "{frame.opener.hierarchy()}": window.close()')
