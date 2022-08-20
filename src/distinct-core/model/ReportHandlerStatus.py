from enum import Enum

class ReportHandlerStatus(Enum):
  INIT = 0
  RUNNING = 1
  STOPPED = -1
