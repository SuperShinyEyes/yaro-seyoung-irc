#Socket client example in python
from thread import *
import socket   #for sockets
import sys  #for exit


def listen_thread(conn):
    #Sending message to connected client
    conn.send('Welcome to the server. Type something and hit enter\n') #send only takes string

    #infinite loop so that function do not terminate and thread do not end.
    while True:

        #Receiving from client
        data = conn.recv(1024)
        reply = 'OK...' + data

        if not data:
            break

        print(data)

    #came out of loop
    conn.close()

#create an INET, STREAMing socket
def create_socket():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        print('Failed to create socket')
        sys.exit()

    return s

listening_socket = create_socket()
talking_socket = create_socket()
print('Socket Created')

host = 'Aalto';
port = 8888;
# remote_ip = "10.100.57.138"
remote_ip = "localhost"

# try:
#     remote_ip = socket.gethostbyname( host )
#
# except socket.gaierror:
#     #could not resolve
#     print 'Hostname could not be resolved. Exiting'
#     sys.exit()

#Connect to remote server

listening_socket.connect((remote_ip , port))
talking_socket.connect((remote_ip , port))
start_new_thread(listen_thread ,(listening_socket,))

print('Socket Connected to ' + host + ' on ip ' + remote_ip)

#Send some data to remote server
message = "GET / HTTP/1.1\r\n\r\n"

try :
    #Set the whole string
    talking_socket.sendall(message)
except socket.error:
    #Send failed
    print('Send failed')
    sys.exit()

print('Message send successfully')




#now keep talking with the client
while True:
    #Now receive data
    try :
        message = raw_input(">>> ")
        #Set the whole string
        talking_socket.sendall(message)
    except socket.error:
        #Send failed
        print('Send failed')
        sys.exit()




s.close()
