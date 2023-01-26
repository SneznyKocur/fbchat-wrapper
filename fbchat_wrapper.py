"""
A simple wrapper for the fbchat library 
please use only with https://github.com/SneznyKocur/fbchat

Made with <3 by: SneznyKocur
"""


import os
import logging
import json
import threading
import datetime
import validators
import fbchat
from fbchat.models import Message
from PIL import Image
from PIL import ImageDraw

from PIL import ImageFont
import ffmpeg


class CommandNotRegisteredException(Exception):
    pass


class Wrapper(fbchat.Client):
    def __init__(self, email: str, password: str, prefix=""):
        logformat = "[%(levelname)s] [%(asctime)s]:  %(message)s"
        logging.basicConfig(
            format=logformat, datefmt="%m/%d/%Y %I:%M:%S", level=logging.INFO
        )
        self._command_list = dict()
        self.Prefix = prefix or "!"
        super(Wrapper, self).__init__(email, password)

    def _addCommand(self, name: str, func, args: list, description: str = None):
        self._command_list.update({f"{name}": [func, args, description]})

    def Command(self, name: str, args: list, description: str = None):
        def wrapper(func):
            self._addCommand(name, func, args, description)

        return wrapper

    def _arg_split(self, _args):
        part = ""
        for i, x in enumerate(_args.split(" ")[1:]):
            if x.startswith('"'):
                for chunk in _args.split(" ")[i + 1 :]:
                    if chunk.endswith('"'):
                        part += " " + chunk
                        break
                    part += " " + chunk
                    continue
                break    
            part += x
            break
        return part.replace('"', "")

    def onMessage(
        self, author_id, message_object, thread_id, thread_type, ts, **kwargs
    ):
        if message_object.author == self.uid:
            return
        logging.info(f"Succesfully Registered {len(self._command_list)} commands")
        self.mid = message_object.uid
        self.markAsDelivered(thread_id, message_object.uid)
        self.markAsRead(thread_id)
        self.thread = (thread_id, thread_type)
        self.text = message_object.text
        self.author = self.utils_getUserName(author_id)
        logging.info(f"Recieved {self.text} from {self.author}")

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
        _args = self.text.replace(self.Prefix, "", 1).replace(commandName, "", 1)
        part = self._arg_split(_args)
        args = list()
        args.append(part)

        if not commandName in self._command_list:
            self.reply(f"{commandName} is an invalid command")
            raise CommandNotRegisteredException

        command = self._command_list[commandName][0]

        # argument separation
        argsdict = dict()
        for i, x in enumerate(self._command_list[commandName][1]):
            argsdict.update({x: args[i]})

        t = threading.Thread(
            target=command,
            kwargs={
                "text": self.text,
                "args": argsdict,
                "thread": self.thread,
                "author": self.author,
                "message": message_object,
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

    def reply(self, text: str, thread: tuple = None):
        if thread is None:
            thread = self.thread
        thread_id, thread_type = thread
        self.send(
            fbchat.Message(text=text, reply_to_id=self.mid),
            thread_id=thread_id,
            thread_type=thread_type,
        )

    def sendFile(self, filepath, thread=None):
        if thread is None:
            thread = self.thread
        thread_id, thread_type = thread
        if validators.url(filepath):
            self.sendRemoteFiles(filepath, thread_id=thread_id, thread_type=thread_type)
        else:
            self.sendLocalFiles(filepath, thread_id=thread_id, thread_type=thread_type)

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
        return threading.activeCount()

    def utils_getUserName(self, id: int):
        return self.fetchUserInfo(id)[id].name

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

            I1.text((1 * 0, (i + 1) * 10), name, (255, 255, 255), font)
            for y, x in enumerate(helpdict[name]["args"]):
                I1.text(((2 + y) * 20 + 10, (i + 1) * 10), x, (255, 255, 0), font)
            I1.text(
                (3 * 20 + 50, (i + 1) * 10),
                helpdict[name]["description"],
                (255, 255, 255),
                font,
            )

        I1.text((220, 290), "marian3 beta", (190, 255, 190), font)
        img.save("./help.png")
        return "./help.png"
