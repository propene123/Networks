import sys
import json
from socket import *


# function takes a socket and returns a tuple of server
# response type and server response payload
def parseResponse(socket):
    try:
        sentence = socket.recv(1024).decode()
        # split response into expected length in bytes
        # and json payload as string
        splitSentence = sentence.split('_', 1)
        length = int(splitSentence[0])
        message = splitSentence[1]
        # check json payload is of expected length
        messageLength = len(message.encode('utf-8'))
        if(messageLength < length):
            # receive rest of json payload
            message += socket.recv(length - messageLength).decode()
        # parse json into dictionary
        obj = json.loads(message)
        return (obj['type'], obj['payload'])
    # if the response is malformed inform the user
    except (IndexError, ValueError):
        return ('ERROR', 'Server sent malformed response')
    except (json.JSONDecodeError, KeyError):
        return ('ERROR', 'Server sent malformed response')
    # inform the user if a timeout occurred
    except timeout:
        print('Server timed out')
        socket.close()
        exit()
    # inform the user if the socket failed during the operation
    except (ConnectionError, OSError):
        print('The connection has been closed by the server')
        socket.close()
        exit()


# function takes a socket and json paylaod as string
# and encodes the message before sending it
def sendMessage(socket, msg):
    # calculate length of json string in bytes
    length = len(msg.encode('utf-8'))
    # prepend json string with length
    message = str(length) + '_' + msg
    try:
        # send the message
        socket.sendall(message.encode())
    # notify user if the server is down
    except (ConnectionError, OSError):
        print('Server is down... Exiting Client')
        socket.close()
        exit()


# function takes a socket and sends a GET_BOARDS message
def getBoards(socket):
    msgType = 'GET_BOARDS'
    # create json payload as a string
    msgJson = json.dumps({'type': msgType})
    # pass msg type and payload to sendMessage
    sendMessage(socket, msgJson)


# function takes a socket and sends a GET_MESSAGES message
def getMessages(socket, boardNumber):
    msgType = 'GET_MESSAGES'
    # create json payload as a string
    msgJson = json.dumps({'type': msgType, 'board': boards[boardNumber - 1]})
    # pass msg type and payload to sendMessage
    sendMessage(socket, msgJson)


# function takes a socket and sends a GET_MESSAGES message
def postMessage(socket, boardNumber, title, content):
    msgType = 'POST_MESSAGE'
    # create json payload as a string
    msgJson = json.dumps({'type': msgType,
                          'board': boards[boardNumber - 1],
                          'title': title,
                          'msg': content})
    # pass msg type and payload to sendMessage
    sendMessage(socket, msgJson)


# function takes a socket and sends a GET_BOARDS message
# parses the response and parses it before printing a list
# of boards to the screen. And returns new list of boards
def refresh(socket):
    getBoards(socket)
    response = parseResponse(socket)
    respType = response[0]
    respPayload = response[1]
    boards = respPayload
    # check if the response is an error
    if(respType == 'ERROR'):
        # print the error and exit the client
        print(respPayload)
        socket.close()
        exit()
    # print list of board names numbered in ascending order
    i = 1
    for board in respPayload:
        print(str(i) + '.', board.replace('_', ' '))
        i += 1
    # return the new list of boards
    return boards


# read command line args as server address and port
serverAddress = sys.argv[1]
serverPort = sys.argv[2]
# create socket object
clientSocket = socket(AF_INET, SOCK_STREAM)
# attempt to establish a connection to server
try:
    clientSocket.connect((serverAddress, int(serverPort)))
except BaseException:
    # if connection failed print to user and exit client
    print("Could not open requested server and port")
    exit()
# ensure socket timesout after 10 seconds
clientSocket.settimeout(10)
# get list of boards
boards = refresh(clientSocket)
# main client loop
while True:
    # prompt user for input
    userInput = input(
        'Enter a board number to view lastest 100 messages from that board.'
        'Enter POST to post a message. Enter REFRESH to refresh list of boa'
        'rds. Enter QUIT to close the client\n')
    # if input is digit check its a valid board entry
    if(userInput.isdigit()):
        index = int(userInput)
        if(index < 1 or index > len(boards)):
            print('Please enter a number on the list')
            continue
        # get messages from the selected board
        getMessages(clientSocket, index)
        response = parseResponse(clientSocket)
        # if response is an error print it
        if(response[0] == 'ERROR'):
            print(response[1])
        else:
            i = 0
            # print titles with message content beneath title
            for title in response[1]['titles']:
                print(
                    '*********************************************************'
                    '********************************')
                print(title.replace('_', ' '))
                print(response[1]['messages'][i])
                i += 1
            print(
                '*********************************************************'
                '********************************')
    # if user enters POST prompt for post info
    elif(userInput.upper() == 'POST'):
        userInput = input('Enter number of board to post to\n')
        # check the board number is an actual number
        if(not userInput.isdigit()):
            print('Input is not a number')
            continue
        index = int(userInput)
        # check the board number is valid
        if(index < 1 or index > len(boards)):
            print('Please enter a number on the list')
            continue
        # prompt user for message title and contents
        title = input('Enter message title\n')
        msgText = input('Enter message content\n')
        # send the message to the client
        postMessage(clientSocket, index, title, msgText)
        # wait for resposne
        response = parseResponse(clientSocket)
        # if reponse is an error print to user
        if(response[0] == 'ERROR'):
            print(response[1])
        else:
            # print success
            print(response[1])
    # if user enters REFRESH get new list of boards
    elif(userInput.upper() == 'REFRESH'):
        boards = refresh(clientSocket)
    # if user enters QUIT break out of main loop and exit
    elif(userInput.upper() == 'QUIT'):
        break
    # print if user input is not a vaild option
    else:
        print('invalid input try again')

clientSocket.close()
