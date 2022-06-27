import discord
import os
from datetime import datetime

# Token is a secret stored on okd
TOKEN = os.environ.get('DISCORDTOKEN', 'default value')

client = discord.Client()


def is_time_elapsed(time, now):
    if now > time:
        return now - time >= 30
    return (now + 60) - time >= 30


@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if 'test' in message.content:
        timestamp = open('timestamp', 'r')
        time = timestamp.read()
        timestamp.close()
        minute = datetime.now().strftime('%M')
        hour = int(datetime.now().strftime('%H'))
        fulltime = datetime.now().strftime('%H:%M')
        msg = ''
        if time == "" or is_time_elapsed(int(time), int(minute)):
            timestamp = open('timestamp', 'w')
            timestamp.write(minute)
            if 2 <= hour < 8:
                msg = 'morning shift'
            if 8 <= hour < 17:
                msg = 'day shift'
            if 17 <= hour < 22:
                msg = 'evening shift'
            if 22 <= hour < 24 or 0 <= hour < 2:
                msg = 'night shift'
            await message.channel.send(msg)
        else:
            await message.channel.send(fulltime)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


client.run(TOKEN)
