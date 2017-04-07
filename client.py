"""
client.py
Created by
    Yaroslav Getman 473475
    Seyoung Park 217495
on 6th.April.2017.

Our project is a simple IRC program implemented using Python 3.x
For cloud server connection, connect to 178.62.226.63(DigitalOcean VPS):

    python3 client.py 178.62.226.63

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
        return msg == QUIT_CMD

    def parse_user_input(self):
        message = sys.stdin.readline().strip()
        if self.is_quitting(message):
            self.quit(kill_loop=True)
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
            self.close(kill_loop=True)

    def parse_message(self):
        data = self.socket.recv(1024)

        if self.is_close_message(data):
            self.show_system_alert("Shutdown by server. See you again!")
            self.close(kill_loop=True)
        else:
            self.prompt_message(data)

    def is_close_message(self, data):
        return not data or data.decode() == CLOSE_CMD

    def close(self, kill_loop=False):
        '''
        Passive session termination by server.
        Raise halts the while loop in listen()
        '''
        self.socket.close()
        print("All sockets closed")
        if kill_loop:
            raise CloseYarong

    def quit(self, kill_loop=False):
        '''
        Active session termination by user.
        '''
        self.socket.sendall(QUIT_CMD.encode())
        self.close(kill_loop=kill_loop)


    def welcome(self):
        import os
        dir_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(dir_path, 'welcome_msg')
        with open(file_path) as f:
            print(f.read())

    def show_system_alert(self, msg):
        print("\n[[[[!!ALERT!!]]]]\n{:s}\n".format(msg))

    def is_valid_username(self, username):
        if len(username) >= 5 and username.isalnum():
            return True

        reply_too_short = "Too short. At least 5 characters."
        reply_not_alphanumeric = "Accepts only alphabets and numbers"

        if len(username) < 5 and not username.isalnum():
            reply = reply_too_short + " " + reply_not_alphanumeric
        elif not username.isalnum():
            reply = reply_not_alphanumeric
        elif len(username) < 5:
            reply = reply_too_short

        self.show_system_alert(reply)

        return False


    def set_username(self):
        instruction = ">>> Type in your username in lowercase alphanumeric. Must be at least 5 characters.\n"
        while True:
            username = input(instruction)
            if not self.is_valid_username(username):
                continue

            self.send_message("/nickname {:s}".format(username))
            debug("Receiving reply...")
            data = self.socket.recv(1024)

            if not data:
                raise UsernameSettingError

            reply = data.decode()
            if reply == ACCEPT_REPLY:
                debug("Accepted")
                return username
            else:
                debug("Not Accepted")
                print(reply)


    def listen(self):
        print("Welcome {:s}! Start a conversation!".format(self.username))
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
        '''
        First set username.
        Then start a session
        '''
        self.welcome()
        try:
            self.username = self.set_username()
        except KeyboardInterrupt:
            self.quit()
        except UsernameSettingError:
            print("There was an error when setting a username.")
            return
        except CloseYarong:
            return
        else:
            try:
                self.listen()
            except KeyboardInterrupt:
                self.quit()
            except CloseYarong:
                pass
            finally:
                print("Over")


def is_cloud_mode():
    mode = input("Do you want to go cloud(DigitalOcean)?(y/n)")
    return mode in ["y", 'Y', 'yes', "YES"]


def main():
    yarongClient = None
    ip = "localhost"
    if is_cloud_mode():
        print("Okay, taking you to DigitalOcean(178.62.226.63:8888)")
        ip = '178.62.226.63'
    else:
        print("Running on localhost:8888")


    # Is server running?
    try:
        yarongClient = YarongClient(host_ip=ip)
    except ConnectionRefusedError:
        print("The server is not running.")
    else:
        yarongClient.run()

if __name__ == "__main__":
    main()
