from bot.handlers import general, friends, tournaments, admin
from bot.handlers.answer_to_message import manager as answer_to_message_manager
from bot.bot_context import BotContext
from utils.custom_logger import logger

# Initializing bot context
logger.debug('Initializing BotContext...')
bot_context = BotContext()
logger.info('BotContext initialized successfully.')

# Loading user configuration mappings
logger.debug('Loading user configuration mappings...')
bot_context.load_user_config_matching()
logger.info('User configuration mappings loaded successfully.')


# Registering handlers
logger.debug('Registering all handlers...')
general.register_handlers(bot_context)
friends.register_handlers(bot_context)
tournaments.register_handlers(bot_context)
admin.register_handlers(bot_context)
answer_to_message_manager.register_handlers(bot_context)
logger.info('All handlers registered successfully.')
