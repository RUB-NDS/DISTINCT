class Frame():

    def __init__(self, href="", hierarchy="", html=""):
        self.href = href
        self.hierarchy = hierarchy
        self.html = html

        self.parent = None
        self.opener = None

        self.popups = {} # {0: Frame, 1: Frame, ...} -> ._popups[0], .popups[1]
        self.frames = [] # [Frame, Frame, ...] -> .frames[0], .frames[1]

    def insert_frame(self, frame):
        self.frames.append(frame)
        return len(self.frames) - 1

    def insert_popup(self, index, frame):
        self.popups[index] = frame
        return index

    def delete_frame(self, index):
        self.frames.splice(index, 1)

    def delete_popup(self, index):
        del self.popups[index]
    