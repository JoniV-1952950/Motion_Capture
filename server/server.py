import select
import socket
import sys, threading
from MSG_KIND import MSG_KIND
import time
import os
import socket_utils as su
import tracking
import cv2 as cv
#############################################


#############################################
STREAM = False
start_time = time.time()

aspect_ratio = 4/3
app_port = 5000
nrOfCams = 2

list_app_sockets = []
list_man_sockets = []

app_connections = 0
man_connections = 0

#############################################


#############################################
def thread_send_data():
    global STREAM
    while True:
        try: 
            str_msg = input()
            if str_msg == MSG_KIND.IMG.value:
                su.sendToOne(str_msg.encode('utf-8'), list_app_sockets[0])
            elif str_msg == MSG_KIND.MARKERS.value:
                su.sendToAll(str_msg.encode('utf-8'), list_app_sockets)
            elif str_msg == MSG_KIND.DEBUG.value:
                su.sendToAll(MSG_KIND.MARKERS.value.encode('utf-8'), list_app_sockets)
                su.sendToOne(MSG_KIND.IMG.value.encode('utf-8'), list_app_sockets[0])
            elif str_msg == MSG_KIND.LIST_CAMS.value:
                for i in range(len(list_app_sockets)):
                    if list_app_sockets[i] is None and list_man_sockets[i] is not None:
                        print("#", i, ":", list_man_sockets[i].getpeername()[0], "NONE", list_man_sockets[i].getpeername()[1])
                    elif list_app_sockets[i] is not None and list_man_sockets[i] is None:
                        print("#", i, ":", list_app_sockets[i].getpeername()[0], list_app_sockets[i].getpeername()[1], "NONE")
                    else:
                        print("#", i, ":", list_app_sockets[i].getpeername()[0], list_app_sockets[i].getpeername()[1], list_man_sockets[i].getpeername()[1])
            elif str_msg.startswith(MSG_KIND.INTRINSIC_CALIBRATE.value):
                STREAM = False
                camNr = int(str_msg[1:])
                if camNr > len(list_app_sockets):
                    print("--- This camera does not exist")
                su.sendToOne(MSG_KIND.INTRINSIC_CALIBRATE.value.encode('utf-8'), list_app_sockets[camNr])
            elif str_msg == MSG_KIND.EXTRINSIC_CALIBRATE.value:
                pass
            elif str_msg == MSG_KIND.STREAM.value:
                STREAM = True
            elif str_msg == MSG_KIND.END_STREAM.value:
                STREAM = False
            elif str_msg == MSG_KIND.REBOOT.value or str_msg == MSG_KIND.SHUTDOWN.value or str_msg == MSG_KIND.RESTART.value:
                su.sendToAll(str_msg.encode('utf-8'), list_man_sockets)
            elif str_msg.startswith(MSG_KIND.REBOOT.value) or str_msg.startswith(MSG_KIND.SHUTDOWN.value) or str_msg.startswith(MSG_KIND.RESTART.value):
                camNr = int(str_msg[4:])
                if camNr > len(list_app_sockets):
                    print("--- This camera does not exist")
                su.sendToOne(str_msg.encode('utf-8'), list_man_sockets[camNr])
            elif str_msg == MSG_KIND.UPDATE.value:
                su.sendToAll(str_msg.encode('utf-8'), list_man_sockets)
                su.sendPiFiles("C:/Users/joniv/Documents/master/MP/Motion_Capture/python", list_man_sockets)
            else:
                print("= Unknown command")
        except (KeyboardInterrupt, EOFError):
            STREAM = False
            su.sendToAll(MSG_KIND.RESTART.value.encode('utf-8'), list_man_sockets)
            os._exit(0)
#############################################


#############################################
def addrInList(addr, list):
    for i in range(len(list)):
        if list[i] is not None and list[i].getpeername()[0] == addr[0]:
            return i
    return -1
#############################################


