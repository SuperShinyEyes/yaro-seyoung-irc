#!/usr/bin/env python3

"""
Yaroslav Getman 473475
Seyoung Park 217495
17.03.2017

Our project is a simple IRC program implemented using Python3
"""

import socket
import sys
import select

import random
random.seed()

"""
Constants for commands.
"""
CLOSE_CMD='/close'      # Server shuts down
QUIT_CMD = '/quit'      # Client leaves
NICKNAME_CMD = '/nickname'

ACCEPT_REPLY = '/accept'


'''
Debug constants
'''
DEBUG_MODE = True

def debug(msg):
    if DEBUG_MODE:
        print(msg)

class CloseYarong(Exception):
    pass
    '''
    Used in client to end the session.
    It's raised by CLOSE_CMD sent by server.
    '''

class UsernameSettingError(Exception):
    pass
    '''
    Used in client to end the session.
    It's raised by CLOSE_CMD sent by server.
    '''

class YarongNode(object):
    """
    Parent class for server and client
    """
    def __init__(self, host='', host_ip='localhost', host_port=8888, timeout_in_sec=2):
        self.host = host
        self.host_ip = host_ip
        self.host_port = host_port
        self.listner_socket_timeout_in_sec = timeout_in_sec
        self.close_delay_in_sec = timeout_in_sec + 1
        self.socket = None
        self.username = None

    def create_socket(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error:
            print('Failed to create socket')
            sys.exit()

        return s

    def close(self):
        pass

    def listen(self):
        pass

    def run(self):
        pass




class YarongSessionSocket(object):
    """
    Pair of socket for one server-client session.
    """
    def __init__(self, socket, address):
        self.socket = socket
        self.address = address[0]
        self.port = address[1]
        self.username = self.generate_username()

    def generate_username(self):
        return "USER-{:d}".format(random.randint(1000000, 9999999))
