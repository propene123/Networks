import sys
import json
import os
from socket import *
from threading import Thread, Lock
from datetime import datetime


# function takes filepath, ip and port tuple, message type
# and whether an operation was successful or not
def writeToLog(path, address, messageType, success):
    # lock mutex so only 1 thread can write to log at once
    with logLock:
        try:
            with open(path, 'a') as f:
                try:
                    # create 1 line of output
                    outLine = ''
                    # output starts with client address and port
                    outLine += address[0] + ':' + str(address[1]) + '\t'
                    # then the time and date of the request
                    outLine += datetime.today().strftime('%c') + '\t'
                    # then the type of request
                    outLine += messageType + '\t'
                    # finally whether or not the request was successful
                    if(success):
                        outLine += 'OK'
                    else:
                        outLine += 'ERROR'
                    outLine += '\n'
                    f.write(outLine)
                # if the log file cannot be written to the notify user
                # and exit server
                except IOError:
                    print('Could not write to log file... exiting server')
                    exit()
        # if the log file cannot be opened then print error and exit
        # server
        except FileNotFoundError:
            print('Could not open log file... exiting server')
            exit()


# function takes a socket, response type, and payload
# and sends the response message to the client
def sendMessage(socket, respType, payload):
    # encodes respType and payload as json string
    response = json.dumps({'type': respType, 'payload': payload})
    # calculate lenght of json string in bytes
    length = len(response.encode('utf-8'))
    # prepend json string with length
    message = str(length) + '_' + response
    # attempt to send resposne to client
    try:
        socket.sendall(message.encode())
    # if the client has closed notify user
    except (ConnectionError, OSError):
        print('Connection was closed on a client thread')


# function takes a socket gets a lsit of all subfolders of
# boards folder and sends that to the client socket
def getBoards(socket):
    payload = ''
    respType = ''
    # returns list of everything in boards folder that is
    # a directory
    payload = [
        x for x in os.listdir(
            os.path.join(
                os.getcwd(),
                'board')) if os.path.isdir(
            os.path.join(
                os.path.join(
                    os.getcwd(),
                    'board'),
                x))]
    # if there are no boards send ERROR back to client
    if not payload:
        respType = 'ERROR'
        payload = 'No boards defined'
        # write error to log file
        writeToLog(logPath, socket.getpeername(), 'GET_BOARDS', False)
    else:
        # write success to log file
        respType = 'GET_BOARDS_RESPONSE'
        writeToLog(logPath, socket.getpeername(), 'GET_BOARDS', True)
    # send response to client
    sendMessage(socket, respType, payload)


# helper function to determine if a board exisits or not
def boardExists(board):
    res = False
    # get board as filepath
    boardPath = os.path.join(os.getcwd(), 'board', board)
    # set result to True if board exists and is a file
    if os.path.exists(boardPath) and os.path.isdir(boardPath):
        res = True
    # return result
    return res


# function takes socket and board name
def getMessages(socket, board):
    payload = ''
    respType = ''
    # if board does not exist send Error to user
    if (not boardExists(board)):
        payload = 'Board does not exist'
        respType = 'ERROR'
        # log ERROR
        writeToLog(logPath, socket.getpeername(), 'GET_MESSAGES', False)
    else:
        # get board name as filepath
        boardPath = os.path.join(os.getcwd(), 'board', board)
        # returns list of all files in board folder
        names = [os.path.splitext(x)[0] for x in os.listdir(
            boardPath) if os.path.isfile(os.path.join(boardPath, x))]
        # sort filenames into descending order
        names.sort(reverse=True)
        # take only the first 100 message files
        names = names[:100]
        messages = []
        # for each message read its contents into another list
        for i in range(len(names)):
            filepath = os.path.join(os.getcwd(), 'board', board, names[i])
            with open(filepath) as f:
                contents = ''
                contents += f.readlines()
                messages += contents
            # edit list of message titles to not be the full filenames
            names[i] = names[i].split('-', 2)[2]
        # create response payload
        payload = {'titles': names, 'messages': messages}
        respType = 'GET_MESSAGES_RESPONSE'
        # log success
        writeToLog(logPath, socket.getpeername(), 'GET_MESSAGES', True)
    # send response to client
    sendMessage(socket, respType, payload)


