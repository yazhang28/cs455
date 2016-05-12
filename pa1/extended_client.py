"""
Yao Zhang, yazhang@bu.edu
CS 455, Fall 2015
pa0, part 2
extended_client.py
"""

from socket import *
from base64 import b64encode
import re
import os
import time
import string

End= b'\n'
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

# method used to raise error if user entered incorrect string for continuing or ending experiment (thereby closing client and server connection)
def user_term_error(user_in):
    if user_in != 'yes' and user_in != 'no':
        raise AssertionError('Please enter yes or no.')

# method used to raise error if port number input by user is not an int
def port_error(port):
    if port < 0:
        raise AssertionError('Port number must be a nonnegative integer!')

# method used to raise error if measure type, number of probes or message size entered by user is not an integer when converting string to int
def csp_msg_error(np, ms, sd):
    try:
        int(np)
        int(ms)
        int(sd)
    except ValueError:
        raise AssertionError('<NUMBER OF PROBES>, <MESSAGE SIZE>, <SERVER DELAY> must be an integer!')

# method used to check if message received from server during connection setup phase is 404. returns True or False
def csp_404_error(csp):
    csp_tokens = tokenize(csp)
    return (csp_tokens[0] == '404')

# method used to tokenize string
def tokenize(string):
    tokens = [t for t in re.split(r"(\s)", string)]
    return tokens

# method used to ask user for connection setup message.
def get_fields():
    while True:
        try:
            # asking user for csp message                             
            print('Connection setup message in the following format: ')
            print('<MEASUREMENT TYPE><WS><NUMBER OF PROBES><WS><MESSAGE SIZE><WS><SERVER DELAY>')
            print()
            print('<MEASUREMENT TYPE> : rtt or tput')
            print('<NUMBER OF PROBES> : an integer value of at least 1 or greater')
            print('<MESSAGE SIZE> : an integer value of at least 1 or greater')
            print('<SERVER DELAY> : an integer.')
            print('<WS> : whitespace')
            print()

            SETUP = input('Input connection setup message: ')
        
            # splitting client string into tokens to log the information in the message and check for errors
            tokens = tokenize(SETUP)

            # checking format of user string. if input in the format: 'rtt 10 100 0' there will be a total of 7 tokens including whitespace
            # also checks for value type error 
            check1 = tokens[0]
            check2 = tokens[2]
            check3 = tokens[4]
            check4 = tokens[6]
            csp_msg_error(check2, check3, check4)

            # if user enters string of the correct format and of correct type, returns tokens 
            return tokens       
        except (ValueError, IndexError):
            print('String must adhere to format!')
        except AssertionError as e:
            print(str(e))
            print()

# assigning str for mp based on payload size specified
def assign_str(p):
    r_str = b64encode(os.urandom(p)).decode('utf-8')
    return r_str
    
# method used to get rtt or throughput of probes
def get_rtt_tput(payload, probes):
    
    # variable used to calculate Round Trip Time and Throughput
    MEAN_RTT = 0
    MEAN_TPUT = 0
    TPUT = 0

    # sending probe messages from 1 to up to NUMBER_OF_PROBES variable
    for np in range(1, probes + 1):
        # assigning current time to start
        start = time.time()

        # creating and connecting client socket 
        clientSocket = socket(AF_INET, SOCK_STREAM)

        # assigning random string of size PAYLOAD
        random_str = assign_str(PAYLOAD)
        
        # mp_client_string in the format: 'm 1 <random_str>\n'
        mp_client_string = 'm ' + str(np) + ' ' + random_str + '\n'

        # converting client string into a byte object
        mp_client_msg = mp_client_string.encode(encoding='UTF-8')
        
        clientSocket.connect((serverName,serverPort))
        # sending probe message
        clientSocket.send(mp_client_msg)
        
        # probe message is recieved from server and stored in mp_retrieved_ms
        #mp_retrieved_msg = clientSocket.recv(1024)
        mp_retrieved_msg = recv_end(clientSocket)
        #print(mp_retrieved_msg)
        
        # calulating rtt and throughput
        elapsed = (time.time()-start)
        MEAN_RTT += elapsed

        try: 
            TPUT = payload/elapsed
            MEAN_TPUT += TPUT
        except ZeroDivisionError:
            print()

        # printing RTT or TPUT for probe depending on what measure type user specified in CSP
        if MEASURE_TYPE == 'rtt':
            print('Probe ' + str(np) + ' Round Trip Time: ' + str(elapsed) + ' seconds')
        else:
            print('Time to receive: ' + str(elapsed) , ' seconds')
            print('Probe ' + str(np) + ' throughput: ' + str(TPUT) + ' B/sec')
            
    # calculating mean RTT and mean throughput
    MEAN_RTT /= int(NUMBER_OF_PROBES)
    MEAN_TPUT /= int(NUMBER_OF_PROBES)

    # printing mean RTT or mean TPUT for probe depending on what measure type user specified in CSP
    if MEASURE_TYPE == 'rtt':
        print('Mean Round Trip time of ' + str(NUMBER_OF_PROBES) + ' probes of ' + str(PAYLOAD) + ' bytes each : ' + str(MEAN_RTT) + ' seconds')
    if MEASURE_TYPE == 'tput':
        print('Mean Throughput of ' + str(NUMBER_OF_PROBES) + ' probes of ' + str(PAYLOAD) + ' bytes each : ' + str(MEAN_TPUT) + ' B/s')
    print()

