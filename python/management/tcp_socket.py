import select
import socket
from msg_handler import msg_handler
import time

my_socket = None

# hardcoded server address
serverHost = "192.168.0.1"
serverPort = 5000

nrOfRetries = 0
maxRetries = 10
#############################################
def create_socket(port):
    global my_socket, serverHost, serverPort, nrOfRetries
    
    nrOfRetries += 1
    if nrOfRetries > maxRetries:
        exit(1)    
    host = ""
    # try to create a new socket with the given address
    try:
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        my_socket.bind((host, port))
    except socket.error as e:
        print("Something went wrong. Exception: %s, retrying in 3 sec" % (e,))
        my_socket.close()
        time.sleep(3)
        port -= 1
        create_socket(port)
#############################################


#############################################
def connect_socket():
    global my_socket, serverHost, serverPort, nrOfRetries
    
    nrOfRetries += 1
    if nrOfRetries >= maxRetries:
        exit(1)
    
    # try to connect to the server
    try:
        my_socket.connect((serverHost, serverPort))
        print("You succesfully connected to the server.")
    except ConnectionRefusedError:
        print("Server does not want a connection. Make sure the server is running. retrying in 3 sec")
        time.sleep(3)
        connect_socket()
    except socket.error as e: 
        print("Something went wrong. Exception %s, retrying in 3 sec" % (e,))
        time.sleep(3)
        connect_socket()
#############################################


#############################################
def socket_receiver(port):
    global my_socket
    try:
        create_socket(port)
        # create server connection
        connect_socket()
        # keep doing this until the user wants to exit
        while True:
            # wait for 0.1 seconds for incoming data
            readable, writeable, exceptional = select.select([my_socket], [], [my_socket])
            
            # if there is a socket in the readable list (can only be s), read the data and print it
            try:
                data = my_socket.recv(4).decode('utf-8') # Wait for, and then receive, incoming data
                msg_handler(data, my_socket)
            except ConnectionResetError:
                print("Connection reset by peer: retrying in 3 sec")
                time.sleep(3)
                my_socket.close()
                create_socket(port)
                connect_socket()
            except socket.error as e:
                print("Something went wrong reading data. Exception: %s" % (e,))
    finally:
        my_socket.detach()
        my_socket.close()
#############################################


#############################################
def recvall(sock, n):
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data
#############################################


#############################################
def send(data):
    global my_socket
    try:
        my_socket.sendall(data)
    except socket.error as e:
        print("Something went wrong reading data. Exception: %s" % (e,))
#############################################
      
