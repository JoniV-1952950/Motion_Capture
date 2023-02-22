from enum import Enum

class MSG_KIND(Enum):
    IMG = "n"
    MARKERS = "d"
    MARKERS_STREAM = "s"
    INTRINSIC_CALIBRATE = "i"
    EXTRINSIC_CALIBRATE = "c"