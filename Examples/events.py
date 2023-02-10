import fbchat_wrapper as fbw
from py_fbchat.models import *

client = fbw.Wrapper(email="youremail@example.com",password="yourpassword",prefix="prefix") # replace with actual info

@client.Event
def onBlock(author_id,**kwargs): # arguments from https://fbchat.readthedocs.io/en/stable/api.html
    print(f"{fbw.Wrapper.utils_getUserName(author_id)} Blocked me :(")

@client.Event
def onUnBlock(author_id,**kwargs): # https://fbchat.readthedocs.io/en/stable/api.html
    print(f"{fbw.Wrapper.utils_getUserName(author_id)} Unblocked me :)")