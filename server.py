#!/usr/bin/env python3
import socket
import sys
# from _thread import *
import threading
import logging
import select

logging.basicConfig(
    level=logging.DEBUG,
    format='(%(threadName)-10s) %(message)s',
)

CLOSE_MSG='/close'
QUIT_MSG = '/quit'

class YarongServerThread(threading.Thread):
    """docstring for ."""
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, *, daemon=None):
        super().__init__(group=group, target=target, name=name,
                         daemon=daemon)
        self.client_socket = kwargs["socket"]
        self.threads_stop_event = kwargs["event"]
        self.server = kwargs["server"]
        self.client_port = kwargs["port"]

    def is_client_quitting(self, msg):
        return msg == QUIT_MSG


    def listen(self):
        #Sending message to client_connected client
        self.client_socket.sendall('Welcome to the server. Type something and hit enter\n'.encode())

        #infinite loop so that function do not terminate and thread do not end.
        while not self.threads_stop_event.is_set():
            ready = select.select([self.client_socket], [], [], self.server.listner_socket_timeout_in_sec)
            #Receiving from client

            if ready[0]:
                data = self.client_socket.recv(1024)
            else:
                logging.debug(ready)
                logging.debug("Not ready yet")
                continue

            if not data or self.is_client_quitting(data.decode()):
                print("Client quits")

                break

            msg = '[%s]>>> %s' % (self.client_port, data.decode())

            logging.debug("propagate")
            self.server.propagate_msg(msg, self.client_socket)

        #came out of loop
        self.server.client_quits(self.client_socket, self.client_port)

    def run(self):
        logging.debug("Running")
        self.listen()




class YarongServer(object):

    """docstring for ."""
    def __init__(self, num_nodes=10, host='', port=8888, listener_timeout_in_sec=2):
        self.num_nodes = num_nodes
        self.host = host
        self.port = port
        self.listner_socket_timeout_in_sec = listener_timeout_in_sec
        self.close_delay_in_sec = listener_timeout_in_sec + 1
        '''
        client_sockets = {speaker_socket: (listener_socket, (address, port) )}

        '''
        self.client_sockets = {}
        self.client_threads = []
        self.socket = None
        self.initialize_socket()
        self.threads_stop_event = threading.Event()


    def initialize_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Set socket to non-blocking mode.
        # Read "How to set timeout on python's socket recv method?":
        # http://stackoverflow.com/a/2721734/3067013
        # self.socket.setblocking(0)

        print('Socket created')
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bind()
        print('Socket now listening')
        self.socket.listen(self.num_nodes)

    def bind(self):
        #Bind socket to local host and port
        try:
            self.socket.bind((self.host, self.port))
        except socket.error as e:
            print('Bind failed. Error Code : ' + str(e[0]) + ' Message ' + e[1])
            sys.exit()
        else:
            print('Socket bind complete')

#Start listening on socket




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
        listener_socket = self.client_sockets[speaker_socket][0]
        listener_socket.close()

        if not close_all:
            self.client_sockets.pop(speaker_socket, None)

    def close_all_client_sockets(self, ):
        for (speaker_socket, v) in self.client_sockets.items():
            (listener_socket, _) = v
            listener_socket.sendall(CLOSE_MSG.encode())
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
                listener_socket, listener_address = self.socket.accept()
                speaker_socket, speaker_address = self.socket.accept()
                speaker_socket.setblocking(False)
                (listner_ip, listener_port) = listener_address
                print('Connected with ' + listener_address[0] + ':' + str(listener_address[1]))
                self.client_sockets[speaker_socket] = (listener_socket, speaker_address)

                #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
                thread_dict = {"socket":speaker_socket, "port":listener_port, "event":self.threads_stop_event, "server":self}
                thread = YarongServerThread(name=str(listener_port),kwargs=thread_dict)
                thread.start()
                # self.client_threads.append(thread)
                # start_new_thread(self.client_thread ,(speaker_socket,))
            except KeyboardInterrupt:
                break

        print("Close server socket")
        self.close()

    def close(self):
        import time
        self.threads_stop_event.set()
        print("Closing....")
        time.sleep(self.close_delay_in_sec)
        self.close_all_client_sockets()
        self.socket.close()



if __name__ == "__main__":
    yarong = YarongServer()
    yarong.run()
