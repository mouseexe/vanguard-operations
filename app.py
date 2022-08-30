import discord
import os
import math
import re
from datetime import datetime

# Token is a secret stored on okd
TOKEN = os.environ.get('DISCORDTOKEN', 'default value')

client = discord.Client( intents = discord.Intents.default())

# Personal cooldown is X minutes, global cooldown is Y minutes
global_cadence = 10
user_cadence = 120

# X votes needed to lift, must be done in Y minutes
votes = 6
vote_expiration = 2


# Helper method to calculate time elapsed delta
def get_time_elapsed(old_time, new_time):
    delta = new_time - old_time
    return math.floor(delta.total_seconds() / 60)


# Helper method to write to specified file
def write(file, message):
    timestamp = open(file, 'w')
    timestamp.write(message)
    timestamp.close()


# check if someone hasn't been lifted by that message yet
def is_liftable(reactions):
    for reaction in reactions:
        if reaction.emoji == '👼':
            return False
    return True


def get_timeslot(time):
    hour = int(time.strftime('%H'))
    day = time.weekday()

    # times seem to be four hours ahead because of UTC
    # Monday = 0, Sunday = 6
    # Bot will send back the original message, with the bot ping replaced with the relevant timezone ping
    # Check if weekend before setting any other pings
    if (day == 4 and hour >= 21) or 4 < day <= 6 or (day == 0 and hour <= 2):
        return 'weekend'
    else:
        # 2 AM to 8 AM
        if 6 <= hour < 12:
            return 'morning'
        # 8 AM to 5 PM
        if 12 <= hour < 21:
            return 'day'
        # 5 PM to 10 PM
        if 21 <= hour < 24 or 0 <= hour < 2:
            return 'evening'
        # 10 PM to 2 AM
        if 2 <= hour < 6:
            return 'night'


async def create_message(timeslot, message, now, msg, admin_pinged):
    try:
        # Read timestamp file for last ping time
        timestamp = open(timeslot, 'r')
        time = timestamp.read()
        timestamp.close()
    except:
        # Create file and populate if it doesn't exist
        write(timeslot, str(datetime.fromtimestamp(0)))
        time = datetime.fromtimestamp(0)

    try:
        # read timestamp file for the last user ping
        userstamp = open(str(message.author), 'r')
        usertime = userstamp.read()
        userstamp.close()
    except:
        # Create file and populate if it doesn't exist
        write(str(message.author), str(datetime.fromtimestamp(0)))
        usertime = datetime.fromtimestamp(0)

    then = datetime.fromisoformat(str(time))
    userthen = datetime.fromisoformat(str(usertime))

    if not admin_pinged:
        if get_time_elapsed(then, now) >= global_cadence and get_time_elapsed(userthen, now) >= user_cadence:
            # write here, write now
            write(timeslot, str(now))
            write(str(message.author), str(now))

            await message.reply(msg)
        else:
            await message.reply('Ping available in ' + str(max((global_cadence - get_time_elapsed(then, now)), (user_cadence - get_time_elapsed(userthen, now)))) + ' minutes.')


