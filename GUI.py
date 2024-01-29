#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 30 13:36:58 2021

@author: bing
"""

# import all the required  modules
import threading
import select
from tkinter import *
from tkinter import font
from tkinter import ttk
from tkinter.messagebox import showinfo,askokcancel,WARNING
from tkinter import filedialog
from chat_utils import *
import json
from autocorrect import spell
import pygame
from mss import mss
from youtubemain import *

# GUI class for the chat
class GUI:
    # constructor method
    def __init__(self, send, recv, file_recv, sm, s):
        # chat window which is currently hidden
        self.Window = Tk()
        self.Window.withdraw()
        self.send = send
        self.recv = recv
        self.file_recv = file_recv
        self.sm = sm
        self.socket = s
        self.my_msg = ""
        self.system_msg = ""

        self.emoji_1 = PhotoImage(file='1.png')
        self.emoji_2 = PhotoImage(file='2.png')
        self.emoji_3 = PhotoImage(file='3.png')
        self.emoji_4 = PhotoImage(file='4.png')
        self.emoji_5 = PhotoImage(file='5.png')
        self.emoji_6 = PhotoImage(file='6.png')
        self.emoji_7 = PhotoImage(file='7.png')
        self.emoji_8 = PhotoImage(file='8.png')
        self.emoji_9 = PhotoImage(file='9.png')
        self.emojis = [self.emoji_1, self.emoji_2, self.emoji_3, 
                       self.emoji_4, self.emoji_5, self.emoji_6,
                       self.emoji_7, self.emoji_8, self.emoji_9]

        pygame.mixer.init()
        self.music_counter = 0

        self.file_coming = False

    def login(self):
        # login window
        self.login = Toplevel()
        # set the title
        self.login.title("Login")
        self.login.resizable(width=False,
                             height=False)
        self.login.configure(width=400,
                             height=300)
        # create a Label
        self.pls = Label(self.login,
                         text="Please login to continue",
                         justify=CENTER,
                         font="Helvetica 14 bold")

        self.pls.place(relheight=0.15,
                       relx=0.2,
                       rely=0.07)
        # create a Label
        self.labelName = Label(self.login,
                               text="Name: ",
                               font="Helvetica 12")

        self.labelName.place(relheight=0.2,
                             relx=0.1,
                             rely=0.2)

        # create a entry box for
        # tyoing the message
        self.entryName = Entry(self.login,
                               font="Helvetica 14")

        self.entryName.place(relwidth=0.4,
                             relheight=0.12,
                             relx=0.35,
                             rely=0.2)

        # set the focus of the curser
        self.entryName.focus()

        self.labelPwd = Label(self.login,
                              text="Password: ",
                              font="Helvetica 12")

        self.labelPwd.place(relheight=0.2,
                            relx=0.1,
                            rely=0.35)

        # create a entry box for
        # tyoing the message
        self.entryPwd = Entry(self.login, show='*', font="Helvetica 14")

        self.entryPwd.place(relwidth=0.4,
                            relheight=0.12,
                            relx=0.35,
                            rely=0.35)

        # create a Continue Button
        # along with action
        self.go = Button(self.login,
                         text="CONTINUE",
                         font="Helvetica 14 bold",
                         command=lambda: self.goAhead(self.entryName.get(), self.entryPwd.get()))
        self.go.bind('<Return>',lambda: self.goAhead(self.entryName.get(), self.entryPwd.get()))
        self.go.place(relx=0.4,
                      rely=0.55)
        self.Window.mainloop()

    def goAhead(self, name, pwd):
        if len(name) > 0:
            msg = json.dumps({"action": "login", "name": name, 'pwd': pwd})
            self.send(msg)
            response = json.loads(self.recv())
            if response["status"] == 'ok':
                self.login.destroy()
                self.sm.set_state(S_LOGGEDIN)
                self.sm.set_myname(name)
                self.layout(name)
                self.textCons.config(state=NORMAL)
                # self.textCons.insert(END, "hello" +"\n\n")
                self.textCons.insert(END, menu + "\n\n")
                self.textCons.config(state=DISABLED)
                self.textCons.see(END)
                #while True:
                    #self.proc()

                # the thread to receive messages
                process = threading.Thread(target=self.proc)
                process.daemon = True
                process.start()


            elif response["status"] == "wrong pwd":
                showinfo(
                    title='Error',
                    message='Wrong password, try again'
                )
                self.entryName.delete(0, END)
                self.entryPwd.delete(0, END)

            elif response["status"] == 'duplicate':
                showinfo(
                    title='Error',
                    message='Duplicate username, try again'
                )
                self.entryName.delete(0, END)
                self.entryPwd.delete(0, END)

    # The main layout of the chat
    def layout(self, name):

        self.name = name
        # to show chat window
        self.Window.deiconify()
        self.Window.title("CHATROOM")
        self.Window.resizable(width=False,
                              height=False)
        self.Window.configure(width=470,
                              height=550,
                              bg="#17202A")
        self.labelHead = Label(self.Window,
                               bg="#17202A",
                               fg="#EAECEE",
                               text=self.name,
                               font="Helvetica 13 bold",
                               pady=5)

        self.labelHead.place(relwidth=1)
        self.line = Label(self.Window,
                          width=450,
                          bg="#ABB2B9")

        self.line.place(relwidth=1,
                        rely=0.07,
                        relheight=0.012)

        self.textCons = Text(self.Window,
                             width=20,
                             height=2,
                             bg="#17202A",
                             fg="#EAECEE",
                             font="Helvetica 14",
                             padx=5,
                             pady=5)

        self.textCons.place(relheight=0.645,
                            relwidth=1,
                            rely=0.08)

        self.labelBottom = Label(self.Window,
                                 bg="#ABB2B9",
                                 height=120)

        self.labelBottom.place(relwidth=1,
                               rely=0.625)

        # toolbar
        self.buttonEmoji = Button(self.labelBottom,
                                  text="Emoji",
                                  font="Helvetica 10 bold",
                                  width=10,
                                  bg="#ABB2B9",
                                  command=lambda: self.emoji())

        self.buttonEmoji.place(relx=0.011,
                               rely=0.018,
                               relheight=0.015,
                               relwidth=0.22)
        self.buttonEmoji.config(state=DISABLED)

        self.buttonFile = Button(self.labelBottom,
                                  text="File",
                                  font="Helvetica 10 bold",
                                  width=10,
                                  bg="#ABB2B9",
                                  command=lambda: self.send_file())

        self.buttonFile.place(relx=0.241,
                               rely=0.018,
                               relheight=0.015,
                               relwidth=0.22)
        self.buttonFile.config(state=DISABLED)

        self.buttonMusic = Button(self.labelBottom,
                                 text="Play music",
                                 font="Helvetica 10 bold",
                                 width=10,
                                 bg="#ABB2B9",
                                 command=lambda: self.music())

        self.buttonMusic.place(relx=0.471,
                              rely=0.001,
                              relheight=0.015,
                              relwidth=0.22)

        self.ch_but = Button(self.labelBottom,
                             text='Clear history',
                             font="Helvetica 10 bold",
                             width=10,
                             bg="#ABB2B9",
                             command=self.clear_history)
        self.ch_but.place(relx=0.701,
                          rely=0.001,
                          relheight=0.015,
                          relwidth=0.22)

        self.buttonShot = Button(self.labelBottom,
                             text='Screenshot',
                             font="Helvetica 10 bold",
                             width=10,
                             bg="#ABB2B9",
                             command=self.shot)
        self.buttonShot.place(relx=0.011,
                          rely=0.001,
                          relheight=0.015,
                          relwidth=0.22)

        self.buttonGame = Button(self.labelBottom,
                                 text='Wordle',
                                 font="Helvetica 10 bold",
                                 width=10,
                                 bg="#ABB2B9",
                                 command=self.play_game)

        self.buttonGame.place(relx=0.241,
                              rely=0.001,
                              relheight=0.015,
                              relwidth=0.22)

        # message box
        self.entryMsg = Entry(self.labelBottom,
                              bg="#2C3E50",
                              fg="#EAECEE",
                              font="Helvetica 13")
        # place the given widget
        # into the gui window
        self.entryMsg.place(relwidth=0.74,
                            relheight=0.06,
                            rely=0.036,
                            relx=0.011)

        self.entryMsg.focus()

        # create a Send Button
        self.buttonMsg = Button(self.labelBottom,
                                text="Send",
                                font="Helvetica 10 bold",
                                width=20,
                                bg="#ABB2B9",
                                command=lambda: self.sendButton(self.entryMsg.get()))
        self.buttonMsg.bind('<Return>',lambda: self.sendButton(self.entryMsg.get()))

        self.buttonMsg.place(relx=0.77,
                             rely=0.036,
                             relheight=0.06,
                             relwidth=0.22)

        self.textCons.config(cursor="arrow")

        # create a scroll bar
        scrollbar = Scrollbar(self.textCons)

        # place the scroll bar
        # into the gui window
        scrollbar.place(relheight=1,
                        relx=0.974)

        scrollbar.config(command=self.textCons.yview)

        self.textCons.config(state=DISABLED)

    # function to basically start the thread for sending messages

    def sendButton(self, msg):
        if self.sm.get_state()==S_CHATTING:
            word_lst=msg.split(' ')
            for i in range(len(word_lst)):
                if word_lst[i].isalpha():
                    word_lst[i] = spell(word_lst[i])
                else:
                    pointer = -1
                    while word_lst[i][pointer].isalpha():
                        pointer -= 1
                    word_lst[i] = spell(word_lst[i][:pointer]) + word_lst[i][pointer:]
            msg = ' '.join(word_lst)
            #print(msg)
        self.my_msg = msg
        self.entryMsg.delete(0, END)
        self.textCons.config(state=NORMAL)
        self.textCons.insert(END, msg+'\n')
        self.textCons.config(state=DISABLED)
        self.textCons.see(END)

    def emoji(self):
        self.emoji_bank = Toplevel()
        self.emoji_bank.title('Emoji Bank')

        self.buttonEmoji1 = Button(self.emoji_bank, image=self.emoji_1, command=lambda: self.send_emoji(1))
        self.buttonEmoji1.grid(column=0, row=0, padx=5, pady=5)

        self.buttonEmoji2 = Button(self.emoji_bank, image=self.emoji_2, command=lambda: self.send_emoji(2))
        self.buttonEmoji2.grid(column=1, row=0, padx=5, pady=5)

        self.buttonEmoji3 = Button(self.emoji_bank, image=self.emoji_3, command=lambda: self.send_emoji(3))
        self.buttonEmoji3.grid(column=2, row=0, padx=5, pady=5)

        self.buttonEmoji4 = Button(self.emoji_bank, image=self.emoji_4, command=lambda: self.send_emoji(4))
        self.buttonEmoji4.grid(column=0, row=1, padx=5, pady=5)

        self.buttonEmoji5 = Button(self.emoji_bank, image=self.emoji_5, command=lambda: self.send_emoji(5))
        self.buttonEmoji5.grid(column=1, row=1, padx=5, pady=5)

        self.buttonEmoji6 = Button(self.emoji_bank, image=self.emoji_6, command=lambda: self.send_emoji(6))
        self.buttonEmoji6.grid(column=2, row=1, padx=5, pady=5)

        self.buttonEmoji7 = Button(self.emoji_bank, image=self.emoji_7, command=lambda: self.send_emoji(7))
        self.buttonEmoji7.grid(column=0, row=2, padx=5, pady=5)

        self.buttonEmoji8 = Button(self.emoji_bank, image=self.emoji_8, command=lambda: self.send_emoji(8))
        self.buttonEmoji8.grid(column=1, row=2, padx=5, pady=5)

        self.buttonEmoji9 = Button(self.emoji_bank, image=self.emoji_9, command=lambda: self.send_emoji(9))
        self.buttonEmoji9.grid(column=2, row=2, padx=5, pady=5)

    def send_emoji(self, emoji_num):
        self.emoji_bank.destroy()
        self.my_msg = '#e ' + str(emoji_num)
        self.my_emoji = self.emojis[emoji_num - 1]
        self.textCons.config(state=NORMAL)
        self.textCons.image_create(END, image=self.my_emoji)
        self.textCons.insert(END, "\n\n")
        self.textCons.config(state=DISABLED)
        self.textCons.see(END)

    def send_file(self):
        self.Window.filename = filedialog.askopenfilename(title='Select a file',
                                                          filetypes=(('png files', '*.png'), ('jpg files', '*.jpg'), ('txt files', '*.txt'),
                                                                     ('mp3 files', '*.mp3'), ('mp4 files', '*.mp4')))
        self.my_msg = '#f'+self.Window.filename

    def recv_file(self):
        self.file_recv()
        self.sm.file_end()

    def music(self):
        if self.music_counter == 0:
            pygame.mixer.music.load('./audio/the-cradle-of-your-soul.mp3')
            pygame.mixer.music.play(loops=0)
            self.music_counter = 1
            self.buttonMusic.config(text='Stop music')
        else:
            pygame.mixer.music.stop()
            self.music_counter = 0
            self.buttonMusic.config(text='Play music')

    def clear_history(self):
        answer=askokcancel(title='Watch out!', message='Press ok if you want to delete all history.',icon=WARNING)
        if answer:
            showinfo(title='Deletion status',message='You have kissed goodbye to your history.')
            self.textCons.config(state=NORMAL)
            self.textCons.delete(1.0, END)
            self.textCons.config(state=DISABLED)
            self.my_msg='h'

    def shot(self):
        shot_file = filedialog.asksaveasfilename(defaultextension='.png', initialdir='./', title='Save the screenshot',
                                                 filetypes=(('png files', '*.png'), ('jpg files', '*.jpg')))
        with mss() as sct:
            filename = sct.shot(mon=-1, output=shot_file)
        showinfo(title='Notice', message='The screenshot has been successfully save!')

    def play_game(self):
        LetterGame()

    def proc(self):
        # print(self.msg)
        while True:
            read, write, error = select.select([self.socket], [], [], 0)
            peer_msg = []
            # print(self.msg)
            if self.socket in read:
                if self.sm.file_sending:
                    self.recv_file()
                else:
                    peer_msg = self.recv()
            if len(self.my_msg) > 0 or len(peer_msg) > 0:
                # print(self.system_msg)
                self.system_msg = self.sm.proc(self.my_msg, peer_msg)
                self.my_msg = ""
                if self.system_msg[-2:] == '#e':
                    self.peer_emoji = self.emojis[int(self.system_msg[-3]) - 1]
                    self.textCons.config(state=NORMAL)
                    self.textCons.insert(END, self.system_msg[:-3])
                    self.textCons.image_create(END, image=self.peer_emoji)
                    self.textCons.insert(END, "\n")
                    self.textCons.config(state=DISABLED)
                    self.textCons.see(END)
                else:
                    self.textCons.config(state=NORMAL)
                    self.textCons.insert(END, self.system_msg + "\n\n")
                    self.textCons.config(state=DISABLED)
                    self.textCons.see(END)

                if self.sm.get_state() == S_CHATTING:
                    self.buttonEmoji.config(state=NORMAL)
                    self.buttonFile.config(state=NORMAL)
                else:
                    self.buttonEmoji.config(state=DISABLED)
                    self.buttonFile.config(state=DISABLED)

    def run(self):
        self.login()


# create a GUI class object
if __name__ == "__main__":
    g = GUI()
    g = GUI()
