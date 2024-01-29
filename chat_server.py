"""
Created on Tue Jul 22 00:47:05 2014

@author: alina, zzhang
"""

import time
import socket
import select
import os
import sys
import string
import indexer
import json
import pickle as pkl
from chat_utils import *
import chat_group as grp
from common_word import *
from error_correction import *

class Server:
    def __init__(self):
        self.new_clients = []  # list of new sockets of which the user id is not known
        self.logged_name2sock = {}  # dictionary mapping username to socket
        self.logged_sock2name = {}  # dict mapping socket to user name
        self.all_sockets = []
        self.group = grp.Group()
        # start server
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(SERVER)
        self.server.listen(5)
        self.all_sockets.append(self.server)
        # initialize past chat indices
        self.indices = {}
        # sonnet
        # self.sonnet_f = open('AllSonnets.txt.idx', 'rb')
        # self.sonnet = pkl.load(self.sonnet_f)
        # self.sonnet_f.close()
        self.sonnet = indexer.PIndex("AllSonnets.txt")
        # password management
        self.passwords = {}
        self.pwd_history()
        #file transfer
        self.file_coming = False
        self.filename = None
        self.filesize = None
        self.filesender = None

    def pwd_history(self):
        try:
            pwd_f = open('password.pk', 'rb')
            self.passwords = pkl.load(pwd_f)
            pwd_f.close()
        except IOError:
            pwd_f = open('password.pk', 'wb')
            pwd_f.close()

    def new_client(self, sock):
        # add to all sockets and to new clients
        print('new client...')
        sock.setblocking(0)
        self.new_clients.append(sock)
        self.all_sockets.append(sock)

    def login(self, sock):
        # read the msg that should have login code plus username
        try:
            msg = json.loads(myrecv(sock))
            print("login:", msg)
            if len(msg) > 0:
    
                if msg["action"] == "login":
                    name = msg["name"]
                    pwd = msg["pwd"]
                    if self.group.is_member(name):  # a client under this name has already logged in
                        mysend(sock, json.dumps(
                            {"action": "login", "status": "duplicate"}))
                        print(name + ' duplicate login attempt')
                    else:
                        # load chat history of that user
                        if name not in self.indices.keys():
                            try:
                                self.indices[name] = pkl.load(
                                    open(name + '.idx', 'rb'))
                            except IOError:  # chat index does not exist, then create one
                                self.indices[name] = indexer.Index(name)
                                os.mkdir('./'+name+'receiver')
                                self.passwords[name] = pwd
                                with open('password.pk', 'wb') as f:
                                    pkl.dump(self.passwords, f)
    
                        if pwd != self.passwords[name]:
                            mysend(sock, json.dumps(
                                {"action": "login", "status": "wrong pwd"}))
    
                        else:
                            print(name + ' logged in')
                            self.group.join(name)
                            mysend(sock, json.dumps(
                                {"action": "login", "status": "ok"}))
                            # move socket from new clients list to logged clients
                            self.new_clients.remove(sock)
                            # add into the name to sock mapping
                            self.logged_name2sock[name] = sock
                            self.logged_sock2name[sock] = name
                else:
                    print('wrong code received')
            else:  # client died unexpectedly
                self.logout(sock)
        except:
            self.all_sockets.remove(sock)
            
    def logout(self, sock):
        # remove sock from all lists
        name = self.logged_sock2name[sock]
        pkl.dump(self.indices[name], open(name + '.idx', 'wb'))
        del self.indices[name]
        del self.logged_name2sock[name]
        del self.logged_sock2name[sock]
        self.all_sockets.remove(sock)
        self.group.leave(name)
        sock.close()
        
# ==============================================================================
# main command switchboard
# ==============================================================================
    def handle_msg(self, from_sock):
        # read msg code
        msg = myrecv(from_sock)
        if len(msg) > 0:
            # ==============================================================================
            # handle connect request
            # ==============================================================================
            msg = json.loads(msg)
            if msg["action"] == "connect":
                to_name = msg["target"]
                from_name = self.logged_sock2name[from_sock]
                if to_name == from_name:
                    msg = json.dumps({"action": "connect", "status": "self"})
                # connect to the peer
                elif self.group.is_member(to_name):
                    to_sock = self.logged_name2sock[to_name]
                    self.group.connect(from_name, to_name)
                    the_guys = self.group.list_me(from_name)
                    msg = json.dumps(
                        {"action": "connect", "status": "success"})
                    for g in the_guys[1:]:
                        to_sock = self.logged_name2sock[g]
                        mysend(to_sock, json.dumps(
                            {"action": "connect", "status": "request", "from": from_name}))
                else:
                    msg = json.dumps(
                        {"action": "connect", "status": "no-user"})
                mysend(from_sock, msg)

# ==============================================================================
# handle emoji exchange
# ==============================================================================
            elif msg["action"] == "emoji":
                from_name = self.logged_sock2name[from_sock]
                the_guys = self.group.list_me(from_name)

                for g in the_guys[1:]:
                    to_sock = self.logged_name2sock[g]
                    mysend(to_sock, json.dumps(
                        {"action": "emoji", "from": msg["from"], "emoji": msg["emoji"]}))

# =============================================================================
# handle deleting history
# =============================================================================
            elif msg["action"] == "clear history":
                f = open(msg['from'] + '.idx', 'wb')
                pkl.dump(indexer.Index(msg['from']), f)
                f.close()
                self.indices[msg['from']] = indexer.Index(msg['from'])

