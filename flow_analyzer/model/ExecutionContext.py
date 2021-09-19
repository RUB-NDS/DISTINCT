import re
import logging

from model.Frame import Frame
from mermaid.SequenceDiagram import SequenceDiagram

logger = logging.getLogger(__name__)

class ExecutionContext():

    def __init__(self):
        self.topframe = None
        self.results = {}
        self.sequencediagram = SequenceDiagram()

    def __str__(self):
        if not self.topframe:
            return ""
        
        dump = {"val": "top"}
        def go_down(current, dump, indent):
            for i in range(0, len(current.frames)):
                dump["val"] += "\n{}-> frames[{}]".format('\t'*indent, i)
                go_down(current.frames[i], dump, indent+1)
            for i in current.popups.keys():
                if current.popups[i].closed:
                    continue
                dump["val"] += "\n{}-> popups[{}]".format('\t'*indent, i)
                go_down(current.popups[i], dump, indent+1)
        
        go_down(self.topframe, dump, 1)
        return dump["val"]

    def process_message(self, message):
        if "report" in message:
            self.process_report(message["report"])
        if "cmd" in message:
            self.process_cmd(message["cmd"])

    def process_cmd(self, cmd):
        command = cmd["command"]
        params = cmd["params"]
        
        if command == "show" and params[0] == "context":
            print(self)
        elif command == "show" and params[0] == "results":
            for key, val in self.results.items():
                print(f"key={key}, val={val}")
        elif command == "show" and params[0] == "mermaid":
            print(self.sequencediagram)
        elif command == "show" and params[0] == "plot":
            self.sequencediagram.plot()

    def process_report(self, report):
        key = report["key"]
        val = report["val"]
        
        if key == "documentloading":
            """ DOCUMENT LOADING
                The document is still loading.
                -> href, hierarchy
            """
            print("Document loading: " + val["hierarchy"])
            pass
        elif key == "documentinteractive":
            """ DOCUMENT INTERACTIVE
                The document has finished loading. We can now access the DOM elements.
                But sub-resources such as scripts and frames are still loading.
                -> href, hierarchy
            """
            print("Document interactive: " + val["hierarchy"])
            pass
        elif key == "documentcomplete":
            """ DOCUMENT COMPLETED
                The page is fully loaded.
                -> href, hierarchy, html
            """
            print("Document complete: " + val["hierarchy"])
            pass
        elif key == "framecreated":
            """ FRAME CREATED
                -> href, hierarchy, html
            """
            print("Frame completed: " + val["hierarchy"])
            frame = Frame(href=val["href"], html=val["html"])
            self.insert_frame(val["hierarchy"], frame)
            
            # Mermaid
            if frame.parent:
                self.sequencediagram.add_iframe(frame.hierarchy(), frame.parent.hierarchy())
            elif frame.opener:
                self.sequencediagram.add_popup(frame.hierarchy(), frame.opener.hierarchy())
            else:
                self.sequencediagram.add_topframe()
            self.sequencediagram.url_get(frame.hierarchy(), frame.href)
        
        elif key == "framedestroyed":
            """ FRAME DESTROYED
                -> href, hierarchy
            """
            frame = self.get_frame(val["hierarchy"])
            
            if not frame:
                logger.error(
                    f"""Failed to remove frame '{val["hierarchy"]}' since it
                    does not exist."""
                )
                return

            # Mermaid
            if frame.parent:
                self.sequencediagram.close_iframe(frame.hierarchy(), frame.parent.hierarchy())
            elif frame.opener:
                self.sequencediagram.close_popup(frame.hierarchy(), frame.opener.hierarchy())

            self.remove_frame(val["hierarchy"])
            
        elif key == "popupopened":
            """ POPUP OPENED
                -> href, hierarchy, url
            """
            pass
        
        elif key == "popupclosed":
            """ POPUP CLOSED
                -> href, hierarchy
            """
            frame = self.get_frame(val["hierarchy"])

            if not frame:
                logger.error(
                    f"""Failed to remove frame '{val["hierarchy"]}' since it
                    does not exist."""
                )
                return

            # Mermaid
            self.sequencediagram.close_popup(frame.hierarchy(), frame.opener.hierarchy())

            self.remove_frame(val["hierarchy"])
        
        elif key == "dumpframe":
            """ FRAME DUMPED
                -> href, hierarchy, html
            """
            pass
        
        elif key == "result":
            """ RESULT
                -> href, hierarchy, key, val
            """
            self.results[val["key"]] = val["val"]
        
        elif key == "event":
            """ EVENT
                -> href, hierarchy, event
            """
            pass
        
        elif key == "formsubmit":
            """ FORM SUBMITTED
                -> href, hierarchy, action, form
            """
            pass
        
        elif key == "formpost":
            """ FORM POST RESPONSE TYPE
                -> href, hierarchy, action, form
            """
            pass
    
    def get_frame(self, hierarchy):
        """ Get frame in hierarchy
            Returns frame, if frame is found
            Returns None, if frame is not found
        """
        path = hierarchy.split(".")

        if not self.topframe:
            return None
        
        current = self.topframe
        for i in range(0, len(path) - 1):
            frames = re.search("frames\[(\d)+\]", path[i])
            popups = re.search("popups\[(\d)+\]", path[i])

            if frames:
                frame_idx = int(frames.group(1))
                try:
                    current = current.frames[frame_idx]
                except IndexError as e:
                    return None
            elif popups:
                popup_idx = int(popups.group(1))
                try:
                    current = current.popups[popup_idx]
                except KeyError as e:
                    return None
        
        last = path[-1]
        frames = re.search("frames\[(\d)+\]", last)
        popups = re.search("popups\[(\d)+\]", last)

        if last == "top":
            return self.topframe # This is our topframe
        elif frames:
            frame_idx = int(frames.group(1))
            try:
                return current.frames[frame_idx]
            except IndexError as e:
                return None
        elif popups:
            popup_idx = int(popups.group(1))
            try:
                return current.popups[popup_idx]
            except KeyError as e:
                return None
        else:
            return None

    def insert_frame(self, hierarchy, frame):
        """ Insert frame and all superior frames and superior popups in tree (if not existent)
            Returns True, if frame inserted successfully
            Returns False, if frame not inserted successfully
        """
        
        # If frame already exists, just update its basic values
        # but keep it in tree with .frames[] and .popups[] references
        old_frame = self.get_frame(hierarchy)
        if old_frame:
            self.update_frame(old_frame, frame)
            return True

        path = hierarchy.split(".")

        current = self.topframe
        for i in range(0, len(path) - 1):
            frames = re.search("frames\[(\d)+\]", path[i])
            popups = re.search("popups\[(\d)+\]", path[i])

            if frames:
                frame_idx = int(frames.group(1))
                try:
                    current = current.frames[frame_idx]
                except IndexError as e:
                    # Create intermediate iframe
                    logger.debug(
                        f""" Creating new intermediate iframe with index {frame_idx}
                        in frame '{current.hierarchy()}'"""
                    )
                    inter_frame = Frame()
                    inter_frame.parent = current
                    inter_frame.opener = None
                    idx = current.insert_frame(inter_frame)
                    if idx != frame_idx:
                        logger.error(
                            f""" New iframe was inserted at index {idx} but expected
                            to be inserted at index {frame_idx} in frame '{current.hierarchy()}'"""
                        )
                        return False
                    current = current.frames[frame_idx]
            elif popups:
                popup_idx = int(popups.group(1))
                try:
                    current = current.popups[popup_idx]
                except KeyError as e:
                    # Create intermediate popup
                    logger.debug(
                        f""" Creating new intermediate popup with index {popup_idx}
                        in frame '{current.hierarchy()}'"""
                    )
                    inter_frame = Frame()
                    inter_frame.parent = None
                    inter_frame.opener = current
                    idx = current.insert_popup(popup_idx, inter_frame)
                    if idx != popup_idx:
                        logger.error(
                            f""" New popup was inserted at index {idx} but expected
                            to be inserted at index {popup_idx} in frame '{current.hierarchy()}'"""
                        )
                        return False
                    current = current.popups[popup_idx]
            elif path[i] == "top" and current == None:
                # Create topframe
                logger.debug("Creating intermediate topframe")
                inter_frame = Frame()
                inter_frame.parent = None
                inter_frame.opener = None
                self.topframe = inter_frame
                current = self.topframe
        
        last = path[-1]
        frames = re.search("frames\[(\d)+\]", last)
        popups = re.search("popups\[(\d)+\]", last)
        
        if frames:
            frame_idx = int(frames.group(1))
            frame.parent = current
            frame.opener = None
            if frame_idx < len(current.frames):
                # Update frame
                idx = current.update_frame(frame_idx, frame)
            else:
                # Append frame
                idx = current.insert_frame(frame)
            if idx != frame_idx:
                logger.error(
                    f""" New iframe was inserted at index {idx} but expected
                    to be inserted at index {frame_idx} in frame '{current.hierarchy()}'"""
                )
                return False
        elif popups:
            popup_idx = int(popups.group(1))
            frame.parent = None
            frame.opener = current
            idx = current.insert_popup(popup_idx, frame) # popups are dict -> overwrite
            if idx != popup_idx:
                logger.error(
                    f""" New popup was inserted at index {idx} but expected
                    to be inserted at index {popup_idx} in frame '{current.hierarchy()}'"""
                )
                return False
        elif last == "top" and not self.topframe:
            self.topframe = frame

        return True

    def remove_frame(self, hierarchy):
        """ Removes frame and all subframes and subpopups from tree
            Returns True, if frame removed successfully
            Returns False, if frame not removed successfully
        """
        path = hierarchy.split(".")
        
        current = self.topframe
        for i in range(0, len(path) - 1):
            frames = re.search("frames\[(\d)+\]", path[i])
            popups = re.search("popups\[(\d)+\]", path[i])

            if frames:
                frame_idx = int(frames.group(1))
                try:
                    current = current.frames[frame_idx]
                except IndexError as e:
                    logger.warning(f"""
                        Failed to remove frame '{hierarchy}' 
                        because frame '{current.hierarchy()}'
                        does not contain iframe with index {frame_idx}"""
                    )
                    return False
            elif popups:
                popup_idx = int(popups.group(1))
                try:
                    current = current.popups[popup_idx]
                except KeyError as e:
                    logger.warning(f"""
                        Failed to remove frame '{hierarchy}' 
                        because frame '{current.hierarchy()}'
                        does not contain popup with index {popup_idx}"""
                    )
                    return False
        
        last = path[-1]
        frames = re.search("frames\[(\d)+\]", last)
        popups = re.search("popups\[(\d)+\]", last)

        if last == "top":
            self.topframe = None # This is our topframe
        elif frames:
            frame_idx = int(frames.group(1))
            current.delete_frame(frame_idx)
        elif popups:
            popup_idx = int(popups.group(1))
            current.delete_popup(popup_idx)

        return True

    def update_frame(self, old_frame, new_frame):
        """ Update old frame with new frame but keep  """
        old_frame.href = new_frame.href
        old_frame.html = new_frame.html

        
