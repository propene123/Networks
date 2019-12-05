import sys
import json
import os
from socket import *
from threading import Thread
from datetime import datetime

def getBoards(socket):
     payload = ''
     respType = ''
     payload = [x for x in os.listdir(os.path.join(os.getcwd(), 'board')) if os.path.isdir(os.path.join(os.path.join(os.getcwd(), 'board'), x))]
     if not payload:
          respType = 'ERROR'
          payload = 'No boards defined'
     else:
          respType = 'GET_BOARDS_RESPONSE'
     response = json.dumps({'type': respType, 'payload': payload})
     length = len(payload.encode('utf-8'))
     message = str(length) + '_' + response
     socket.sendall(message.encode())


def boardExists(board):
     res = False
     boardPath = os.path.join(os.getcwd(), 'board', board)
     if os.path.exists(boardPath) and os.path.isdir(boardPath):
          res = True
     return res

def getMessages(socket, board):
     payload = ''
     respType = ''
     if (not boardExists(board)):
          payload = 'Board does not exist'
          respType = 'ERROR'
     else:
          boardPath = os.path.join(os.getcwd(), 'board', board)
          names = [os.path.splitext(x)[0] for x in os.listdir(boardPath) if os.path.isfile(os.path.join(boardPath, x))]
          names.sort(reverse = True)
          names = names[:100]
          messages = []
          for name in names:
               try:
                    f = open(os.path.join(os.getcwd(), 'board', board, name))
                    messages += f.readlines()
               finally:
                    f.close()
          payload = {'titles': names, 'messages': messages}
          respType = 'GET_MESSAGES_RESPONSE'
     response = json.dumps({'type':respType, 'payload': payload})
     length = len(response.encode('utf-8'))
     message = str(length) + '_' + response
     socket.sendall(message.encode())


def postMessage(socket, board, title, msg):
     payload = ''
     respType = ''
     if (not boardExists(board)):
          payload = 'Board does not exist'
          respType = 'ERROR'
     else:
          filename = datetime.today().strftime('%Y%m%d-%H%M%S-') + title.replace(' ', '_')
          filepath = os.path.join(os.getcwd(), 'board', board, filename)
          try:
               f = open(filepath, 'w')
               f.write(msg)
               respType = 'POST_MESSAGE_RESPONSE'
               payload = 'Successfully posted message'
          except OSError:
              respType = 'ERROR'
              payload = 'Could not create message with that title'
          finally:
               f.close()
     response = json.dumps({'type':respType, 'payload': payload})
     length = len(response.encode('utf-8'))
     message = str(length) + '_' + response
     socket.sendall(message.encode())
          
def unrecognisedMessage(socket):
     payload = 'That command is not a recognised command'
     respType = 'ERROR'
     response = json.dumps({'type':respType, 'payload': payload})
     length = len(response.encode('utf-8'))
     message = str(length) + '_' + response
     socket.sendall(message.encode())



def handleMessage(msg, socket):
     obj = json.loads(msg)
     if(obj['type'] == 'GET_BOARDS'):
          getBoards(socket)
     elif(obj['type'] == 'GET_MESSAGES'):
          getMessages(socket, obj['board'])
     elif(obj['type'] == 'POST_MESSAGE'):
          postMessage(socket, obj['board'], obj['title'], obj['msg'])
     else:
          unrecognisedMessage(socket)

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








