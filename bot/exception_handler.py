from telebot import TeleBot, ExceptionHandler
import traceback


class CustomExceptionHandler(ExceptionHandler):
    def __init__(self, bot: TeleBot, developer_id: int):
        self.bot = bot
        self.developer_id = developer_id

    def handle(self, exception: Exception) -> None:
        # Получаем информацию об ошибке
        error_message = (
            f"An error occurred:\n{type(exception).__name__}: {exception}\n\n"
        )
        error_message += f"Traceback:\n{traceback.format_exc()}"

        # Отправляем сообщение разработчику
        self.bot.send_message(
            self.developer_id, f"Error Alert:\n{error_message}"
        )
