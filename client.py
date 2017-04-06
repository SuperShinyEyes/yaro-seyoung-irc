"""
Yaroslav Getman 473475
Seyoung Park 217495
17.03.2017

Our project is a simple IRC program implemented using Python3
"""
#!/usr/bin/env python3
from yarong import *

class YarongClient(YarongNode):

    """IRC client"""
    def __init__(self, host='', host_ip='localhost', host_port=8888, timeout_in_sec=2):
        super(YarongClient, self).__init__(host, host_ip, host_port, timeout_in_sec)

        self.socket = None
        # self.input_socket = None
        self.init_socket_connect()

    def init_socket_connect(self):
        self.socket = self.create_socket()
        # self.input_socket = self.create_socket()

        self.socket.connect((self.host_ip , self.host_port))
        # self.input_socket.connect((self.host_ip , self.host_port))


    def is_close(self,data):
        return data == CLOSE_MSG

    def close(self):
        import time
        self.threads_stop_event.set()
        print("Closing....")
        time.sleep(self.close_delay_in_sec)


        self.socket.close()
        print("All sockets closed")

    def quit(self):
        self.socket.sendall(QUIT_MSG.encode())
        self.threads_stop_event.set()
        self.close()


    def welcome(self):
        import os
        dir_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(dir_path, 'welcome_msg')
        with open(file_path) as f:
            print(f.read())


    def run(self):
        self.welcome()
        thread_kwargs = {
        "socket":self.socket, "event": self.threads_stop_event,
        "client": self, "other_client_port": self.host_port
        }
        thread = YarongClientListenerThread(kwargs=thread_kwargs)
        thread.start()

        # input_thread_kwargs = {
        # "socket":self.socket, "event": self.threads_stop_event,
        # "client": self
        # }
        # input_thread = YarongClientInputThread(kwargs=input_thread_kwargs)
        # input_thread.start()

        try:
            print("waiting for event to be set")
            # Blocks the main thread until event is set.
            self.threads_stop_event.wait()
            print("event was set")

        except KeyboardInterrupt:
            self.quit()
        finally:
            print("Over")



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

    def is_session_close(self, data):
        return data == CLOSE_MSG

    def prompt_message(self, encoded_msg):
        logging.debug(encoded_msg.decode())

    def is_user_input(self, data_source):
        logging.debug(sys.stdin)
        logging.debug(data_source)
        return data_source == sys.stdin

    def is_quitting(self, msg):
        return msg == QUIT_MSG

    def parse_user_input(self):
        message = sys.stdin.readline().strip()
        if self.is_quitting(message):
            self.client.quit()
            return

        try :
            #Set the whole string
            self.socket.sendall(message.encode())
        except socket.error:
            #Send failed
            print('Send failed')
            self.client.close()

    def parse_message(self):
        data = self.socket.recv(1024)

        if not data or self.is_session_close(data.decode()):
            logging.debug("Session closes")
            self.client.close()
        else:
            self.prompt_message(data)

    def run(self):
        #Sending message to client_connected client
        self.socket.sendall('Welcome to the server. Type something and hit enter\n'.encode())

        #infinite loop so that function do not terminate and thread do not end.
        while not self.threads_stop_event.is_set():
            ready = select.select([self.socket, sys.stdin], [], [], self.client.listner_socket_timeout_in_sec)

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
                # logging.debug("No data nor input")
                continue

            data_source = ready[0][0]

            # logging.debug("data or input")
            if self.is_user_input(data_source):
                # logging.debug("User typed something")
                self.parse_user_input()

            else:
                self.parse_message()
            # # logging.debug("Got msg")
            # data = self.socket.recv(1024)
            #
            # if not data or self.is_session_close(data.decode()):
            #     print("Session closes")
            #     break
            #
            # self.prompt_message(data)

        #came out of loop
        self.client.close()



# class YarongClientInputThread(threading.Thread):
#     """
#     Listens to user inputs.
#     """
#     def __init__(self, group=None, target=None, name=None,
#                  args=(), kwargs=None, *, daemon=None):
#         super().__init__(group=group, target=target, name=name,
#                          daemon=daemon)
#         self.socket = kwargs["socket"]
#         self.threads_stop_event = kwargs["event"]
#         self.client = kwargs["client"]
#
#     def is_quitting(self, msg):
#         return msg == QUIT_MSG
#
#     def run(self):
#         while not self.threads_stop_event.is_set():
#
#             # Non-blocking user input mechanism
#             # Read "Keyboard input with timeout in Python":
#             # http://stackoverflow.com/a/2904057/3067013
#             user_input_sources, _, _ = select.select(
#                 [sys.stdin],    # Reads
#                 [],             # Writes
#                 [],             # Exceptions
#                 self.client.listner_socket_timeout_in_sec
#             )
#             if not user_input_sources:
#                 continue
#
#             message = user_input_sources[0].readline().strip()
#
#             if self.is_quitting(message):
#                 self.client.quit()
#                 break
#
#             try :
#                 #Set the whole string
#                 self.socket.sendall(message.encode())
#             except socket.error:
#                 #Send failed
#                 print('Send failed')
#                 self.client.close()
#
#         print("leave input_thingie")


if __name__ == "__main__":
    yarongClient = YarongClient()
    yarongClient.run()
