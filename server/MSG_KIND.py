from enum import Enum

class MSG_KIND(Enum):
    IMG = "n"
    MARKERS = "m"
    DEBUG = "d"
    STREAM = "s"
    END_STREAM = "q"
    TEXT = "t"
    LIST_CAMS = "ls"
    INTRINSIC_CALIBRATE = "i"
    EXTRINSIC_CALIBRATE = "c"
    UPDATE = "upda"
    SHUTDOWN = "shut"
    REBOOT = "rebo"
    RESTART = "rest"