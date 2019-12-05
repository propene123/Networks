import sys
import json
import os
from socket import *
from threading import Thread

def getBoards(socket):
     boards = [x for x in os.listdir(os.path.join(os.getcwd(), 'board')) if os.path.isdir(os.path.join(os.path.join(os.getcwd(), 'board'), x))]
     msgJson = json.dumps({'type': 'GET_BOARDS_RESPONSE', 'payload': boards})
     length = len(msgJson.encode('utf-8'))
     message = str(length) + '_' + msgJson
     socket.sendall(message.encode())




def getMessages(socket, board):
     boardPath = os.path.join(os.getcwd(), 'board', board)
     payload = ''
     respType = ''
     if (not os.path.exists(boardPath) or not os.path.isdir(boardPath)):
          payload = 'board does not exist'
          respType = 'ERROR'
     else:
          payload = [os.path.splitext(x)[0] for x in os.listdir(boardPath) if os.path.isfile(os.path.join(boardPath, x))]
          payload.sort(reverse = True)
          respType = 'GET_MESSAGES_RESPONSE'
     response = json.dumps({'type':respType, 'payload': payload})
     length = len(response.encode('utf-8'))
     message = str(length) + '_' + response
     socket.sendall(message.encode())


def postMessage(socket):
     pass

def handleMessage(msg, socket):
     obj = json.loads(msg)
     if(obj['type'] == 'GET_BOARDS'):
          getBoards(socket)
     if(obj['type'] == 'GET_MESSAGES'):
          getMessages(socket, obj['board'])


def clientThread(socket):
     while True:
          sentence = socket.recv(1024).decode();
          if not sentence:
               break
          splitSentence = sentence.split('_', 1)
          length = int(splitSentence[0])
          message = splitSentence[1]
          messageLength = len(message.encode('utf-8'))
          if(messageLength < length):
               message += socket.recv(length - messageLength).decode()
          handleMessage(message, socket)
     socket.close()

serverAddress = sys.argv[1]
serverPort = sys.argv[2]
serverSocket = socket(AF_INET,SOCK_STREAM)
try:
     serverSocket.bind((serverAddress, int(serverPort)))
except:
     print("Could not open requested server and port")
     exit()
serverSocket.settimeout(0.2)
serverSocket.listen(5)  
while True:
     try:
          (connectionSocket, addr) = serverSocket.accept()
          x = Thread(target=clientThread, daemon=True, args=(connectionSocket,))
          x.start()
     except timeout:
          pass








