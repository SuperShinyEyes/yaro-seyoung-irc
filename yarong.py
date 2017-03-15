#!/usr/bin/env python3
import socket
import sys
import threading
import logging
import select

logging.basicConfig(
    level=logging.DEBUG,
    format='(%(threadName)-10s) %(message)s',
)

CLOSE_MSG='/close'
QUIT_MSG = '/quit'



class YarongNode(object):
    """docstring for Yarong."""
    def __init__(self, host='', host_ip='localhost', host_port=8888, listener_timeout_in_sec=2):
        self.host = host
        self.host_ip = host_ip
        self.host_port = host_port
        self.listner_socket_timeout_in_sec = listener_timeout_in_sec
        self.close_delay_in_sec = listener_timeout_in_sec + 1
        self.threads_stop_event = threading.Event()

    def create_socket(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error:
            print('Failed to create socket')
            sys.exit()

        return s



class YarongServer(YarongNode):

    """docstring for ."""
    def __init__(self, num_nodes=10, host='', host_ip='localhost', host_port=8888, listener_timeout_in_sec=2):
        super(YarongServer, self).__init__(host, host_ip, host_port, listener_timeout_in_sec)
        '''
        client_sockets = {speaker_socket: (listener_socket, (address, port) )}
        client_sockets = {speaker_socket: socket_pair}

        '''
        self.client_sockets = {}
        self.client_threads = []
        self.socket = None
        self.num_nodes = num_nodes
        self.init_socket_bind()



    def init_socket_bind(self):
        self.socket = self.create_socket()
        print('Socket created')
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bind()
        print('Socket now listening')
        self.socket.listen(self.num_nodes)

    def bind(self):
        #Bind socket to local host and port
        try:
            self.socket.bind((self.host, self.host_port))
        except socket.error as e:
            print('Bind failed. Error Code : ' + str(e[0]) + ' Message ' + e[1])
            sys.exit()
        else:
            print('Socket bind complete')


    def propagate_msg(self, msg, sender=None):
        if sender:
            '''

            '''
            for pair in self.client_sockets.values():
                if pair.speaker_socket is not sender:
                    pair.listener_socket.sendall(msg.encode())
        else:
            '''
            Some client has left.
            Send a msg:
            "User A has left"
            '''
            for pair in self.client_sockets.values():
                pair.listener_socket.sendall(msg.encode())

    def client_quits(self, speaker_socket, speaker_port):
        self.close_client_connection(speaker_socket)

        msg = "Client %s left the channel." % (speaker_port)
        self.propagate_msg(msg)
        print(msg)

    def close_client_connection(self, speaker_socket, close_all=False):
        speaker_socket.close()
        self.client_sockets[speaker_socket].listener_socket.close()

        if not close_all:
            self.client_sockets.pop(speaker_socket, None)

    def close_all_client_sockets(self, ):
        for (speaker_socket, v) in self.client_sockets.items():
            (listener_socket, _) = v
            listener_socket.sendall(CLOSE_MSG.encode())
            self.close_client_connection(speaker_socket, True)

        self.client_sockets = {}


    def add_client(self, socket_pair):
        self.client_sockets[socket_pair.speaker_socket] = socket_pair

        thread = YarongServerClientListenerThread(
            name=str(socket_pair.listener_port),
            kwargs={
                "socket":socket_pair.speaker_socket,
                "port":socket_pair.listener_port,
                "event":self.threads_stop_event,
                "server":self
            }
        )
        thread.start()


    def run(self):
        print("Server running...")
        accept_listener_thread = YarongServerAcceptListenerThread(
            name="accept_listener_thread",
            kwargs={
                "event": self.threads_stop_event,
                "server": self
            }
        )
        accept_listener_thread.start()
        try:
            #wait to accept a connection - blocking call
            self.threads_stop_event.wait()
        except KeyboardInterrupt:
            pass

        self.close()


    def close(self):
        import time
        self.threads_stop_event.set()
        print("Closing....")
        time.sleep(self.close_delay_in_sec)
        self.close_all_client_sockets()
        self.socket.close()


class YarongClient(YarongNode):

    """docstring for ."""
    def __init__(self, host='', host_ip='localhost', host_port=8888, listener_timeout_in_sec=2):
        super(YarongClient, self).__init__(host, host_ip, host_port, listener_timeout_in_sec)

        self.listener_socket = None
        self.input_socket = None
        self.init_socket_connect()

    def init_socket_connect(self):
        self.listener_socket = self.create_socket()
        self.input_socket = self.create_socket()

        self.listener_socket.connect((self.host_ip , self.host_port))
        self.input_socket.connect((self.host_ip , self.host_port))


    def is_close(self,data):
        return data == CLOSE_MSG

    def close_client(self):
        import time
        self.threads_stop_event.set()
        print("Closing....")
        time.sleep(self.close_delay_in_sec)

        self.input_socket.close()
        self.listener_socket.close()
        print("All sockets closed")

    def close_client_by_client(self):
        self.input_socket.sendall("/quit".encode())
        self.close_client()


    def welcome(self):
        with open('welcome_msg') as f:
            print(f.read())


    def run(self):
        listener_thread_kwargs = {
        "socket":self.listener_socket, "event": self.threads_stop_event,
        "client": self, "other_client_port": self.host_port
        }
        listener_thread = YarongClientListenerThread(kwargs=listener_thread_kwargs)
        listener_thread.start()

        input_thread_kwargs = {
        "socket":self.input_socket, "event": self.threads_stop_event,
        "client": self
        }
        input_thread = YarongClientInputThread(kwargs=input_thread_kwargs)
        input_thread.start()

        try:
            print("waiting for event to be set")
            self.threads_stop_event.wait()
            print("event was set")

        except KeyboardInterrupt:
            self.close_client_by_client()
        finally:
            print("Over")


class YarongSocketPair(object):
    def __init__(self, listener_socket, listener_address, speaker_socket, speaker_address):
        self.listener_socket = listener_socket
        self.listener_address = listener_address[0]
        self.listener_port = listener_address[1]
        self.speaker_socket = speaker_socket
        self.speaker_address  = speaker_address[0]
        self.speaker_port  = speaker_address[1]



class YarongServerAcceptListenerThread(threading.Thread):
    """docstring for ."""
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, *, daemon=None):
        super().__init__(group=group, target=target, name=name,
                         daemon=daemon)
        self.threads_stop_event = kwargs["event"]
        self.server = kwargs["server"]

    def run(self):
        logging.debug("Run!")
        #infinite loop so that function do not terminate and thread do not end.
        while not self.threads_stop_event.is_set():
            ready = select.select([self.server.socket], [], [], self.server.listner_socket_timeout_in_sec)
            #Receiving from client

            if not ready[0]:
                continue

            listener_socket, listener_address = self.server.socket.accept()
            speaker_socket, speaker_address = self.server.socket.accept()
            '''
            Q. Do I need to set a socket as non-blocking?
            '''
            # Set socket to non-blocking mode.
            # Read "How to set timeout on python's socket recv method?":
            # http://stackoverflow.com/a/2721734/3067013
            # self.socket.setblocking(False)
            # speaker_socket.setblocking(False)
            (listner_ip, listener_port) = listener_address
            logging.debug('Connected with ' + listener_address[0] + ':' + str(listener_address[1]))
            socket_pair = YarongSocketPair(
                listener_socket,
                listener_address,
                speaker_socket,
                speaker_address
            )
            self.server.add_client(socket_pair)



