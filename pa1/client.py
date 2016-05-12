"""
Yao Zhang, yazhang@bu.edu
CS 455, Fall 2015
pa0, part 1
client.py
"""

from socket import *

# method used to raise error if port number input by user is not an int
def port_error(port):
    if port < 0:
        raise AssertionError('Port number must be a nonnegative integer!')

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

# asking user for IP address and port number, catching error for invalid port number
while True:
    try:
        # asking user for serverName
        serverName = input('Please enter the hostname or IP address of the server: ')

        serverPort = int(input('Please enter the port number of the server: '))
        port_error(serverPort)
        
        # creating client socket
        clientSocket = socket(AF_INET, SOCK_STREAM)
        
        # initiating TCP connection between client and server
        print('Attempting to connect...')
        clientSocket.connect((serverName,serverPort))
        break
    except ValueError:
        print('Port must be a number!')
    except AssertionError as e:
        print('Invalid port number. Error: ' + str(e))
    except Exception as e:
        print('Unable to connect to server. Error Code: ' + str(e))

# asking user for message
message = input('Input message: ')

# adding end deliminter to mark end of string
message += '\n'
    
# converting client string into a byte object
msg_b = message.encode(encoding='UTF-8')

# sending client message 
clientSocket.send(msg_b)

# characters received by server is sent back and stored in csp_retrieved_msg
retrieved_msg = recv_end(clientSocket)

# converting server message into a string to print to screen
retrieved_str = retrieved_msg.decode(encoding='UTF-8')

# printing server message to screen
print(retrieved_str)
print('Closing client connection...')
clientSocket.close()
