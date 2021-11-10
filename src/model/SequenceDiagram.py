import os
import json

class SequenceDiagram:

    def __init__(self, outputdir):
        """ Constructor """
        self.sequencefile = f"{outputdir}/sequencediagram.txt" # setup output file
        self.stm("@startuml") # first line to start sequence diagram

    def stm(self, stm):
        """ Add statement to sequence diagram """
        with open(f"{self.sequencefile}", "a+") as f:
            f.write(stm + "\n")

    def compile(self):
        with open(f"{self.sequencefile}", "a+") as f:
            f.write("@enduml") # last line to end sequence diagram
        os.system(f"java -jar ../plantuml/plantuml.jar -svg {self.sequencefile}")

    @staticmethod
    def linebreaks(input: str, every: int = 200, escape: bool = False):
        """ Returns input string with linebreaks after x characters """
        lines = input.splitlines()
        newlined = []
        
        for line in lines:
            for i in range(0, len(line), every):
                # We need a space as first char because plantuml treats lines that begin with
                # ' or /' as comments, which leads to rendering errors
                if len(line) >= 1 and line[i] == "'":
                    newlined.append(f" {line[i:i+every]}")
                elif len(line) >= 2 and line[i:i+2] == "/'":
                    newlined.append(f" {line[i:i+every]}")
                else:
                    newlined.append(line[i:i+every])
        
        if escape:
            return "\\n".join(newlined) # escape line breaks
        else:
            return "\n".join(newlined) # do not escape line breaks

    """ Print events to sequence diagram """

    def extensioninit(self, frame):
        self.stm(f'participant "{frame.hierarchy()}"')
        self.stm(
            f'note right of "{frame.hierarchy()}"\n'
            f'<code>\n'
            f'Event: Extension Init\n'
            f'URL: {self.linebreaks(frame.href)}\n'
            f'</code>\n'
            f'end note'
        )

    def documentinteractive(self, frame):
        self.stm(f'participant "{frame.hierarchy()}"')
        self.stm(
            f'note right of "{frame.hierarchy()}"\n'
            f'<code>\n'
            f'Event: Document Interactive\n'
            f'URL: {self.linebreaks(frame.href)}\n'
            f'HTML:\n'
            f'{self.linebreaks(frame.html, every=500)}\n'
            f'</code>\n'
            f'end note'
        )

    def documentbeforeunload(self, frame):
        self.stm(f'participant "{frame.hierarchy()}"')
        self.stm(
            f'note right of "{frame.hierarchy()}"\n'
            f'<code>\n'
            f'Event: Document Before Unload\n'
            f'</code>\n'
            f'end note'
        )

    def httpredirect(self, frame, status_code, location):
        self.stm(f'participant "{frame.hierarchy()}"')
        self.stm(
            f'note right of "{frame.hierarchy()}"\n'
            f'<code>\n'
            f'Event: HTTP Redirect\n'
            f'Status Code: {status_code}\n'
            f'Source: {self.linebreaks(frame.href)}\n'
            f'Location: {self.linebreaks(location)}\n'
            f'</code>\n'
            f'end note'
        )

    def formsubmit(self, frame, formbody):
        self.stm(f'participant "{frame.hierarchy()}"')
        self.stm(
            f'note right of "{frame.hierarchy()}"\n'
            f'<code>\n'
            f'Event: Form Submit\n'
            f'URL: {self.linebreaks(frame.href)}\n'
            f'Body: {self.linebreaks(json.dumps(formbody))}\n'
            f'</code>\n'
            f'end note'
        )

    def dumpframe(self, hierarchy, html):
        self.stm(f'participant "{hierarchy}"')
        self.stm(
            f'note right of "{hierarchy}"\n'
            f'<code>\n'
            f'Event: Dump Frame\n'
            f'HTML:\n'
            f'{self.linebreaks(html, every=500)}\n'
            f'</code>\n'
            f'end note'
        )

    def windowopen(self, frame):
        self.stm(f'participant "{frame.hierarchy()}"')
        self.stm(f'participant "{frame.opener.hierarchy()}"')
        self.stm(f'"{frame.opener.hierarchy()}" -> "{frame.hierarchy()}": window.open()')
        self.stm(
            f'note right of "{frame.hierarchy()}"\n'
            f'<code>\n'
            f'Event: Window Open\n'
            f'URL: {self.linebreaks(frame.href)}\n'
            f'</code>\n'
            f'end note'
        )

    def windowclose(self, frame):
        self.stm(f'participant "{frame.hierarchy()}"')
        self.stm(f'participant "{frame.opener.hierarchy()}"')
        self.stm(
            f'note right of "{frame.hierarchy()}"\n'
            f'<code>\n'
            f'Event: Window Close\n'
            f'</code>\n'
            f'end note'
        )
        self.stm(f'"{frame.hierarchy()}" -> "{frame.opener.hierarchy()}": window.close()')

    def postmessagereceived(self, receiver, sender, data, datatype, targetorigincheck):
        self.stm(f'participant "{receiver}"')
        self.stm(f'participant "{sender}"')
        self.stm(f'"{sender}" -> "{receiver}": window.postMessage()')
        
        if targetorigincheck == "*":
            self.stm(
                f'note right of "{receiver}" #red\n'
                f'<code>\n'
                f'Event: PostMessage Received\n'
                f'Target Origin Check: {targetorigincheck}\n'
                f'Data Type: {datatype}\n'
                f'Data: {self.linebreaks(json.dumps(data))}\n'
                f'</code>\n'
                f'end note'
            )
        else:
            self.stm(
                f'note right of "{receiver}" #green\n'
                f'<code>\n'
                f'Event: PostMessage Received\n'
                f'Target Origin Check: {targetorigincheck}\n'
                f'Data Type: {datatype}\n'
                f'Data: {self.linebreaks(json.dumps(data))}\n'
                f'</code>\n'
                f'end note'
            )

    def localstorageset(self, hierarchy, key, val):
        self.stm(f'participant "{hierarchy}"')
        self.stm(
            f'note right of "{hierarchy}"\n'
            f'<code>\n'
            f'Event: LocalStorage Set\n'
            f'Key: {self.linebreaks(key)}\n'
            f'Value: {self.linebreaks(val)}\n'
            f'</code>\n'
            f'end note'
        )

    def sessionstorageset(self, hierarchy, key, val):
        self.stm(f'participant "{hierarchy}"')
        self.stm(
            f'note right of "{hierarchy}"\n'
            f'<code>\n'
            f'Event: SessionStorage Set\n'
            f'Key: {self.linebreaks(key)}\n'
            f'Value: {self.linebreaks(val)}\n'
            f'</code>\n'
            f'end note'
        )

    def cookieset(self, hierarchy, val):
        self.stm(f'participant "{hierarchy}"')
        self.stm(
            f'note right of "{hierarchy}"\n'
            f'<code>\n'
            f'Event: Cookie Set\n'
            f'Value: {self.linebreaks(val)}\n'
            f'</code>\n'
            f'end note'
        )
    
    def idbset(self, hierarchy, db, objectstore, keypath, key, val):
        self.stm(f'participant "{hierarchy}"')
        self.stm(
            f'note right of "{hierarchy}"\n'
            f'<code>\n'
            f'Event: IndexedDB Set\n'
            f'Database: {self.linebreaks(db)}\n'
            f'Object Store: {self.linebreaks(objectstore)}\n'
            f'Key Path: {self.linebreaks(keypath)}\n'
            f'Key: {self.linebreaks(key)}\n'
            f'Value: {self.linebreaks(val)}\n'
            f'</code>\n'
            f'end note'
        )

    def windowpropnew(self, hierarchy, key, val, valtype):
        self.stm(f'participant "{hierarchy}"')
        self.stm(
            f'note right of "{hierarchy}"\n'
            f'<code>\n'
            f'Event: Window Property New\n'
            f'Key: {self.linebreaks(key)}\n'
            f'Value Type: {self.linebreaks(valtype)}\n'
            f'Value: {self.linebreaks(json.dumps(val))}\n'
            f'</code>\n'
            f'end note'
        )
    
    def windowpropchanged(self, hierarchy, key, val, valtype):
        self.stm(f'participant "{hierarchy}"')
        self.stm(
            f'note right of "{hierarchy}"\n'
            f'<code>\n'
            f'Event: Window Property Changed\n'
            f'Key: {self.linebreaks(key)}\n'
            f'Value Type: {self.linebreaks(valtype)}\n'
            f'Value: {self.linebreaks(json.dumps(val))}\n'
            f'</code>\n'
            f'end note'
        )
    
    def closedaccessed(self, hierarchy, closed):
        self.stm(f'participant "{hierarchy}"')
        self.stm(
            f'note right of "{hierarchy}"\n'
            f'<code>\n'
            f'Event: Closed Accessed\n'
            f'Closed: {closed}\n'
            f'</code>\n'
            f'end note'
        )