class YarongServerClientListenerThread(threading.Thread):
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


    def run(self):
        #Sending message to client_connected client
        self.client_socket.sendall('Welcome to the server. Type something and hit enter\n'.encode())

        #infinite loop so that function do not terminate and thread do not end.
        while not self.threads_stop_event.is_set():
            ready = select.select(
                [self.client_socket],
                [],
                [],
                self.server.listner_socket_timeout_in_sec
            )

            if not ready[0]:
                continue

            data = self.client_socket.recv(1024)

            if not data or self.is_client_quitting(data.decode()):
                print("Client quits")
                break

            msg = '#%s:\n%s\n' % (self.client_port, data.decode())

            logging.debug("propagate")
            self.server.propagate_msg(msg, self.client_socket)

        #came out of loop
        self.server.client_quits(self.client_socket, self.client_port)



class YarongClientListenerThread(threading.Thread):
    """docstring for ."""
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, *, daemon=None):
        super().__init__(group=group, target=target, name=name,
                         daemon=daemon)
        self.socket = kwargs["socket"]
        self.threads_stop_event = kwargs["event"]
        self.client = kwargs["client"]
        self.other_client_port = kwargs["other_client_port"]

    def is_session_close(self, data):
        return data == CLOSE_MSG

    def prompt_message(self, encoded_msg):
        logging.debug(encoded_msg.decode())

    def run(self):
        #Sending message to client_connected client
        self.socket.sendall('Welcome to the server. Type something and hit enter\n'.encode())

        #infinite loop so that function do not terminate and thread do not end.
        while not self.threads_stop_event.is_set():
            ready = select.select([self.socket], [], [], self.client.listner_socket_timeout_in_sec)
            #Receiving from client

            if not ready[0]:
                continue

            data = self.socket.recv(1024)

            if not data or self.is_session_close(data.decode()):
                print("Session closes")
                break

            self.prompt_message(data)

        #came out of loop
        self.client.close_client()



class YarongClientInputThread(threading.Thread):
    """docstring for ."""
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, *, daemon=None):
        super().__init__(group=group, target=target, name=name,
                         daemon=daemon)
        self.socket = kwargs["socket"]
        self.threads_stop_event = kwargs["event"]
        self.client = kwargs["client"]

    def run(self):
        while not self.threads_stop_event.is_set():

            # Non-blocking user input mechanism
            # Read "Keyboard input with timeout in Python":
            # http://stackoverflow.com/a/2904057/3067013
            user_input_sources, _, _ = select.select(
                [sys.stdin],    # Reads
                [],             # Writes
                [],             # Exceptions
                self.client.listner_socket_timeout_in_sec
            )
            if not user_input_sources:
                continue

            message = user_input_sources[0].readline().strip()
            try :
                #Set the whole string
                self.socket.sendall(message.encode())
            except socket.error:
                #Send failed
                print('Send failed')
                self.client.close_client()

        print("leave input_thingie")
