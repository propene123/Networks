import sys
from socket import *
from threading import Thread

def getBoards():
     pass


def getMessages():
     pass


def postMessage():
     pass

def handleMessage(msg):
     pass


def clientThread(socket):
     while True:
          sentence = socket.recv(1024).decode();
          splitSentence = sentence.split('_', 1)
          length = int(splitSentence[0])
          message = splitSentence[1]
          messageLength = length(message.encode('utf-8'))
          if(messageLength < length):
               message += socket.recv(length - messageLength).decode()
          handleMessage(message)

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








