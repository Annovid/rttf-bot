from bot.bot_chat import bot_context


def main():
    bot_context.load_user_config_matching()
    bot_context.bot.infinity_polling()


if __name__ == "__main__":
    main()
