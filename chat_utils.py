import socket
import time
import os

# use local loop back address by default
#CHAT_IP = '127.0.0.1'
# CHAT_IP = socket.gethostbyname(socket.gethostname())
CHAT_IP = socket.gethostbyname(socket.gethostname())

CHAT_PORT = 1112
SERVER = (CHAT_IP, CHAT_PORT)

menu = "\n++++ Choose one of the following commands\n \
        time: calendar time in the system\n \
        who: to find out who else are there\n \
        c _peer_: to connect to the _peer_ and chat\n \
        ? _term_: to search your chat logs where _term_ appears\n \
        p _#_: to get number <#> sonnet\n \
        m _x(num)_: to get your x most used words \n \
        q: to leave the chat system\n\n"

S_OFFLINE = 0
S_CONNECTED = 1
S_LOGGEDIN = 2
S_CHATTING = 3

SIZE_SPEC = 5

CHAT_WAIT = 0.2
SIZE = 1024
FORMAT = "utf-8"

def print_state(state):
    print('**** State *****::::: ')
    if state == S_OFFLINE:
        print('Offline')
    elif state == S_CONNECTED:
        print('Connected')
    elif state == S_LOGGEDIN:
        print('Logged in')
    elif state == S_CHATTING:
        print('Chatting')
    else:
        print('Error: wrong state')


def mysend(s, msg):
    # append size to message and send it
    msg = ('0' * SIZE_SPEC + str(len(msg)))[-SIZE_SPEC:] + str(msg)
    msg = msg.encode()
    total_sent = 0
    while total_sent < len(msg):
        sent = s.send(msg[total_sent:])
        if sent == 0:
            print('server disconnected')
            break
        total_sent += sent


def myrecv(s):
    # receive size first
    size = ''
    while len(size) < SIZE_SPEC:
        text = s.recv(SIZE_SPEC - len(size)).decode()
        if not text:
            print('disconnected')
            return('')
        size += text
    size = int(size)
    # now receive message
    msg = ''
    while len(msg) < size:
        text = s.recv(size-len(msg)).decode()
        if text == b'':
            print('disconnected')
            break
        msg += text
    #print ('received '+message)
    return (msg)


def myfile_send(s, file_address, file_size):
    with open(file_address, "rb") as f:
        c = 0
        while c <= int(file_size):
            if int(file_size) - c >= SIZE:
                data = f.read(SIZE)
            else:
                data = f.read(int(file_size) - c)
            if not (data):
                break
            s.send(data)
            c += len(data)


def myfile_receive(s, file_path, file_name, file_size):
    with open(file_path + file_name, "wb") as f:
        c = 0
        while c <= int(file_size):
            if int(file_size) - c >= SIZE:
                data = s.recv(SIZE)
            else:
                data = s.recv(int(file_size) - c)
            if not (data):
                break
            f.write(data)
            c += len(data)


def text_proc(text, user):
    ctime = time.strftime('%d.%m.%y,%H:%M', time.localtime())
    # message goes directly to screen
    return('(' + ctime + ') ' + user + ' : ' + text)