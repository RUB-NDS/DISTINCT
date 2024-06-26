class Frame():

    def __init__(self, href=None, html=None):
        self.href = href
        self.html = html

        self.parent = None
        self.opener = None

        self.popups = {} # {0: Frame, 1: Frame, ...} -> ._sso._popups[0], ._sso._popups[1]
        self.frames = {} # {0: Frame, 1: Frame, ...} -> .frames[0], .frames[1]

        self.closed = False

    def __str__(self):
        return self.hierarchy()

    def hierarchy(self):
        """ Algorithm 1: Determine frame hierarchy """
        path = {"val": ""}
        def go_up(current, path):
            if current.parent:
                # I am an iframe. -> Which child iframe am I?
                for i in current.parent.frames.keys():
                    if current.parent.frames[i] == current:
                        path["val"] = f"frames[{i}]" + ("." if len(path["val"]) else "") + path["val"]
                go_up(current.parent, path)
            elif current.opener:
                # I am a popup. -> Which popup am I?
                for i in current.opener.popups.keys():
                    if current.opener.popups[i] == current:
                        path["val"] = f"popups[{i}]" + ("." if len(path["val"]) else "") + path["val"]
                go_up(current.opener, path)
            else:
                # I am the primary window.
                path["val"] = "top" + ("." if len(path["val"]) else "") + path["val"]
        go_up(self, path)
        return path["val"]

    """ IFRAMES """

    def insert_iframe(self, index, frame):
        """ Insert iframe at index """
        self.frames[index] = frame
        return index

    def delete_iframe(self, index):
        """ Delete iframe at index """
        del self.frames[index]

        # When iframes are deleted, we must shift the frames array to the left
        # Example:
        # Before: top.frames[0], top.frames[1], top.frames[2]
        # top.frames[1] is unloaded
        # After: top.frames[0], top.frames[1]
        # What happened? -> top.frames[2] is now top.frames[1]
        new_frames = {}
        for idx, frame in enumerate(self.frames.values()):
            new_frames[idx] = frame
        self.frames = new_frames

    """ POPUPS """

    def insert_popup(self, index, frame):
        """ Insert popup at index """
        self.popups[index] = frame
        return index

    def delete_popup(self, index):
        """ Delete popup at index """
        self.popups[index].closed = True
    