from socket import *
import json

serverName = '127.0.0.1'
serverPort = 9999
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))
sentence = '21_{"type":"GET_BOARDS"}'
clientSocket.sendall(sentence.encode())
resp = clientSocket.recv(1024).decode()
restJson = json.loads(resp.split('_', 1)[1])
print(restJson['payload'])
sentence = '21_{"type":"GET_BOARDS"}'
clientSocket.sendall(sentence.encode())
resp = clientSocket.recv(1024).decode()
restJson = json.loads(resp.split('_', 1)[1])
print(restJson['payload'])
clientSocket.close()

