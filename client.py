import sys
import json
from socket import *

serverAddress = sys.argv[1]
serverPort = sys.argv[2]
clientSocket = socket(AF_INET, SOCK_STREAM)
try:
     clientSocket.bind((serverAddress, int(serverPort)))
except:
     print("Could not open requested server and port")
     exit()
#sentence = '{"type": "POST_MESSAGE", "board": "Strangely_named_board", "title": "test bro lel kekw", "msg": "Hello this is a test message kedaaaaah"}'
sentence = '{"type": "GET_MESSAGES", "board": "Strangely_named_board"}'
sentence = (str(len(sentence.encode('utf-8'))) + '_') + sentence
clientSocket.sendall(sentence.encode())
resp = clientSocket.recv(1024).decode()
restJson = json.loads(resp.split('_', 1)[1])
print(restJson['payload'])
clientSocket.close()

