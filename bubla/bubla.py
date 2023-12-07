import datetime
import logging
import random
from utils import config

import discord
from discord.ext import commands, tasks

from . import cogs

log = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.message_content = True


class Bubla(commands.Bot):
    cogs_list = [
        'general',
        'rally_calendar',
        'dev',
    ]

    def __init__(self) -> None:
        super().__init__(
            command_prefix=commands.when_mentioned_or(config.DISCORD_COMMAND_PREFIX),
            intents=intents,
            help_command=commands.DefaultHelpCommand(),
        )
        """
        This creates custom bot variables so that we can access these variables in cogs more easily.

        For example, The config is available using the following code:
        - self.config # In this class
        - bot.config # In this file
        - self.bot.config # In cogs
        """
        self.config = config
        self.prefix = config.DISCORD_COMMAND_PREFIX
        self.database = None

    async def load_cogs(self) -> None:

        for cog_name in self.cogs_list:
            try:
                await self.load_extension(f"bubla.cogs.{cog_name}")
                log.info(f"Cog {cog_name} loaded")
            except Exception as e:
                exception = f"{type(e).__name__}: {e}"
                log.error(f"failed to load {cog_name}\n{exception}")

    async def setup_hook(self) -> None:
        log.info("-------------------")
        await self.load_cogs()
        self.status_task.start()
        # self.timed_hello.start()

    @tasks.loop(minutes=1.0)
    async def status_task(self) -> None:
        statuses = ["DiRT Rally", "Dirt Rally 2.0", "Richard Burns Rally", "EA WRC"]
        await self.change_presence(activity=discord.Game(random.choice(statuses)))

    @status_task.before_loop
    async def before_status_task(self) -> None:
        await self.wait_until_ready()

    @tasks.loop(time=datetime.time(hour=9, minute=50, tzinfo=datetime.timezone.utc))
    async def timed_hello(self) -> None:
        channel = self.get_channel(config.DISCORD_REMINDER_CHANNEL_ID)
        await channel.send('timed hello')

    @timed_hello.before_loop
    async def before_timed_hello(self) -> None:
        await self.wait_until_ready()

    async def on_message(self, message: discord.Message) -> None:
        """
        The code in this event is executed every time someone sends a message, with or without the prefix

        :param message: The message that was sent.
        """
        # if message.guild.id != config.DISCORD_BOT_GUILD_ID:
        #     return
        if message.author == self.user or message.author.bot:
            return
        await self.process_commands(message)

    async def get_reminder_channels(self) -> list[discord.TextChannel]:
        guilds = self.fetch_guilds()
        log.info(f"guilds: {guilds}")
        reminder_channels = []
        async for guild in guilds:
            log.info(f"guild: {guild}")
            guild_channels = await guild.fetch_channels()
            log.info(f"guild_channels: {guild_channels}")
            tmp_channels = [channel for channel in guild_channels
                            if channel.name == config.DISCORD_REMINDER_CHANNEL_NAME]
            reminder_channels += tmp_channels
            log.info(f"tmp_channels: {tmp_channels}")
        log.info(f"reminder_channels: {reminder_channels}")
        return reminder_channels
