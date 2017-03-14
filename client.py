#!/usr/bin/env python3

#Socket client example in python
from _thread import *
import socket   #for sockets
import sys  #for exit
import os
import select
from threading import Event
import logging

WELCOME_MSG = ""
CLOSE_MSG='/close'

logging.basicConfig(
    level=logging.DEBUG,
    format='%(message)s',
)

def is_close(data):
    return data == CLOSE_MSG

def close_client(exit_event):
    print("close_client(exit_event)")
    speaker_socket.close()
    listener_socket.close()
    print("exiting listen_thread")
    exit_event.set()

def close_client_by_client(exit_event):
    speaker_socket.sendall("/quit".encode())
    close_client(exit_event)

def listen_thread(conn, exit_event):
    #Sending message to connected client
    # conn.sendall('Welcome to the server. Type something and hit enter\n') #send only takes string

    #infinite loop so that function do not terminate and thread do not end.
    while True:

        #Receiving from client
        data = conn.recv(1024)

        if not data or is_close(data.decode()):
            break

        logging.debug(data.decode())

    #came out of loop
    close_client(exit_event)

    # Better solution than this.
    #os._exit(1)


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
    while not exit_event.is_set():
        try :
            message = input(">>> ")
            #Set the whole string
            conn.sendall(message.encode())
        except socket.error:
            #Send failed
            print('Send failed')
            close_client(exit_event)
            #sys.exit()
    print("leave input_thingie")

start_new_thread(input_thingie ,(speaker_socket, e_event))

#now keep talking with the client

    #Now receive data
try:
    print("waiting for event to be set")
    e_event.wait()
    print("event was set")

except KeyboardInterrupt:
    close_client_by_client(e_event)
