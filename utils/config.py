import json
import os

DISCORD_BOT_SECRET_PATH = os.path.abspath('credentials/discord_bot_secret.json')

REMINDER_CHANNEL_ID = 482629422181122051

COMMAND_PREFIX = '.'

CALENDAR_ID = ('7304e91b1051c078c561adc8143c9ca58d5e73950b6c0a91e5fca48850188e1a@group.calendar.google.com')
CREDENTIALS_FILENAME = 'credentials/calendar_secret.json'
TOKEN_FILENAME = 'credentials/calendar_token.json'

DAYS_END_SOON = 2
DAYS_START_SOON = 3


def load_discord_secret(filename):
    data = None
    with open(filename) as f:
        data = json.load(f)

    if not data:
        raise Exception('Cannot load discord secret')

    discord_bot_secret = data['discord_bot_secret']

    return discord_bot_secret
