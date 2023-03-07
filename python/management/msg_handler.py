import os
import psutil
import sys
sys.path.append("/home/pi/Motion_Capture/python/app")
from MSG_KIND import MSG_KIND
import tcp_socket as ts


#############################################
def msg_handler(msg, sock):
    if msg == MSG_KIND.UPDATE.value:
        os.chdir("/home/pi/Motion_Capture/python")
        len_files = int.from_bytes(ts.recvall(sock, 4), 'little')
        
        for i in range(len_files):
            len_data = int.from_bytes(ts.recvall(sock, 4), 'little')
            fileinfo = ts.recvall(sock, len_data).decode()
            filename, filesize = fileinfo.split(';')
            filesize = int(filesize)
            
            with open(filename, "wb") as f:
                bytes_read = ts.recvall(sock, filesize)
                f.write(bytes_read)
        stop_apps(True)
    elif msg == MSG_KIND.REBOOT.value:
        os.system("reboot")
    elif msg == MSG_KIND.SHUTDOWN.value:
        os.system("shutdown now")
    elif msg == MSG_KIND.RESTART.value:
        stop_apps()        
    return None
#############################################


#############################################
def stop_apps(this_app = False):
    this_proc = None
    for proc in psutil.process_iter():
        pinfo = proc.as_dict(attrs=['pid', 'name'])
        procname = str(pinfo['name'])
        procpid = str(pinfo['pid'])
        if "python" in procname and procpid != str(os.getpid()):
            proc.kill()
        elif procpid == str(os.getpid()) and this_app is True:
            this_proc = proc
    if this_proc is not None:
        os._exit(0)
#############################################