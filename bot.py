import asyncio
from io import BytesIO
from operator import itemgetter
import os
import random

import glitch
from PIL import Image
import requests
import telepot
from telepot.aio.delegate import pave_event_space, per_chat_id, create_open

import secrets


class GlitchChat(telepot.aio.helper.ChatHandler):
    async def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        self.the_file = None
        self.glitched_file = None

        if content_type == 'text':
            await self.bot.sendMessage(chat_id, msg['text'])
        elif content_type == 'photo':
            biggest_file = sorted(
                msg['photo'],
                key=itemgetter('file_size')
            )[-1]
            await self._get_the_file(biggest_file['file_id'])
            await self.glitch_the_image(self.the_file)
            if self.the_file is not None:
                await bot.sendPhoto(
                    chat_id,
                    open(self.glitched_file, 'rb')
                )

    async def _get_the_file(self, file_id):
        file_info = await self.bot.getFile(file_id)
        url = "https://api.telegram.org/file/bot{}/{}".format(
            secrets.TOKEN, file_info['file_path'])
        req = requests.get(url)
        if req.status_code == 200:
            im = Image.open(BytesIO(req.content))
            filename = "glitch_images/{}.jpg".format(file_id)
            im.save(filename, 'JPEG')
            self.the_file = filename
            return
        self.the_file = None
        return

    async def glitch_the_image(self, filename):
        glitcher = glitch.Glitch()
        dirless_filename = os.path.split(filename)[-1]
        extless_filename = os.path.splitext(dirless_filename)[0]
        glitcher.glitch(
            filename,
            "glitch_images/{}_glitched.jpg".format(extless_filename),
            times=5,
            mode=random.choice("ridsc")
        )

        files = list(filter(
            lambda f: extless_filename in f,
            os.listdir(path='glitch_images')
        ))
        self.glitched_file = "glitch_images/{}".format(random.choice(files))
        return


bot = telepot.aio.DelegatorBot(secrets.TOKEN, [
    pave_event_space()(
        per_chat_id(), create_open, GlitchChat, timeout=10
    )
])

loop = asyncio.get_event_loop()
loop.create_task(bot.message_loop())

print("Listening...")

loop.run_forever()
