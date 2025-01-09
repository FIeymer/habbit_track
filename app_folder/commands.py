# TODO: привычки добавляются капсом - исправить
# TODO: Посмотреть пункт 3 в ТЗ и реализововать согласно описанию
# TODO: Добавить учёт дней в привычке
# TODO: Добавить напоминание о выполнение привычки в заданный момент времени
# TODO: Добавить возможность отмечать выполнение привычки, если не выполнена сбрасывать счётчик

import telebot
import httpx
from telebot.types import Message, Dict, InlineKeyboardMarkup, InlineKeyboardButton, BotCommand, CallbackQuery

from config import BOT_TOKEN
from phrase import phrase_dict

import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(BOT_TOKEN)
FASTAPI_URL = "http://habit_tracker_api:8000/users/"

# creating user states
user_states: Dict[int, Dict[str, str]] = {}
STEP_ADD_HABIT = "ask_habit"
STEP_PROCESS_DATA = "process_data"
STEP_SET_LANG = "set_lang"
STEP_DELETE_HABIT = "delete_habit"

# creating hint for bot command
commands_eng = [
    BotCommand("/add_new_habit", "Send to add new habit"),
    BotCommand("/help", "Show help message"),
    BotCommand("/add_habit", "Add new habit to the list"),
    BotCommand("/delete_habit", "Remove a habit from the list")
]

commands_rus = [
    BotCommand("/add_new_habit", "Отправьте для добавления новой привычки"),
    BotCommand("/help", "Показать справку"),
    BotCommand("/add_habit", "Добавить в список новую привычку"),
    BotCommand("/delete_habit", "Удалить из списка привычку")
]


def get_user_language(user_id: int) -> str:
    try:
        response = httpx.post(f"{FASTAPI_URL}get_language", params={"user_id": user_id})
        response.raise_for_status()
        return response.json().get("language")
    except httpx.RequestError as e:
        return f"Ошибка соединения с сервером: {e}"
    except httpx.HTTPStatusError as e:
        return f"Ошибка сервера: {e.response.text}"


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

    user_states[message.from_user.id] = {
        'step': STEP_SET_LANG,
        'command': 'start'
    }


@bot.callback_query_handler(func=lambda query: user_states.get(query.message.chat.id, {}).get('step') == STEP_SET_LANG)
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

    user_states[call.message.chat.id] = {
        'step': STEP_PROCESS_DATA
    }

    try:
        response = httpx.post(FASTAPI_URL, json=user_data)
        response.raise_for_status()
    except httpx.RequestError as e:
        bot.send_message(call.message.chat.id, f"Ошибка соединения с сервером: {e}")
    except httpx.HTTPStatusError as e:
        bot.send_message(call.message.chat.id, f"Ошибка сервера: {e.response.text}")


@bot.message_handler(commands=['help'])
def help_command(message: Message) -> None:
    lang = get_user_language(message.from_user.id)
    text = phrase_dict[lang]['help_text']
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['add_habit'])
def add_habit(message: Message) -> None:
    lang = get_user_language(message.from_user.id)
    bot.send_message(message.chat.id, phrase_dict[lang]['add_habit'])

    user_states[message.chat.id] = {
        'step': STEP_ADD_HABIT
    }


@bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('step') == STEP_ADD_HABIT)
def adding_habit(message: Message) -> None:
    habit_title = message.text.upper()
    lang = get_user_language(message.from_user.id)
    user_states[message.chat.id]['step'] = STEP_PROCESS_DATA

    try:
        response = httpx.post(f"{FASTAPI_URL}habit", params={"user_id": message.from_user.id, "habit_title": habit_title})
        response.raise_for_status()
        bot.send_message(message.chat.id, phrase_dict[lang]['habit_added'])
    except httpx.RequestError as e:
        bot.send_message(message.chat.id, f"Ошибка соединения с сервером: {e}")
    except httpx.HTTPStatusError as e:
        bot.send_message(message.chat.id, f"Ошибка сервера: {e.response.text}")


@bot.callback_query_handler(func=lambda query: user_states.get(query.message.chat.id, {}).get('step') == STEP_DELETE_HABIT)
def delete_habit(call: CallbackQuery) -> None:
    habit_title = call.data
    lang = get_user_language(call.message.chat.id)
    logger.info(f"Язык = {lang}, call.data = {call.data}, call.message.from_user.id == {call.message.from_user.id}, call.message.chat.id == {call.message.chat.id}")
    user_states[call.message.chat.id]['step'] = STEP_PROCESS_DATA

    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    try:
        response = httpx.delete(f"{FASTAPI_URL}habit", params={"user_id": call.message.chat.id, "habit_title": habit_title})
        response.raise_for_status()
        bot.send_message(call.message.chat.id, phrase_dict[lang]['habit_deleted'])
    except httpx.RequestError as e:
        bot.send_message(call.message.chat.id, f"Ошибка соединения с сервером: {e}")
    except httpx.HTTPStatusError as e:
        bot.send_message(call.message.chat.id, f"Ошибка сервера: {e.response.text}")


@bot.message_handler(commands=['delete_habit'])
def delete_habit(message: Message) -> None:
    lang = get_user_language(message.from_user.id)
    bot.send_message(message.chat.id, phrase_dict[lang]['delete_habit'], reply_markup=chose_habit(message.from_user.id))

    user_states[message.chat.id] = {
        'step': STEP_DELETE_HABIT,
    }


def chose_habit(user_id: int) -> InlineKeyboardMarkup:
    habits_list = get_habits_list(user_id)
    keyboard = InlineKeyboardMarkup()
    for habit in habits_list:
        button = InlineKeyboardButton(text=habit, callback_data=habit)
        keyboard.add(button)
    return keyboard


def get_habits_list(user_id: int) -> list:
    try:
        response = httpx.post(f"{FASTAPI_URL}habits_list", params={"user_id": user_id})
        response.raise_for_status()
        return response.json()
    except httpx.RequestError as e:
        bot.send_message(user_id, f"Ошибка соединения с сервером: {e}")
    except httpx.HTTPStatusError as e:
        bot.send_message(user_id, f"Ошибка сервера: {e.response.text}")