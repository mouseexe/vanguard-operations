import discord
import os
from datetime import datetime

# Token is a secret stored on okd
TOKEN = os.environ.get('DISCORDTOKEN', 'default value')

client = discord.Client()


def get_time_elapsed(time, now):
    if now >= time:
        return now - time
    return (now + 60) - time


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
        msg = ''
        if time == "" or get_time_elapsed(int(time), int(minute)) >= 30:
            timestamp = open('timestamp', 'w')
            timestamp.write(minute)
            # times seem to be four hours ahead
            # 2 AM to 8 AM
            if 6 <= hour < 12:
                msg = 'This will ping the morning shift.'
            # 8 AM to 5 PM
            if 12 <= hour < 21:
                msg = 'This will ping the day shift.'
            # 5 PM to 10 PM
            if 21 <= hour < 24 or 0 <= hour < 2:
                msg = 'This will ping the evening shift.'
            # 10 PM to 2 AM
            if 2 <= hour < 6:
                msg = 'This will ping the night shift.'
            await message.channel.send(msg)
        else:
            await message.channel.send('Someone else pinged too recently! You can ping again in' + str(get_time_elapsed(int(time), int(minute))) + 'minutes.')


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


client.run(TOKEN)
