from bot.bot_context import bot_context
from bot.handlers import general, friends, tournaments, admin
from bot.handlers.answer_to_message import manager as answer_to_message_manager
from utils.custom_logger import logger


# Registering handlers
logger.debug('Registering all handlers...')
general.register_handlers(bot_context)
friends.register_handlers(bot_context)
tournaments.register_handlers(bot_context)
admin.register_handlers(bot_context)
answer_to_message_manager.register_handlers(bot_context)
logger.info('All handlers registered successfully.')
