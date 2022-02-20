import os

class SequenceDiagram:

    def __init__(self):
        self.stms = [] # Lines of sequence diagram
        self.stm("@startuml") # First line to start sequence diagram

    def stm(self, stm):
        """ Add statement to sequence diagram """
        self.stms.append(stm)

    def svg(self):
        """ Compile sequence diagram to SVG """
        temp_sequence_file_txt = "/tmp/distinct-seq-diagram.txt"
        temp_sequence_file_svg = "/tmp/distinct-seq-diagram.svg"

        # Write sequence diagram to file
        with open(temp_sequence_file_txt, "w") as f:
            f.write("\n".join(self.stms + ["\n@enduml"]))

        # Compile sequence diagram to SVG
        os.system(f"java -jar ./plantuml/plantuml.jar -svg {temp_sequence_file_txt}")

        # Read SVG from file
        svg = None
        with open(temp_sequence_file_svg, "r") as f:
            svg = f.read()
        return svg

    @staticmethod
    def linebreaks(input, every = 200, escape = False):
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

    def note(self, participant, report_id, report_timestamp, report_name,
        report_keyval, linebreaks = 100, color = None
    ):
        """ Add note to sequence diagram """
        note = (
            f'participant "{participant}"\n'
            f'note right of "{participant}" {f"#{color}" if color else ""}\n'
            f'<code>\n'
            f'ID: {report_id}\n'
            f'Timestamp: {report_timestamp}\n'
            f'Report: {report_name}\n'
        )

        for key, val in report_keyval.items():
            note += f"{key}: {self.linebreaks(val, every=linebreaks)}\n"

        note += (
            f'</code>\n'
            f'end note'
        )
        self.stm(note)

    def arrow(self, participant_source, participant_target, report_name):
        """ Add arrow from source to target in sequence diagram """
        self.stm(
            f'participant "{participant_source}"\n'
            f'participant "{participant_target}"\n'
            f'"{participant_source}" -> "{participant_target}": Report: {report_name}'
        )
