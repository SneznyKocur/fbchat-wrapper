"""
A simple wrapper for the fbchat library 
please use only with https://github.com/SneznyKocur/fbchat
Works only with python 3.8.*

Please Contribute as my code probably sucks :/

Made with <3 by: SneznyKocur
"""


import os
import json
import threading
import datetime
import validators
import fbchat
from fbchat.models import Message, ThreadType
from PIL import Image
from PIL import ImageDraw

from PIL import ImageFont
import ffmpeg


class CommandNotRegisteredException(Exception):
    pass


class Wrapper(fbchat.Client):
    def __init__(self, email: str, password: str, prefix=""):
        self._command_list = dict()
        self.Prefix = prefix or "!"
        super(Wrapper, self).__init__(email, password)

    def _addCommand(self, name: str, func, args: list, description: str = None):
        self._command_list.update({f"{name}": [func, args, description]})

    def Command(self, name: str, args: list, description: str = None):
        def wrapper(func):
            self._addCommand(name, func, args, description)

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
        if author_id != self.uid:
            with open(os.getcwd() + "/messages.txt", "r") as f:
                lol = json.load(f)
                lol["messages"][mid]["UNSENT"] = True

            with open(os.getcwd() + "/messages.txt", "w", encoding="utf-8") as f:
                json.dump(lol, f)

    def sendmsg(self, text: str, thread: tuple = None):
        if thread is None:
            thread = self.thread
        thread_id, thread_type = thread
        self.send(Message(text=text), thread_id=thread_id, thread_type=thread_type)

    def reply(self, text: str, thread: tuple = None) -> tuple:
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
        if thread is None:
            thread = self.thread
        thread_id, thread_type = thread
        if validators.url(filepath):
            self.sendRemoteFiles(filepath,message=message, thread_id=thread_id, thread_type=thread_type)
        else:
            self.sendLocalFiles(filepath, message=message, thread_id=thread_id, thread_type=thread_type)

    def utils_isURL(self, input):
        return validators.url(input)
    def utils_compressVideo(self, input, output):
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
        return len(threading.enumerate())
    def utils_getUserName(self, id: int):
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
        return self.fetchThreadInfo(thread_id)[thread_id].type

    def utils_getThreadFromUserIndex(self,id: str) -> tuple:
        if not id: return
        if id.isnumeric(): 
            thread_type = self.utils_getThreadType(int(id))
            thread_id = id
            thread = (thread_id,thread_type)
        else:
            name = id.split("[")[0]
            ids = self.utils_searchForUsers(name)
            thread_id = ids[int(id.split("[")[1].replace("]",""))]
            thread_type = self.utils_getThreadType(int(thread_id)) 
            thread = (thread_id,thread_type)
        return thread
    def utils_getIDFromUserIndex(self, id:str) -> int:
        name = id.split("[")[0]
        ids = self.utils_searchForUsers(name)
        return ids[int(id.split("[")[1].replace("]",""))]
    def utils_genHelpImg(self) -> str:
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
