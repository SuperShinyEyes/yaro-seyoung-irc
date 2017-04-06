#!/usr/bin/env python3

"""
Yaroslav Getman 473475
Seyoung Park 217495
17.03.2017

Our project is a simple IRC program implemented using Python3
"""

import socket
import sys
import threading
import logging
import select

logging.basicConfig(
    level=logging.DEBUG,
    format='(%(threadName)-10s) %(message)s',
)
"""
Constants for commands.
"""
CLOSE_MSG='/close'      # Server shuts down
QUIT_MSG = '/quit'      # Client leaves

class CloseYarong(Exception): pass

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
        self.threads_stop_event = threading.Event()

    def create_socket(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error:
            print('Failed to create socket')
            sys.exit()

        return s



class YarongSessionSocket(object):
    """
    Pair of socket for one server-client session.
    """
    def __init__(self, socket, address):
        self.socket = socket
        self.address = address[0]
        self.port = address[1]
