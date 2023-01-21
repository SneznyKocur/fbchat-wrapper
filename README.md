# fbchat wrapper

# example echo bot:
'''import fbchat_wrapper as fbw

client = fbw.Wrapper(prefix="!", email="", password="")

@client.Command()
def test(text,args,thread,author,message):
    client.reply(text)


client.listen()'''