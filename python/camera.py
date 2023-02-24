from picamera2 import Picamera2, Preview
import time
import numpy as np
import cv2 as cv

intrinsic_filename = "home/pi/Motion_Capture/cam_mtxs/intrinsic.npz"

img_size = (1280,720)

chessboardPattern = (11,8)
minimumNumberOfChessPatterns = 20

cam = None
mtx = None
dist = None
newcameramtx = None
roi = None

# # # # # # # # # # # # # # # 
def save_intrinsic(loc_mtx, loc_dist, loc_newcameramtx, loc_roi):
    np.savez(intrinsic_filename, mtx=loc_mtx, dist=loc_dist, newcameramtx=loc_newcameramtx, roi=loc_roi)
# # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # 
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
# # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # 
def find_intrinsic_matrix():
    # termination criteria
    criteria = (cv.TermCriteria_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    
    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((chessboardPattern[0] * chessboardPattern[1], 3), np.float32)
    objp[:,:2] = np.mgrid[0:chessboardPattern[0], 0:chessboardPattern[1]].T.reshape(-1,2)
    
    # Arrays to store object points and image points from all the images.
    objpoints = [] # 3d point in real world space
    imgpoints = [] # 2d points in image plane.
    
    # images = utils.load_images("checkerboard_imgs.xml")
    for i in range(minimumNumberOfChessPatterns):
        time.sleep(1.5)
        while True:
            img = cam.capture_array()        
            print("frame taken")
            gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
            
            ret, corners = cv.findChessboardCorners(gray, chessboardPattern, None)
        
            # If found, add object points, image points (after refining them)
            if ret is True:
                print("===== Found corners " + str(i))
                objpoints.append(objp)
                cornersSub = cv.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
                imgpoints.append(cornersSub)
                # Draw and display the corners
                cv.drawChessboardCorners(img, chessboardPattern, cornersSub, ret)
                cv.imshow('img', img)
                break
    cv.destroyAllWindows()
    
    ret, loc_mtx, loc_dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
    
    h, w = img.shape[:2]
    loc_newcameramtx, loc_roi = cv.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w,h))
    
    # Calculate the error
    mean_error = 0
    for i in range(len(objpoints)):
        imgpoints2, _ = cv.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
        error = cv.norm(imgpoints[i], imgpoints2, cv.NORM_L2)/len(imgpoints2)
        mean_error += error
    print( "total error: {}".format(mean_error/len(objpoints)) )
    
    save_intrinsic(loc_mtx, loc_dist, loc_newcameramtx, loc_roi)
    
    mtx, dist, newcameramtx, roi = loc_mtx, loc_dist, loc_newcameramtx, loc_roi
# # # # # # # # # # # # # # # # #     

# # # # # # # # # # # # # # # # # 
def cam_setup():
    global cam, mtx, dist, newcameramtx, roi
    # set up picamera
    cam = Picamera2()
    cam_config = cam.create_video_configuration({"format":"YUV420", "size":img_size},lores={"size":(640, 480)}, display="lores")
    cam.configure(cam_config)
    cam.start_preview(Preview.QTGL)
    cam.start()
    # load from file
    mtx, dist, newcameramtx, roi = load_intrinsic()
# # # # # # # # # # # # # # # # # 

# # # # # # # # # # # # # # # # # 
def frame():
    img = cam.capture_array()
    img = img[:img_size[1]]
    if mtx is not None:    
        undistorted_img = cv.undistort(img, mtx, dist, None, newcameramtx) 
        return undistorted_img
    return img
# # # # # # # # # # # # # # # # #