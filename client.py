#!/usr/bin/env python3

import socket
import sys          # For user inputs
import select       # For non-blocking
import threading
import logging      # For Debugging in threads

CLOSE_MSG='/close'

logging.basicConfig(
    level=logging.DEBUG,
    format='%(message)s',
)

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


    def listen(self):
        #Sending message to client_connected client
        self.socket.sendall('Welcome to the server. Type something and hit enter\n'.encode())

        #infinite loop so that function do not terminate and thread do not end.
        while not self.threads_stop_event.is_set():
            ready = select.select([self.socket], [], [], self.client.listner_socket_timeout_in_sec)
            #Receiving from client

            if ready[0]:
                data = self.socket.recv(1024)
            else:
                # logging.debug(ready)
                # logging.debug("Not ready yet")
                continue

            if not data or self.is_session_close(data.decode()):
                print("Session closes")

                break

            msg = '[%s]>>> %s' % (self.other_client_port, data.decode())

            logging.debug(msg)

        #came out of loop
        self.client.close_client()

    def run(self):
        logging.debug("Running Listner thread")
        self.listen()


class YarongClientInputThread(threading.Thread):
    """docstring for ."""
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, *, daemon=None):
        super().__init__(group=group, target=target, name=name,
                         daemon=daemon)
        self.socket = kwargs["socket"]
        self.threads_stop_event = kwargs["event"]
        self.client = kwargs["client"]

    def get_user_input(self):
        while not self.threads_stop_event.is_set():

            # Non-blocking user input mechanism
            # Read "Keyboard input with timeout in Python":
            # http://stackoverflow.com/a/2904057/3067013
            user_input_sources, _, _ = select.select(
            [sys.stdin],
            [],
            [],
            self.client.listner_socket_timeout_in_sec
            )
            if not user_input_sources:
                continue

            message = user_input_sources[0].readline().strip()
            try :
                # message = input(">>> ")
                #Set the whole string
                self.socket.sendall(message.encode())
            except socket.error:
                #Send failed
                print('Send failed')
                self.client.close_client()

        print("leave input_thingie")

    def run(self):
        logging.debug("Running Input thread")
        self.get_user_input()

class YarongClient(object):
    """docstring for ."""
    def __init__(self, host='', host_ip='localhost', host_port=8888, listener_timeout_in_sec=2):

        self.host = host
        self.host_ip = host_ip
        self.host_port = host_port
        self.listner_socket_timeout_in_sec = listener_timeout_in_sec
        self.close_delay_in_sec = listener_timeout_in_sec + 1

        self.listener_socket = self.create_socket()
        self.input_socket = self.create_socket()
        self.threads_stop_event = threading.Event()
        self.establish_socket_connections()

    def establish_socket_connections(self):
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


    #create an INET, STREAMing socket
    def create_socket(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error:
            print('Failed to create socket')
            sys.exit()

        return s

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

if __name__ == "__main__":
    yarongClient = YarongClient()
    yarongClient.run()
