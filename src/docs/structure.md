Разделение большого кода Telegram-бота на множество файлов сделает проект более структурированным, модульным и поддерживаемым. Вот как можно организовать файлы и модули для данного кода:

---

## **1. Основная структура проекта**
```plaintext
project/
├── bot/
│   ├── __init__.py
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── general.py         # Общие команды (start, help, back)
│   │   ├── friends.py         # Команды управления друзьями (add_friend, delete_friend)
│   │   ├── tournaments.py     # Команды связанные с турнирами
│   │   ├── fallback.py        # Обработчики для сообщений без команд
│   └── bot_setup.py           # Настройка бота (bot_context, регистрация хендлеров)
├── services/
│   ├── __init__.py
│   ├── user_service.py        # Работа с UserConfig
│   ├── friend_service.py      # Работа с друзьями
│   ├── tournament_service.py  # Работа с турнирами
├── utils/
│   ├── __init__.py
│   ├── general.py             # Вспомогательные функции (get_text, parse_id)
│   ├── rttf.py                # Работа с API RTTF
│   ├── settings.py            # Настройки
│   ├── models.py              # Модели: UserConfig, Tournament
│   ├── state_machine.py       # FSM для управления состояниями
├── main.py                    # Точка входа в приложение
└── requirements.txt           # Зависимости
```

---

## **2. Файлы и их содержание**

### **`main.py`**
Точка входа для запуска бота.

```python
from bot.bot_setup import bot_context

if __name__ == '__main__':
    bot_context.bot.infinity_polling()
```

---

### **`bot/bot_setup.py`**
Настройка бота, регистрация хендлеров.

```python
from telegram import Bot
from telegram.ext import Dispatcher
from bot.handlers import general, friends, tournaments, fallback
from utils.settings import settings
from bot.bot_context import BotContext

# Создаём бот и контекст
bot = Bot(token=settings.BOT_TOKEN)
bot_context = BotContext(bot)

# Регистрация хендлеров
general.register_handlers(bot_context)
friends.register_handlers(bot_context)
tournaments.register_handlers(bot_context)
fallback.register_handlers(bot_context)
```

---

### **`bot/handlers/general.py`**
Обработчики для команд `/start`, `/help`, `/back`.

```python
from telegram import Message
from bot.bot_context import BotContext
from utils.general import get_text
from utils.models import StateMachine

def register_handlers(bot_context: BotContext):
    bot = bot_context.bot

    @bot.message_handler(commands=['start'])
    def start(message: Message):
        text = get_text('start.txt')
        bot.reply_to(message, text)
        with bot_context.user_config_session(message.from_user.id) as user_config:
            user_config.state = StateMachine.MAIN

    @bot.message_handler(commands=['help', 'back'])
    def help_or_back(message: Message):
        text = get_text('help.txt')
        bot.reply_to(message, text)
        with bot_context.user_config_session(message.from_user.id) as user_config:
            user_config.state = StateMachine.MAIN
```

---

### **`bot/handlers/friends.py`**
Обработчики для команд `/add_friend`, `/delete_friend`, `/get_friends`.

```python
from telegram import Message
from bot.bot_context import BotContext
from utils.general import parse_id, get_valid_initials
from utils.rttf import get_player_info

def register_handlers(bot_context: BotContext):
    bot = bot_context.bot

    @bot.message_handler(commands=['add_friend'])
    def add_friend(message: Message):
        bot.reply_to(message, 'Инструкции для добавления друга...')
        with bot_context.user_config_session(message.from_user.id) as user_config:
            user_config.state = StateMachine.ADD_FRIEND

    @bot.message_handler(commands=['get_friends'])
    def get_friends(message: Message):
        # Логика работы с друзьями
        pass

    @bot.message_handler(commands=['delete_friend'])
    def delete_friend(message: Message):
        # Логика удаления друзей
        pass
```

---

### **`bot/handlers/tournaments.py`**
Обработчики для команд связанных с турнирами.

```python
from telegram import Message
from bot.bot_context import BotContext
from services.tournament_service import TournamentService

def register_handlers(bot_context: BotContext):
    bot = bot_context.bot
    tournament_service = TournamentService()

    @bot.message_handler(commands=['get_tournaments_info'])
    def get_tournaments_info(message: Message):
        # Логика получения информации о турнирах
        pass
```

---

### **`services/user_service.py`**
Сервис для работы с пользователями.

```python
class UserService:
    def get_user_config(self, user_id):
        # Получить конфигурацию пользователя
        pass

    def update_user_state(self, user_id, state):
        # Обновить состояние пользователя
        pass
```

---

### **`services/friend_service.py`**
Сервис для управления друзьями.

```python
class FriendService:
    def add_friend(self, user_id, friend_id):
        # Логика добавления друга
        pass

    def delete_friend(self, user_id, friend_id):
        # Логика удаления друга
        pass

    def get_friends(self, user_id):
        # Получение списка друзей
        pass
```

---

### **`services/tournament_service.py`**
Сервис для работы с турнирами.

```python
class TournamentService:
    def get_tournament_info(self, friend_ids):
        # Логика получения информации о турнирах
        pass
```

---

### **`utils/general.py`**
Вспомогательные функции.

```python
def get_text(file_name):
    with open(f"texts/{file_name}", "r", encoding="utf-8") as f:
        return f.read()

def parse_id(text):
    # Разбор ID из текста
    pass
```

---

### **Преимущества такой структуры**
1. **Читаемость:** Код разделён по логическим модулям.
2. **Модульность:** У каждого файла есть своя зона ответственности.
3. **Расширяемость:** Легко добавлять новые функции, не ломая существующий код.
4. **Тестируемость:** Каждый файл можно протестировать отдельно.