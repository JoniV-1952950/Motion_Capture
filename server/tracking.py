import numpy as np
import cv2 as cv
from math import sqrt
import socket_utils as su

#############################################
def handle_incoming_img(sock, aspect):
    len_data = su.recvall(sock, 4) # Wait for, and then receive, incoming data
    len_data = int.from_bytes(len_data, "little")
    x = int(sqrt(len_data*aspect))
    y = int(x/aspect)
    shape = (y,x)
    
    data = su.recvall(sock, len_data)
    
    img = np.frombuffer(data, dtype="uint8").reshape(shape)
    cv.imshow("img", img)
    cv.waitKey(1)
#############################################


#############################################
def handle_incoming_2d_locs(sock, aspect):
    len_data = su.recvall(sock, 4) # Wait for, and then receive, incoming data
    len_data = int.from_bytes(len_data, "little")
    x = int(len_data/(2*np.dtype(np.float32).itemsize))
    shape = (x, 2)
    
    data = su.recvall(sock, len_data)

    locs_2d = np.frombuffer(data, dtype=np.float32).reshape(shape)
    print(locs_2d)
#############################################