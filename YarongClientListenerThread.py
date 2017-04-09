import threading
from yarong import *

class YarongClientListenerThread(threading.Thread):
    """
    Waits for incoming messages from the server.
    """
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, *, daemon=None):
        super().__init__(group=group, target=target, name=name,
                         daemon=daemon)
        self.socket = kwargs["socket"]
        self.threads_stop_event = kwargs["event"]
        self.client = kwargs["client"]
        self.other_client_port = kwargs["other_client_port"]
        self.output = kwargs["output"]

    def is_session_close(self, data):
        return data == CLOSE_CMD

    def prompt_message(self, encoded_msg):
        logging.debug(encoded_msg.decode())

    def run(self):
        #Sending message to client_connected client
        # self.socket.sendall('Welcome to the server. Type something and hit enter\n'.encode())
        # self.output("Set start!")
        #infinite loop so that function do not terminate and thread do not end.
        while not self.threads_stop_event.is_set():
            ready = select.select([self.socket], [], [], self.client.listner_socket_timeout_in_sec)

            if self.threads_stop_event.is_set():
                '''
                Case: When a user sends "/quit".
                The client will close itself. However this loop might be not
                synchronized so it will call self.client.close() again.
                Thus "return".
                '''
                return

            #Receiving from client

            if not ready[0]:
                continue

            data = self.socket.recv(1024)

            if not data or self.is_session_close(data.decode()):
                print("Session closes")
                break

            data = data.decode()
            # self.prompt_message(data)
            if len(data) > 0 and data[-1] == "\n":
                data = data[:-1]
            self.output(data)

        #came out of loop
        self.client.close()
