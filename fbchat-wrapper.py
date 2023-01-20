import fbchat

class CommandNotRegisteredException(Exception):
    pass

class Client(fbchat.Client):
    def __init__(self, prefix = ""):
        self.listen()
        self._commandList = dict()
        self.Prefix = prefix or "!"

    

    def _addCommand(name: str, func):
        self._commandList.append({f"{name}":func)
        print(self._commandList)

    def registerCommand(self,**kwargs):
        def wrapper(func):
            self._addCommand(func.__name__, func)
        return wrapper


    def onMessage(self,author_id,message_object, thread_id, thread_type, **kwargs):
        self.mid = message_object.uid
        self.markAsDelivered(thread_id, message_object.uid)
        self.markAsRead(thread_id)
        self.thread = (thread_id,thread_type)
        self.text = message_object.text
        self.author = self.utils_getUserName(author_id)

        commandName = self.text.replace(self.Prefix, "", 1)

        if not commandName in self._commandList:
            raise CommandNotRegisteredException
        
        self._commandList[commandName](self.text, self.thread, self.author, message_object)
        

    def send(text: str, thread: tuple = None):
        if thread is None:
            thread = self.thread
        
        self.send(Message(text=text),thread)
    
    def reply(text: str, thread: tuple = None):
        if thread is None:
            thread = self.thread
        self.send(fbchat.Message(text=text, reply_to_id = mid))
        



    def utils_getUserName(id: int):
        self.fetchUserInfo(id)[id]