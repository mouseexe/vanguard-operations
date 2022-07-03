import discord
import os
import math
import re
from datetime import datetime

# Token is a secret stored on okd
TOKEN = os.environ.get('DISCORDTOKEN', 'default value')

client = discord.Client()

# Personal cooldown is 2 hours, global cooldown is 10 minutes
global_cadence = 10
user_cadence = 120


# Helper method to calculate time elapsed delta
def get_time_elapsed(old_time, new_time):
    delta = new_time - old_time
    return math.floor(delta.total_seconds() / 60)


# Helper method to write to specified file
def write(file, message):
    timestamp = open(file, 'w')
    timestamp.write(message)
    timestamp.close()


@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    # general log statement
    # print(str(message.author) + ': ' + message.content)

    # reset clock if admin wants to
    if message.content == '/reset' and message.author.guild_permissions.administrator:
        write('timestamp', 'override')
        await message.add_reaction('✔')

    # This is the ID for the Vanguard Operations bot
    if '<@991063755939016875>' in message.content:
        try:
            # Read timestamp file for last ping time
            timestamp = open('timestamp', 'r')
            time = timestamp.read()
            timestamp.close()
        except:
            # Create file and populate if it doesn't exist
            write('timestamp', '')
            time = ''

        try:
            # read timestamp file for the last user ping
            userstamp = open(str(message.author), 'r')
            usertime = userstamp.read()
            userstamp.close()
        except:
            # Create file and populate if it doesn't exist
            write(str(message.author), '')
            usertime = ''

        # Set time if global file is not empty or override
        then = datetime.fromtimestamp(0)
        if time != '' and time != 'override':
            then = datetime.fromisoformat(str(time))

        # Set time if user file is not empty
        userthen = datetime.fromtimestamp(0)
        if usertime != '':
            userthen = datetime.fromisoformat(str(usertime))

        # If message contains a timestamp, use that instead of the current time
        if '<t:' in message.content:
            now = datetime.fromtimestamp(int(re.search('<t:.{10}>', message.content).group(0)[3:13]))
        else:
            # Otherwise just use the current time
            now = datetime.now()
        hour = int(now.strftime('%H'))
        day = now.weekday()
        msg = ''

        if time == '' or time == 'override' or (get_time_elapsed(then, now) >= global_cadence and (usertime == '' or get_time_elapsed(userthen, now) >= user_cadence)):
            # write here, write now
            write('timestamp', str(now))
            write(str(message.author), str(now))

            # times seem to be four hours ahead because of UTC
            # Monday = 0, Sunday = 6
            # Check if weekend before setting any other pings
            if (day == 4 and hour >= 21) or 4 < day <= 6 or (day == 0 and hour <= 2):
                # This is the ID for Weekend
                msg = '<@&991109494253822012>'
                # msg = 'weekend'
            else:
                # 2 AM to 8 AM
                if 6 <= hour < 12:
                    # This is the ID for Morning (2 AM - 8 AM)
                    msg = '<@&991090248433950803>'
                    # msg = 'morning'
                # 8 AM to 5 PM
                if 12 <= hour < 21:
                    # This is the ID for Day (8 AM - 5 PM)
                    msg = '<@&991090325894336542>'
                    # msg = 'day'
                # 5 PM to 10 PM
                if 21 <= hour < 24 or 0 <= hour < 2:
                    # This is the ID for Evening (5 PM - 10 PM)
                    msg = '<@&991090361369784360>'
                    # msg = 'evening'
                # 10 PM to 2 AM
                if 2 <= hour < 6:
                    # This is the ID for Night (10 PM - 2 AM)
                    msg = '<@&991090429342679110>'
                    # msg = 'night'
            await message.reply(msg)
        else:
            await message.reply('Ping available in ' + str(max((global_cadence - get_time_elapsed(then, now)), (user_cadence - get_time_elapsed(userthen, now)))) + ' minutes.')
    # else:
        # log only on failure
        # print(str(message.author) + ': ' + message.content)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


client.run(TOKEN)
