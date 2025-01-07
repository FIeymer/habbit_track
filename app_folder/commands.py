import telebot
import httpx
from telebot.types import Message, Dict, InlineKeyboardMarkup, InlineKeyboardButton, BotCommand, CallbackQuery

from config import BOT_TOKEN
from phrase import phrase_dict
from models import User

bot = telebot.TeleBot(BOT_TOKEN)
FASTAPI_URL = "http://habit_tracker_api:8000/users/"

# creating user states
user_states: Dict[int, Dict[str, str]] = {}
STEP_ASK_TOKEN = "ask_token"
STEP_ASK_CURRENCY = "ask_currency"
STEP_PROCESS_DATA = "process_data"

# creating hint for bot command
commands_eng = [
    BotCommand("/add_new_habit", "Send to add new habit"),
    BotCommand("/help", "Show help message"),
    BotCommand("/add_habit", "Add new habit to the list")
]

commands_rus = [
    BotCommand("/add_new_habit", "Отправьте для добавления новой привычки"),
    BotCommand("/help", "Показать справку"),
    BotCommand("/add_habit", "Добавить в список новую привычку")
]


def get_user_language(user_id: int) -> str:
    user = User.get(User.user_id)
    return user.language

def choose_langs() -> InlineKeyboardMarkup:
    # Creating buttons
    button_1 = InlineKeyboardButton(text="Eng", callback_data="Eng")
    button_2 = InlineKeyboardButton(text="Rus", callback_data="Rus")

    # Creating keyboard and adding buttons to keyboard
    keyboard = InlineKeyboardMarkup()
    keyboard.add(button_1, button_2)
    return keyboard


@bot.message_handler(commands=['start'])
def handle_start(message: Message) -> None:
    # Answering user to bot start in 2 languages and giving possibility to choose language
    bot.send_message(message.from_user.id, 'Hello, I am a bot for tracking your habits!\nChoose your language below.⤵️\n\n'
                                           'Приветствую, я бот для отслеживания твоих привычек!\nВыберите ваш язык ниже.⤵️\n\n',
                     reply_markup=choose_langs())


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call: CallbackQuery) -> None:
    # Getting user data and language and writing it to database
    bot.send_message(call.message.chat.id, phrase_dict[call.data]['chose_lang'])
    if call.data == "Eng":
        bot.set_my_commands(commands_eng)
    elif call.data == "Rus":
        bot.set_my_commands(commands_rus)

    bot.send_message(call.message.chat.id, phrase_dict[call.data]['help_text'])
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

    user_data = {
        "user_id": call.from_user.id,
        "username": call.from_user.username,
        "first_name": call.from_user.first_name,
        "last_name": call.from_user.last_name,
        "language": call.data,
    }

    try:
        response = httpx.post(FASTAPI_URL, json=user_data)
        response.raise_for_status()
        bot.send_message(call.message.chat.id, "Данные пользователя сохранены.")
    except httpx.RequestError as e:
        bot.send_message(call.message.chat.id, f"Ошибка соединения с сервером: {e}")
    except httpx.HTTPStatusError as e:
        bot.send_message(call.message.chat.id, f"Ошибка сервера: {e.response.text}")


@bot.message_handler(commands=['add_habit'])
def add_habit(message: Message) -> None:
    lang = get_user_language(message.from_user.id)
    bot.send_message(message.chat.id, lang)
