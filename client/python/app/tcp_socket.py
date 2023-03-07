import select
import socket
from msg_handler import msg_handler
import time

my_socket = None

# hardcoded server address
serverHost = "192.168.0.1"
serverPort = 5000

#############################################
def create_socket(port):
    global my_socket, serverHost, serverPort
    
    host = ""
    # try to create a new socket with the given address
    try:
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        my_socket.bind((host, port))
    except socket.error as e:
        print("Something went wrong creating the socket. Exception: %s, retrying in 3 sec" % (e,))
        my_socket.close()
        time.sleep(3)
        port += 1
        create_socket(port)
#############################################    

#############################################
def connect_socket():
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
            readable, writeable, exceptional = select.select([my_socket], [], [my_socket])
            
            try:
                data = my_socket.recv(1).decode('utf-8') # Wait for, and then receive, incoming data
                send_data = msg_handler(data)
                if send_data:
                    my_socket.sendall(send_data)
            except socket.error as ConnectionResetError:
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
def send(data):
    global my_socket
    try:
        my_socket.sendall(data)
    except socket.error as e:
        print("Something went wrong reading data. Exception: %s" % (e,))
#############################################