# first while loop allows for multiple experiments to be run without having to recompile and restart tcpclient.py
while True:
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

    # on successful input string, retrieve the fields to log info
    fields = get_fields()
    # logging in info
    MEASURE_TYPE = fields[0]
    NUMBER_OF_PROBES = int(fields[2])
    PAYLOAD = int(fields[4])
    SERVER_DELAY = int(fields[6])
    
    ###Connection Setup Phase (CSP)###

    # sending the string sentence through client's socket into TCP connection for connection setup
    csp_client_str = 's ' + MEASURE_TYPE + ' ' + str(NUMBER_OF_PROBES) + ' ' + str(PAYLOAD) + ' ' + str(SERVER_DELAY) + '\n'
    
    # converting client string into a byte object
    csp_client_msg = csp_client_str.encode(encoding='UTF-8')

    # sending client message 
    clientSocket.send(csp_client_msg)

    # characters received by server is sent back and stored in csp_retrieved_msg
    #csp_retrieved_msg = clientSocket.recv(1024)
    csp_retrieved_msg = recv_end(clientSocket)

    # converting server message into a string to print to screen
    csp_retrieved_str = csp_retrieved_msg.decode(encoding='UTF-8')

    # printing server message to screen
    print(csp_retrieved_str)

    ###Measurement Phase (MP)###
    
    # checking for csp 404 error
    csp_404 = csp_404_error(csp_retrieved_str)
    
    if csp_404 == False:
        get_rtt_tput(PAYLOAD, NUMBER_OF_PROBES)

    ####Connection Termination Phase (CTP)####

    while True:
        try:
            # asking user if they want to start a new experiment and handles invalid user input
            # if yes, go back into outer while loop
            
            new_experiment = input('Would you like to start a new experiment? Enter yes or no: ')
            user_term_error(new_experiment)
            break                    
        except AssertionError as e:
            print(str(e))
            
    '''        
    if user attempts to close server connection after connection on server side already
    closed (due to CSP 404 error), closes connection for them without having user
    input CTP message (to prevent ConnectionResetError)
    '''
    if csp_404 == True:
        if new_experiment == 'yes':
            print('Server connection closed.')
            print(csp_retrieved_str)
            print('Please restart server before starting a new experiment.')
        else:
            print('Server connection closed. ')
            print(csp_retrieved_str)
            print('Closing client connection...')
            clientSocket.close()
            break 
        
    # the case where server connection is still open but user no longer wants to conduct experiments
    else:
        if new_experiment == 'no':
            # has user enter t for termination
            user_term = input('To end connection, enter t: ')

            # tokenizes user input and fetches the first token because server uses len(tokens) == 1 to proceed to ctp
            terminate = tokenize(user_term)[0]
            
            clientSocket = socket(AF_INET, SOCK_STREAM)
            clientSocket.connect((serverName, serverPort))

            tcp_client_string = terminate + '\n'
            
            # converting client string into a byte object
            tcp_client_msg = tcp_client_string.encode(encoding='UTF-8')
            
            # sending terminate message
            clientSocket.send(tcp_client_msg)

            ctp_retrieved_msg = recv_end(clientSocket)
            #ctp_retrieved_msg = clientSocket.recv(1024)
            # retrieving server message and converts it into a string to print to screen
            ctp_retrieved_str = ctp_retrieved_msg.decode(encoding='UTF-8')
            print(ctp_retrieved_str)
        
            # closing TCP connection
            print('Closing client connection...')
            clientSocket.close()

            # breaking out of outer while loop ending all interaction with client
            break
