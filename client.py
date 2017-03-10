#Socket client example in python

import socket   #for sockets
import sys  #for exit

#create an INET, STREAMing socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error:
    print('Failed to create socket')
    sys.exit()

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
s.connect((remote_ip , port))

print('Socket Connected to ' + host + ' on ip ' + remote_ip)

#Send some data to remote server
message = "GET / HTTP/1.1\r\n\r\n"

try :
    #Set the whole string
    s.sendall(message)
except socket.error:
    #Send failed
    print('Send failed')
    sys.exit()

print('Message send successfully')

while True:
    #Now receive data
    try :
        message = raw_input(">>> ")
        #Set the whole string
        s.sendall(message)
    except socket.error:
        #Send failed
        print('Send failed')
        sys.exit()


    reply = s.recv(4096)

    print(reply)
