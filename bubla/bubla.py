import datetime
import logging
import random
from utils import config

import discord
from discord.ext import commands, tasks

from . import cogs


logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.message_content = True


class Bubla(commands.Bot):
    cogs_list = [
        'general',
        'rally_calendar'
    ]

    def __init__(self) -> None:
        super().__init__(
            command_prefix=commands.when_mentioned_or(config.COMMAND_PREFIX),
            intents=intents,
            help_command=None,
        )
        """
        This creates custom bot variables so that we can access these variables in cogs more easily.

        For example, The config is available using the following code:
        - self.config # In this class
        - bot.config # In this file
        - self.bot.config # In cogs
        """
        self.logger = logger
        self.config = config
        self.prefix = config.COMMAND_PREFIX
        self.database = None

    async def load_cogs(self) -> None:

        for cog_name in self.cogs_list:
            try:
                await self.load_extension(f"bubla.cogs.{cog_name}")
                self.logger.info(f"Cog {cog_name} loaded")
            except Exception as e:
                exception = f"{type(e).__name__}: {e}"
                self.logger.error(f"failed to load {cog_name}\n{exception}")

    async def setup_hook(self) -> None:
        self.logger.info("-------------------")
        await self.load_cogs()
        self.status_task.start()
        self.timed_hello.start()

    @tasks.loop(minutes=1.0)
    async def status_task(self) -> None:
        statuses = ["John Wayne movie", "Watching over baking"]
        await self.change_presence(activity=discord.Game(random.choice(statuses)))

    @status_task.before_loop
    async def before_status_task(self) -> None:
        await self.wait_until_ready()

    @tasks.loop(time=datetime.time(hour=9, minute=50, tzinfo=datetime.timezone.utc))
    async def timed_hello(self) -> None:
        channel = self.get_channel(config.REMINDER_CHANNEL_ID)
        await channel.send('timed hello')

    @timed_hello.before_loop
    async def before_timed_hello(self) -> None:
        await self.wait_until_ready()

    async def on_message(self, message: discord.Message) -> None:
        """
        The code in this event is executed every time someone sends a message, with or without the prefix

        :param message: The message that was sent.
        """
        if message.author == self.user or message.author.bot:
            return
        await self.process_commands(message)
