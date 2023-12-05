import datetime
import logging

import discord
import tabulate

import google_calendar
from utils import config
from discord.ext import commands, tasks

log = logging.getLogger(__name__)


class RallyCalendar(commands.Cog, name="rally_calendar"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.calendar = google_calendar.Calendar(config.CALENDAR_ID, config.CALENDAR_SECRET_FILENAME,
                                                 config.CALENDAR_TOKEN_FILENAME)

        self.timed_reminder.start()
        self.refresh_calendar.start()

    def compare_event_timing(self, discord_event, calendar_event):
        if discord_event.start_time >= calendar_event.end or discord_event.end_time <= calendar_event.start:
            return False
        return True

    def find_events_collision(self, discord_events, calendar_event):
        log.info(f"searching for collision with {calendar_event.start}->{calendar_event.end}")
        for discord_event in discord_events:
            log.info(f"event:{discord_event.name} {discord_event.start_time} -> {discord_event.end_time}")
            if self.compare_event_timing(discord_event, calendar_event):
                log.info("collision")
                return True
        log.info("no collision found")
        return False

    async def reminder_core(self, ctx):
        log.debug("reminder()")
        events = self.calendar.get_events_current()
        if not events:
            log.debug("no events")
            return
        event = events[0]
        today = datetime.date.today()
        log.debug(event.start)
        log.debug(today)
        message = []
        if event.start.date() == today:
            message = ["Just started today!!!!", self.calendar.format_events(events),
                       "", "Previous week results:", preview(await self.get_leaderboard_message())]
        else:
            log.info(f"event ends soon")
            message = await self.rally_ends_soon()  # for notification message
            calendar_events = self.calendar.get_events_next()  # for pre-planning new event

            await self.plan_next_events(calendar_events)

        if message:
            message = '\n'.join(message)
            # channel = self.bot.get_channel(config.REMINDER_CHANNEL_ID)
            await ctx.send(message)

    async def plan_next_events(self, calendar_events):
        if not calendar_events:
            log.info("no events to be planned")
            return

        log.info("planning next event")
        guild = self.bot.get_guild(config.DISCORD_BOT_GUILD_ID)
        discord_events = await guild.fetch_scheduled_events()
        for calendar_event in calendar_events:
            log.info(f"checking event {calendar_event.summary}")
            if not self.find_events_collision(discord_events, calendar_event):
                # create discord event
                log.info(f"Creating event {calendar_event.summary}")
                await guild.create_scheduled_event(
                    name=calendar_event.summary,
                    description=calendar_event.description,
                    start_time=calendar_event.start,
                    end_time=calendar_event.end,
                    entity_type=discord.EntityType.external,
                    privacy_level=discord.PrivacyLevel.guild_only,
                    location="DiRT Rally 2.0"
                )
                continue
            else:
                log.info(f"event {calendar_event.summary} exists")

    @tasks.loop(time=datetime.time(hour=config.CALENDAR_REFRESH_HOUR, minute=00, tzinfo=datetime.timezone.utc))
    async def refresh_calendar(self):
        await self.calendar.get_events_current()

    @tasks.loop(time=datetime.time(hour=config.DISCORD_REMINDER_HOUR, minute=00, tzinfo=datetime.timezone.utc))
    async def timed_reminder(self) -> None:
        channel = self.bot.get_channel(config.DISCORD_REMINDER_CHANNEL_ID)
        await self.reminder_core(channel)

    @commands.command()
    async def reminder(self, ctx):
        await self.reminder_core(ctx)

    @timed_reminder.before_loop
    async def before_timed_hello(self) -> None:
        await self.bot.wait_until_ready()

    @commands.command()
    async def rally(self, ctx, subcommand=None):
        result = []
        if not subcommand:
            result = await self.rally_now() + [""] + await self.rally_upcoming()
        else:
            if subcommand == "now":
                result = await self.rally_now()
            elif subcommand == "upcoming":
                result = await self.rally_upcoming()
            elif subcommand == "next":
                result = await self.rally_next()
            elif subcommand == "ends":
                result = await self.rally_ends_soon()
            else:
                result = await self.help()
        result = '\n'.join(result)
        await ctx.send(f"{result}")

    async def rally_now(self):
        events = self.calendar.get_events_current()
        if not events:
            return ["No current rally events available."]
        result = ["Current rally events:", self.calendar.format_events(events)]
        return result

    async def rally_upcoming(self):
        events = self.calendar.get_events_upcoming()
        if not events:
            return ["No upcoming rally events available."]
        result = ["Upcoming rally events:", self.calendar.format_events(events)]
        return result

    async def rally_next(self):
        events = self.calendar.get_events_next()
        if not events:
            return ["No next rally events available."]
        result = ["Next rally events:", self.calendar.format_events(events)]
        return result

    async def rally_ends_soon(self):
        events = self.calendar.get_events_end_soon()
        if not events:
            return []
        result = ["Rally events ends soon:", self.calendar.format_events(events)]
        return result

    async def help(self):
        return [
            "Rally subcommands help",
            f"```{self.bot.prefix}rally [<subcommand>]```",
            "if `<subcommand>` is not specified, shows compound rally events plan, otherwise",
            "* `now`: Shows current rally events",
            "* `upcoming`: Shows upcoming rally events",
            "* `next`: Shows next rally events, starting soon",
            "* `ends`: Shows rally events that ends soon",
            "",
            f"🚧 ```{self.bot.prefix}leaderboard``` -- PREVIEW: display leaderboard on current event",
            f"🚧 ```{self.bot.prefix}standings``` -- PREVIEW: display current standings",
        ]

    async def get_results(self):
        return [
            {'rank': 1, 'name': 'sykynxCZ', 'isVIP': False, 'isFounder': False, 'isPlayer': False, 'isDnfEntry': False,
             'playerDiff': 0, 'vehicleName': 'Mitsubishi Space Star R5', 'stageTime': '09:29.276', 'stageDiff': '--',
             'totalTime': '44:24.696', 'totalDiff': '--', 'nationality': 'eLngCzech'},
            {'rank': 2, 'name': 'aranelek', 'isVIP': False, 'isFounder': False, 'isPlayer': True, 'isDnfEntry': False,
             'playerDiff': 1, 'vehicleName': 'Ford Fiesta R5', 'stageTime': '10:00.872', 'stageDiff': '+00:31.596',
             'totalTime': '46:21.601', 'totalDiff': '+01:56.905', 'nationality': 'eLngCzech'},
            {'rank': 3, 'name': 'Maidens', 'isVIP': False, 'isFounder': False, 'isPlayer': False, 'isDnfEntry': False,
             'playerDiff': -1, 'vehicleName': 'ŠKODA Fabia R5', 'stageTime': '12:06.080', 'stageDiff': '+02:36.804',
             'totalTime': '47:50.198', 'totalDiff': '+03:25.502', 'nationality': 'eLngCzech'},
            {'rank': 4, 'name': 'ThePlagueDoc24', 'isVIP': False, 'isFounder': False, 'isPlayer': False,
             'isDnfEntry': False, 'playerDiff': 0, 'vehicleName': 'Ford Fiesta R5', 'stageTime': '10:52.032',
             'stageDiff': '+01:22.756', 'totalTime': '48:57.641', 'totalDiff': '+04:32.945',
             'nationality': 'eLngBritish'},
            {'rank': 5, 'name': 'Risinek', 'isVIP': False, 'isFounder': False, 'isPlayer': False, 'isDnfEntry': False,
             'playerDiff': 0, 'vehicleName': 'ŠKODA Fabia R5', 'stageTime': '09:46.415', 'stageDiff': '+00:17.139',
             'totalTime': '49:43.359', 'totalDiff': '+05:18.663', 'nationality': 'eLngCzech'},
            {'rank': 6, 'name': 'mischmo', 'isVIP': False, 'isFounder': False, 'isPlayer': False, 'isDnfEntry': False,
             'playerDiff': 0, 'vehicleName': 'ŠKODA Fabia R5', 'stageTime': '10:51.945', 'stageDiff': '+01:22.669',
             'totalTime': '52:00.002', 'totalDiff': '+07:35.306', 'nationality': 'eLngCzech'},
            {'rank': 7, 'name': 'VohultoNeboUhni', 'isVIP': False, 'isFounder': False, 'isPlayer': False,
             'isDnfEntry': True, 'playerDiff': 0, 'vehicleName': 'ŠKODA Fabia R5', 'stageTime': '30:00.000',
             'stageDiff': '+20:30.724', 'totalTime': '01:59:09.272', 'totalDiff': '+01:14:44.576',
             'nationality': 'eLngCzech'}]

    async def get_headers(self):
        return ['rank', 'name', 'vehicleName',
                'totalTime', 'totalDiff']

    async def get_standings(self):
        return [{'rank': 1, 'isMe': False, 'nationality': 'eLngCzech', 'displayName': 'Maidens', 'totalPoints': 25,
                 'eventPoints': [{'eventIndex': 0, 'points': 7}, {'eventIndex': 1, 'points': 4},
                                 {'eventIndex': 2, 'points': 5}, {'eventIndex': 3, 'points': 9},
                                 {'eventIndex': 4, 'points': 0}, {'eventIndex': 5, 'points': 0},
                                 {'eventIndex': 6, 'points': 0}, {'eventIndex': 7, 'points': 0},
                                 {'eventIndex': 8, 'points': 0}, {'eventIndex': 9, 'points': 0},
                                 {'eventIndex': 10, 'points': 0}, {'eventIndex': 11, 'points': 0}]},
                {'rank': 2, 'isMe': True, 'nationality': 'eLngCzech', 'displayName': 'aranelek', 'totalPoints': 21,
                 'eventPoints': [{'eventIndex': 0, 'points': 3}, {'eventIndex': 1, 'points': 8},
                                 {'eventIndex': 2, 'points': 7}, {'eventIndex': 3, 'points': 3},
                                 {'eventIndex': 4, 'points': 0}, {'eventIndex': 5, 'points': 0},
                                 {'eventIndex': 6, 'points': 0}, {'eventIndex': 7, 'points': 0},
                                 {'eventIndex': 8, 'points': 0}, {'eventIndex': 9, 'points': 0},
                                 {'eventIndex': 10, 'points': 0}, {'eventIndex': 11, 'points': 0}]},
                {'rank': 3, 'isMe': False, 'nationality': 'eLngCzech', 'displayName': 'sykynxCZ', 'totalPoints': 17,
                 'eventPoints': [{'eventIndex': 0, 'points': 5}, {'eventIndex': 1, 'points': 6},
                                 {'eventIndex': 2, 'points': 1}, {'eventIndex': 3, 'points': 5},
                                 {'eventIndex': 4, 'points': 0}, {'eventIndex': 5, 'points': 0},
                                 {'eventIndex': 6, 'points': 0}, {'eventIndex': 7, 'points': 0},
                                 {'eventIndex': 8, 'points': 0}, {'eventIndex': 9, 'points': 0},
                                 {'eventIndex': 10, 'points': 0}, {'eventIndex': 11, 'points': 0}]},
                {'rank': 4, 'isMe': False, 'nationality': 'eLngCzech', 'displayName': 'Risinek', 'totalPoints': 14,
                 'eventPoints': [{'eventIndex': 0, 'points': 4}, {'eventIndex': 1, 'points': 5},
                                 {'eventIndex': 2, 'points': 1}, {'eventIndex': 3, 'points': 4},
                                 {'eventIndex': 4, 'points': 0}, {'eventIndex': 5, 'points': 0},
                                 {'eventIndex': 6, 'points': 0}, {'eventIndex': 7, 'points': 0},
                                 {'eventIndex': 8, 'points': 0}, {'eventIndex': 9, 'points': 0},
                                 {'eventIndex': 10, 'points': 0}, {'eventIndex': 11, 'points': 0}]},
                {'rank': 5, 'isMe': False, 'nationality': 'eLngCzech', 'displayName': 'SharpEye24', 'totalPoints': 12,
                 'eventPoints': [{'eventIndex': 0, 'points': 0}, {'eventIndex': 1, 'points': 2},
                                 {'eventIndex': 2, 'points': 4}, {'eventIndex': 3, 'points': 6},
                                 {'eventIndex': 4, 'points': 0}, {'eventIndex': 5, 'points': 0},
                                 {'eventIndex': 6, 'points': 0}, {'eventIndex': 7, 'points': 0},
                                 {'eventIndex': 8, 'points': 0}, {'eventIndex': 9, 'points': 0},
                                 {'eventIndex': 10, 'points': 0}, {'eventIndex': 11, 'points': 0}]},
                {'rank': 6, 'isMe': False, 'nationality': 'eLngCzech', 'displayName': 'mischmo', 'totalPoints': 10,
                 'eventPoints': [{'eventIndex': 0, 'points': 2}, {'eventIndex': 1, 'points': 3},
                                 {'eventIndex': 2, 'points': 3}, {'eventIndex': 3, 'points': 2},
                                 {'eventIndex': 4, 'points': 0}, {'eventIndex': 5, 'points': 0},
                                 {'eventIndex': 6, 'points': 0}, {'eventIndex': 7, 'points': 0},
                                 {'eventIndex': 8, 'points': 0}, {'eventIndex': 9, 'points': 0},
                                 {'eventIndex': 10, 'points': 0}, {'eventIndex': 11, 'points': 0}]},
                {'rank': 7, 'isMe': False, 'nationality': 'eLngCzech', 'displayName': 'nert', 'totalPoints': 5,
                 'eventPoints': [{'eventIndex': 0, 'points': 1}, {'eventIndex': 1, 'points': 1},
                                 {'eventIndex': 2, 'points': 2}, {'eventIndex': 3, 'points': 1},
                                 {'eventIndex': 4, 'points': 0}, {'eventIndex': 5, 'points': 0},
                                 {'eventIndex': 6, 'points': 0}, {'eventIndex': 7, 'points': 0},
                                 {'eventIndex': 8, 'points': 0}, {'eventIndex': 9, 'points': 0},
                                 {'eventIndex': 10, 'points': 0}, {'eventIndex': 11, 'points': 0}]},
                {'rank': 8, 'isMe': False, 'nationality': 'eLngCzech', 'displayName': 'xholesov', 'totalPoints': 3,
                 'eventPoints': [{'eventIndex': 0, 'points': 1}, {'eventIndex': 1, 'points': 1},
                                 {'eventIndex': 2, 'points': 0}, {'eventIndex': 3, 'points': 1},
                                 {'eventIndex': 4, 'points': 0}, {'eventIndex': 5, 'points': 0},
                                 {'eventIndex': 6, 'points': 0}, {'eventIndex': 7, 'points': 0},
                                 {'eventIndex': 8, 'points': 0}, {'eventIndex': 9, 'points': 0},
                                 {'eventIndex': 10, 'points': 0}, {'eventIndex': 11, 'points': 0}]},
                {'rank': 9, 'isMe': False, 'nationality': 'eLngCzech', 'displayName': 'VohultoNeboUhni',
                 'totalPoints': 1, 'eventPoints': [{'eventIndex': 0, 'points': 0}, {'eventIndex': 1, 'points': 0},
                                                   {'eventIndex': 2, 'points': 0}, {'eventIndex': 3, 'points': 1},
                                                   {'eventIndex': 4, 'points': 0}, {'eventIndex': 5, 'points': 0},
                                                   {'eventIndex': 6, 'points': 0}, {'eventIndex': 7, 'points': 0},
                                                   {'eventIndex': 8, 'points': 0}, {'eventIndex': 9, 'points': 0},
                                                   {'eventIndex': 10, 'points': 0}, {'eventIndex': 11, 'points': 0}]}]

    @commands.command()
    async def leaderboard(self, ctx):
        message = await self.get_leaderboard_message()
        await ctx.send(preview(message))

    async def get_leaderboard_message(self):
        results = await self.get_results()
        headers = await self.get_headers()
        results = [{k: line[k] for k in headers} for line in results]
        message = tabulate.tabulate(results, headers="keys")
        return f"```{message}```"

    @commands.command()
    async def standings(self, ctx):
        message = await self.get_standings_message()
        await ctx.send(preview(message))

    async def get_standings_message(self):
        data = await self.get_standings()
        headers = ['rank', 'displayName', 'totalPoints']
        results = []
        for line in data:
            eventpoints = line['eventPoints']
            eventpoints = {line['eventIndex']: line['points'] for line in eventpoints}
            line_result = {k: line[k] for k in headers}

            results.append(line_result | eventpoints)
        message = tabulate.tabulate(results, headers="keys")
        return f"```{message}```"


def preview(message):
    return '\n'.join([
        "# 🚧 PREVIEW REPOSNSE MOCK DATA 🚧",
        message,
        "# 🚧 END OF PREVIEW REPOSNSE 🚧"
    ])


async def setup(bot) -> None:
    await bot.add_cog(RallyCalendar(bot))
