from socket import *
import json

serverName = '127.0.0.1'
serverPort = 9999
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))
#sentence = '{"type": "POST_MESSAGE", "board": "Strangely_named_board", "title": "test bro lel kekw", "msg": "Hello this is a test message kedaaaaah"}'
sentence = '{"type": "GET_MESSAGES", "board": "Strangely_named_board"}'
sentence = (str(len(sentence.encode('utf-8'))) + '_') + sentence
clientSocket.sendall(sentence.encode())
resp = clientSocket.recv(1024).decode()
restJson = json.loads(resp.split('_', 1)[1])
print(restJson['payload'])
clientSocket.close()

