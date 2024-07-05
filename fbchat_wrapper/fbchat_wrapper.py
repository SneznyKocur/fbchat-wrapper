"""
A simple wrapper for the fbchat library 
please use only with https://github.com/SneznyKocur/fbchat (pip install py-fbchat)
Works only with python 3.8.*

Please Contribute as my code probably sucks :/

Made with <3 by: SneznyKocur
"""


import os
import threading
import validators
import py_fbchat as fbchat
from py_fbchat.models import Message, ThreadType
from PIL import Image
from PIL import ImageDraw
import logging
from PIL import ImageFont
import ffmpeg
from zipfile import ZipFile
import wget

def _setup():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    if not "ffmpeg.exe" in os.listdir() or not "font.ttf" in os.listdir():
        print(f"Downloading ffmpeg to {os.getcwd()}")
        wget.download("https://github.com/SneznyKocur/fbchat-wrapper/blob/main/extern.zip?raw=true","temp.zip")
        with ZipFile("temp.zip", 'r') as zObject:
            zObject.extractall(
                path=os.getcwd())
        os.remove("temp.zip")

class CommandNotRegisteredException(Exception):
    pass


class Wrapper(fbchat.Client):
    """
    Main Wrapper Class
    includes most functions
    """
    def __init__(self, email: str, password: str, prefix=""):
        self.logger = logging.getLogger("wrapper")
        _setup()
        self._command_list = dict()
        self._event_list = dict()
        self.Prefix = prefix or "!"
        self.logger.info("logging in")
        super().__init__(email, password)

    def _addEvent(self,name,func):
        self._event_list.update({f"{name}":func})

    def _addCommand(self, name: str, func, args: list, description: str = None):
        self._command_list.update({f"{name}": [func, args, description]})

    def Command(self, name: str, args: list, description: str = None):
        """Register a Command

        Args:
            name (str): name of the command
            args (list): list of arguments the command needs [str,str]
            description (str, optional): description of the command. Defaults to None.
        """
        def wrapper(func):
            self._addCommand(name, func, args, description)

        return wrapper

    def Event(self):
        """Register an Event
        """
        def wrapper(func):
            self._addEvent(func.__name__, func)
        return wrapper
    
    def _arg_split(self,args):
        inside = False
        end = list()
        part = ""
        for char in args:
            if char == '"':
                inside = not inside
                if not inside:
                    end.append(part)
            elif char == " ":
                if inside:
                    part+=char
                else:
                    end.append(part)
                    part = ""
            else:
                part+=char
        end.append(part)
        return list(dict.fromkeys(end[1:]))

    def onMessage(
        self, author_id, message_object, thread_id, thread_type, ts, **kwargs
    ):
        
        """DO NOT CALL"""
        print("got message")
        self.logger.debug("got message")
        if message_object.author == self.uid:
            print(message_object.author,"is",self.uid)
            return
        self.mid = message_object.uid
        try:
            #self.markAsDelivered(thread_id, message_object.uid)
            #self.markAsRead(thread_id)
            ...
        except:
            self.logger.warning("Failed to mark as read")
        self.thread = (thread_id, thread_type)
        print(self.thread)
        self.text = message_object.text
        print(self.text)
        #self.author = self.utils.getUserName(author_id)
        self.author = self.fetchUserInfo(author_id)[author_id].name
        print(self.author,self.text)
        if not self.text: 
            print("no text")
            if "onMessage" in self._event_list:
                t = threading.Thread(target=self._event_list["onMessage"],kwargs={"author_id":author_id,"message_object":message_object,"thread_id":thread_id,"thread_type":thread_type,"ts":ts})
                t.start()
            return

        if not self.text.startswith(self.Prefix):
            print(self.text,"doesn't start with",self.Prefix) 
            if "onMessage" in self._event_list:
                t = threading.Thread(target=self._event_list["onMessage"],kwargs={"author_id":author_id,"message_object":message_object,"thread_id":thread_id,"thread_type":thread_type,"ts":ts})
                t.start()
            return
        commandName = self.text.replace(self.Prefix, "", 1).split(" ")[0]
        args = list()
        _args = self.text.replace(self.Prefix, "", 1).replace(commandName, "", 1)
        parts = self._arg_split(_args)
        for part in parts:
            args.append(part)
        print(commandName,args)
        if not commandName in self._command_list:
            self.reply(f"{commandName} is an invalid command")
            raise CommandNotRegisteredException

        command = self._command_list[commandName][0]
        # argument separation
        argsdict = dict()
        for i, x in enumerate(self._command_list[commandName][1]):
            argsdict.update({x: args[i]})
        self.logger.info(f"calling command {command} in {self.thread[0]}")
        t = threading.Thread(
            target=command,
            kwargs={
                "text": self.text,
                "args": argsdict,
                "thread": self.thread,
                "author": self.author,
                "message": message_object,
                "ts": ts
            },
        )
        t.start()

    def onMessageUnsent(self, **kwargs):
        """DO NOT CALL (event handle)"""
        if "onMessageUnsent" in self._event_list:
            self._event_list["onMessageUnsent"](**kwargs)
            
    def on2FACode(self,**kwargs):
        """DO NOT CALL (event handle)"""
        if "on2FACode" in self._event_list:
                self._event_list["on2FACode"](**kwargs)

    def onAdminAdded(self,**kwargs):
        """DO NOT CALL (event handle)"""
        if "onAdminAdded" in self._event_list:
                self._event_list["onAdminAdded"](**kwargs)

    def onAdminRemoved(self,**kwargs):
        """DO NOT CALL (event handle)"""
        if "onAdminRemoved" in self._event_list:
                self._event_list["onAdminRemoved"](**kwargs)

    def onApprovalModeChange(self,**kwargs):
        """DO NOT CALL (event handle)"""
        if "onApprovalModeChange" in self._event_list:
                self._event_list["onApprovalModeChange"](**kwargs)

    def onBlock(self,**kwargs):
        """DO NOT CALL (event handle)"""
        if "onBlock" in self._event_list:
                self._event_list["onBlock"](**kwargs)

    def onBuddylistOverlay(self,**kwargs):
        """DO NOT CALL (event handle)"""
        if "onBuddylistOverlay" in self._event_list:
                self._event_list["onBuddylistOverlay"](**kwargs)

    def onCallEnded(self,**kwargs):
        """DO NOT CALL (event handle)"""
        if "onCallEnded" in self._event_list:
                self._event_list["onCallEnded"](**kwargs)

    def onCallStarted(self,**kwargs):
        """DO NOT CALL (event handle)"""
        if "onCallStarted" in self._event_list:
                self._event_list["onCallStarted"](**kwargs)

    def onChatTimestamp(self,**kwargs):
        """DO NOT CALL (event handle)"""
        if "onChatTimestamp" in self._event_list:
                self._event_list["onChatTimestamp"](**kwargs)

    def onColorChange(self,**kwargs):
        """DO NOT CALL (event handle)"""
        if "onColorChange" in self._event_list:
                self._event_list["onColorChange"](**kwargs)

    def onEmojiChange(self,**kwargs):
        """DO NOT CALL (event handle)"""
        if "onEmojiChange" in self._event_list:
                self._event_list["onEmojiChange"](**kwargs)

    def onFriendRequest(self,**kwargs):
        """DO NOT CALL (event handle)"""
        if "onFriendRequest" in self._event_list:
                self._event_list["onFriendRequest"](**kwargs)

    def onGamePlayed(self,**kwargs):
        """DO NOT CALL (event handle)"""
        if "onGamePlayed" in self._event_list:
                self._event_list["onGamePlayed"](**kwargs)

    def onImageChange(self,**kwargs):
        """DO NOT CALL (event handle)"""
        if "onImageChange" in self._event_list:
                self._event_list["onImageChange"](**kwargs)

    def onInbox(self,**kwargs):
        """DO NOT CALL (event handle)"""
        if "onInbox" in self._event_list:
                self._event_list["onInbox"](**kwargs)


    def onLiveLocation(self,**kwargs):
        """DO NOT CALL (event handle)"""
        if "onLiveLocation" in self._event_list:
                self._event_list["onLiveLocation"](**kwargs)

    def onLoggedIn(self,**kwargs):
        """DO NOT CALL (event handle)"""
        if "onLoggedIn" in self._event_list:
                self._event_list["onLoggedIn"](**kwargs)
            

    def onLoggingIn(self,**kwargs):
        """DO NOT CALL (event handle)"""
        if "onLoggingIn" in self._event_list:
                self._event_list["onLoggingIn"](**kwargs)

    def onMarkedSeen(self,**kwargs):
        """DO NOT CALL (event handle)"""
        if "onMarkedSeen" in self._event_list:
                self._event_list["onMarkedSeen"](**kwargs)


    def onMessageDelivered(self,**kwargs):
        """DO NOT CALL (event handle)"""
        if "onMessageDelivered" in self._event_list:
                self._event_list["onMessageDelivered"](**kwargs)

    def onMessageError(self,**kwargs):
        """DO NOT CALL (event handle)"""
        if "onMessageError" in self._event_list:
                self._event_list["onMessageError"](**kwargs)

    def onMessageSeen(self,**kwargs):
        """DO NOT CALL (event handle)"""
        if "onMessageSeen" in self._event_list:
                self._event_list["onMessageSeen"](**kwargs)

    def onMessageUnsent(self,**kwargs):
        """DO NOT CALL (event handle)"""
        if "onMessageUnsent" in self._event_list:
                self._event_list["onMessageUnsent"](**kwargs)

    def onNicknameChange(self,**kwargs):
        """DO NOT CALL (event handle)"""
        if "onNicknameChange" in self._event_list:
                self._event_list["onNicknameChange"](**kwargs)

    def onPendingMessage(self,**kwargs):
        """DO NOT CALL (event handle)"""
        if "onPendingMessage" in self._event_list:
                self._event_list["onPendingMessage"](**kwargs)

    def onPeopleAdded(self,**kwargs):
        """DO NOT CALL (event handle)"""
        if "onPeopleAdded" in self._event_list:
                self._event_list["onPeopleAdded"](**kwargs)

    def onPersonRemoved(self,**kwargs):
        """DO NOT CALL (event handle)"""
        if "onPersonRemoved" in self._event_list:
                self._event_list["onPersonRemoved"](**kwargs)

    def onPlanCreated(self,**kwargs):
        """DO NOT CALL (event handle)"""
        if "onPlanCreated" in self._event_list:
                self._event_list["onPlanCreated"](**kwargs)

    def onPlanDeleted(self,**kwargs):
        """DO NOT CALL (event handle)"""
        if "onPlanDeleted" in self._event_list:
                self._event_list["onPlanDeleted"](**kwargs)

    def onPlanEdited(self,**kwargs):
        """DO NOT CALL (event handle)"""
        if "onPlanEdited" in self._event_list:
                self._event_list["onPlanEdited"](**kwargs)

    def onPlanEnded(self,**kwargs):
        """DO NOT CALL (event handle)"""
        if "onPlanEnded" in self._event_list:
                self._event_list["onPlanEnded"](**kwargs)

    def onPlanParticipation(self,**kwargs):
        """DO NOT CALL (event handle)"""
        if "onPlanParticipation" in self._event_list:
                self._event_list["onPlanParticipation"](**kwargs)

    def onPollCreated(self,**kwargs):
        """DO NOT CALL (event handle)"""
        if "onPollCreated" in self._event_list:
                self._event_list["onPollCreated"](**kwargs)

    def onPollVoted(self,**kwargs):
        """DO NOT CALL (event handle)"""
        if "onPollVoted" in self._event_list:
                self._event_list["onPollVoted"](**kwargs)

    def onQprimer(self,**kwargs):
        """DO NOT CALL (event handle)"""
        if "onQprimer" in self._event_list:
                self._event_list["onQprimer"](**kwargs)

    def onReactionAdded(self,**kwargs):
        """DO NOT CALL (event handle)"""
        if "onReactionAdded" in self._event_list:
                self._event_list["onReactionAdded"](**kwargs)

    def onReactionRemoved(self,**kwargs):
        """DO NOT CALL (event handle)"""
        if "onReactionRemoved" in self._event_list:
                self._event_list["onReactionRemoved"](**kwargs)

    def onTitleChange(self,**kwargs):
        """DO NOT CALL (event handle)"""
        if "onTitleChange" in self._event_list:
                self._event_list["onTitleChange"](**kwargs)

    def onTyping(self,**kwargs):
        """DO NOT CALL (event handle)"""
        if "onTyping" in self._event_list:
                self._event_list["onTyping"](**kwargs)

    def onUnblock(self,**kwargs):
        """DO NOT CALL (event handle)"""
        if "onUnblock" in self._event_list:
                self._event_list["onUnblock"](**kwargs)

    def onUnknownMesssageType(self,**kwargs):
        """DO NOT CALL (event handle)"""
        if "onUnknownMesssageType" in self._event_list:
                self._event_list["onUnknownMesssageType"](**kwargs)

    def onUserJoinedCall(self,**kwargs):
        """DO NOT CALL (event handle)"""
        if "onUserJoinedCall" in self._event_list:
                self._event_list["onUserJoinedCall"](**kwargs)





    def sendmsg(self, text: str, thread: tuple = None) -> None:
        """Sends a Message

        Args:
            text (str): message content
            thread (tuple, optional): thread tuple. Defaults to None.
        """
        if thread is None:
            thread = self.thread
        thread_id, thread_type = thread
        self.send(Message(text=text), thread_id=thread_id, thread_type=thread_type)
    def reply(self, text: str, thread: tuple = None) -> tuple:
        """replies to a message

        Args:
            text (str): Message Content
            thread (tuple, optional): thread tuple. Defaults to None.

        Returns:
            tuple: thread tuple
        """
        if thread is None:
            thread = self.thread
        thread_id, thread_type = thread
        self.send(
            fbchat.Message(text=text, reply_to_id=self.mid),
            thread_id=thread_id,
            thread_type=thread_type,
        )
        return thread
    def sendFile(self, filepath, message: str = None, thread=None) -> tuple:
        """Sends file

        Args:
            filepath (_type_): path or link to the file
            message (str, optional): message to send with the file. Defaults to None.
            thread (_type_, optional): thread tuple. Defaults to None.

        """
        if thread is None:
            thread = self.thread
        thread_id, thread_type = thread
        if validators.url(filepath):
            self.sendRemoteFiles(filepath,message=message, thread_id=thread_id, thread_type=thread_type)
        else:
            self.sendLocalFiles(filepath, message=message, thread_id=thread_id, thread_type=thread_type)


    
    def utils_threadCount(self) -> int:
        """get current alive thread count

        Returns:
            int: current alive thread count
        """
        return len(threading.enumerate())
    
    
