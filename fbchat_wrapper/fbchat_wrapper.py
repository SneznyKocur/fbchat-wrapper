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
        
        _setup()
        self._command_list = dict()
        self._event_list = dict()
        self.Prefix = prefix or "!"
        print("logging in")
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
        """DO NOT CALL (event handle)"""
        print("got message")
        if message_object.author == self.uid:
            return
        self.mid = message_object.uid
        try:
            self.markAsDelivered(thread_id, message_object.uid)
            self.markAsRead(thread_id)
        except:
            print("Failed to mark as read")
        self.thread = (thread_id, thread_type)
        self.text = message_object.text
        self.author = self.utils.getUserName(author_id)

        if not self.text: return

        if not self.text.startswith(self.Prefix):
            if "onMessage" in self._event_list:
                self._event_list["onMessage"](author_id=author_id,message_object=message_object,thread_id=thread_id,thread_type=thread_type,ts=ts,**kwargs)
            return
        commandName = self.text.replace(self.Prefix, "", 1).split(" ")[0]
        args = list()
        _args = self.text.replace(self.Prefix, "", 1).replace(commandName, "", 1)
        parts = self._arg_split(_args)
        for part in parts:
            args.append(part)

        if not commandName in self._command_list:
            self.reply(f"{commandName} is an invalid command")
            raise CommandNotRegisteredException

        command = self._command_list[commandName][0]
        # argument separation
        argsdict = dict()
        for i, x in enumerate(self._command_list[commandName][1]):
            argsdict.update({x: args[i]})
        print(f"calling command {command} in {self.thread[0]}")
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

    def utils_isURL(self, input):
        """Check if input is url

        Args:
            input (str): input

        Returns:
            bool: is url?
        """
        return validators.url(input)
    def utils_compressVideo(self, input, output):
        """Compresses video to be sendable with messenger

        Args:
            input (str): input video file path
            output (str): output video file path
        """
        # Reference: https://en.wikipedia.org/wiki/Bit_rate#Encoding_bit_rate
        min_audio_bitrate = 32000
        max_audio_bitrate = 256000

        probe = ffmpeg.probe(input)
        # Video duration, in s.
        duration = float(probe["format"]["duration"])
        # Audio bitrate, in bps.
        audio_bitrate = float(
            next((s for s in probe["streams"] if s["codec_type"] == "audio"), None)[
                "bit_rate"
            ]
        )
        # Target total bitrate, in bps.
        target_total_bitrate = (50000 * 1024 * 8) / (1.073741824 * duration)

        # Target audio bitrate, in bps
        if 10 * audio_bitrate > target_total_bitrate:
            audio_bitrate = target_total_bitrate / 10
            if audio_bitrate < min_audio_bitrate < target_total_bitrate:
                audio_bitrate = min_audio_bitrate
            elif audio_bitrate > max_audio_bitrate:
                audio_bitrate = max_audio_bitrate
        # Target video bitrate, in bps.
        video_bitrate = target_total_bitrate - audio_bitrate

        i = ffmpeg.input(input)
        ffmpeg.output(
            i,
            os.devnull,
            **{"c:v": "libx264", "b:v": video_bitrate, "pass": 1, "f": "mp4"},
        ).overwrite_output().run()
        ffmpeg.output(
            i,
            output,
            **{
                "c:v": "libx264",
                "b:v": video_bitrate,
                "pass": 2,
                "c:a": "aac",
                "b:a": audio_bitrate,
            },
        ).overwrite_output().run()
    def utils_threadCount(self) -> int:
        """get current alive thread count

        Returns:
            int: current alive thread count
        """
        return len(threading.enumerate())
    def utils_genHelpImg(self,footer:str = None) -> str:
        """Generates help image from commands

        Args:
            footer (str, optional): _image footer. Defaults to None.

        Returns:
            str: file path
        """
        helpdict = dict()
        for x in self._command_list:
            helpdict.update(
                {
                    x: {
                        "description": self._command_list[x][2],
                        "args": self._command_list[x][1],
                    }
                }
            )
        # desciption = 2
        # args = 1
        # func = 0

        img = Image.new("RGBA", (300, 300), color=(20, 20, 20))
        I1 = ImageDraw.Draw(img)
        font = ImageFont.truetype("./font.ttf")

        for i, name in enumerate(helpdict):

            I1.text((0, (i + 1) * 10), name, (255, 255, 255), font) # name
        
            for y, x in enumerate(helpdict[name]["args"]):
                I1.text(((5+7*y) * 10, (i + 1) * 10), x, (255, 255, 0), font) # args

            I1.text(
                (4 * 20 + 100, (i + 1) * 10),
                helpdict[name]["description"],
                (255, 255, 255),
                font,
            )

        I1.text((0, 290), footer, (190, 255, 190), font)
        img.save("./help.png")
        return os.path.abspath("./help.png")

    def utils_searchForUsers(self,query: str) -> list:
        """Searches for users

        Args:
            query (str): query to search for

        Returns:
            list: list of user ids
        """
        _ = []
        for user in self.searchForUsers(query):
            _.append(user.uid)
        return _

    def utils_getIDFromUserIndex(self, userindex:str) -> int:
        """Fetches id of user @ userindex

        Args:
            userindex (str): username[index]

        Returns:
            int: user.uid
        """
        name = userindex.split("[")[0]
        ids = self.searchForUsers(name)
        return ids[int(userindex.split("[")[1].replace("]",""))]
    
    def utils_getUserName(self, id: int):
        """Gets the username of user @ id

        Args:
            id (int): id of user
        Returns:
            str: username
        """
        return self.fetchUserInfo(id)[id].name
    
    def utils_getThreadType(self,thread_id: int) -> ThreadType:
        """Gets threadtype of a thread @ thread_id

        Args:
            thread_id (int): the id

        Returns:
            ThreadType: type of thread
        """
        return self.fetchThreadInfo(thread_id)[thread_id].type
    def utils_getThreadFromUserIndex(self,userindex: str) -> tuple:
        """Fetches thread from user @ userindex

        Args:
            userindex (str): username[index]

        Returns:
            tuple: thread tuple
        """
        if not userindex: return
        if userindex.isnumeric(): 
            thread_type = self.getThreadType(int(userindex))
            thread_id = userindex
            thread = (thread_id,thread_type)
        else:
            name = userindex.split("[")[0]
            ids = self.searchForUsers(name)
            thread_id = ids[int(userindex.split("[")[1].replace("]",""))]
            thread_type = self.getThreadType(int(thread_id)) 
            thread = (thread_id,thread_type)
        return thread