from enum import Enum

class MSG_KIND(Enum):
    IMG = "n"
    MARKERS = "m"
    MARKERS_STREAM = "s"
    INTRINSIC_CALIBRATE = "i"
    EXTRINSIC_CALIBRATE = "c"
    UPDATE = "upda"
    SHUTDOWN = "shut"
    REBOOT = "rebo"
    RESTART = "rest"