class Frame():

    def __init__(self, href="", hierarchy="", html="", parent=None, opener=None):
        self.href = href
        self.hierarchy = hierarchy
        self.html = html

        self.parent = parent
        self.opener = opener

        self.popups: list(Frame) = {}
        self.frames: list(Frame) = {}

        # js operations
    