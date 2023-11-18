import datetime

import tabulate

import google_calendar
from utils import config
from discord.ext import commands, tasks


class RallyCalendar(commands.Cog, name="rally_calendar"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.logger = self.bot.logger
        self.calendar = google_calendar.Calendar(config.CALENDAR_ID, config.CREDENTIALS_FILENAME, config.TOKEN_FILENAME)

        self.rally_reminder.start()

    @tasks.loop(minutes=1.0)
    async def rally_reminder(self) -> None:
        message = await self.rally_ends_soon()
        self.logger.info("rally_reminder() firing")
        if message:
            message = '\n'.join(message)
            channel = self.bot.get_channel(config.REMINDER_CHANNEL_ID)
            await channel.send(message)

    @rally_reminder.before_loop
    async def before_rally_reminder(self) -> None:
        await self.bot.wait_until_ready()

    @tasks.loop(time=datetime.time(hour=9, minute=50, tzinfo=datetime.timezone.utc))
    async def timed_hello(self) -> None:
        channel = self.bot.get_channel(config.REMINDER_CHANNEL_ID)
        await channel.send('timed hello')

    @timed_hello.before_loop
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
        return [{'rank': 1, 'name': 'sykynxCZ', 'isVIP': False, 'isFounder': False, 'isPlayer': False, 'isDnfEntry': False, 'playerDiff': 0, 'vehicleName': 'Mitsubishi Space Star R5', 'stageTime': '09:29.276', 'stageDiff': '--', 'totalTime': '44:24.696', 'totalDiff': '--', 'nationality': 'eLngCzech'}, {'rank': 2, 'name': 'aranelek', 'isVIP': False, 'isFounder': False, 'isPlayer': True, 'isDnfEntry': False, 'playerDiff': 1, 'vehicleName': 'Ford Fiesta R5', 'stageTime': '10:00.872', 'stageDiff': '+00:31.596', 'totalTime': '46:21.601', 'totalDiff': '+01:56.905', 'nationality': 'eLngCzech'}, {'rank': 3, 'name': 'Maidens', 'isVIP': False, 'isFounder': False, 'isPlayer': False, 'isDnfEntry': False, 'playerDiff': -1, 'vehicleName': 'ŠKODA Fabia R5', 'stageTime': '12:06.080', 'stageDiff': '+02:36.804', 'totalTime': '47:50.198', 'totalDiff': '+03:25.502', 'nationality': 'eLngCzech'}, {'rank': 4, 'name': 'ThePlagueDoc24', 'isVIP': False, 'isFounder': False, 'isPlayer': False, 'isDnfEntry': False, 'playerDiff': 0, 'vehicleName': 'Ford Fiesta R5', 'stageTime': '10:52.032', 'stageDiff': '+01:22.756', 'totalTime': '48:57.641', 'totalDiff': '+04:32.945', 'nationality': 'eLngBritish'}, {'rank': 5, 'name': 'Risinek', 'isVIP': False, 'isFounder': False, 'isPlayer': False, 'isDnfEntry': False, 'playerDiff': 0, 'vehicleName': 'ŠKODA Fabia R5', 'stageTime': '09:46.415', 'stageDiff': '+00:17.139', 'totalTime': '49:43.359', 'totalDiff': '+05:18.663', 'nationality': 'eLngCzech'}, {'rank': 6, 'name': 'mischmo', 'isVIP': False, 'isFounder': False, 'isPlayer': False, 'isDnfEntry': False, 'playerDiff': 0, 'vehicleName': 'ŠKODA Fabia R5', 'stageTime': '10:51.945', 'stageDiff': '+01:22.669', 'totalTime': '52:00.002', 'totalDiff': '+07:35.306', 'nationality': 'eLngCzech'}, {'rank': 7, 'name': 'VohultoNeboUhni', 'isVIP': False, 'isFounder': False, 'isPlayer': False, 'isDnfEntry': True, 'playerDiff': 0, 'vehicleName': 'ŠKODA Fabia R5', 'stageTime': '30:00.000', 'stageDiff': '+20:30.724', 'totalTime': '01:59:09.272', 'totalDiff': '+01:14:44.576', 'nationality': 'eLngCzech'}]

    async def get_headers(self):
        return ['rank', 'name', 'vehicleName',
                'totalTime', 'totalDiff']

    async def get_standings(self):
        return [{'rank': 1, 'isMe': False, 'nationality': 'eLngCzech', 'displayName': 'Maidens', 'totalPoints': 25, 'eventPoints': [{'eventIndex': 0, 'points': 7}, {'eventIndex': 1, 'points': 4}, {'eventIndex': 2, 'points': 5}, {'eventIndex': 3, 'points': 9}, {'eventIndex': 4, 'points': 0}, {'eventIndex': 5, 'points': 0}, {'eventIndex': 6, 'points': 0}, {'eventIndex': 7, 'points': 0}, {'eventIndex': 8, 'points': 0}, {'eventIndex': 9, 'points': 0}, {'eventIndex': 10, 'points': 0}, {'eventIndex': 11, 'points': 0}]}, {'rank': 2, 'isMe': True, 'nationality': 'eLngCzech', 'displayName': 'aranelek', 'totalPoints': 21, 'eventPoints': [{'eventIndex': 0, 'points': 3}, {'eventIndex': 1, 'points': 8}, {'eventIndex': 2, 'points': 7}, {'eventIndex': 3, 'points': 3}, {'eventIndex': 4, 'points': 0}, {'eventIndex': 5, 'points': 0}, {'eventIndex': 6, 'points': 0}, {'eventIndex': 7, 'points': 0}, {'eventIndex': 8, 'points': 0}, {'eventIndex': 9, 'points': 0}, {'eventIndex': 10, 'points': 0}, {'eventIndex': 11, 'points': 0}]}, {'rank': 3, 'isMe': False, 'nationality': 'eLngCzech', 'displayName': 'sykynxCZ', 'totalPoints': 17, 'eventPoints': [{'eventIndex': 0, 'points': 5}, {'eventIndex': 1, 'points': 6}, {'eventIndex': 2, 'points': 1}, {'eventIndex': 3, 'points': 5}, {'eventIndex': 4, 'points': 0}, {'eventIndex': 5, 'points': 0}, {'eventIndex': 6, 'points': 0}, {'eventIndex': 7, 'points': 0}, {'eventIndex': 8, 'points': 0}, {'eventIndex': 9, 'points': 0}, {'eventIndex': 10, 'points': 0}, {'eventIndex': 11, 'points': 0}]}, {'rank': 4, 'isMe': False, 'nationality': 'eLngCzech', 'displayName': 'Risinek', 'totalPoints': 14, 'eventPoints': [{'eventIndex': 0, 'points': 4}, {'eventIndex': 1, 'points': 5}, {'eventIndex': 2, 'points': 1}, {'eventIndex': 3, 'points': 4}, {'eventIndex': 4, 'points': 0}, {'eventIndex': 5, 'points': 0}, {'eventIndex': 6, 'points': 0}, {'eventIndex': 7, 'points': 0}, {'eventIndex': 8, 'points': 0}, {'eventIndex': 9, 'points': 0}, {'eventIndex': 10, 'points': 0}, {'eventIndex': 11, 'points': 0}]}, {'rank': 5, 'isMe': False, 'nationality': 'eLngCzech', 'displayName': 'SharpEye24', 'totalPoints': 12, 'eventPoints': [{'eventIndex': 0, 'points': 0}, {'eventIndex': 1, 'points': 2}, {'eventIndex': 2, 'points': 4}, {'eventIndex': 3, 'points': 6}, {'eventIndex': 4, 'points': 0}, {'eventIndex': 5, 'points': 0}, {'eventIndex': 6, 'points': 0}, {'eventIndex': 7, 'points': 0}, {'eventIndex': 8, 'points': 0}, {'eventIndex': 9, 'points': 0}, {'eventIndex': 10, 'points': 0}, {'eventIndex': 11, 'points': 0}]}, {'rank': 6, 'isMe': False, 'nationality': 'eLngCzech', 'displayName': 'mischmo', 'totalPoints': 10, 'eventPoints': [{'eventIndex': 0, 'points': 2}, {'eventIndex': 1, 'points': 3}, {'eventIndex': 2, 'points': 3}, {'eventIndex': 3, 'points': 2}, {'eventIndex': 4, 'points': 0}, {'eventIndex': 5, 'points': 0}, {'eventIndex': 6, 'points': 0}, {'eventIndex': 7, 'points': 0}, {'eventIndex': 8, 'points': 0}, {'eventIndex': 9, 'points': 0}, {'eventIndex': 10, 'points': 0}, {'eventIndex': 11, 'points': 0}]}, {'rank': 7, 'isMe': False, 'nationality': 'eLngCzech', 'displayName': 'nert', 'totalPoints': 5, 'eventPoints': [{'eventIndex': 0, 'points': 1}, {'eventIndex': 1, 'points': 1}, {'eventIndex': 2, 'points': 2}, {'eventIndex': 3, 'points': 1}, {'eventIndex': 4, 'points': 0}, {'eventIndex': 5, 'points': 0}, {'eventIndex': 6, 'points': 0}, {'eventIndex': 7, 'points': 0}, {'eventIndex': 8, 'points': 0}, {'eventIndex': 9, 'points': 0}, {'eventIndex': 10, 'points': 0}, {'eventIndex': 11, 'points': 0}]}, {'rank': 8, 'isMe': False, 'nationality': 'eLngCzech', 'displayName': 'xholesov', 'totalPoints': 3, 'eventPoints': [{'eventIndex': 0, 'points': 1}, {'eventIndex': 1, 'points': 1}, {'eventIndex': 2, 'points': 0}, {'eventIndex': 3, 'points': 1}, {'eventIndex': 4, 'points': 0}, {'eventIndex': 5, 'points': 0}, {'eventIndex': 6, 'points': 0}, {'eventIndex': 7, 'points': 0}, {'eventIndex': 8, 'points': 0}, {'eventIndex': 9, 'points': 0}, {'eventIndex': 10, 'points': 0}, {'eventIndex': 11, 'points': 0}]}, {'rank': 9, 'isMe': False, 'nationality': 'eLngCzech', 'displayName': 'VohultoNeboUhni', 'totalPoints': 1, 'eventPoints': [{'eventIndex': 0, 'points': 0}, {'eventIndex': 1, 'points': 0}, {'eventIndex': 2, 'points': 0}, {'eventIndex': 3, 'points': 1}, {'eventIndex': 4, 'points': 0}, {'eventIndex': 5, 'points': 0}, {'eventIndex': 6, 'points': 0}, {'eventIndex': 7, 'points': 0}, {'eventIndex': 8, 'points': 0}, {'eventIndex': 9, 'points': 0}, {'eventIndex': 10, 'points': 0}, {'eventIndex': 11, 'points': 0}]}]

    @commands.command()
    async def leaderboard(self, ctx):
        results = await self.get_results()
        headers = await self.get_headers()

        results = [{k: line[k] for k in headers} for line in results]

        message = tabulate.tabulate(results, headers="keys")
        await ctx.send(preview(f"```{message}```"))

    @commands.command()
    async def standings(self, ctx):
        data = await self.get_standings()

        headers = ['rank', 'displayName', 'totalPoints']

        results = []
        for line in data:
            eventpoints = line['eventPoints']
            eventpoints = {line['eventIndex']: line['points'] for line in eventpoints}
            line_result = {k: line[k] for k in headers}

            results.append(line_result | eventpoints)

        message = tabulate.tabulate(results, headers="keys")

        await ctx.send(preview(f"```{message}```"))


def preview(message):
    return '\n'.join([
        "# 🚧 PREVIEW REPOSNSE MOCK DATA 🚧",
        message,
        "# 🚧 END OF PREVIEW REPOSNSE 🚧"
    ])

async def setup(bot) -> None:
    await bot.add_cog(RallyCalendar(bot))
