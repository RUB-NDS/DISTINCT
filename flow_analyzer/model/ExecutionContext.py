import re
import logging

from model.Frame import Frame

logger = logging.getLogger(__name__)

class ExecutionContext():

    def __init__(self):
        self.topframe = None
        self.results = {}

    def __str__(self):
        if not self.topframe:
            return ""
        
        dump = {"val": "top"}
        def go_down(current, dump, indent):
            for i in range(0, len(current.frames)):
                dump["val"] += "\n{}-> frames[{}]".format('\t'*indent, i)
                go_down(current.frames[i], dump, indent+1)
            for i in current.popups.keys():
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
            print("COMMAND: show context\n" + str(self))
        elif command == "show" and params[0] == "results":
            print("COMMAND: show results\n")
            for key, val in self.results.items():
                print(f"key={key}, val={val}")

    def process_report(self, report):
        key = report["key"]
        val = report["val"]
        
        if key == "framecreated":
            # href, hierarchy, (html)
            frame = Frame(href=val["href"])
            self.insert_frame(val["hierarchy"], frame)
        elif key == "framedestroyed":
            # href, hierarchy
            self.remove_frame(val["hierarchy"])
        elif key == "popupopened":
            # href, hierarchy, url
            pass
        elif key == "popupclosed":
            # href, hierarchy
            self.remove_frame(val["hierarchy"])
        elif key == "html":
            # href, hierarchy, html
            pass
        elif key == "dumpframe":
            # href, hierarchy
            pass
        elif key == "result":
            # href, hierarchy, key, val
            self.results[val["key"]] = val["val"]
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
            return current.frames[frame_idx]
        elif popups:
            popup_idx = int(popups.group(1))
            return current.popups[popup_idx]
        else:
            return None

    def insert_frame(self, hierarchy, frame):
        """ Insert frame and all superior frames and superior popups in tree (if not existent)
            Overwrites frame, so all iframes and popups are lost!
            Returns True, if frame inserted successfully
            Returns False, if frame not inserted successfully
        """
        if hierarchy == "top":
            self.topframe = frame
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
                    logger.info(
                        f""" Creating new iframe with index {frame_idx}
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
                    logger.info(
                        f""" Creating new popup with index {popup_idx}
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
                logger.info("Creating topframe")
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
