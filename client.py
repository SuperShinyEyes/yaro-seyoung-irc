#Socket client example in python
from thread import *
import socket   #for sockets
import sys  #for exit
import os

from threading import Event

WELCOME_MSG = ""
CLOSE_MSG='/close'

def is_close(data):
    return data == CLOSE_MSG

def close():
    print("close()")
    speaker_socket.close()
    listener_socket.close()

def listen_thread(conn, exit_event):
    #Sending message to connected client
    conn.send('Welcome to the server. Type something and hit enter\n') #send only takes string

    #infinite loop so that function do not terminate and thread do not end.
    while True:

        #Receiving from client
        data = conn.recv(1024)
        reply = 'OK...' + data

        if not data or is_close(data):
            break

        print(data)

    #came out of loop
    close()

    # Better solution than this.
    #os._exit(1)
    print "exiting listen_thread"
    exit_event.set()

#create an INET, STREAMing socket
def create_socket():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        print('Failed to create socket')
        sys.exit()

    return s

def welcome():
    with open('welcome_msg') as f:
        print(f.read())

listener_socket = create_socket()
speaker_socket = create_socket()

print('Socket Created')

host = 'Aalto';
port = 8888;
# remote_ip = "10.100.57.138"
remote_ip = "localhost"

listener_socket.connect((remote_ip , port))
speaker_socket.connect((remote_ip , port))

e_event = Event()

start_new_thread(listen_thread ,(listener_socket, e_event))

welcome()
# print('Socket Connected to ' + host + ' on ip ' + remote_ip)

def input_thingie(conn, exit_event):
    try :
        message = raw_input(">>> ")
        #Set the whole string
        conn.sendall(message)
    except socket.error:
        #Send failed
        print('Send failed')
        close()
        #sys.exit()
        exit_event.set()
    print("leave input_thingie")

start_new_thread(input_thingie ,(speaker_socket, e_event))

#now keep talking with the client

    #Now receive data
try:
    print "waiting for event to be set"
    e_event.wait()
    print "event was set"

except KeyboardInterrupt:
    speaker_socket.sendall("/quit")
    close()
