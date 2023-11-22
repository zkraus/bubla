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
        await ctx.send(f"Hello there, general {ctx.author}")

    @commands.command()
    async def add(self, ctx, a, b):
        try:
            await ctx.send(int(a)+int(b))
        except Exception as e:
            await ctx.send(e)

    @commands.command()
    async def help(self, context: Context) -> None:
        embed = discord.Embed(
            title="Help", description="List of available commands:", color=0xBEBEFE
        )
        for i in self.bot.cogs:
            if i == "owner" and not (await self.bot.is_owner(context.author)):
                continue
            cog = self.bot.get_cog(i.lower())
            list_commands = cog.get_commands()
            data = []
            for command in list_commands:
                description = command.description.partition("\n")[0]
                data.append(f"{config.DISCORD_COMMAND_PREFIX}{command.name} - {description}")
            help_text = "\n".join(data)
            embed.add_field(
                name=i.capitalize(), value=f"```{help_text}```", inline=False
            )
        await context.send(embed=embed)


async def setup(bot) -> None:
    await bot.add_cog(General(bot))
