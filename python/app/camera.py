from picamera2 import Picamera2, Preview
import time
import numpy as np
import cv2 as cv
import tcp_socket as ts
from MSG_KIND import MSG_KIND

#############################################
intrinsic_filename = "home/pi/Motion_Capture/cam_mtxs/intrinsic.npz"

img_size = (640,480)

chessboardPattern = (11,8)
minimumNumberOfChessPatterns = 20

cam = None
mtx = None
dist = None
newcameramtx = None
roi = None
#############################################


############################################# 
def save_intrinsic(loc_mtx, loc_dist, loc_newcameramtx, loc_roi):
    np.savez(intrinsic_filename, mtx=loc_mtx, dist=loc_dist, newcameramtx=loc_newcameramtx, roi=loc_roi)
#############################################


#############################################
def load_intrinsic():
    try:
        container = np.load(intrinsic_filename)
        loc_mtx = container["mtx"]
        loc_dist = container["dist"]
        loc_newcameramtx = container["newcameramtx"]
        loc_roi = container["roi"]
        return loc_mtx, loc_dist, loc_newcameramtx, loc_roi
    except Exception as e:
        print("File does not exist")
        return None, None, None, None
#############################################


#############################################
def find_intrinsic_matrix():
    global mtx, dist, newcameramtx, roi
    # termination criteria
    criteria = (cv.TermCriteria_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    
    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((chessboardPattern[0] * chessboardPattern[1], 3), np.float32)
    objp[:,:2] = np.mgrid[0:chessboardPattern[0], 0:chessboardPattern[1]].T.reshape(-1,2)
    
    # Arrays to store object points and image points from all the images.
    objpoints = [] # 3d point in real world space
    imgpoints = [] # 2d points in image plane.
    
    for i in range(minimumNumberOfChessPatterns):
        time.sleep(1.5)
        while True:
            img = cam.capture_array()
            img = img[:img_size[1]]       
            
            # send frame to server for visual purposes
            img_bytes = img.tobytes()
            img_bytes = MSG_KIND.IMG.value.encode('utf-8') + len(img_bytes).to_bytes(4, "little") + img_bytes
            ts.send(img_bytes)
            
            ret, corners = cv.findChessboardCorners(img, chessboardPattern, None)
        
            # If found, add object points, image points (after refining them)
            if ret is True:
                string = "Found corners " + str(i+1)
                ts.send(MSG_KIND.TEXT.value.encode('utf-8') + len(string).to_bytes(4, "little") + string.encode('utf-8'))
                
                objpoints.append(objp)
                cornersSub = cv.cornerSubPix(img, corners, (11,11), (-1,-1), criteria)
                imgpoints.append(cornersSub)
                break
            
            string = "Empty frame"
            ts.send(MSG_KIND.TEXT.value.encode('utf-8') + len(string).to_bytes(4, "little") + string.encode('utf-8'))
    
    ret, loc_mtx, loc_dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, img.shape[::-1], None, None)
    
    h, w = img.shape[:2]
    loc_newcameramtx, loc_roi = cv.getOptimalNewCameraMatrix(loc_mtx, loc_dist, (w, h), 1, (w,h))
    
    # Calculate the error
    mean_error = 0
    for i in range(len(objpoints)):
        imgpoints2, _ = cv.projectPoints(objpoints[i], rvecs[i], tvecs[i], loc_mtx, loc_dist)
        error = cv.norm(imgpoints[i], imgpoints2, cv.NORM_L2)/len(imgpoints2)
        mean_error += error
        
    string = "Total error: {}".format(mean_error/len(objpoints))
    ts.send(MSG_KIND.TEXT.value.encode('utf-8') + len(string).to_bytes(4, "little") + string.encode('utf-8'))
    
    save_intrinsic(loc_mtx, loc_dist, loc_newcameramtx, loc_roi)
    
    mtx, dist, newcameramtx, roi = loc_mtx, loc_dist, loc_newcameramtx, loc_roi
#############################################    


#############################################
def cam_setup():
    global cam, mtx, dist, newcameramtx, roi
    # set up picamera
    cam = Picamera2()
    cam_config = cam.create_video_configuration({"format":"YUV420", "size":img_size})
    
    cam.configure(cam_config)
    cam.start()

    # load from file
    mtx, dist, newcameramtx, roi = load_intrinsic()
#############################################

#############################################
def frame():
    img = cam.capture_array()
    img = img[:img_size[1]]
    return img
#############################################


#############################################
def undistort_markers(markers):
    global mtx, dist, newcameramtx
    markers = np.array([markers], dtype=np.float32)
    if mtx is not None:
        markers = cv.undistortPoints(markers, mtx, dist, None, newcameramtx)
    return markers[0]