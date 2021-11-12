class Frame():

    def __init__(self, href=None, html=None):
        self.href = href
        self.html = html

        self.parent = None
        self.opener = None

        self.popups = {} # {0: Frame, 1: Frame, ...} -> ._sso._popups[0], ._sso._popups[1]
        self.frames = [] # [Frame, Frame, ...] -> .frames[0], .frames[1]

        self.closed = False

    def __str__(self):
        return self.hierarchy()

    def hierarchy(self):
        """ Algorithm 1: Determine frame hierarchy """
        path = {"val": ""}
        def go_up(current, path):
            if current.parent:
                # I am an iframe. -> Which child iframe am I?
                for i in range(0, len(current.parent.frames)):
                    if current.parent.frames[i] == current:
                        path["val"] = f"frames[{i}]" + ("." if len(path["val"]) else "") + path["val"]
                go_up(current.parent, path)
            elif current.opener:
                # I am a popup. -> Which popup am I?
                for i in range(0, len(current.opener.popups)):
                    if current.opener.popups[i] == current:
                        path["val"] = f"popups[{i}]" + ("." if len(path["val"]) else "") + path["val"]
                go_up(current.opener, path)
            else:
                # I am the primary window.
                path["val"] = "top" + ("." if len(path["val"]) else "") + path["val"]
        go_up(self, path)
        return path["val"]

    """ FRAMES """

    def insert_frame(self, frame):
        """ Append frame to list """
        self.frames.append(frame)
        return len(self.frames) - 1

    def update_frame(self, index, frame):
        """ Update frame in list """
        self.frames[index] = frame
        return index

    def delete_frame(self, index):
        """ Delete frame at index """
        self.frames.pop(index)

    """ POPUPS """

    def insert_popup(self, index, frame):
        """ Insert popup at index """
        self.popups[index] = frame
        return index

    def delete_popup(self, index):
        """ Delete popup at index """
        self.popups[index].closed = True
    