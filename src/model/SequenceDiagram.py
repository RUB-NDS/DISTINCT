import webbrowser
import plantuml
import os

from helpers import insert_newlines

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
            f'URL: {insert_newlines(frame.href)}\n'
            f'end note'
        )

    def documentinteractive(self, frame):
        self.statement(f'participant "{frame.hierarchy()}"')
        if frame.opener:
            self.statement(
                f'note right of "{frame.hierarchy()}"\n'
                f'Event: Document Interactive\n'
                f'URL: {insert_newlines(frame.href)}\n'
                f'HTML: {insert_newlines(frame.html)}\n'
                f'end note'
            )
        else:
            self.statement(
                f'note right of "{frame.hierarchy()}"\n'
                f'Event: Document Interactive\n'
                f'URL: {insert_newlines(frame.href)}\n'
                f'HTML: REDACTED\n'
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
            f'URL: {insert_newlines(frame.href)}\n'
            f'Body: {insert_newlines(formbody)}\n'
            f'end note'
        )

    def dumpframe(self, hierarchy, html):
        self.statement(f'participant "{hierarchy}"')
        self.statement(
            f'note right of "{hierarchy}"\n'
            f'Event: Dump Frame\n'
            f'HTML:\n'
            f'{insert_newlines(html, every=200)}\n'
            f'end note'
        )

    def windowopen(self, frame):
        self.statement(f'participant "{frame.hierarchy()}"')
        self.statement(f'participant "{frame.opener.hierarchy()}"')
        self.statement(f'"{frame.opener.hierarchy()}" -> "{frame.hierarchy()}": window.open()')
        self.statement(
            f'note right of "{frame.hierarchy()}"\n'
            f'Event: Window Open\n'
            f'URL: {insert_newlines(frame.href)}\n'
            f'end note'
        )

    def windowclose(self, frame):
        self.statement(f'participant "{frame.hierarchy()}"')
        self.statement(f'participant "{frame.opener.hierarchy()}"')
        self.statement(
            f'note right of "{frame.hierarchy()}"\n'
            f'Event: Window Close\n'
            f'end note'
        )
        self.statement(f'"{frame.hierarchy()}" -> "{frame.opener.hierarchy()}": window.close()')

    def postmessagereceived(self, receiver, sender, data, datatype):
        self.statement(f'participant "{receiver}"')
        self.statement(f'participant "{sender}"')
        self.statement(f'"{sender}" -> "{receiver}": window.postMessage()')
        self.statement(
            f'note right of "{receiver}"\n'
            f'Event: PostMessage Received\n'
            f'Data Type: {datatype}\n'
            f'Data: {insert_newlines(data)}\n'
            f'end note'
        )

    def localstorageset(self, hierarchy, key, val):
        self.statement(f'participant "{hierarchy}"')
        self.statement(
            f'note right of "{hierarchy}"\n'
            f'Event: LocalStorage Set\n'
            f'Key: {insert_newlines(key)}\n'
            f'Value: {insert_newlines(val)}\n'
            f'end note'
        )

    def sessionstorageset(self, hierarchy, key, val):
        self.statement(f'participant "{hierarchy}"')
        self.statement(
            f'note right of "{hierarchy}"\n'
            f'Event: SessionStorage Set\n'
            f'Key: {insert_newlines(key)}\n'
            f'Value: {insert_newlines(val)}\n'
            f'end note'
        )

    def cookieset(self, hierarchy, val):
        self.statement(f'participant "{hierarchy}"')
        self.statement(
            f'note right of "{hierarchy}"\n'
            f'Event: Cookie Set\n'
            f'Value: {insert_newlines(val)}\n'
            f'end note'
        )
    
    def idbset(self, hierarchy, db, objectstore, keypath, key, val):
        self.statement(f'participant "{hierarchy}"')
        self.statement(
            f'note right of "{hierarchy}"\n'
            f'Event: IndexedDB Set\n'
            f'Database: {insert_newlines(db)}\n'
            f'Object Store: {insert_newlines(objectstore)}\n'
            f'Key Path: {insert_newlines(keypath)}\n'
            f'Key: {insert_newlines(key)}\n'
            f'Value: {insert_newlines(val)}\n'
            f'end note'
        )
