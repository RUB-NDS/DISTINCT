import os
import json

class SequenceDiagram:

    def __init__(self, outputdir = None):
        """ Constructor """
        # Setup output file
        if outputdir:
            self.sequencefile = f"{outputdir}/sequencediagram.txt"
        else:
            self.sequencefile = None
        
        # First line to start sequence diagram
        self.stm("@startuml")

    def stm(self, stm):
        """ Add statement to sequence diagram """
        if self.sequencefile:
            with open(f"{self.sequencefile}", "a+") as f:
                f.write(stm + "\n")

    def compile(self):
        """ Compile sequence diagram to SVG """
        with open(f"{self.sequencefile}", "a+") as f:
            f.write("@enduml") # last line to end sequence diagram
        os.system(f"java -jar ../tools/plantuml.jar -svg {self.sequencefile}")

    @staticmethod
    def linebreaks(input: str, every: int = 200, escape: bool = False):
        """ Returns input string with linebreaks after x characters """
        lines = str(input).splitlines()
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

    """ Events: Document """

    def documentinit(self, hierarchy, href):
        self.stm(f'participant "{hierarchy}"')
        self.stm(
            f'note right of "{hierarchy}"\n'
            f'<code>\n'
            f'Event: Document Init\n'
            f'URL: {self.linebreaks(href)}\n'
            f'</code>\n'
            f'end note'
        )

    def documentinteractive(self, hierarchy, href, html):
        self.stm(f'participant "{hierarchy}"')
        self.stm(
            f'note right of "{hierarchy}"\n'
            f'<code>\n'
            f'Event: Document Interactive\n'
            f'URL: {self.linebreaks(href)}\n'
            f'HTML:\n'
            f'{self.linebreaks(html, every=500)}\n'
            f'</code>\n'
            f'end note'
        )

    def documentbeforeunload(self, hierarchy):
        self.stm(f'participant "{hierarchy}"')
        self.stm(
            f'note right of "{hierarchy}"\n'
            f'<code>\n'
            f'Event: Document Before Unload\n'
            f'</code>\n'
            f'end note'
        )

    def httpredirect(self, hierarchy, href, status_code, location):
        self.stm(f'participant "{hierarchy}"')
        self.stm(
            f'note right of "{hierarchy}"\n'
            f'<code>\n'
            f'Event: HTTP Redirect\n'
            f'Status Code: {status_code}\n'
            f'Source: {self.linebreaks(href)}\n'
            f'Location: {self.linebreaks(location)}\n'
            f'</code>\n'
            f'end note'
        )

    def formsubmit(self, hierarchy, href, formbody):
        self.stm(f'participant "{hierarchy}"')
        self.stm(
            f'note right of "{hierarchy}"\n'
            f'<code>\n'
            f'Event: Form Submit\n'
            f'URL: {self.linebreaks(href)}\n'
            f'Body: {self.linebreaks(json.dumps(formbody))}\n'
            f'</code>\n'
            f'end note'
        )

    def windowopen(self, hierarchy, opener_hierarchy, url):
        self.stm(f'participant "{hierarchy}"')
        self.stm(f'participant "{opener_hierarchy}"')
        self.stm(f'"{opener_hierarchy}" -> "{hierarchy}": window.open()')
        self.stm(
            f'note right of "{hierarchy}"\n'
            f'<code>\n'
            f'Event: Window Open\n'
            f'URL: {self.linebreaks(url)}\n'
            f'</code>\n'
            f'end note'
        )

    def windowclose(self, hierarchy, opener_hierarchy):
        self.stm(f'participant "{hierarchy}"')
        self.stm(f'participant "{opener_hierarchy}"')
        self.stm(
            f'note right of "{hierarchy}"\n'
            f'<code>\n'
            f'Event: Window Close\n'
            f'</code>\n'
            f'end note'
        )
        self.stm(f'"{hierarchy}" -> "{opener_hierarchy}": window.close()')
    
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

    """ Events: Web Messaging """

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

    def addeventlistener(self, hierarchy, type, method, callback):
        self.stm(f'participant "{hierarchy}"')
        self.stm(
            f'note right of "{hierarchy}"\n'
            f'<code>\n'
            f'Event: Add Event Listener\n'
            f'Type: {type}\n'
            f'Method: {method}\n'
            f'Callback: {self.linebreaks(callback)}\n'
            f'</code>\n'
            f'end note'
        )

    def removeeventlistener(self, hierarchy, type, method, callback):
        self.stm(f'participant "{hierarchy}"')
        self.stm(
            f'note right of "{hierarchy}"\n'
            f'<code>\n'
            f'Event: Remove Event Listener\n'
            f'Type: {type}\n'
            f'Method: {method}\n'
            f'Callback: {self.linebreaks(callback)}\n'
            f'</code>\n'
            f'end note'
        )

    """ Events: Storage """

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

    """ Events: Props """

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
