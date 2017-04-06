"""
Yaroslav Getman 473475
Seyoung Park 217495
17.03.2017

Our project is a simple IRC program implemented using Python3
"""
#!/usr/bin/env python3
from yarong import *

class YarongServer(YarongNode):

    """IRC server."""
    def __init__(self, num_nodes=6, host='', host_ip='localhost', host_port=8888, timeout_in_sec=2):
        super(YarongServer, self).__init__(host, host_ip, host_port, timeout_in_sec)
        '''
        client_sockets = {speaker_socket: socket_pair}
        '''
        self.client_sockets = {}
        self.sockets = {}
        self.client_threads = []
        self.socket = None
        self.num_nodes = num_nodes
        self.init_socket_bind()



    def init_socket_bind(self):
        """
        Creates a socket.
        Reuse the same adress for the socket.
        Bind to a port.
        """
        self.socket = self.create_socket()
        print('Socket created')
        self.sockets[self] = self.socket

        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bind()
        print('Socket now listening')
        self.socket.listen(self.num_nodes) # Defines how many sockets can be connected

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
            User A sends a message.
            Server delivers the message to other clients, but not A.
            '''
            for pair in self.client_sockets.values():
                if pair.speaker_socket is not sender:
                    pair.socket.sendall(msg.encode())
        else:
            '''
            Some client has left.
            Send a msg:
            "User A has left"
            '''
            for pair in self.client_sockets.values():
                pair.socket.sendall(msg.encode())

    def client_quits(self, speaker_socket, speaker_port):
        self.close_client_connection(speaker_socket)

        msg = "Client %s left the channel." % (speaker_port)
        self.propagate_msg(msg)
        print(msg)

    def close_client_connection(self, speaker_socket, close_all=False):
        speaker_socket.close()
        self.client_sockets[speaker_socket].socket.close()
        #
        if not close_all:
            self.client_sockets.pop(speaker_socket, None)

    def close_all_client_sockets(self, ):
        for (speaker_socket, pair) in self.client_sockets.items():
            self.close_client_connection(speaker_socket, True)

        self.client_sockets = {}


    def add_client(self, socket_pair):
        self.client_sockets[socket_pair.speaker_socket] = socket_pair

        thread = YarongServerClientListenerThread(
            name=str(socket_pair.port),
            kwargs={
                "socket":socket_pair.speaker_socket,
                "port":socket_pair.port,
                "event":self.threads_stop_event,
                "server":self
            }
        )
        thread.start()


    def run(self):
        print("Server running...")
        accept_thread = YarongServerAcceptListenerThread(
            name="accept_thread",
            kwargs={
                "event": self.threads_stop_event,
                "server": self
            }
        )
        accept_thread.start()
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



class YarongServerAcceptListenerThread(threading.Thread):
    """
    Waits for new clients.
    """
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

            '''
            According to Python3 doc:
            The return value is a triple of lists of objects that are ready:
            subsets of the first three arguments. When the time-out is reached
            without a file descriptor becoming ready, three empty lists are
            returned.
            '''
            ready = select.select([self.server.socket], [], [], self.server.listner_socket_timeout_in_sec)
            #Receiving from client
            # logging.debug("Listening accept")
            if not ready[0]:
                continue

            socket, address = self.server.socket.accept()
            speaker_socket, speaker_address = self.server.socket.accept()
            '''
            Q. Do I need to set a socket as non-blocking?
            '''
            # Set socket to non-blocking mode.
            # Read "How to set timeout on python's socket recv method?":
            # http://stackoverflow.com/a/2721734/3067013
            # self.socket.setblocking(False)
            # speaker_socket.setblocking(False)
            (listner_ip, port) = address
            logging.debug('Connected with ' + address[0] + ':' + str(address[1]))
            socket_pair = YarongSessionSocket(
                socket,
                address,
                speaker_socket,
                speaker_address
            )
            self.server.add_client(socket_pair)



class YarongServerClientListenerThread(threading.Thread):
    """
    Listens to incoming messages from clients.
    """
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

            if self.threads_stop_event.is_set():
                """
                When server shuts itself down, quit.
                """
                return

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


if __name__ == "__main__":
    yarong = YarongServer()
    yarong.run()
