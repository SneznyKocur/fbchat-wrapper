import fbchat

class Client(fbchat.Client):
    def __init__(self):
        self.listen()

    def onMessage(self,author_id,message_object, thread_id, thread_type, **kwargs):
        self.markAsDelivered(thread_id, message_object.uid)
        self.markAsRead(thread_id)
        self.thread = (thread_id,thread_type)
        text = message_object.text
        author = self.utils_getUserName(author_id)
        def wrapper(func):
            func(text, self.thread, author, message_object)

    def reply(text: str, thread: tuple = None):
        if thread is None:
            thread = self.thread
        self.send(text,thread)



    def utils_getUserName(id: int):
        self.fetchUserInfo(id)[id]