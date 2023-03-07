import camera
import masking
from MSG_KIND import MSG_KIND

#############################################
def msg_handler(msg):
    if msg == MSG_KIND.IMG.value:
        img = camera.frame()
        img_bytes = img.tobytes()
        img_bytes = msg.encode('utf-8') + len(img_bytes).to_bytes(4, "little") + img_bytes
        return img_bytes
    elif msg == MSG_KIND.MARKERS.value:
        img = camera.frame()
        locs_2d = masking.detect_markers(img)
        if locs_2d.shape != (0,2):
            locs_2d = camera.undistort_markers(locs_2d)
        locs_bytes = locs_2d.tobytes()
        locs_bytes = msg.encode('utf-8') + len(locs_bytes).to_bytes(4, "little") + locs_bytes
        return locs_bytes
    elif msg == MSG_KIND.INTRINSIC_CALIBRATE.value:
        camera.find_intrinsic_matrix()
    return None
#############################################