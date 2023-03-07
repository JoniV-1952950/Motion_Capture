import socket
import os

#############################################
def sendToAll(msg_bytes, list_sockets):
    # for every socket in the list except the first one (the listening socket) send the message
    for sendSocket in list_sockets:
        try:
            sendSocket.sendall(msg_bytes)     
        except socket.error as e:
            print("Something went wrong sending the data to other users. Exception: %s" % (e,))
#############################################


#############################################
def sendToOne(msg_bytes, sock):
    try:
        sock.sendall(msg_bytes)     
    except socket.error as e:
        print("Something went wrong sending the data to other users. Exception: %s" % (e,))
#############################################


#############################################        
def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data
#############################################


#############################################
def sendPiFiles(basepath, list_sockets):
    os.chdir(basepath)
    filenames = []
    for path, subdirs, files in os.walk(basepath):
        for name in files:
            filenames.append(path.split('\\')[-1] + '/' + name)

    sendToAll(len(filenames).to_bytes(4, 'little'), list_sockets)
    for filename in filenames:
        sendFile(filename, list_sockets)        
#############################################


#############################################
def sendFile(filename, list_sockets):
    filesize = os.path.getsize(filename)
    msg = f"{filename};{filesize}"
    sendToAll(len(msg).to_bytes(4, 'little') + msg.encode('utf-8'), list_sockets)
    with open(filename, "rb") as f:
        sendToAll(f.read(), list_sockets)
#############################################