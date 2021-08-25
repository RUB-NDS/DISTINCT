import re

from model.Frame import Frame

class ExecutionContext():

    def __init__(self):
        self.topframe = Frame()

    def process_report(self, report):
        key = report["report"]["key"]
        val = report["report"]["val"]
        
        if key == "framecreated":
            # href, hierarchy, html
            pass
        elif key == "framedestroyed":
            # href, hierarchy
            pass
        elif key == "popupopened":
            # href, hierarchy, url
            pass
        elif key == "html":
            # href, hierarchy, html
            pass
        elif key == "dumpframe":
            # href, hierarchy
            pass
        elif key == "result":
            # href, hierarchy, key, val
            pass
        elif key == "event":
            # href, hierarchy, event
            pass
        elif key == "formsubmit":
            # href, hierarchy, action, form
            pass
        elif key == "formpost":
            # href, hierarchy, action, form
            pass

    def get_frame(self, hierarchy):
        # i.e., frame.hierarchy = "top.frames[0].frames[1].popup[0].top.frames[0]"
        
        splitted = hierarchy.split(".")
        current = self.topframe
        
        for i in range(1, len(splitted)):
            frames = re.search("frames\[(\d)+\]", splitted[i])
            popups = re.search("popups\[(\d)+\]", splitted[i])

            if splitted[i] == "top":
                current = current.self
            elif frames:
                frame_idx = frames.group(1)
                current = current.frames[frame_idx]
            elif popups:
                popup_idx = popups.group(1)
                current = current.popups[popup_idx]
