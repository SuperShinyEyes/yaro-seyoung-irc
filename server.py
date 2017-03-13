import socket
import sys
from thread import *

HOST = ''   # Symbolic name meaning all available interfaces
PORT = 8888 # Arbitrary non-privileged port
CLOSE_MSG='/close'
'''
connections = {speaker_socket: (listener_socket, (address, port) )}
'''
connections = {}

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'Socket created'
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

#Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except socket.error , msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()

print 'Socket bind complete'

#Start listening on socket
s.listen(10)
print 'Socket now listening'

def is_client_quitting(msg):
    return msg == "/quit"

def propagate_msg(msg, sender=None):
    if sender:
        for c in connections.keys():
            if c is not sender:
                connections[c][0].sendall(msg)
    else:
        for c in connections.keys():
            connections[c][0].sendall(msg)

def user_quits(speaker_socket, speaker_port):
    close_client_connection(speaker_socket)

    msg = "Client %s left the channel." % (speaker_port)
    propagate_msg(msg)
    print(msg)

def close_client_connection(speaker_socket, close_all=False):
    speaker_socket.close()
    connections[speaker_socket][0].close()
    if not close_all:
        connections.pop(speaker_socket, None)

def close_all_client_connections():
    global connections
    for (speaker_socket, v) in connections.iteritems():
        (listener_socket, _) = v
        listener_socket.sendall(CLOSE_MSG)
        close_client_connection(speaker_socket, True)

    connections = {}


#Function for handling connections. This will be used to create threads
def client_thread(conn):
    #Sending message to connected client
    conn.send('Welcome to the server. Type something and hit enter\n') #send only takes string
    client_port = connections[conn][1][1]

    #infinite loop so that function do not terminate and thread do not end.
    while True:

        #Receiving from client
        data = conn.recv(1024)

        if not data or is_client_quitting(data):
            break

        msg = '[%s]>>> %s' % (client_port, data)

        propagate_msg(msg, conn)

    #came out of loop
    close_client_connection(conn, client_port)



#now keep speaker with the client
while 1:
    try:
        #wait to accept a connection - blocking call
        conn_listener, addr_listener = s.accept()
        conn_speaker, addr_speaker = s.accept()
        print 'Connected with ' + addr_listener[0] + ':' + str(addr_listener[1])
        connections[conn_speaker] = (conn_listener, addr_speaker)

        #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
        start_new_thread(client_thread ,(conn_speaker,))
    except KeyboardInterrupt:
        close_all_client_connections()
        break

s.close()
