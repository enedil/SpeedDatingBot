from discord.ext import commands
import numpy as np


class ShuffleState():
    def __init__(self):
        self.array = []
        

    def shuffle(self):
        self.array = list(zip(*[group[i:] + group[:i] for i, group in enumerate(self.array)]))


def init_globals():
    global bot, shuffleState
    bot = commands.Bot(command_prefix=commands.when_mentioned)
    shuffleState = ShuffleState()
