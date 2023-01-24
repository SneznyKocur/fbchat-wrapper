# fbchat wrapper
[![Pylint](https://github.com/SneznyKocur/fbchat-wrapper/actions/workflows/pylint.yml/badge.svg)](https://github.com/SneznyKocur/fbchat-wrapper/actions/workflows/pylint.yml)
### example echo bot:
```
import fbchat_wrapper as fbw

client = fbw.Wrapper(prefix="!", email="", password="")

@client.Command("say", ["message"], "Sends Message")
def say(text,args,thread,author,message):
    if args:
        client.reply(args["message"])


client.listen()
```
