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
        client_sockets = {client_socket: session_properties}
        '''
        self.client_sockets = {}
        self.num_nodes = num_nodes
        self.init_socket_bind()
        self.username = "ADMINISTRATOR"



    def init_socket_bind(self):
        """
        Creates a socket.
        Reuse the same adress for the socket.
        Bind to a port.
        """
        self.socket = self.create_socket()
        print('Socket created')
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
            for session_socket in self.client_sockets.values():
                if session_socket.socket is not sender:
                    session_socket.socket.sendall(msg.encode())
        else:
            '''
            Some client has left.
            Send a msg:
            "User A has left"
            '''
            for session_socket in self.client_sockets.values():
                session_socket.socket.sendall(msg.encode())

    def client_quits(self, client_socket, client_port):
        self.close_client_connection(client_socket)

        msg = "Client %s left the channel." % (client_port)
        self.propagate_msg(msg)
        print(msg)

    def close_client_connection(self, client_socket, close_all=False):
        client_socket.close()

        if not close_all:
            self.client_sockets.pop(client_socket, None)

    def close_all_client_sockets(self, ):
        for client_socket in self.client_sockets.keys():
            self.close_client_connection(client_socket, True)

        self.client_sockets = {}


    def add_client(self, session_socket):
        '''
        {socket:session_socket_object}
        The key-value system is for easy-finding for removing/closing
        a session.
        '''
        self.client_sockets[session_socket.socket] = session_socket

    def close(self):
        import time
        print("Closing....")
        self.close_all_client_sockets()
        self.socket.close()

    def is_client_quitting(self, msg):
        return msg == QUIT_CMD

    def is_client_setting_username(self, msg):
        return msg.split()[0] == NICKNAME_CMD

    def is_username_unique(self, username):
        client_usernames = [ss.username for ss in self.client_sockets.values()]
        return username not in client_usernames

    def set_client_username(self, msg, client_socket):
        username = msg.split()[1]
        reply = None

        if not self.is_username_unique(username):
            reply = "Username '{:s}' is already taken.'".format(username)
        else:
            self.client_sockets[client_socket].username = username
            reply = ACCEPT_REPLY.encode()

        client_socket.sendall(reply)

    def parse_client_message(self, client_socket):
        data = client_socket.recv(1024)
        client_username = self.client_sockets[client_socket].username

        if not data:
            print("Data broken")
            self.client_quits(client_socket, client_username)

        data = data.decode()

        if self.is_client_quitting(data):
            print("Client quits")
            self.client_quits(client_socket, client_username)

        elif self.is_client_setting_username(data):
            self.set_client_username(data, client_socket)

        else:
            msg = '@%s: %s\n' % (client_username, data)

            print("propagate")
            self.propagate_msg(msg, client_socket)

    def accept_client(self):
        print("New client")
        socket, address = self.socket.accept()

        '''
        Q. Do I need to set a socket as non-blocking?
        '''
        # Set socket to non-blocking mode.
        # Read "How to set timeout on python's socket recv method?":
        # http://stackoverflow.com/a/2721734/3067013
        # self.socket.setblocking(False)
        # speaker_socket.setblocking(False)
        (listner_ip, port) = address
        print('Connected with ' + address[0] + ':' + str(address[1]))
        session_socket = YarongSessionSocket(
            socket,
            address
        )
        self.add_client(session_socket)


    def listen(self):
        sockets = [self.socket]
        while True:

            '''
            According to Python3 doc:
            The return value is a triple of lists of objects that are ready:
            subsets of the first three arguments. When the time-out is reached
            without a file descriptor becoming ready, three empty lists are
            returned.
            '''
            rlist = sockets + list(self.client_sockets.keys())
            ready = select.select(rlist, [], [], self.listner_socket_timeout_in_sec)
            #Receiving from client
            if not ready[0]:
                print("No msg")
                continue

            socket = ready[0][0]
            if socket == self.socket:
                self.accept_client()

            else:
                self.parse_client_message(socket)

    def run(self):
        print("Server running...")

        try:
            self.listen()
        except KeyboardInterrupt:
            pass
        finally:
            self.close()


if __name__ == "__main__":
    yarong = YarongServer()
    yarong.run()
