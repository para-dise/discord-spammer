#!/usr/bin/env python3

from configparser import SafeConfigParser
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial
import asyncio
import discord
import sys
import threading

MAIN_THREAD = threading.current_thread()
parser = SafeConfigParser()
parser.read("settings.ini")

CONTROLLER_ID = parser.get("dcspam", "controller")
TOKENFILE = parser.get("dcspam", "tokens")
PRESENCE = parser.get("dcspam", "presence")
MESSAGE = parser.get("dcspam", "message")
try:
    MSG_COUNT = int(parser.get("dcspam", "message_count"))
except ValueError:
    MSG_COUNT = 10

def create_bot(token):
    if threading.current_thread() != MAIN_THREAD:
        asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()
    akeno = discord.Client(loop=loop)

    @akeno.event
    async def on_ready():
        print(akeno.user.name)
        await akeno.change_presence(game=discord.Game(name=PRESENCE), status=None, afk=False)

    @akeno.event
    async def on_message(message):
        if message.author.id != CONTROLLER_ID:
            return
        if not message.content.startswith('$flood '):
            return
        tuser = message.content[7:]
        target_user = tuser
        print(target_user)
        for i in range(MSG_COUNT):
            await akeno.send_message(akeno.get_channel(target_user), MESSAGE)
            await asyncio.sleep(0.5)

    akeno.run(token, bot=False)

with open(TOKENFILE) as f:
    tokens = [line.rstrip() for line in f]
pool = ThreadPoolExecutor(len(tokens))
futures = [pool.submit(partial(create_bot, token)) for token in tokens]
for x in as_completed(futures):
    print(x.exception())
