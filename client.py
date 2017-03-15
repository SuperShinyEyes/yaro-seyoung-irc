#!/usr/bin/env python3
from yarong import *
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




if __name__ == "__main__":
    yarongClient = YarongClient()
    yarongClient.run()
