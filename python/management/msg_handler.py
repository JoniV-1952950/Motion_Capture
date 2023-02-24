import os
import psutil
import sys
sys.path.append("/home/pi/Motion_Capture/python/app")
from MSG_KIND import MSG_KIND
import socket

# # # # # # # # # # # # 
def msg_handler(msg, sock):
    print(msg)
    if msg == MSG_KIND.UPDATE.value:
        #stop_app()
        os.chdir("/home/pi/Motion_Capture/python")
        len_files = int.from_bytes(recvall(sock, 4), 'little')
        
        for i in range(len_files):
            len_data = int.from_bytes(recvall(sock, 4), 'little')
            fileinfo = recvall(sock, len_data).decode()
            print(fileinfo)
            filename, filesize = fileinfo.split(';')
            filename = os.path.basename(filename)
            filesize = int(filesize)
            
            with open(filename, "wb") as f:
                bytes_read = recvall(sock, filesize)
                f.write(bytes_read)
        
    elif msg == MSG_KIND.REBOOT.value:
        os.system("reboot")
    elif msg == MSG_KIND.SHUTDOWN.value:
        os.system("shutdown")
    elif msg == MSG_KIND.RESTART.value:
        stop_app()        
    return None
# # # # # # # # # # # #

def stop_app():
    for proc in psutil.process_iter():
        pinfo = proc.as_dict(attrs=['pid', 'name'])
        procname = str(pinfo['name'])
        procpid = str(pinfo['pid'])
        if "python" in procname and procpid != str(os.getpid()):
            proc.kill()

# # # # # # # # # # # # # 

def recvall(sock, n):
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data