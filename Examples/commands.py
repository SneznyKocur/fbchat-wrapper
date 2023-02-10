import fbchat_wrapper as fbw
from py_fbchat.models import * 

client = fbw.Wrapper(email="youremail@example.com",password="yourpassword",prefix="prefix") # replace with actual info

@client.Command("say", ["message"], "says stuff")
def say(args, **kwargs):
    client.reply(args["message"])

@client.Command("help", [], "show help")
def help(**kwargs):
    client.sendFile(client.utils_genHelpImg())
