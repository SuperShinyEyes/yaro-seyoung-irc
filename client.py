"""
client.py
Created by
    Yaroslav Getman 473475
    Seyoung Park 217495
on 6th.April.2017.

Our project is a simple IRC program implemented using Python 3.x
"""
#!/usr/bin/env python3
from yarong import *
import sys

class YarongClient(YarongNode):

    """IRC client"""
    def __init__(self, host='', host_ip='localhost', host_port=8888, timeout_in_sec=2):
        super(YarongClient, self).__init__(host, host_ip, host_port, timeout_in_sec)
        self.init_socket_connect()

    def init_socket_connect(self):
        self.socket = self.create_socket()
        self.socket.connect((self.host_ip , self.host_port))

    def prompt_message(self, encoded_msg):
        print(encoded_msg.decode())

    def is_user_input(self, data_source):
        return data_source == sys.stdin

    def is_quitting(self, msg):
        return msg == QUIT_MSG

    def parse_user_input(self):
        message = sys.stdin.readline().strip()
        if self.is_quitting(message):
            self.quit()
            return
        else:
            self.send_message(message)

    def send_message(self, message):
        try :
            #Set the whole string
            self.socket.sendall(message.encode())
        except socket.error:
            #Send failed
            print('Send failed')
            self.close()

    def parse_message(self):
        data = self.socket.recv(1024)

        if self.is_close_message(data):
            self.close()
        else:
            self.prompt_message(data)

    def is_close_message(self, data):
        return not data or data.decode() == CLOSE_MSG

    def close(self):
        '''
        Close Yarong session.
        Raise halts the while loop in listen()
        '''
        self.socket.close()
        print("All sockets closed")
        raise CloseYarong

    def quit(self):
        self.socket.sendall(QUIT_MSG.encode())
        self.close()


    def welcome(self):
        import os
        dir_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(dir_path, 'welcome_msg')
        with open(file_path) as f:
            print(f.read())

    def set_username(self):
        while True:
            username = input(">>> Type in your username in lowercase alphanumeric. Must be at least 5 characters.\n")
            self.send_message(message)
            ready = select.select([self.socket, sys.stdin], [], [], self.listner_socket_timeout_in_sec)

            if not ready[0]:
                # print("No data nor input")
                continue

            data_source = ready[0][0]

            if self.is_user_input(data_source):
                self.parse_user_input()
            else:
                self.parse_message()


    def listen(self):

        while True:
            ready = select.select([self.socket, sys.stdin], [], [], self.listner_socket_timeout_in_sec)

            if not ready[0]:
                # print("No data nor input")
                continue

            data_source = ready[0][0]

            if self.is_user_input(data_source):
                self.parse_user_input()
            else:
                self.parse_message()


    def run(self):
        self.welcome()

        try:
            self.listen()
        except KeyboardInterrupt:
            self.quit()
        except CloseYarong:
            pass
        finally:
            print("Over")



def main():
    yarongClient = None
    if len(sys.argv) > 1:
        ip = sys.argv[1]
        yarongClient = YarongClient(host_ip=ip)
    else:
        yarongClient = YarongClient()
    yarongClient.run()

if __name__ == "__main__":
    main()
