class EventProcessor:
    """ Base class for all event processors.
        An event processor receives an event as input, processes it, and creates some output.
        The event processing part is optional and may only be implemented for some events.
        The output can range from log files to entries in a sequence diagram.
    """

    def __init__(self, ctx, event):

        # Store reference to execution context in which this event was received
        self.ctx = ctx

        # Extract the main parts of an event
        # event = {"id": int, "timestamp": str, "key": str, "val": any}
        self.id = event["id"]
        self.timestamp = event["timestamp"]
        self.key = event["key"]
        self.val = event["val"]
