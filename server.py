import socket
import sys
import thread

HOST = ''   # Symbolic name meaning all available interfaces
PORT = 8888 # Arbitrary non-privileged port

class ConnectionLife():
    def __init__(self):
        self.dead = False

connection_life = ConnectionLife()

connections = [] # Store all connectioins.
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'Socket created'

#Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except socket.error , msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()

print 'Socket bind complete'

#Start listening on socket
s.listen(10)
print 'Socket now listening'

#Function for handling connections. This will be used to create threads
def clientthread(conn, life):
    #Sending message to connected client
    conn.send('Welcome to the server. Type something and hit enter\n') #send only takes string

    #infinite loop so that function do not terminate and thread do not end.
    while not life.dead:

        #Receiving from client
        data = conn.recv(1024)
        reply = 'OK...' + data
        if not data:
            break

        for c in connections:
            if c is not conn:
                c.sendall(reply)

        # conn.sendall(reply)
    print("#came out of loop")
    #came out of loop
    conn.close()

def close_all(socket, connections):
    # for c in connections:
    #     print("close conn")
    #     c.close()
    # thread.interrupt_main()
    socket.close()

#now keep talking with the client
while 1:
    try:
        #wait to accept a connection - blocking call
        conn, addr = s.accept()
        print 'Connected with ' + addr[0] + ':' + str(addr[1])
        connections.append(conn)
        #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
        thread.start_new_thread(clientthread ,(conn,connection_life,))
    except KeyboardInterrupt:
        connection_life.dead = True
        print("KeyboardInterrupt detected")
        break
    # finally:
print("close socket")

close_all(s, connections)
# s.close()
