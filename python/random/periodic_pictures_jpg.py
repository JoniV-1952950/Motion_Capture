from picamera2 import Picamera2, Preview
import time
import cv2 as cv

cam = Picamera2()

def main():
    controls = {"ExposureTime":5000}
    cam_config = cam.create_still_configuration(controls=controls, main={"size": (1280, 720)}, lores={"size":(640, 480)}, display="lores")
    cam.configure(cam_config)
    cam.start_preview(Preview.QTGL)

    cam.start()
    
    for i in range(32):
        time.sleep(4)
        img = cam.capture_array()
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        cv.imwrite("pictures/" + str(i) + ".jpg", gray)
        print(i)
    
if __name__ == "__main__":
    main()