import cv2 as cv 
import numpy as np

# # # # # # # # # # # # 
def detect_markers(orig_img):    
    ret, img = cv.threshold(orig_img, 240, 255, cv.THRESH_BINARY)
    img = cv.medianBlur(img, 9)

    contours, hierarchy = cv.findContours(img, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    locs_2d = np.empty((0,2), dtype=np.uint16)
    for c in contours:
        # compute the center of the contour
        M = cv.moments(c)
        if M["m00"] == 0:
            continue
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        cv.circle(orig_img, (cX, cY), 1, 0, -1)
        locs_2d = np.append(locs_2d, np.array([[cX, cY]], dtype=np.uint16), axis=0)
    return locs_2d
# # # # # # # # # # # #