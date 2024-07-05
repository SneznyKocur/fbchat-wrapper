import validators,ffmpeg,os
from PIL import Image
from PIL import ImageDraw

from PIL import ImageFont
from py_fbchat.models import *
def isURL(input):
    """Check if input is url

        Args:
            input (str): input

        Returns:
            bool: is url?
        """
    return validators.url(input)

def compressVideo(input,output):
    """Compresses video to be sendable with messenger

        Args:
            input (str): input video file path
            output (str): output video file path
    """
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
        **{"c:v": "libx264", "b:v": video_bitrate, "pass": 1, "f": "mp4","loglevel":"error","-stats":""},
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
            "loglevel":"error",
            "-stats":""
        },
    ).overwrite_output().run()

def utils_genHelpImg(footer:str,Wrapper) -> str:
    """Generates help image from commands

    Args:
        footer (str, optional): _image footer. Defaults to None.

    Returns:
        str: file path
    """
    helpdict = dict()
    for x in Wrapper._command_list:
        helpdict.update(
            {
                x: {
                    "description": Wrapper._command_list[x][2],
                    "args": Wrapper._command_list[x][1],
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

        I1.text((0, (i + 1) * 10), name, (255, 255, 255), font) # name
    
        for y, x in enumerate(helpdict[name]["args"]):
            I1.text(((5+7*y) * 10, (i + 1) * 10), x, (255, 255, 0), font) # args

        I1.text(
            (4 * 20 + 100, (i + 1) * 10),
            helpdict[name]["description"],
            (255, 255, 255),
            font,
        )

    I1.text((0, 290), footer, (190, 255, 190), font)
    img.save("./help.png")
    return os.path.abspath("./help.png")

def utils_searchForUsers(query: str,Wrapper) -> list:
    """Searches for users

    Args:
        query (str): query to search for

    Returns:
        list: list of user ids
    """
    _ = []
    for user in Wrapper.searchForUsers(query):
        _.append(user.uid)
    return _

def utils_getIDFromUserIndex( userindex:str,Wrapper) -> int:
    """Fetches id of user @ userindex

    Args:
        userindex (str): username[index]

    Returns:
        int: user.uid
    """
    name = userindex.split("[")[0]
    ids = Wrapper.searchForUsers(name)
    return ids[int(userindex.split("[")[1].replace("]",""))]

def utils_getUserName( id: int,Wrapper):
    """Gets the username of user @ id

    Args:
        id (int): id of user
    Returns:
        str: username
    """
    return Wrapper.fetchUserInfo(id)[id].name

def utils_getThreadType(thread_id: int,Wrapper) -> ThreadType:
    """Gets threadtype of a thread @ thread_id

    Args:
        thread_id (int): the id

    Returns:
        ThreadType: type of thread
    """
    return Wrapper.fetchThreadInfo(thread_id)[thread_id].type
def utils_getThreadFromUserIndex(userindex: str,Wrapper) -> tuple:
    """Fetches thread from user @ userindex

    Args:
        userindex (str): username[index]

    Returns:
        tuple: thread tuple
    """
    if not userindex: return
    if userindex.isnumeric(): 
        thread_type = Wrapper.getThreadType(int(userindex))
        thread_id = userindex
        thread = (thread_id,thread_type)
    else:
        name = userindex.split("[")[0]
        ids = Wrapper.searchForUsers(name)
        thread_id = ids[int(userindex.split("[")[1].replace("]",""))]
        thread_type = Wrapper.getThreadType(int(thread_id)) 
        thread = (thread_id,thread_type)
    return thread
