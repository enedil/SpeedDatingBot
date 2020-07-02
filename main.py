import asyncio
import os
import discord
import discord.ext.commands as commands
import numpy as np
import math
from coolname import generate
from discord import Forbidden

from utils import get_guild

import globals as g

g.init_globals()
bot = g.bot
shuffleState = g.shuffleState


@g.bot.event
async def on_ready():
    print("Ready!")


@g.bot.event
async def on_command_error(ctx, error):
    print("Erroring...", error)
    tasks = [ctx.message.delete(delay=5)]
    if isinstance(error, commands.CommandNotFound):
        tasks.append(ctx.send("HONK?", delete_after=5))
    elif isinstance(error, commands.MissingRole):
        tasks.append(ctx.send("You have no power here!", delete_after=5))
    elif isinstance(error, commands.CheckAnyFailure):
        tasks.append(ctx.send("You have no power here!", delete_after=5))
    elif isinstance(error, commands.NotOwner):
        tasks.append(ctx.send("You have no power here!", delete_after=5))
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        tasks.append(ctx.send("Brakuje parametru: " + str(error.param), delete_after=5))
        tasks.append(ctx.send_help(ctx.command))
    elif isinstance(error, ValueError):
        tasks.append(ctx.send(str(error), delete_after=5))
    elif isinstance(error, commands.errors.BadArgument):
        tasks.append(ctx.send("Błędny parametr", delete_after=5))
        tasks.append(ctx.send_help(ctx.command))
    else:
        print(type(error.original))
        tasks.append(ctx.send(":robot:Bot did an uppsie :'( :robot:", delete_after=5))
        print(ctx.command, type(error))
        await asyncio.gather(*tasks)
        raise error
    await asyncio.gather(*tasks)


async def do_move():
    guild = get_guild()
    tasks = []
    for group, channel in zip(shuffleState.array, shuffleState.channels):
        for member in group:
            if member is None:
                continue
            print(member, channel)
            tasks.append(member.move_to(channel))
    try:
        await asyncio.gather(*tasks)
    except Forbidden as forbidden:
        print("Can't move somebody :(", forbidden)


@bot.command(name='shuffle-start')
@commands.is_owner()
async def shuffle_start(ctx, channel: discord.VoiceChannel, category: discord.CategoryChannel, group_size=5):
    """
    Takes name of voice channel with users currently and name of category
    with channels to be used for the speed-dating
    """
    async with ctx.typing():
        tasks = []
        people = list(channel.members)
        tasks.append(ctx.send("Liczba osób do teleportacji: " + str(len(people))))

        group_count = math.ceil(len(people)/group_size)
        while group_count%2 == 0 or group_count%3 == 0:
            group_count+=1

        groups = [[] for _ in range(group_count)]
        it = 0
        for el in people:
            groups[it].append(el)
            it+=1
            if it >= len(groups):
                it = 0
        while it < len(groups):
            groups[it].append(None)
        groups = np.array(groups)
        shuffleState.array = groups
        shuffleState.channels = []

        async def channels_list_job():
            channels = [category.create_voice_channel(" ".join(generate(2))) for _ in range(group_count)]
            shuffleState.channels = list(await asyncio.gather(*channels))
            print(shuffleState.channels)

        tasks.append(channels_list_job())
        await asyncio.gather(*tasks)
        await do_move()
    await ctx.message.add_reaction('✅')


@bot.command(name='shuffle-next')
@commands.is_owner()
async def do_shuffle(ctx):
    async with ctx.typing():
        shuffleState.shuffle()
        await do_move()
    await ctx.message.add_reaction('✅')


@bot.command(name='remove-voice')
@commands.is_owner()
async def remove_voice(ctx, category: discord.CategoryChannel):
    async with ctx.typing():
        for voice in category.voice_channels:
            await voice.delete()
    await ctx.message.add_reaction('✅')

token = os.environ.get("TOKEN")
g.bot.run(token)