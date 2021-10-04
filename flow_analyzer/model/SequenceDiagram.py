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

    def documentinteractive(self, frame):
        if frame.parent:
            self.statement(f'participant "{frame.hierarchy()}"')
            self.statement(f'participant "{frame.parent.hierarchy()}"')
            self.statement(f'"{frame.parent.hierarchy()}" -> "{frame.hierarchy()}" : Document Interactive')
        elif frame.opener:
            self.statement(f'participant "{frame.hierarchy()}"')
            self.statement(f'participant "{frame.opener.hierarchy()}"')
            self.statement(f'"{frame.opener.hierarchy()}" -> "{frame.hierarchy()}" : Document Interactive')
        else:
            self.statement(f'participant "{frame.hierarchy()}"')
        
        self.statement(f'note right of "{frame.hierarchy()}": URL: "{frame.href}"')

    def documentbeforeunload(self, frame):
        if frame.parent:
            self.statement(f'participant "{frame.hierarchy()}"')
            self.statement(f'participant "{frame.parent.hierarchy()}"')
            self.statement(f'"{frame.hierarchy()}" -> "{frame.parent.hierarchy()}" : Document Unload')
        elif frame.opener:
            self.statement(f'participant "{frame.hierarchy()}"')
            self.statement(f'participant "{frame.opener.hierarchy()}"')
            self.statement(f'"{frame.hierarchy()}" -> "{frame.opener.hierarchy()}" : Document Unload')

    def formsubmit(self, frame, formbody):
        self.statement(
            f'note right of "{frame.hierarchy()}"\n'
            f'POST "{frame.href}"\n'
            f'{formbody}\n'
            f'end note'
        )

    def dumpframe(self, hierarchy, html):
        self.statement(
            f'note right of "{hierarchy}"\n'
            f'HTML:\n'
            f'{html}\n'
            f'end note'
        )
