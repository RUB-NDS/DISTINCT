import re
import logging

from model.Frame import Frame
from model.SequenceDiagram import SequenceDiagram

logger = logging.getLogger(__name__)

class ExecutionContext():

    def __init__(self, config = {}):
        self.topframe = None
        
        # Reports received from chrome extension (i.e., flows, SDKs, ...)
        self.reports = {}

        # History of all events received from chrome extension
        self.history = []

        # Events as visual representation
        outputdir = config["outputdir"] if "outputdir" in config else None
        self.sequencediagram = SequenceDiagram(outputdir)

        if "starttime" in config:
            self.process_report("starttime", config["starttime"])
        if "outputdir" in config:
            self.process_report("outputdir", config["outputdir"])
        if "url" in config:
            self.process_report("url", config["url"])
        if "codeversion" in config:
            self.process_report("codeversion", config["codeversion"])

    def __str__(self):
        """ String representation of execution context is a tree hierarchy
            Example:
            top
                -> popups[0]
                -> frames[0]
                    -> frames[0]
        """
        if not self.topframe:
            return ""
        
        dump = {"val": "top"}
        def go_down(current, dump, indent):
            for i in current.frames.keys():
                dump["val"] += "\n{}-> frames[{}]".format('\t'*indent, i)
                go_down(current.frames[i], dump, indent+1)
            for i in current.popups.keys():
                if current.popups[i].closed:
                    continue
                dump["val"] += "\n{}-> popups[{}]".format('\t'*indent, i)
                go_down(current.popups[i], dump, indent+1)
        
        go_down(self.topframe, dump, 1)
        return dump["val"]

    def process_report(self, key, val):
        if key not in self.reports:
            self.reports[key] = [val]
        else:
            self.reports[key].append(val)

    def process_event(self, event):
        self.history.append(event)
        
        id = event["id"]
        timestamp = event["timestamp"]
        key = event["key"]
        val = event["val"]
        
        if key == "report":
            """ REPORT
                -> href, hierarchy, key, val
            """
            self.process_report(val["key"], val["val"])
        
        elif key == "documentinit":
            """ DOCUMENT INIT
                The document is initiated. Since the extension is executed
                before any other scripts on the page, this state catches the page before any
                other JS redirects or similar are executed.
                -> href, hierarchy
            """
            frame = Frame(href=val["href"])
            new_frame = self.insert_frame(val["hierarchy"], frame)
            
            self.sequencediagram.documentinit(
                id,
                val["hierarchy"],
                val["href"]
            )

        elif key == "documentloading":
            """ DOCUMENT LOADING
                The document is still loading.
                -> href, hierarchy
            """
            pass
        
        elif key == "documentinteractive":
            """ DOCUMENT INTERACTIVE
                The document has finished loading. We can now access the DOM elements.
                But sub-resources such as scripts and frames are still loading.
                -> href, hierarchy, html
            """
            frame = Frame(href=val["href"], html=val["html"])
            new_frame = self.insert_frame(val["hierarchy"], frame)
            
            self.sequencediagram.documentinteractive(
                id,
                val["hierarchy"],
                val["href"],
                val["html"]
            )

        elif key == "documentcomplete":
            """ DOCUMENT COMPLETED
                The page is fully loaded.
                -> href, hierarchy, html
            """
            pass
        
        elif key == "documentbeforeunload":
            """ DOCUMENT BEFOREUNLOAD
                The document and its resources are about to be unloaded.
                -> href, hierarchy
            """
            frame = self.get_frame(val["hierarchy"])
            if frame:
                self.sequencediagram.documentbeforeunload(
                    id,
                    val["hierarchy"]
                )
                self.remove_frame(val["hierarchy"])

        elif key == "httpredirect":
            """ HTTP REDIRECT
                -> href, hierarchy, status_code, location
            """
            frame = self.get_frame(val["hierarchy"])
            
            self.sequencediagram.httpredirect(
                id,
                val["hierarchy"],
                val["href"],
                val["status_code"],
                val["location"]
            )
        
        elif key == "formsubmit":
            """ FORM SUBMITTED
                -> href, hierarchy, action, form
            """
            frame = Frame(href=val["action"])
            new_frame = self.insert_frame(val["hierarchy"], frame)
            
            self.sequencediagram.formsubmit(
                id,
                val["hierarchy"],
                val["action"],
                val["form"]
            )

        elif key == "metaredirect":
            """ META REDIRECT
                -> href, hierarchy, wait_seconds, location
            """
            self.sequencediagram.metaredirect(
                id,
                val["hierarchy"],
                val["href"],
                val["wait_seconds"],
                val["location"]
            )

        elif key == "metareload":
            """ META RELOAD
                -> href, hierarchy, wait_seconds
            """
            self.sequencediagram.metareload(
                id,
                val["hierarchy"],
                val["href"],
                val["wait_seconds"]
            )

        elif key == "refreshredirect":
            """ REFRESH REDIRECT
                -> href, hierarchy, wait_seconds, location, status_code
            """
            self.sequencediagram.refreshredirect(
                id,
                val["hierarchy"],
                val["href"],
                val["wait_seconds"],
                val["location"],
                val["status_code"]
            )

        elif key == "refreshreload":
            """ REFRESH RELOAD
                -> href, hierarchy, wait_seconds, status_code
            """
            self.sequencediagram.refreshreload(
                id,
                val["hierarchy"],
                val["href"],
                val["wait_seconds"],
                val["status_code"]
            )
            
        elif key == "windowopen":
            """ POPUP OPENED
                -> href, hierarchy, url, popup_hierarchy
            """
            frame = Frame(href=val["url"])
            new_frame = self.insert_frame(val["popup_hierarchy"], frame)
            
            self.sequencediagram.windowopen(
                id,
                val["popup_hierarchy"],
                val["hierarchy"],
                val["url"]
            )
        
        elif key == "windowclose":
            """ POPUP CLOSED
                -> href, hierarchy, opener_hierarchy
            """
            old_frame = self.get_frame(val["hierarchy"])
            if old_frame:
                self.sequencediagram.windowclose(
                    id,
                    val["hierarchy"],
                    val["opener_hierarchy"]
                )
                self.remove_frame(val["hierarchy"])

        elif key == "closedaccessed":
            """ CLOSED ACCESSED
                -> href, hierarchy, closed
            """
            self.sequencediagram.closedaccessed(
                id,
                val["hierarchy"],
                val["closed"]
            )

        elif key == "postmessagereceived":
            """ POSTMESSAGE RECEIVED
                -> href, hierarchy, receiver, sender, data, datatype,
                ports = [{channel_id, port_id}], targetorigincheck, sourceoriginaccessed = "yes"/"no"
            """
            self.sequencediagram.postmessagereceived(
                id,
                val["receiver"],
                val["sender"],
                val["data"],
                val["datatype"],
                val["ports"],
                val["targetorigincheck"]
            )

        elif key == "addeventlistener":
            """ ADD EVENT LISTENER
                -> href, hierarchy, type, method, callback
            """
            self.sequencediagram.addeventlistener(
                id,
                val["hierarchy"],
                val["type"],
                val["method"],
                val["callback"]
            )

        elif key == "removeeventlistener":
            """ REMOVE EVENT LISTENER
                -> href, hierarchy, type, method, callback
            """
            self.sequencediagram.removeeventlistener(
                id,
                val["hierarchy"],
                val["type"],
                val["method"],
                val["callback"]
            )

        elif key == "customeventnew":
            """ CUSTOM EVENT NEW
                -> href, hierarchy, type, data, data_type
            """
            self.sequencediagram.customeventnew(
                id,
                val["hierarchy"],
                val["type"],
                val["data"],
                val["data_type"]
            )

        elif key == "customeventreceived":
            """ CUSTOM EVENT RECEIVED
                -> href, hierarchy, type, data, data_type
            """
            self.sequencediagram.customeventreceived(
                id,
                val["hierarchy"],
                val["type"],
                val["data"],
                val["data_type"]
            )

        elif key == "messagechannelnew":
            """ MESSAGE CHANNEL NEW
                -> href, hierarchy, channel_id
            """
            self.sequencediagram.messagechannelnew(
                id,
                val["hierarchy"],
                val["channel_id"]
            )

        elif key == "channelmessagereceived":
            """ CHANNEL MESSAGE RECEIVED
                -> href, hierarchy, channel_id, port_id, source_frame, target_frame, data, data_type
            """
            self.sequencediagram.channelmessagereceived(
                id,
                val["channel_id"],
                val["port_id"],
                val["source_frame"],
                val["target_frame"],
                val["data"],
                val["data_type"]
            )

        elif key == "broadcastchannelnew":
            """ BROADCAST CHANNEL NEW
                -> href, hierarchy, channel_name
            """
            self.sequencediagram.broadcastchannelnew(
                id,
                val["hierarchy"],
                val["channel_name"]
            )
        
        elif key == "broadcastmessagereceived":
            """ BROADCAST MESSAGE RECEIVED
                -> href, hierarchy, channel_name, target_frame, data, data_type
            """
            self.sequencediagram.broadcastmessagereceived(
                id,
                val["channel_name"],
                val["target_frame"],
                val["data"],
                val["data_type"]
            )

        elif key == "broadcastmessagesent":
            """ BROADCAST MESSAGE SENT
                -> href, hierarchy, channel_name, source_frame, data, data_type
            """
            self.sequencediagram.broadcastmessagesent(
                id,
                val["channel_name"],
                val["source_frame"],
                val["data"],
                val["data_type"]
            )

        elif key == "localstorageset":
            """ LOCALSTORAGE SET
                -> href, hierarchy, key, val
            """
            self.sequencediagram.localstorageset(
                id,
                val["hierarchy"],
                val["key"],
                val["val"]
            )

        elif key == "sessionstorageset":
            """ SESSIONSTORAGE SET
                -> href, hierarchy, key, val
            """
            self.sequencediagram.sessionstorageset(
                id,
                val["hierarchy"],
                val["key"],
                val["val"]
            )
        
        elif key == "cookieset":
            """ COOKIE SET
                -> href, hierarchy, val
            """
            self.sequencediagram.cookieset(
                id,
                val["hierarchy"],
                val["val"]
            )
        
        elif key == "idbadd" or key == "idbput":
            """ INDEXEDDB ADD/PUT
                -> href, hierarchy, db, objectstore, keypath, key, val
            """
            self.sequencediagram.idbset(
                id,
                val["hierarchy"],
                val["db"],
                val["objectstore"],
                val["keypath"],
                val["key"],
                val["val"]
            )

        elif key == "windowpropnew":
            """ WINDOW PROP NEW
                -> href, hierarchy, key, val, valtype
            """
            self.sequencediagram.windowpropnew(
                id,
                val["hierarchy"],
                val["key"],
                val["val"],
                val["valtype"]
            )
        
        elif key == "windowpropchanged":
            """ WINDOW PROP CHANGED
                -> href, hierarchy, key, val, valtype
            """
            self.sequencediagram.windowpropchanged(
                id,
                val["hierarchy"],
                val["key"],
                val["val"],
                val["valtype"]
            )

        elif key == "locationset":
            """ LOCATION SET
                -> href, hierarchy, prop, target
            """
            self.sequencediagram.locationset(
                id,
                val["hierarchy"],
                val["href"],
                val["prop"],
                val["target"]
            )

    def update_frame(self, old_frame, new_frame):
        """ Update properties of existing frame with properties of new frame
            Properties: href, html
        """
        old_frame.href = new_frame.href
        old_frame.html = new_frame.html

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
                except KeyError as e:
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
            return self.topframe
        elif frames:
            frame_idx = int(frames.group(1))
            try:
                return current.frames[frame_idx]
            except KeyError as e:
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
            Returns frame, if frame inserted successfully
            Returns None, if frame not inserted successfully
        """
        # If frame already exists, just update its properties
        # but keep it in hierarchy tree with references to parents and children
        old_frame = self.get_frame(hierarchy)
        if old_frame:
            self.update_frame(old_frame, frame)
            return old_frame

        path = hierarchy.split(".")

        current = self.topframe
        for i in range(0, len(path) - 1):
            frames = re.search("frames\[(\d)+\]", path[i])
            popups = re.search("popups\[(\d)+\]", path[i])

            if frames:
                frame_idx = int(frames.group(1))
                try:
                    current = current.frames[frame_idx]
                except KeyError as e:
                    # Create intermediate iframe
                    logger.debug(
                        f""" Creating new intermediate iframe with index {frame_idx}
                        in frame '{current.hierarchy()}'"""
                    )
                    inter_frame = Frame()
                    inter_frame.parent = current
                    inter_frame.opener = None
                    idx = current.insert_iframe(frame_idx, inter_frame)
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
            current.insert_iframe(frame_idx, frame)
        elif popups:
            popup_idx = int(popups.group(1))
            frame.parent = None
            frame.opener = current
            current.insert_popup(popup_idx, frame)
        elif last == "top" and not self.topframe:
            self.topframe = frame

        return frame

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
                except KeyError as e:
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
            self.topframe = None
        elif frames:
            frame_idx = int(frames.group(1))
            if frame_idx in current.frames:
                current.delete_iframe(frame_idx)
        elif popups:
            popup_idx = int(popups.group(1))
            if popup_idx in current.popups:
                current.delete_popup(popup_idx)

        return True
