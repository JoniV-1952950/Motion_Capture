import os
import psutil
import sys
sys.path.append("/home/pi/Motion_Capture/python/")
from MSG_KIND import MSG_KIND

# # # # # # # # # # # # 
def msg_handler(msg):
    print(msg)
    if msg == MSG_KIND.UPDATE.value:
        stop_app()
        os.chdir("/home/pi/Motion_Capture")
        os.system("git pull")
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

