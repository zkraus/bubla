import logging

from bubla import bubla
import utils

utils.logger_settings.config_console_logger(level=logging.DEBUG)

token = utils.config.load_discord_secret(utils.config.DISCORD_BOT_SECRET_FILENAME)

logger = logging.getLogger(__name__)

bot = bubla.Bubla()
bot.run(token, log_handler=None)