# ==============================================================================
# handle messeage exchange: one peer for now. will need multicast later
# ==============================================================================
            elif msg["action"] == "file":
                self.file_coming = True
                self.filename = msg["filename"]
                self.filesize = msg["filesize"]
                self.filesender = msg["from"]

# ==============================================================================
# handle messeage exchange: one peer for now. will need multicast later
# ==============================================================================
            elif msg["action"] == "exchange":
                #msg = error_correction(msg)
                from_name = self.logged_sock2name[from_sock]
                the_guys = self.group.list_me(from_name)
                #said = msg["from"]+msg["message"]
                msg['message'] = error_correction(msg['message'])
                print(msg['message'])
                if msg['message'] == None:
                    mysend(from_sock, json.dumps(
                        {"action": "noise"}))
                else:
                    said2 = text_proc(msg["message"], from_name)
                    self.indices[from_name].add_msg_and_index(said2)
                    for g in the_guys[1:]:
                        to_sock = self.logged_name2sock[g]
                        self.indices[g].add_msg_and_index(said2)
                        mysend(to_sock, json.dumps(
                            {"action": "exchange", "from": msg["from"], "message": msg["message"]}))
# ==============================================================================
#                 listing available peers
# ==============================================================================
            elif msg["action"] == "list":
                from_name = self.logged_sock2name[from_sock]
                msg = self.group.list_all()
                mysend(from_sock, json.dumps(
                    {"action": "list", "results": msg}))
# ==============================================================================
#             retrieve a sonnet
# ==============================================================================
            elif msg["action"] == "poem":
                poem_indx = int(msg["target"])
                from_name = self.logged_sock2name[from_sock]
                print(from_name + ' asks for ', poem_indx)
                poem = self.sonnet.get_poem(poem_indx)
                poem = '\n'.join(poem).strip()
                print('here:\n', poem)
                mysend(from_sock, json.dumps(
                    {"action": "poem", "results": poem}))
# ==============================================================================
#                 time
# ==============================================================================
            elif msg["action"] == "time":
                ctime = time.strftime('%d.%m.%y,%H:%M', time.localtime())
                mysend(from_sock, json.dumps(
                    {"action": "time", "results": ctime}))
# ==============================================================================
#                 search
# ==============================================================================
            elif msg["action"] == "search":
                term = msg["target"]
                from_name = self.logged_sock2name[from_sock]
                print('search for ' + from_name + ' for ' + term)
                # search_rslt = (self.indices[from_name].search(term))
                search_rslt = '\n'.join(
                    [x[-1] for x in self.indices[from_name].search(term)])
                print('server side search: ' + search_rslt)
                mysend(from_sock, json.dumps(
                    {"action": "search", "results": search_rslt}))
# =============================================================================
# search for most used words
# =============================================================================
            elif msg['action'] == 'sfm':
                from_name = self.logged_sock2name[from_sock]
                the_guys = self.group.members.keys()
                num = int(msg['target'])
                print('search for ' + from_name + "'s most used word")
                d = self.indices[from_name].index
                #print("result is "+ chat_history)
                l = sorted(d, key=lambda k: len(d[k]), reverse=True)
                # print(list(self.passwords.keys()))
                for k in l[:]:
                    if (k.isalpha() == False or (k in self.passwords.keys()) or (k in Words)) == True:
                        # print(k)
                        l.remove(k)
                # print(l)
                #print('result is '+l[:num])
                result = '\n'.join(l[:num])
                mysend(from_sock, json.dumps(
                    {"action": "most used words", "results":
                     result}))

# ==============================================================================
# the "from" guy has had enough (talking to "to")!
# ==============================================================================
            elif msg["action"] == "disconnect":
                from_name = self.logged_sock2name[from_sock]
                the_guys = self.group.list_me(from_name)
                self.group.disconnect(from_name)
                the_guys.remove(from_name)
                if len(the_guys) == 1:  # only one left
                    g = the_guys.pop()
                    to_sock = self.logged_name2sock[g]
                    mysend(to_sock, json.dumps({"action": "disconnect"}))
# ==============================================================================
#                 the "from" guy really, really has had enough
# ==============================================================================

        else:
            # client died unexpectedly
            self.logout(from_sock)

# ==============================================================================
# file function
# ==============================================================================
    def file_transfer(self, from_sock):
        myfile_receive(from_sock, 'D:/ICS/final/gui/gui/server_file/', self.filename, self.filesize)
        self.file_coming = False

        from_name = self.logged_sock2name[from_sock]
        the_guys = self.group.list_me(from_name)
        for g in the_guys[1:]:
            to_sock = self.logged_name2sock[g]
            mysend(to_sock, json.dumps(
                {"action": "file", "from": self.filesender, "filename": self.filename, "filesize": self.filesize}))
            myfile_send(to_sock, 'D:/ICS/final/gui/gui/server_file/' + self.filename, self.filesize)
        self.filename = None
        self.filesize = None
        self.filesender = None

# ==============================================================================
# main loop, loops *forever*
# ==============================================================================
    def run(self):
        print('starting server...')
        while(1):
            read, write, error = select.select(self.all_sockets, [], [])
            print('checking logged clients..')
            for logc in list(self.logged_name2sock.values()):
                if logc in read:
                    if self.file_coming:
                        self.file_transfer(logc)
                    else:
                        self.handle_msg(logc)
            print('checking new clients..')
            for newc in self.new_clients[:]:
                if newc in read:
                    self.login(newc)
            print('checking for new connections..')
            if self.server in read:
                # new client request
                sock, address = self.server.accept()
                self.new_client(sock)


def main():
    server = Server()
    server.run()


if __name__ == "__main__":
    main()