# function takes socket, board, title, and message contents
def postMessage(socket, board, title, msg):
    payload = ''
    respType = ''
    # if the board does not exist send ERROR to client
    if (not boardExists(board)):
        payload = 'Board does not exist'
        respType = 'ERROR'
        # log ERROR
        writeToLog(logPath, socket.getpeername(), 'POST_MESSAGE', False)
    else:
        # create message filename. Start with current date and time
        filename = datetime.today().strftime('%Y%m%d-%H%M%S-')
        # next the message title with spaces as underscores
        filename += title.replace(' ', '_')
        # turn filename in filepath
        filepath = os.path.join(os.getcwd(), 'board', board, filename)
        try:
            # open message file
            with open(filepath, 'w') as f:
                # write message contents
                f.write(msg)
                # set response to success
                respType = 'POST_MESSAGE_RESPONSE'
                payload = 'Successfully posted message'
                # log success
                writeToLog(logPath, socket.getpeername(), 'POST_MESSAGE', True)
        # if the file could not be written to or created then ERROR
        except OSError:
            # set resposne to ERROR
            respType = 'ERROR'
            payload = 'Could not create message with that title'
            # log ERROR
            writeToLog(logPath, socket.getpeername(), 'POST_MESSAGE', False)
    # send response to client
    sendMessage(socket, respType, payload)


# function takes a socket and sends an ERROR
def unrecognisedMessage(socket):
    # set response type to ERROR
    payload = 'That command is not a recognised command'
    respType = 'ERROR'
    # send response
    sendMessage(socket, respType, payload)


# function takes json string as msg and a socket
# calls correct message handling function
def handleMessage(msg, socket):
    # test if msg is a valid json string
    try:
        obj = json.loads(msg)
    except json.JSONDecodeError:
        # if not valid json inform client
        unrecognisedMessage(socket)
    try:
        # based on type call correc handler function
        if(obj['type'] == 'GET_BOARDS'):
            getBoards(socket)
        elif(obj['type'] == 'GET_MESSAGES'):
            getMessages(socket, obj['board'])
        elif(obj['type'] == 'POST_MESSAGE'):
            postMessage(socket, obj['board'], obj['title'], obj['msg'])
        else:
            unrecognisedMessage(socket)
    # if no type field inform user of invalid message
    except KeyError:
        unrecognisedMessage(socket)


# function takes socket and spawns a daemon thread
# for the client on that socket
def clientThread(socket):
    # main client loop
    while True:
        try:
            # attempt to read incoming client message
            sentence = socket.recv(1024).decode()
            # if socket is closed break and terminate thread
            if not sentence:
                print("Connection closed on client thread")
                break
            try:
                # attempt to split response into length and payload
                splitSentence = sentence.split('_', 1)
                length = int(splitSentence[0])
                message = splitSentence[1]
            # if error is thrown then message was invalid
            except (IndexError, ValueError):
                # inform client of invalid message
                unrecognisedMessage(socket)
            messageLength = len(message.encode('utf-8'))
            # check all message has been received
            if(messageLength < length):
                # receive rest of message
                message += socket.recv(length - messageLength).decode()
            # handle the message appropriately
            handleMessage(message, socket)
        # if client has been closed inform user and end thread
        except (ConnectionError, OSError):
            print("Connection closed on client thread")
            break
    socket.close()


# read commandline args as server address and port
serverAddress = sys.argv[1]
serverPort = sys.argv[2]
# create server socket
serverSocket = socket(AF_INET, SOCK_STREAM)
# attempt to open server socket
try:
    serverSocket.bind((serverAddress, int(serverPort)))
except BaseException:
    # if socket cant be opened inform user and exit
    print("Could not open requested server and port")
    exit()
# set small timeout so server can be closed via keyboard interrupt
serverSocket.settimeout(0.2)
serverSocket.listen(5)
# create log mutex and logpath
logLock = Lock()
logPath = os.path.join(os.getcwd(), 'server.log')
# main server loop
while True:
    try:
        try:
            # attempt to gain a connection
            (connectionSocket, addr) = serverSocket.accept()
            # pass client socket to new thread to be dealt with
            x = Thread(
                target=clientThread,
                daemon=True,
                args=(
                    connectionSocket,
                ))
            x.start()
        # this exists so keyboard interrupts are possible
        except timeout:
            pass
    # on keyboard interrupt exit server
    except KeyboardInterrupt:
        print('Keyboard interrupt... Closing server')
        break
serverSocket.close()
