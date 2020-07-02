import discord
import globals as g
import settings as s


def get_guild() -> discord.Guild:
    return discord.utils.get(g.bot.guilds, name=s.GUILD_NAME)
