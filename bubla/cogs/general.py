import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
from utils import config


class General(commands.Cog, name="general"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command()
    async def hello(self, ctx):
        """Greetings to you"""
        await ctx.send(f"Hello there, general {ctx.author}")


async def setup(bot) -> None:
    await bot.add_cog(General(bot))
