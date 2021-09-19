from cmd import Cmd

class CliPrompt(Cmd):
    
    prompt = ""

    def __init__(self, event_handler):
        super(CliPrompt, self).__init__()
        self.event_handler = event_handler

    def do_hello(self, params):
        print("Hello, world")
    
    def do_show(self, params):
        self.event_handler.queue_message({"cmd": {"command": "show", "params": params.split(" ")}})

    def do_exit(self, input):
        print("Bye")
        return True
