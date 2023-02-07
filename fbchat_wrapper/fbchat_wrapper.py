"""
A simple wrapper for the fbchat library 
please use only with https://github.com/SneznyKocur/fbchat (pip install py-fbchat)
Works only with python 3.8.*

Please Contribute as my code probably sucks :/

Made with <3 by: SneznyKocur
"""


import os
import json
import threading
import datetime
import validators
import py_fbchat as fbchat
from py_fbchat.models import Message, ThreadType
from PIL import Image
from PIL import ImageDraw

from PIL import ImageFont
import ffmpeg
from zipfile import ZipFile
import wget

def setup():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    if not "ffmpeg.exe" in os.listdir() or not "font.ttf" in os.listdir():
        print("Downloading ffmpeg")
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
        setup()
        self._command_list = dict()
        self._event_list = dict()
        self.Prefix = prefix or "!"
        super(Wrapper, self).__init__(email, password)

    def _addEvent(self,name,func):
        self._event_list.update({f"{name}":func})

    def _addCommand(self, name: str, func, args: list, description: str = None):
        self._command_list.update({f"{name}": [func, args, description]})

    def Command(self, name: str, args: list, description: str = None):
        """
        Registers a Command
        """
        def wrapper(func):
            self._addCommand(name, func, args, description)

        return wrapper

    def Event(self):
        """
        Registers an Event
        """
        def wrapper(func):
            self._addEvent(func.__name__, func)
    
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
        self.author = self.utils_getUserName(author_id)

        if not self.text: return
        # logging
        with open(os.getcwd() + "/messages.txt", "r") as f:
            lol = json.load(f)

            lol["messages"].update(
                {
                    message_object.uid: {
                        message_object.text: self.utils_getUserName(author_id),
                        "time": datetime.datetime.fromtimestamp(ts // 1000).isoformat(),
                        "unsent": False,
                        "Version": f"marian3 beta",
                    }
                }
            )
        with open(os.getcwd() + "/messages.txt", "w", encoding="utf-8") as f:
            json.dump(lol, f, indent=1)

        if not self.text.startswith(self.Prefix):
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

    def onMessageUnsent(self, mid, author_id, thread_id, thread_type, ts, msg):
        # logging
        if author_id != self.uid:
            with open(os.getcwd() + "/messages.txt", "r") as f:
                lol = json.load(f)
                lol["messages"][mid]["UNSENT"] = True

            with open(os.getcwd() + "/messages.txt", "w", encoding="utf-8") as f:
                json.dump(lol, f)
    def on2FACode(self,**kwargs):
        if "on2FACode" in self._event_list:
                self._event_list["on2FACode"](**kwargs)

    def onAdminAdded(self,**kwargs):
        if "onAdminAdded" in self._event_list:
                self._event_list["onAdminAdded"](**kwargs)

    def onAdminRemoved(self,**kwargs):
        if "onAdminRemoved" in self._event_list:
                self._event_list["onAdminRemoved"](**kwargs)

    def onApprovalModeChange(self,**kwargs):
        if "onApprovalModeChange" in self._event_list:
                self._event_list["onApprovalModeChange"](**kwargs)

    def onBlock(self,**kwargs):
        if "onBlock" in self._event_list:
                self._event_list["onBlock"](**kwargs)

    def onBuddylistOverlay(self,**kwargs):
        if "onBuddylistOverlay" in self._event_list:
                self._event_list["onBuddylistOverlay"](**kwargs)

    def onCallEnded(self,**kwargs):
        if "onCallEnded" in self._event_list:
                self._event_list["onCallEnded"](**kwargs)

    def onCallStarted(self,**kwargs):
        if "onCallStarted" in self._event_list:
                self._event_list["onCallStarted"](**kwargs)

    def onChatTimestamp(self,**kwargs):
        if "onChatTimestamp" in self._event_list:
                self._event_list["onChatTimestamp"](**kwargs)

    def onColorChange(self,**kwargs):
        if "onColorChange" in self._event_list:
                self._event_list["onColorChange"](**kwargs)

    def onEmojiChange(self,**kwargs):
        if "onEmojiChange" in self._event_list:
                self._event_list["onEmojiChange"](**kwargs)

    def onFriendRequest(self,**kwargs):
        if "onFriendRequest" in self._event_list:
                self._event_list["onFriendRequest"](**kwargs)

    def onGamePlayed(self,**kwargs):
        if "onGamePlayed" in self._event_list:
                self._event_list["onGamePlayed"](**kwargs)

    def onImageChange(self,**kwargs):
        if "onImageChange" in self._event_list:
                self._event_list["onImageChange"](**kwargs)

    def onInbox(self,**kwargs):
        if "onInbox" in self._event_list:
                self._event_list["onInbox"](**kwargs)

    def onListenError(self,**kwargs):
        if "onListenError" in self._event_list:
                self._event_list["onListenError"](**kwargs)

    def onListening(self,**kwargs):
        if "onListening" in self._event_list:
                self._event_list["onListening"](**kwargs)

    def onLiveLocation(self,**kwargs):
        if "onLiveLocation" in self._event_list:
                self._event_list["onLiveLocation"](**kwargs)

    def onLoggedIn(self,**kwargs):
        if "onLoggedIn" in self._event_list:
                self._event_list["onLoggedIn"](**kwargs)

    def onLoggingIn(self,**kwargs):
        if "onLoggingIn" in self._event_list:
                self._event_list["onLoggingIn"](**kwargs)

    def onMarkedSeen(self,**kwargs):
        if "onMarkedSeen" in self._event_list:
                self._event_list["onMarkedSeen"](**kwargs)

    def onMessage(self,**kwargs):
        if "onMessage" in self._event_list:
                self._event_list["onMessage"](**kwargs)

    def onMessageDelivered(self,**kwargs):
        if "onMessageDelivered" in self._event_list:
                self._event_list["onMessageDelivered"](**kwargs)

    def onMessageError(self,**kwargs):
        if "onMessageError" in self._event_list:
                self._event_list["onMessageError"](**kwargs)

    def onMessageSeen(self,**kwargs):
        if "onMessageSeen" in self._event_list:
                self._event_list["onMessageSeen"](**kwargs)

    def onMessageUnsent(self,**kwargs):
        if "onMessageUnsent" in self._event_list:
                self._event_list["onMessageUnsent"](**kwargs)

    def onNicknameChange(self,**kwargs):
        if "onNicknameChange" in self._event_list:
                self._event_list["onNicknameChange"](**kwargs)

    def onPendingMessage(self,**kwargs):
        if "onPendingMessage" in self._event_list:
                self._event_list["onPendingMessage"](**kwargs)

    def onPeopleAdded(self,**kwargs):
        if "onPeopleAdded" in self._event_list:
                self._event_list["onPeopleAdded"](**kwargs)

    def onPersonRemoved(self,**kwargs):
        if "onPersonRemoved" in self._event_list:
                self._event_list["onPersonRemoved"](**kwargs)

    def onPlanCreated(self,**kwargs):
        if "onPlanCreated" in self._event_list:
                self._event_list["onPlanCreated"](**kwargs)

    def onPlanDeleted(self,**kwargs):
        if "onPlanDeleted" in self._event_list:
                self._event_list["onPlanDeleted"](**kwargs)

    def onPlanEdited(self,**kwargs):
        if "onPlanEdited" in self._event_list:
                self._event_list["onPlanEdited"](**kwargs)

    def onPlanEnded(self,**kwargs):
        if "onPlanEnded" in self._event_list:
                self._event_list["onPlanEnded"](**kwargs)

    def onPlanParticipation(self,**kwargs):
        if "onPlanParticipation" in self._event_list:
                self._event_list["onPlanParticipation"](**kwargs)

    def onPollCreated(self,**kwargs):
        if "onPollCreated" in self._event_list:
                self._event_list["onPollCreated"](**kwargs)

    def onPollVoted(self,**kwargs):
        if "onPollVoted" in self._event_list:
                self._event_list["onPollVoted"](**kwargs)

    def onQprimer(self,**kwargs):
        if "onQprimer" in self._event_list:
                self._event_list["onQprimer"](**kwargs)

    def onReactionAdded(self,**kwargs):
        if "onReactionAdded" in self._event_list:
                self._event_list["onReactionAdded"](**kwargs)

    def onReactionRemoved(self,**kwargs):
        if "onReactionRemoved" in self._event_list:
                self._event_list["onReactionRemoved"](**kwargs)

    def onTitleChange(self,**kwargs):
        if "onTitleChange" in self._event_list:
                self._event_list["onTitleChange"](**kwargs)

    def onTyping(self,**kwargs):
        if "onTyping" in self._event_list:
                self._event_list["onTyping"](**kwargs)

    def onUnblock(self,**kwargs):
        if "onUnblock" in self._event_list:
                self._event_list["onUnblock"](**kwargs)

    def onUnknownMesssageType(self,**kwargs):
        if "onUnknownMesssageType" in self._event_list:
                self._event_list["onUnknownMesssageType"](**kwargs)

    def onUserJoinedCall(self,**kwargs):
        if "onUserJoinedCall" in self._event_list:
                self._event_list["onUserJoinedCall"](**kwargs)





    def sendmsg(self, text: str, thread: tuple = None) -> None:
        """
        Sends a Message to a thread
        if thread is None, thread is the thread of the last message sent

        """
        if thread is None:
            thread = self.thread
        thread_id, thread_type = thread
        self.send(Message(text=text), thread_id=thread_id, thread_type=thread_type)
    def reply(self, text: str, thread: tuple = None) -> tuple:
        """
        Replies to last message sent 
        if thread is None, thread is the thread of the last message sent

        Returns thread tuple
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
        """
        Sends File to a thread
        if thread is None, thread is the thread of the last message sent

        Returns thread tuple
        """
        if thread is None:
            thread = self.thread
        thread_id, thread_type = thread
        if validators.url(filepath):
            self.sendRemoteFiles(filepath,message=message, thread_id=thread_id, thread_type=thread_type)
        else:
            self.sendLocalFiles(filepath, message=message, thread_id=thread_id, thread_type=thread_type)



    def utils_isURL(self, input):
        """
        Returns True if input is url
        """
        return validators.url(input)
    def utils_compressVideo(self, input, output):
        """
        Compresses video to be sendable with messenger
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
        """
        Returns current alive thread count
        """
        return len(threading.enumerate())
    def utils_getUserName(self, id: int):
        """
        Gets the username of a user
        """
        return self.fetchUserInfo(id)[id].name

    def utils_searchForUsers(self,query: str) -> list:
        """
        returns list of user ids for the query
        """
        _ = []
        for user in self.searchForUsers(query):
            _.append(user.uid)
        return _
    def utils_getThreadType(self,thread_id: int) -> ThreadType:
        """
        Fetches the threadtype of a thread
        """
        return self.fetchThreadInfo(thread_id)[thread_id].type

    def utils_getThreadFromUserIndex(self,userindex: str) -> tuple:
        """
        Fetches the thread ID of user[index]
        """
        if not userindex: return
        if userindex.isnumeric(): 
            thread_type = self.utils_getThreadType(int(userindex))
            thread_id = userindex
            thread = (thread_id,thread_type)
        else:
            name = userindex.split("[")[0]
            ids = self.utils_searchForUsers(name)
            thread_id = ids[int(userindex.split("[")[1].replace("]",""))]
            thread_type = self.utils_getThreadType(int(thread_id)) 
            thread = (thread_id,thread_type)
        return thread
    def utils_getIDFromUserIndex(self, userindex:str) -> int:
        """
        Fetches the ID of user[index]
        """
        name = userindex.split("[")[0]
        ids = self.utils_searchForUsers(name)
        return ids[int(userindex.split("[")[1].replace("]",""))]
    def utils_genHelpImg(self) -> str:
        """
        Generates a help.png image with all registered commands
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

        I1.text((0, 290), "marian3 v1.0.0, made with <3 by SneznyKocur", (190, 255, 190), font)
        img.save("./help.png")
        return "./help.png"

