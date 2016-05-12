"""
Yao Zhang, yazhang@bu.edu
CS 455, Fall 2015
pa0 part1
server.py
"""

from socket import *

# method used to raise error if port number input by user is not an int or less than 0
def port_error(port):
    if port < 0:
        raise AssertionError('Port number must be a nonnegative integer')

End = b'\n'
def recv_end(the_socket):
    total_data=[];data=''
    while True:
            data=the_socket.recv(8192)
            if End in data:
                total_data.append(data[:data.find(End)])
                break
            total_data.append(data)
            if len(total_data)>1:
                #check if end_of_data was split
                last_pair=total_data[-2]+total_data[-1]
                if End in last_pair:
                    total_data[-2]=last_pair[:last_pair.find(End)]
                    total_data.pop() 
                    break
    return b''.join(total_data)

# asking user for port number and catching error for invalid port number
while True:
    try:
        serverPort = int(input('Please enter the port number of the server: '))
        port_error(serverPort)
        break
    except ValueError:
        print('Port must be a number!')
    except AssertionError as e:
        print('Invalid port number. Error: ' + str(e))

# creating TCP socket 'welcoming socket' for handshake
serverSocket = socket(AF_INET,SOCK_STREAM)

# associating server port number with the socket
serverSocket.bind(('',serverPort))

# listening for TCP connection requests from client 
# max number of queued connection is at least 1
serverSocket.listen(1)

print ('The server is ready to receive')
while 1:

    # when client establishes connection, creates a new socket in the server dedicated to this particular client
    # now client and server can send bytes to each other
    connectionSocket, addr = serverSocket.accept()

    # stores received message from client in received_msg
    #received_msg = connectionSocket.recv(1024)
    message = recv_end(connectionSocket)

    # converting server message into a string to print to screen
    received_str = message.decode(encoding='UTF-8')

    # adding end deliminter to mark end of string
    received_str += '\n'

    # converting client string into a byte object
    received_msg = received_str.encode(encoding='UTF-8')
    
    # echoing message to client
    connectionSocket.send(received_msg)

    
