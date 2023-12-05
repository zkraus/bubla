import json
import os
import logging

log = logging.getLogger(__name__)


def load_discord_secret(filename):
    data = None
    with open(filename) as f:
        data = json.load(f)

    if not data:
        raise Exception('Cannot load discord secret')

    discord_bot_secret = data['discord_bot_secret']

    return discord_bot_secret


def load_config(filename):
    data = None
    with open(filename) as f:
        data = json.load(f)
    if not data:
        log.error(f"Unable to load config.")
        raise Exception('Cannot load config, sorry')

    return data


config_data = load_config('credentials/config.json')

DISCORD_BOT_GUILD_ID = config_data['discord_bot_guild_id']

DISCORD_BOT_SECRET_FILENAME = config_data['discord_bot_secret_filename']

DISCORD_REMINDER_CHANNEL_ID = config_data['discord_reminder_channel_id']

DISCORD_COMMAND_PREFIX = config_data['discord_command_prefix']

CALENDAR_ID = config_data['calendar_id']
CALENDAR_SECRET_FILENAME = config_data['calendar_secret_filename']
CALENDAR_TOKEN_FILENAME = config_data['calendar_token_filename']
CALENDAR_API_KEY_FILENAME = config_data['calendar_api_key_filename']
CALENDAR_REFRESH_HOUR = config_data['calendar_refresh_hour']

DISCORD_EVENT_END_SOON_DAYS = config_data['discord_event_end_soon_days']
DISCORD_EVENT_START_SOON_DAYS = config_data['discord_event_start_soon_days']

DISCORD_REMINDER_HOUR = config_data['discord_reminder_hour']
