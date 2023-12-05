import datetime
import logging

import discord
import tabulate

import google_calendar
from utils import config
from discord.ext import commands, tasks

log = logging.getLogger(__name__)


class Dev(commands.Cog, name="dev"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.calendar = google_calendar.Calendar(config.CALENDAR_ID, config.CALENDAR_SECRET_FILENAME,
                                                 config.CALENDAR_TOKEN_FILENAME)

        self.start = datetime.datetime.strptime("2023-12-07", "%Y-%m-%d").astimezone()
        self.end = self.start + datetime.timedelta(days=3)

    @commands.command()
    async def make_event(self, ctx: commands.Context) -> None:
        guild = self.bot.get_guild(config.DISCORD_BOT_GUILD_ID)
        await guild.create_scheduled_event(
            name="Test",
            start_time=self.start,
            end_time=self.end,
            entity_type=discord.EntityType.external,
            privacy_level=discord.PrivacyLevel.guild_only,
            location="Everywhere",
        )

        await ctx.send("Done")

    def compare_event_timing(self, event, start, end):
        if event.start_time >= end or event.end_time <= start:
            return False
        return True

    def find_events_collision(self, events, start, end):
        log.info(f"searching for collision with {start}->{end}")
        for event in events:
            log.info(f"event:{event.name} {event.start_time} -> {event.end_time}")
            if self.compare_event_timing(event, start, end):
                log.info("collision")
                return True
        log.info("no collision found")
        return False

    @commands.command()
    async def get_events(self, ctx: commands) -> None:
        guild = self.bot.get_guild(config.DISCORD_BOT_GUILD_ID)

        events = await guild.fetch_scheduled_events()
        print(events)

        start = datetime.datetime.strptime("2023-12-03", "%Y-%m-%d").astimezone()
        end = start + datetime.timedelta(days=1)
        start = self.start
        end = self.end
        self.find_events_collision(events, start, end)



async def setup(bot) -> None:
    await bot.add_cog(Dev(bot))
