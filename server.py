import sys
import json
import os
from socket import *
from threading import Thread, Lock
from datetime import datetime


def writeToLog(path, address, messageType, success):
     with logLock:
          try:
               with open(path, 'a') as f:
                    try:
                         outLine = ''
                         outLine += address[0]+':'+str(address[1])+'\t'
                         outLine += datetime.today().strftime('%c')+'\t'
                         outLine += messageType+'\t'
                         if(success):
                              outLine += 'OK'
                         else:
                              outLine += 'ERROR'
                         outLine += '\n'
                         f.write(outLine)
                    except IOError:
                         print('Could not write to log file... exiting server')
                         exit()
          except FileNotFoundError:
               print('Could not open log file... exiting server')
               exit()

def sendMessage(socket, respType, payload):
     response = json.dumps({'type': respType, 'payload': payload})
     length = len(response.encode('utf-8'))
     message = str(length) + '_' + response
     try:
          socket.sendall(message.encode())
     except ConnectionError:
          print('Connection was closed on a client thread')


def getBoards(socket):
     payload = ''
     respType = ''
     payload = [x for x in os.listdir(os.path.join(os.getcwd(), 'board')) if os.path.isdir(os.path.join(os.path.join(os.getcwd(), 'board'), x))]
     if not payload:
          respType = 'ERROR'
          payload = 'No boards defined'
          writeToLog(logPath, socket.getpeername(), 'GET_BOARDS', False)
     else:
          respType = 'GET_BOARDS_RESPONSE'
          writeToLog(logPath, socket.getpeername(), 'GET_BOARDS', True)
     sendMessage(socket, respType, payload)


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
          writeToLog(logPath, socket.getpeername(), 'GET_MESSAGES', False)
     else:
          boardPath = os.path.join(os.getcwd(), 'board', board)
          names = [os.path.splitext(x)[0] for x in os.listdir(boardPath) if os.path.isfile(os.path.join(boardPath, x))]
          names.sort(reverse = True)
          names = names[:100]
          messages = []
          for name in names:
               with open(os.path.join(os.getcwd(), 'board', board, name)) as f:
                    messages += f.readlines()
          payload = {'titles': names, 'messages': messages}
          respType = 'GET_MESSAGES_RESPONSE'
          writeToLog(logPath, socket.getpeername(), 'GET_MESSAGES', True)
     sendMessage(socket, respType, payload)



def postMessage(socket, board, title, msg):
     payload = ''
     respType = ''
     if (not boardExists(board)):
          payload = 'Board does not exist'
          respType = 'ERROR'
          writeToLog(logPath, socket.getpeername(), 'POST_MESSAGE', False)
     else:
          filename = datetime.today().strftime('%Y%m%d-%H%M%S-') + title.replace(' ', '_')
          filepath = os.path.join(os.getcwd(), 'board', board, filename)
          try:
               with open(filepath, 'w') as f:
                    f.write(msg)
                    respType = 'POST_MESSAGE_RESPONSE'
                    payload = 'Successfully posted message'
                    writeToLog(logPath, socket.getpeername(), 'POST_MESSAGE', True)
          except OSError:
              respType = 'ERROR'
              payload = 'Could not create message with that title'
              writeToLog(logPath, socket.getpeername(), 'POST_MESSAGE', False)
     sendMessage(socket, respType, payload)

          
def unrecognisedMessage(socket):
     payload = 'That command is not a recognised command'
     respType = 'ERROR'
     sendMessage(socket, respType, payload)




def handleMessage(msg, socket):
     try:
          obj = json.loads(msg)
     except json.JSONDecodeError:
          unrecognisedMessage(socket)
     try:
          if(obj['type'] == 'GET_BOARDS'):
               getBoards(socket)
          elif(obj['type'] == 'GET_MESSAGES'):
               getMessages(socket, obj['board'])
          elif(obj['type'] == 'POST_MESSAGE'):
               postMessage(socket, obj['board'], obj['title'], obj['msg'])
          else:
               unrecognisedMessage(socket)
     except KeyError:
          unrecognisedMessage(socket)

def clientThread(socket):
     while True:
          try:
               sentence = socket.recv(1024).decode();
               if not sentence:
                    break
               try:
                    splitSentence = sentence.split('_', 1)
                    length = int(splitSentence[0])
                    message = splitSentence[1]
               except (IndexError, ValueError):
                    unrecognisedMessage(socket)
               messageLength = len(message.encode('utf-8'))
               if(messageLength < length):
                    message += socket.recv(length - messageLength).decode()
               handleMessage(message, socket)
          except ConnectionError:
               print("Connection closed on client thread")
               break
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
logLock = Lock()
logPath = os.path.join(os.getcwd(), 'server.log')

while True:
     try:
          (connectionSocket, addr) = serverSocket.accept()
          x = Thread(target=clientThread, daemon=True, args=(connectionSocket,))
          x.start()
     except timeout:
          pass








