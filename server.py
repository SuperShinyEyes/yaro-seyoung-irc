#!/usr/bin/env python3
import socket
import sys
from _thread import *

class YarongServer(object):
    HOST = ''   # Symbolic name meaning all available interfaces
    PORT = 8888 # Arbitrary non-privileged port
    CLOSE_MSG='/close'
    QUIT_MSG = '/quit'

    """docstring for ."""
    def __init__(self, num_nodes=10):
        self.num_nodes = num_nodes
        '''
        client_sockets = {speaker_socket: (listener_socket, (address, port) )}
        '''
        self.client_sockets = {}
        self.socket = None
        self.initialize_socket()


    def initialize_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('Socket created')
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bind()
        print('Socket now listening')
        self.socket.listen(self.num_nodes)

    def bind(self):
        #Bind socket to local host and port
        try:
            self.socket.bind((YarongServer.HOST, YarongServer.PORT))
        except socket.error as e:
            print('Bind failed. Error Code : ' + str(e[0]) + ' Message ' + e[1])
            sys.exit()
        else:
            print('Socket bind complete')

#Start listening on socket



    def is_client_quitting(self, msg):
        return msg == YarongServer.QUIT_MSG

    def propagate_msg(self, msg, sender=None):
        if sender:
            for c in self.client_sockets.keys():
                if c is not sender:
                    self.client_sockets[c][0].sendall(msg.encode())
        else:
            '''
            Some client has left.
            Send a msg:
            "User A has left"
            '''
            for c in self.client_sockets.keys():
                self.client_sockets[c][0].sendall(msg.encode())

    def client_quits(self, speaker_socket, speaker_port):
        self.close_client_connection(speaker_socket)

        msg = "Client %s left the channel." % (speaker_port)
        self.propagate_msg(msg)
        print(msg)

    def close_client_connection(self, speaker_socket, close_all=False):
        speaker_socket.close()
        self.client_sockets[speaker_socket][0].close()
        if not close_all:
            self.client_sockets.pop(speaker_socket, None)

    def close_all_client_sockets(self, ):
        for (speaker_socket, v) in self.client_sockets.iteritems():
            (listener_socket, _) = v
            listener_socket.sendall(YarongServer.CLOSE_MSG.encode())
            self.close_client_connection(speaker_socket, True)

        self.client_sockets = {}


    #Function for handling client_sockets. This will be used to create threads
    def client_thread(self, client_socket):
        #Sending message to client_connected client
        client_socket.sendall('Welcome to the server. Type something and hit enter\n'.encode())
        client_port = self.client_sockets[client_socket][1][1]

        #infinite loop so that function do not terminate and thread do not end.
        while True:

            #Receiving from client
            data = client_socket.recv(1024)

            if not data or self.is_client_quitting(data):
                print("Client quits")

                break

            msg = '[%s]>>> %s' % (client_port, data)

            self.propagate_msg(msg, client_socket)

        #came out of loop
        self.client_quits(client_socket, client_port)


    def run(self):
        while True:
            try:
                #wait to accept a connection - blocking call
                conn_listener, addr_listener = self.socket.accept()
                conn_speaker, addr_speaker = self.socket.accept()
                print('Connected with ' + addr_listener[0] + ':' + str(addr_listener[1]))
                self.client_sockets[conn_speaker] = (conn_listener, addr_speaker)

                #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
                start_new_thread(self.client_thread ,(conn_speaker,))
            except KeyboardInterrupt:

                break

        print("Close server socket")

    def close(self):
        self.close_all_client_sockets()
        self.socket.close()


if __name__ == "__main__":
    yarong = YarongServer()
    yarong.run()