@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    # general log statement
    # print(str(message.author) + ': ' + message.content)

    # reset clock if admin wants to
    if '/reset' in message.content and message.author.guild_permissions.administrator:
        readfile = message.content[7:len(message.content)]
        write(readfile, str(datetime.fromtimestamp(0)))
        await message.add_reaction('✔')

    if '/read' in message.content and message.author.guild_permissions.administrator:
        readfile = message.content[6:len(message.content)]
        timefile = open(readfile, 'r')
        read = timefile.read()
        timefile.close()
        await message.reply(read)

    # vote lift reaction start (only works if message contains /votelift and a user to lift
    if '/votelift' in message.content and bool(re.search('<@.{18}>', message.content)):
        await message.add_reaction('🗳️')

    now = datetime.now()
    admin_pinged = message.author.guild_permissions.administrator

    # Ping-ahead for weekend
    if '<@&991109494253822012>' in message.content:
        timeslot = 'weekend'
        msg = message.content
        create_message(timeslot, message, now, msg, admin_pinged)
        return

    # Ping-ahead for morning
    if '<@&991090248433950803>' in message.content:
        timeslot = 'morning'
        msg = message.content
        create_message(timeslot, message, now, msg, admin_pinged)
        return

    # Ping-ahead for day
    if '<@&991090325894336542>' in message.content:
        timeslot = 'day'
        msg = message.content
        create_message(timeslot, message, now, msg, admin_pinged)
        return

    # Ping-ahead for evening
    if '<@&991090361369784360>' in message.content:
        timeslot = 'evening'
        msg = message.content
        create_message(timeslot, message, now, msg, admin_pinged)
        return

    # Ping-ahead for night
    if '<@&991090429342679110>' in message.content:
        timeslot = 'night'
        msg = message.content
        create_message(timeslot, message, now, msg, admin_pinged)
        return

    # This is the ID for the Vanguard Operations bot
    if '<@991063755939016875>' in message.content:
        # If message contains a timestamp, use that instead of the current time
        if '<t:' in message.content:
            time = datetime.fromtimestamp(int(re.search('<t:.{10}>', message.content).group(0)[3:13]))
        else:
            # Otherwise just use the current time
            time = now
        timeslot = get_timeslot(time)

        if timeslot == 'weekend':
            # This is the ID for Weekend
            msg = message.content.replace('<@991063755939016875>', '<@&991109494253822012>')
        else:
            # 2 AM to 8 AM
            if timeslot == 'morning':
                # This is the ID for Morning (2 AM - 8 AM)
                msg = message.content.replace('<@991063755939016875>', '<@&991090248433950803>')
            # 8 AM to 5 PM
            if timeslot == 'day':
                # This is the ID for Day (8 AM - 5 PM)
                msg = message.content.replace('<@991063755939016875>', '<@&991090325894336542>')
            # 5 PM to 10 PM
            if timeslot == 'evening':
                # This is the ID for Evening (5 PM - 10 PM)
                msg = message.content.replace('<@991063755939016875>', '<@&991090361369784360>')
            # 10 PM to 2 AM
            if timeslot == 'night':
                # This is the ID for Night (10 PM - 2 AM)
                msg = message.content.replace('<@991063755939016875>', '<@&991090429342679110>')
            else:
                msg = message.content
        # msg = message.content.replace('<@991063755939016875>', timeslot)

        create_message(timeslot, message, now, msg, False)
        return

    # else:
        # log only on failure
        # print(str(message.author) + ': ' + message.content)


@client.event
async def on_reaction_add(reaction, user):
    if '/votelift' in reaction.message.content and is_liftable(reaction.message.reactions):
        # you only have X minutes to get the votes
        if reaction.emoji == '🗳️':
            if get_time_elapsed(reaction.message.created_at, datetime.now()) > vote_expiration:
                # clear votes
                await reaction.message.clear_reaction('🗳️')
                # show vote failed emoji
                await reaction.message.add_reaction('❌')
                return

            # If the reaction is on a votelift message, and it hits X votes total (bot reaction included), lift and clear reactions
            if reaction.count >= votes:
                lifted_id = int(re.search('<@.{18}>', reaction.message.content).group(0)[2:20])
                lifted = await reaction.message.guild.fetch_member(lifted_id)
                afk_channel = client.get_channel(878743239199424532)
                await lifted.move_to(afk_channel)
                # remove all votes
                await reaction.message.clear_reaction('🗳️')
                # add angel to signify lifting has occurred
                await reaction.message.add_reaction('👼')

        # don't allow people to react with angel before lifting occurs
        if reaction.emoji == '👼' and user != client.user:
            await reaction.remove(user)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


client.run(TOKEN)