#############################################
def handleConnect(sock):
    global list_app_sockets, list_man_sockets, app_connections, man_connections
    # accept and get socket
    (conn, addr) = sock.accept()
    print('= New connection established: ' + str(addr))
    # add socket to list of connections
    if addr[1] >= app_port:
        idx = addrInList(addr, list_man_sockets)
        if idx < 0:
            list_app_sockets.append(conn)
            list_man_sockets.insert(len(list_app_sockets)-1, None)
        else:
            list_app_sockets[idx] = conn
        app_connections += 1
    else:
        idx = addrInList(addr, list_app_sockets)
        if idx < 0:
            list_man_sockets.append(conn)
            list_app_sockets.insert(len(list_man_sockets)-1, None)
        else:
            list_man_sockets[idx] = conn
        man_connections += 1
#############################################


#############################################
def handleDisconnect(sock): 
    global list_app_sockets, list_man_sockets, app_connections, man_connections
    
    idx = -1
    # remove the client from the list of sockets
    if sock in list_app_sockets: 
        idx = list_app_sockets.index(sock)
        list_app_sockets[idx] = None
        app_connections -= 1
    if sock in list_man_sockets: 
        idx = list_man_sockets.index(sock)
        list_man_sockets[idx] = None
        man_connections -= 1
    if sock not in list_app_sockets and sock not in list_man_sockets and idx:
        list_app_sockets.pop(idx)
        list_man_sockets.pop(idx)
    print("= Disconnected: " + str(sock.getpeername()))
        
    # close the connection with the client
    sock.close()
    connectState()
#############################################


#############################################
def connectState():
    global sock_listen
    print("--- Waiting for all camera's to connect...")
    while True:
        readable, _, _ = select.select([sock_listen], [], [])
        for sock in readable: 
            handleConnect(sock)
        if app_connections >= nrOfCams and man_connections >= nrOfCams:
            print("--- All cameras connected!")
            return
#############################################


#############################################
if __name__ == "__main__":
    # server address
    host = "192.168.0.1"
    port = 5000

    # create a socket to listen for incoming connection requests
    try:
        sock_listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_listen.bind((host, port))
        sock_listen.listen(1)
    except socket.error as e:
        print("Something went wrong starting the server. Exception: %s" % (e, ))
        sys.exit(1)

    # create a list of sockets
    list_app_sockets = []
    list_man_sockets = []
    
    start_time = time.time()

    # Start a thread to read user input
    t = threading.Thread(target=thread_send_data, daemon=True)
    t.start()
    
    connectState()

    while True:
        # wait for incoming data
        readable, writeable, exceptional = select.select(list_app_sockets + list_man_sockets, [], list_app_sockets + list_man_sockets,0)
        if len(readable) < app_connections:
            continue
        for sock in readable: 
            try:
                kind = su.recvall(sock, 1)
                if kind is not None:
                    kind = kind.decode('utf-8')
                # no data probably means the connection is closed
                if not kind:
                    handleDisconnect(sock)
                elif kind == MSG_KIND.MARKERS.value:
                    if STREAM:
                        print("FPS: %.2f" % (1.0 / (time.perf_counter() - start_time)))
                        start_time = time.perf_counter()
                        su.sendToAll(kind.encode('utf-8'), list_app_sockets)
                    tracking.handle_incoming_2d_locs(sock, aspect_ratio)
                elif kind == MSG_KIND.IMG.value:
                    if STREAM:
                        print("FPS: %.2f" % (1.0 / (time.perf_counter() - start_time)), end='\r')
                        start_time = time.perf_counter()
                        su.sendToOne(kind.encode('utf-8'), list_app_sockets[0])
                    tracking.handle_incoming_img(sock, aspect_ratio)
                elif kind == MSG_KIND.TEXT.value:
                    len_data = int.from_bytes(su.recvall(sock, 4), 'little')
                    print("---", sock.getpeername()[0], ':', su.recvall(sock, len_data).decode('utf-8'))
                else:
                    continue
            # Client disconnected
            except ConnectionResetError:
                handleDisconnect(sock)
                continue
            except socket.error as e:
                print("Something went wrong receiving data. Exception: %s" % (e,))
                continue
#############################################