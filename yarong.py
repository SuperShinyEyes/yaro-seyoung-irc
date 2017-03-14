class YarongObject(object):
    """docstring for Yarong."""
    def __init__(self, arg):

        self.arg = arg

    def create_socket(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error:
            print('Failed to create socket')
            sys.exit()

        return s
