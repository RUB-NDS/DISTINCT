from cmd import Cmd

from config import terminate_proxy, store_all_cookies

class CliPrompt(Cmd):
    
    prompt = "> "

    def __init__(self, driver, proxy, outputdir, chromeprofile, event_handler):
        super(CliPrompt, self).__init__()
        
        self.driver = driver
        self.proxy = proxy
        self.outputdir = outputdir
        self.chromeprofile = chromeprofile
        self.event_handler = event_handler
    
    def do_show(self, params):
        self.event_handler.queue_message(
            {"cmd": {"command": "show", "params": params.split(" ")}}
        )

    def do_compile(self, params):
        self.event_handler.execution_context.sequencediagram.compile()

    def do_dumpcookies(self, params):
        store_all_cookies(self.driver, self.outputdir)

    def do_exit(self, params):
        """ Exit the tool """

        # Cleanup ...
        terminate_proxy(self.proxy)
        store_all_cookies(self.driver, self.outputdir)
        # delete_chromeprofile(chromeprofile)
        
        print("Bye")
        return True
