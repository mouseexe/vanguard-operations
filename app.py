import discord
import os
import math
import re
from datetime import datetime

# Token is a secret stored on okd
TOKEN = os.environ.get('DISCORDTOKEN', 'default value')

VANGUARD_OPS = '<@991063755939016875>'

# Bot will ping:
WEEKEND = '<@&991109494253822012>'
MORNING = '<@&991090248433950803>'
DAY = '<@&991090325894336542>'
EVENING = '<@&991090361369784360>'
NIGHT = '<@&991090429342679110>'
ALL = '<@&1148738786688258101>'

# Users can ping:
WEEKEND_PING = '<@&1014641471724470423>'
MORNING_PING = '<@&1014641233924214874>'
DAY_PING = '<@&1014641312919720046>'
EVENING_PING = '<@&1014641367584084028>'
NIGHT_PING = '<@&1014641419849302189>'

client = discord.Client(intents=discord.Intents.all())

# Personal cooldown is X minutes, global cooldown is Y minutes
global_cadence = 10
user_cadence = 60

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
    # Adjust this whenever Daylight Savings starts or ends

    # Set according to whether or not Daylight Savings Time is active
    is_daylight = False

    daylight_offset = 18000
    if is_daylight:
        daylight_offset = 14400

    time = datetime.fromtimestamp(time.timestamp() - daylight_offset)

    hour = int(time.strftime('%H'))
    day = time.weekday()

    # Monday = 0, Sunday = 6
    # Bot will send back the original message, with the bot ping replaced with the relevant timezone ping
    # Check if weekend before setting any other pings
    if (day == 4 and hour >= 17) or 4 < day < 6 or (day == 6 and hour < 22):
        return 'weekend'
    else:
        # 2 AM to 8 AM
        if 2 <= hour < 8:
            return 'morning'
        # 8 AM to 5 PM
        elif 8 <= hour < 17:
            return 'day'
        # 5 PM to 10 PM
        elif 17 <= hour < 22:
            return 'evening'
        # 10 PM to 2 AM
        else:
            return 'night'


async def create_message(message, timeslot, now, replacement_string):
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

    if get_time_elapsed(then, now) >= global_cadence and get_time_elapsed(userthen, now) >= user_cadence:
        # write here, write now
        write(timeslot, str(now))
        write(str(message.author), str(now))

        if timeslot == 'weekend':
            msg = message.content.replace(replacement_string, ALL + ' ' + WEEKEND)
        elif timeslot == 'morning':
            msg = message.content.replace(replacement_string, ALL + ' ' + MORNING)
        # 8 AM to 5 PM
        elif timeslot == 'day':
            msg = message.content.replace(replacement_string, ALL + ' ' + DAY)
        # 5 PM to 10 PM
        elif timeslot == 'evening':
            msg = message.content.replace(replacement_string, ALL + ' ' + EVENING)
        # 10 PM to 2 AM
        elif timeslot == 'night':
            msg = message.content.replace(replacement_string, ALL + ' ' + NIGHT)
        else:
            msg = message.content
        # logging catch-all to stop pings
        # msg = message.content.replace(replacement_string, timeslot)

        await message.reply(msg)
    else:
        msg = message.content.replace(replacement_string, ALL)
        await message.reply(msg)
        # Old code to inform user they're on cooldown, should be unneeded with All Pings
        # await message.reply('Ping available in ' + str(max((global_cadence - get_time_elapsed(then, now)), (user_cadence - get_time_elapsed(userthen, now)))) + ' minutes.')
    return


@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    # general log statement
    # print(str(message.author) + ': ' + message.content)

    now = datetime.now()

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

    if WEEKEND_PING in message.content:
        await create_message(message, 'weekend', now, WEEKEND_PING)
    elif MORNING_PING in message.content:
        await create_message(message, 'morning', now, MORNING_PING)
    elif DAY_PING in message.content:
        await create_message(message, 'day', now, DAY_PING)
    elif EVENING_PING in message.content:
        await create_message(message, 'evening', now, EVENING_PING)
    elif NIGHT_PING in message.content:
        await create_message(message, 'night', now, NIGHT_PING)
    elif VANGUARD_OPS in message.content:
        await create_message(message, get_timeslot(now), now, VANGUARD_OPS)

    # else:
        # log only on failure
        # print(str(message.author) + ': ' + message.content)


@client.event
async def on_reaction_add(reaction, user):
    # Vote lift code isn't working, I should fix this one day
    if '/votelift' in reaction.message.content and is_liftable(reaction.message.reactions):
        # you only have X minutes to get the votes
        if reaction.emoji == '🗳️':
            if get_time_elapsed(reaction.message.created_at, datetime.now()) > vote_expiration:
                # clear votes
                await reaction.message.clear_reaction('🗳️')
                # show vote failed emoji
                await reaction.message.add_reaction('❌')
                return

            # If the reaction is on a votelift message, and it hits X votes total (w/ bot), lift and clear reactions
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
