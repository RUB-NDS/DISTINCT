import re
import logging

from model.Frame import Frame

logger = logging.getLogger(__name__)

class ExecutionContext():

    def __init__(self):
        self.topframe = None

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
    
    def insert_frame(self, hierarchy, frame):
        """ Insert frame and all superior frames and superior popups in tree (if not existent)
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
            idx = current.insert_popup(popup_idx, frame)
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
