import logging

import discord
import json

import bubla
import utils
import logger_settings

logger_settings.config_console_logger()

token = utils.load_discord_secret(utils.discord_secret_path)

logger = logging.getLogger(__name__)

bot = bubla.Bubla()
bot.run(token, log_handler=None)
