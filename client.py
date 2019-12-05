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
        exit()

def sendMessage(socket, respType, payload):
     response = json.dumps({'type': respType, 'payload': payload})
     length = len(payload.encode('utf-8'))
     message = str(length) + '_' + response
     socket.sendall(message.encode())

def getBoards(socket):
    msgType = 'GET_BOARDS'
    sendMessage(socket, msgType, '')
    
def getMessages(boardNumber):
    


serverAddress = sys.argv[1]
serverPort = sys.argv[2]
clientSocket = socket(AF_INET, SOCK_STREAM)
try:
     clientSocket.connect((serverAddress, int(serverPort)))
except:
     print("Could not open requested server and port")
     exit()
clientSocket.settimeout(10000)
getBoards(clientSocket)
response = parseResponse(clientSocket)
respType = response[0]
respPayload = response[1]
boards = respPayload
if(respType == 'ERROR'):
    print (respPayload)
    exit()
i = 1
for board in respPayload:
    print(str(i) + '.', board)
    i += 1

while True:
    userInput = input('Enter a board number to view lastest 100 messages from that board. Enter POST to post a message. Enter REFRESH to refresh list of boards. Enter QUIT to close the client\n')
    
    if(userInput.isdigit):
        getMessages(userInput)
    elif(userInput.upper() == 'POST'):
        pass
    elif(userInput.upper() == 'REFRESH'):
        pass
    elif(userInput.upper() == 'QUIT'):
        pass
    else:
        print('invalid input try again')
        pass

clientSocket.close()

