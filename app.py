import discord
import os
from datetime import datetime

# Token is a secret stored on okd
TOKEN = os.environ.get('DISCORDTOKEN', 'default value')

client = discord.Client()

cadence = 30


# that was then, this is now
def get_time_elapsed(that, this):
    delta = this - that
    return delta.total_seconds() / 60


def write(message):
    timestamp = open('timestamp', 'w')
    timestamp.write(message)
    timestamp.close()


@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    # reset clock if admin wants to
    if message.content == '/reset' and message.author.guild_permissions.administrator:
        write('override')
        await message.add_reaction('✔')

    # This is the ID for the Vanguard Operations bot
    if '<@991063755939016875>' in message.content:
        # Read timestamp file for last ping time
        timestamp = open('timestamp', 'r')
        time = timestamp.read()
        timestamp.close()

        then = datetime.now()
        if time != '' and time != 'override':
            then = datetime.fromisoformat(time)
        now = datetime.now()
        hour = int(datetime.now().strftime('%H'))
        day = datetime.now().weekday()
        msg = ''

        if time == '' or time == 'override' or get_time_elapsed(then, now) >= cadence:
            # write here, write now
            write(str(now))
            if (day == 4 and hour >= 21) or 4 < day <= 6 or (day == 0 and hour <= 2):
                # This is the ID for Weekend
                msg = '<@&991109494253822012>'
            # times seem to be four hours ahead
            # 2 AM to 8 AM
            if 6 <= hour < 12:
                # This is the ID for Morning (2 AM - 8 AM)
                msg = '<@&991090248433950803>'
            # 8 AM to 5 PM
            if 12 <= hour < 21:
                # This is the ID for Day (8 AM - 5 PM)
                msg = '<@&991090325894336542>'
            # 5 PM to 10 PM
            if 21 <= hour < 24 or 0 <= hour < 2:
                # This is the ID for Evening (5 PM - 10 PM)
                msg = '<@&991090361369784360>'
            # 10 PM to 2 AM
            if 2 <= hour < 6:
                # This is the ID for Night (10 PM - 2 AM)
                msg = '<@&991090429342679110>'
            await message.reply(msg)
        else:
            await message.reply('Ping available in ' + str(cadence - get_time_elapsed(then, now)) + ' minutes.')
    else:
        print(str(message.author) + ': ' + message.content)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


client.run(TOKEN)
