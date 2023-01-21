import fbchat
from fbchat.models import *
class CommandNotRegisteredException(Exception):
    pass

class Wrapper(fbchat.Client):
    def __init__(self, email: str, password: str, prefix = ""):
        
        self._commandList = dict()
        self.Prefix = prefix or "!"
        super(Wrapper, self).__init__(email,password)
    def _addCommand(self, name: str, func):
        self._commandList.update({f"{name}":func})
        print(self._commandList)

    def Command(self,**kwargs):
        def wrapper(func):
            self._addCommand(func.__name__, func)
        return wrapper


    def onMessage(self,author_id,message_object, thread_id, thread_type, **kwargs):
        if message_object.author != self.uid:
            self.mid = message_object.uid
            self.markAsDelivered(thread_id, message_object.uid)
            self.markAsRead(thread_id)
            self.thread = (thread_id,thread_type)
            self.text = message_object.text
            self.author = self.utils_getUserName(author_id)

            if not self.text.startswith(self.Prefix):
                return

            commandName = self.text.replace(self.Prefix, "", 1).split(" ")[0]
            args=self.text.replace(self.Prefix, "", 1).split(" ")[1:]

            if not commandName in self._commandList:
                print(self._commandList, commandName)
                raise CommandNotRegisteredException
            
            command = self._commandList[commandName]
            command(self.text, args,  self.thread, self.author, message_object)
            

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
        



    def utils_getUserName(self, id: int):
        return self.fetchUserInfo(id)[id].name