from cmd import Cmd

class CliPrompt(Cmd):
    
    def __init__(self, event_handler):
        super(CliPrompt, self).__init__()
        self.event_handler = event_handler

    def do_hello(self, input):
        print("Hello, world")
    
    def do_dumpcontext(self, input):
        message = {"cmd": {"command": "dumpcontext", "params": {}}}
        self.event_handler.queue_message(message)

    def do_exit(self, input):
        print("Bye")
        return True
