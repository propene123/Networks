import sys
import json
from socket import *

def parseResponse(socket):
    try:
        sentence = socket.recv(1024).decode();
        splitSentence = sentence.split('_', 1)
        length = int(splitSentence[0])
        message = splitSentence[1]
        messageLength = len(message.encode('utf-8'))
        if(messageLength < length):
            message += socket.recv(length - messageLength).decode()
        obj = json.loads(message)
        return (obj['type'], obj['payload'])
    except (IndexError, ValueError):
        return ('ERROR', 'Server sent malformed response')
    except (json.JSONDecodeError, KeyError):
        return ('ERROR', 'Server sent malformed response')
    except timeout:
        print('Server timed out')
        socket.close()
        exit()

def sendMessage(socket, msg):
     length = len(msg.encode('utf-8'))
     message = str(length) + '_' + msg
     try:
        socket.sendall(message.encode())
     except ConnectionError:
        print('Server is down... Exiting Client')
        socket.close()
        exit()


def getBoards(socket):
    msgType = 'GET_BOARDS'
    msgJson = json.dumps({'type': msgType})
    sendMessage(socket, msgJson)
    
def getMessages(socket, boardNumber):
    msgType = 'GET_MESSAGES'
    msgJson = json.dumps({'type': msgType, 'board': boards[boardNumber-1]})
    sendMessage(socket, msgJson)


def postMessage(socket, boardNumber, title, content):
    msgType = 'POST_MESSAGE'
    msgJson = json.dumps({'type': msgType, 'board': boards[boardNumber-1], 'title': title, 'msg': content})
    sendMessage(socket, msgJson)

def refresh(socket):
    getBoards(socket)
    response = parseResponse(socket)
    respType = response[0]
    respPayload = response[1]
    boards = respPayload
    if(respType == 'ERROR'):
        print (respPayload)
        socket.close()
        exit()
    i = 1
    for board in respPayload:
        print(str(i) + '.', board.replace('_', ' '))
        i += 1
    return boards


serverAddress = sys.argv[1]
serverPort = sys.argv[2]
clientSocket = socket(AF_INET, SOCK_STREAM)
try:
     clientSocket.connect((serverAddress, int(serverPort)))
except:
     print("Could not open requested server and port")
     exit()
clientSocket.settimeout(10)
boards = refresh(clientSocket)
while True:
    userInput = input('Enter a board number to view lastest 100 messages from that board. Enter POST to post a message. Enter REFRESH to refresh list of boards. Enter QUIT to close the client\n')
    if(userInput.isdigit()):
        index = int(userInput)
        if(index < 1 or index > len(boards)):
            print('Please enter a number on the list')
            continue
        getMessages(clientSocket, index)
        response = parseResponse(clientSocket)
        if(response[0] == 'ERROR'):
            print(response[1])
        else:
            i = 0
            for title in response[1]['titles']:
                print('*****************************************************************************************')
                print(title)
                print(response[1]['messages'][i])
                i+=1
            print('*****************************************************************************************')

    elif(userInput.upper() == 'POST'):
        userInput = input('Enter number of board to post to\n')
        if(not userInput.isdigit()):
            print('Input is not a number')
            continue
        index = int(userInput)
        if(index < 1 or index > len(boards)):
            print('Please enter a number on the list')
            continue
        title = input('Enter message title\n')
        msgText = input('Enter message content\n')
        postMessage(clientSocket, index, title, msgText)
        response = parseResponse(clientSocket)
        if(response[0] == 'ERROR'):
            print(response[1])
        else:
            print(response[1])
    elif(userInput.upper() == 'REFRESH'):
        boards = refresh(clientSocket)
    elif(userInput.upper() == 'QUIT'):
        break
    else:
        print('invalid input try again')

clientSocket.close()

