# Fbchat-wrapper

## A simple library to make programming in fbchat easier

## Installation:
```
pip install fbchat-wrapper
```

### example echo bot

```
import fbchat_wrapper as fbw

client = fbw.Wrapper(prefix="!", email="", password="")

@client.Command("say", ["message"], "Sends Message")
def say(args,**kwargs):
    if args:
        client.reply(args["message"])


client.listen()
```

Made with <3 by:

```
 ____                               _  __
/ ___| _ __   ___ _____ __  _   _  | |/ /___   ___ _   _ _ __
\___ \| '_ \ / _ \_  / '_ \| | | | | ' // _ \ / __| | | | '__|
 ___) | | | |  __// /| | | | |_| | | . \ (_) | (__| |_| | |
|____/|_| |_|\___/___|_| |_|\__, | |_|\_\___/ \___|\__,_|_|
                            |___/
```
