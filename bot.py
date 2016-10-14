from io import BytesIO
from operator import itemgetter
import os
import random
import time

import glitch
from PIL import Image
import requests
import telepot

import secrets


def _get_the_file(bot, file_id):
    file_info = bot.getFile(file_id)
    url = "https://api.telegram.org/file/bot{}/{}".format(
        secrets.TOKEN, file_info['file_path'])
    req = requests.get(url)
    if req.status_code == 200:
        im = Image.open(BytesIO(req.content))
        filename = "glitch_images/{}.jpg".format(file_id)
        im.save(filename, 'JPEG')
        return filename
    return None


def glitch_the_image(filename):
    glitcher = glitch.Glitch()
    dirless_filename = os.path.split(filename)[-1]
    extless_filename = os.path.splitext(dirless_filename)[0]
    glitcher.glitch(
        filename,
        "glitch_images/{}_glitched.jpg".format(extless_filename),
        times=5,
        mode="i"
    )

    files = list(filter(
        lambda f: extless_filename in f,
        os.listdir(path='glitch_images')
    ))
    return "glitch_images/{}".format(random.choice(files))


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)

    if content_type == 'text':
        bot.sendMessage(chat_id, msg['text'])
    elif content_type == 'photo':
        biggest_file = sorted(msg['photo'], key=itemgetter('file_size'))[-1]
        the_file = _get_the_file(bot, biggest_file['file_id'])
        glitched_file = glitch_the_image(the_file)
        if the_file is not None:
            bot.sendPhoto(
                chat_id,
                open(glitched_file, 'rb')
            )

bot = telepot.Bot(secrets.TOKEN)
bot.message_loop(handle)

print("Listening...")

while 1:
    time.sleep(10)
