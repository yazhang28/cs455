"""
Yao Zhang, yazhang@bu.edu
CS 455, Fall 2015
pa0 part2
extended_server.py
"""

from socket import *
import re
import time
import string

# variables
PROTOCOL_PHASE = ''
MEASUREMENT_TYPE = ''
NUMBER_OF_PROBES = ''
MESSAGE_SIZE = ''
SERVER_DELAY = ''

# n is counter for keeping track of probe increments
n = 0

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

    # CONNECTION SETUP PHASE

    # stores received message from client in received_msg
    received_msg = recv_end(connectionSocket)
    #print(received_msg)

    # converting client's message by first decoding the bytes into a string and storing it in str_msg
    str_msg = received_msg.decode(encoding='UTF-8')

    # splitting client string into tokens to log the information in the message
    tokens = [t for t in re.split(r"(\s)", str_msg)]
    # removes white space in token list
    tokens = [t for t in tokens if not t.isspace() and not t == ' ' and not t == '']
    #print(tokens)

    # checking format of client's string message
    csp_match = re.match(r"^([s][\s](tput|rtt)[\s][1-9][0-9]*[\s][1-9][0-9]*[\s](0|[1-9][0-9]*))$", str_msg)
    if csp_match != None:

        # variables for logging info
        NUMBER_OF_PROBES = int(tokens[2])
        SERVER_DELAY = int(tokens[4])
        
        # informing client to proceed to next phase
        connectionSocket.send(b'200 OK : Ready\n')
        
        # delaying time to send message to client
        #time.sleep(SERVER_DELAY)

    # if string failed to match csp format, check the first token, if 'm' go into measure phase
    elif tokens[0] == 'm':
        # n is incremented each time new probe is received 
        n += 1
        # closing connection if probe sequence numbers are not being incremented by 1        
        if int(tokens[1]) != n:
            connectionSocket.send(b'404 ERROR : Invalid Measurement Message\n')
            print('Closing connection...')
            connectionSocket.close()
            break
        else:
            # echoing message to client
            str_msg += '\n'
            #print(str_msg)
            received_msg = str_msg.encode(encoding='UTF-8')
            # delaying time to send message to client
            time.sleep(SERVER_DELAY)
            connectionSocket.send(received_msg)
            
        # restarting counter once it reaches max number of probes   
        if n == NUMBER_OF_PROBES:
            n = 0

    # if string failed to match the cases above, check the first token, if 't' go into connection termination phase
    # using length of tokens to check because client sends a string with no white spaces. So when server tokenizes the string it will be of len 1 and enter csp phase 
    
    elif len(tokens) == 1:
        print(len(tokens))
        if tokens[0] == 't':
            connectionSocket.send(b'200 OK : Closing Connection\n')
            print('closing connection...\n')
            connectionSocket.close()
        else:
            # sending error message if incorrect format and closes connection
            connectionSocket.send(b'404 ERROR: Invalid Connection Termination Message\n')
            print('Closing connection...')
            connectionSocket.close()
            break

    else:
        # if server fails to match string with csp, mp, and ctp last case is incorrect format of csp message
        connectionSocket.send(b'404 ERROR : Invalid Connection Setup Message\n')
        # closing connection socket for that particular client
        print('Closing connection...')
        connectionSocket.close()
        break

    
