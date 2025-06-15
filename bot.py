import json
import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

import os
TOKEN = os.getenv("BOT_TOKEN")

# Файлы для хранения данных
CHAT_USERS_FILE = "chat_users.json"
USER_NAMES_FILE = "user_names.json"

# Храним имена пользователей
user_names = {}
waiting_for_name = set()

# Храним всех участников чата
chat_users = set()

# Загружаем chat_users из файла при старте
def load_chat_users():
    global chat_users
    if os.path.exists(CHAT_USERS_FILE):
        with open(CHAT_USERS_FILE, "r") as f:
            data = json.load(f)
            chat_users.update(data)
            print(f"Загружено пользователей: {len(chat_users)}")

# Загружаем user_names из файла при старте
def load_user_names():
    global user_names
    if os.path.exists(USER_NAMES_FILE):
        with open(USER_NAMES_FILE, "r") as f:
            user_names.update(json.load(f))
            print(f"Загружено имён пользователей: {len(user_names)}")

# Сохраняем chat_users в файл
def save_chat_users():
    with open(CHAT_USERS_FILE, "w") as f:
        json.dump(list(chat_users), f)

# Сохраняем user_names в файл
def save_user_names():
    with open(USER_NAMES_FILE, "w") as f:
        json.dump(user_names, f)

# Приветственная команда
def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    if user_id not in chat_users:
        chat_users.add(user_id)
        save_chat_users()

    waiting_for_name.add(user_id)
    update.message.reply_text("Привет! Ты подключён к чату. Как тебя называть? Напиши своё имя:")

# Обработка всех текстовых сообщений
def echo(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    text = update.message.text

    if user_id in waiting_for_name:
        user_names[str(user_id)] = text  # Сохраняем как str, чтобы json не ругался
        waiting_for_name.remove(user_id)
        save_user_names()
        update.message.reply_text(f"Отлично, {text}! Теперь ты участвуешь в чате.")
        return

    name = user_names.get(str(user_id), update.message.from_user.first_name)
    message_to_send = f"{name}: {text}"

    for chat_user_id in chat_users:
        try:
            context.bot.send_message(chat_id=chat_user_id, text=message_to_send)
        except Exception as e:
            print(f"Ошибка при отправке пользователю {chat_user_id}: {e}")

# Основной запуск бота
def main():
    load_chat_users()
    load_user_names()

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    print("Бот запущен!")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
