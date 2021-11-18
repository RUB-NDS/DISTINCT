import os

class SequenceDiagram:

    def __init__(self, outputdir = None):
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
    def linebreaks(input, every = 200, escape = False):
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

    def note(self, participant, event_id, event_timestamp, event_name,
        event_keyval, linebreaks = 100, color = None
    ):
        """ Add note to sequence diagram """
        note = (
            f'participant "{participant}"\n'
            f'note right of "{participant}" {f"#{color}" if color else ""}\n'
            f'<code>\n'
            f'ID: {event_id}\n'
            f'Event: {event_name}\n'
        )
        
        for key, val in event_keyval.items():
            note += f"{key}: {self.linebreaks(val, every=linebreaks)}\n"
        
        note += (
            f'</code>\n'
            f'end note'
        )
        self.stm(note)

    def arrow(self, participant_source, participant_target, event_name):
        """ Add arrow from source to target in sequence diagram """
        self.stm(
            f'participant "{participant_source}"\n'
            f'participant "{participant_target}"\n'
            f'"{participant_source}" -> "{participant_target}": Event: {event_name}'
        )
