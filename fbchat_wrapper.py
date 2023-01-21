import fbchat
from fbchat.models import *
import validators
import threading
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import ffmpeg
import os

class CommandNotRegisteredException(Exception):
    pass

class Wrapper(fbchat.Client):
    def __init__(self, email: str, password: str, prefix = ""):
        
        self._commandList = dict()
        self.Prefix = prefix or "!"
        super(Wrapper, self).__init__(email,password)
    def _addCommand(self, name: str, func, args: list, description: str = None):
        self._commandList.update({f"{name}":[func, args, description]})
        print(self._commandList)

    def Command(self,name: str, args: list, description: str = None):
        def wrapper(func):
            self._addCommand(name, func, args, description)
        return wrapper


    def _argSplit(self, _args):
        part = ""
        for i, x in enumerate(_args.split(" ")[1:]):
            if x.startswith('"'):
                
                for chunk in _args.split(" ")[i+1:]:
                    print(chunk)
                    if chunk.endswith('"'):
                        part+=" "+chunk
                        print("chunk ends")
                        break
                    else:
                        part+=" "+chunk
                        print("chunk continues")
                        continue
                break
            else:
                part += x 
                print(part)
            break
        return part.replace('"', "")

    def onMessage(self,author_id,message_object, thread_id, thread_type, **kwargs):
        if message_object.author == self.uid:
            return
        self.mid = message_object.uid
        self.markAsDelivered(thread_id, message_object.uid)
        self.markAsRead(thread_id)
        self.thread = (thread_id,thread_type)
        self.text = message_object.text
        self.author = self.utils_getUserName(author_id)

        if not self.text.startswith(self.Prefix):
            return

        commandName = self.text.replace(self.Prefix, "", 1).split(" ")[0]
        _args=self.text.replace(self.Prefix, "", 1).replace(commandName, "", 1)
        part = self._argSplit(_args)
        args = list()
        args.append(part)

            
        if not commandName in self._commandList:
            self.reply(f"{commandName} is an invalid command")
            raise CommandNotRegisteredException
        
        command = self._commandList["commands"][commandName][0]

        # argument separation
        argsdict = dict()
        for i,x in enumerate(self._commandList[commandName][1]):
            argsdict.update({x:args[i]})
        

        t = threading.Thread(target=command,args=(self.text, argsdict,  self.thread, self.author, message_object))
        t.start()
            

    def sendmsg(self, text: str, thread: tuple = None):
        if thread is None:
            thread = self.thread
        thread_id, thread_type = thread
        self.send(Message(text=text),thread_id=thread_id,thread_type=thread_type)
    
    def reply(self, text: str, thread: tuple = None):
        if thread is None:
            thread = self.thread
        print(self.mid)    
        thread_id, thread_type = thread
        self.send(fbchat.Message(text=text,reply_to_id=self.mid),thread_id=thread_id,thread_type=thread_type)
        
    def sendFile(self, filepath, thread):
        if thread is None:
            thread = self.thread   
        thread_id, thread_type = thread
        if validators.url(filepath):
            self.sendRemoteFiles(filepath, thread_id=thread_id, thread_type=thread_type)
        else:
            self.sendLocalFiles(filepath, thread_id=thread_id, thread_type=thread_type)





    def utils_compressVideo(input, output):
        import ffmpeg
        # Reference: https://en.wikipedia.org/wiki/Bit_rate#Encoding_bit_rate
        min_audio_bitrate = 32000
        max_audio_bitrate = 256000

        probe = ffmpeg.probe(input,cmd="./ffprobe")
        # Video duration, in s.
        duration = float(probe['format']['duration'])
        # Audio bitrate, in bps.
        audio_bitrate = float(next(
            (s for s in probe['streams'] if s['codec_type'] == 'audio'), None)['bit_rate'])
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
        ffmpeg.output(i, os.devnull,
                    **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 1, 'f': 'mp4'}
                    ).overwrite_output().run()
        ffmpeg.output(i, output,
                    **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 2, 'c:a': 'aac', 'b:a': audio_bitrate}
                    ).overwrite_output().run()

    def utils_threadCount(self) -> int:
        return threading.activeCount()

    def utils_getUserName(self, id: int):
        return self.fetchUserInfo(id)[id].name

    def utils_genHelpImg(self) -> str:
        helpdict = dict(commands={})
        for x in self._commandList:
            helpdict["commands"].update({
                "name":x, 
                "description":self._commandList[x][2],
                "args":self._commandList[x][1]})
        
        Commands = self._commandList.keys()
        # desciption = 2
        # args = 1
        # func = 0

        # TODO: add image generationň
        img = Image.new('RGBA', (300, 300), color = (20,20, 20))
        I1 = ImageDraw.Draw(img)
        font = ImageFont.truetype("./font.ttf")

        for i, name in enumerate(helpdict["commands"]["name"]):
            I1.text((1*20,(i+1)*10),name,(255,255,255),font)
            