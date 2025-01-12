from datetime import datetime

import telebot
import httpx
from telebot.types import Message, Dict, InlineKeyboardMarkup, InlineKeyboardButton, BotCommand, CallbackQuery

from config import BOT_TOKEN
from phrase import phrase_dict
from commands import get_user_language, get_habits_list, scheduler, schedule_user_reminders

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
STEP_DAILY_STATUS = "daily_status"
STEP_ASK_REMINDER = "set_reminder"

# creating hint for bot command
commands_eng = [
    BotCommand("/start", "Launching and changing the bot language"),
    BotCommand("/help", "Show help message"),
    BotCommand("/add_habit", "Add new habit to the list"),
    BotCommand("/delete_habit", "Remove a habit from the list"),
    BotCommand("/daily_habits", "Remove a habit from the list"),
]

commands_rus = [
    BotCommand("/start", "Запуск и изменения языка бота"),
    BotCommand("/help", "Показать справку"),
    BotCommand("/add_habit", "Добавить в список новую привычку"),
    BotCommand("/delete_habit", "Удалить из списка привычку"),
    BotCommand("/daily_habits", "Посмотреть список привычек на сегодня"),
]


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
    (bot.send_message
     (message.from_user.id,
      'Hello, I am a bot to track your habits!\nSelect your language below.⤵️\n\n'
      'Приветствую, я бот для отслеживания твоих привычек!\nВыберите ваш язык ниже.⤵️\n\n',
      reply_markup=choose_langs()))

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
    habit_title = message.text
    lang = get_user_language(message.from_user.id)
    user_states[message.chat.id] = {
        'step': STEP_ASK_REMINDER,
        'habit_title': habit_title
    }

    try:
        response = httpx.post(f"{FASTAPI_URL}habit", params={"user_id": message.from_user.id,
                                                             "habit_title": habit_title})
        response.raise_for_status()
        bot.send_message(message.chat.id, phrase_dict[lang]['habit_added'])
        bot.send_message(message.chat.id, phrase_dict[lang]['check_daily_habits'])
    except httpx.RequestError as e:
        bot.send_message(message.chat.id, f"Ошибка соединения с сервером: {e}")
    except httpx.HTTPStatusError as e:
        bot.send_message(message.chat.id, f"Ошибка сервера: {e.response.text}")


@bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('step') == STEP_ASK_REMINDER)
def aks_time(message: Message) -> None:
    lang = get_user_language(message.from_user.id)
    user_states[message.chat.id]['step'] = STEP_PROCESS_DATA
    habit_title = user_states[message.chat.id]['habit_title']
    time = message.text  # Ожидается формат 'HH:MM'
    reminder_time = datetime.strptime(time, "%H:%M").time()

    if reminder_time:
        try:
            response = httpx.post(f"{FASTAPI_URL}update_reminder", params={"user_id": message.from_user.id,
                                                                           "habit_title": habit_title,
                                                                           "time": reminder_time})
            response.raise_for_status()
            bot.send_message(message.chat.id, phrase_dict[lang]['habit_added'])
            bot.send_message(message.chat.id, phrase_dict[lang]['check_daily_habits'])
        except httpx.RequestError as e:
            bot.send_message(message.chat.id, f"Ошибка соединения с сервером: {e}")
        except httpx.HTTPStatusError as e:
            bot.send_message(message.chat.id, f"Ошибка сервера: {e.response.text}")
        except ValueError:
            bot.send_message(message.chat.id, "Пожалуйста, введите время в формате HH:MM.")


@bot.callback_query_handler(
    func=lambda query: user_states.get(query.message.chat.id, {}).get('step') == STEP_DELETE_HABIT)
def delete_habit(call: CallbackQuery) -> None:
    habit_title = call.data
    lang = get_user_language(call.message.chat.id)
    user_states[call.message.chat.id]['step'] = STEP_PROCESS_DATA

    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    try:
        response = httpx.delete(f"{FASTAPI_URL}habit",
                                params={"user_id": call.message.chat.id,
                                        "habit_title": habit_title})
        response.raise_for_status()
        bot.send_message(call.message.chat.id, phrase_dict[lang]['habit_deleted'])
    except httpx.RequestError as e:
        bot.send_message(call.message.chat.id, f"Ошибка соединения с сервером: {e}")
    except httpx.HTTPStatusError as e:
        bot.send_message(call.message.chat.id, f"Ошибка сервера: {e.response.text}")


@bot.message_handler(commands=['delete_habit'])
def delete_habit(message: Message) -> None:
    lang = get_user_language(message.from_user.id)
    bot.send_message(message.chat.id,
                     phrase_dict[lang]['delete_habit'],
                     reply_markup=chose_habit(message.from_user.id))

    user_states[message.chat.id] = {
        'step': STEP_DELETE_HABIT,
    }


def chose_habit(user_id: int, list_type='total') -> InlineKeyboardMarkup:
    habits_list = get_habits_list(user_id, list_type)
    keyboard = InlineKeyboardMarkup()
    if habits_list is None:
        habits_list = []
    for habit_dict in habits_list:
        habit_title = habit_dict["habit_title"]
        days_count = habit_dict["days_count"]
        text = f"{habit_title} ({days_count}/21)"
        button = InlineKeyboardButton(text=text, callback_data=habit_title)
        keyboard.add(button)
    return keyboard


@bot.message_handler(commands=['daily_habits'])
def check_daily_habits(message: Message) -> None:
    lang = get_user_language(message.from_user.id)
    bot.send_message(message.chat.id,
                     phrase_dict[lang]['daily_habits'],
                     reply_markup=chose_habit(message.from_user.id,
                                              list_type='daily'))

    user_states[message.chat.id] = {
        'step': STEP_DAILY_STATUS,
    }


@bot.callback_query_handler(
    func=lambda query: user_states.get(query.message.chat.id, {}).get('step') == STEP_DAILY_STATUS)
def daily_habit(call: CallbackQuery) -> None:
    habit_title = call.data
    lang = get_user_language(call.message.chat.id)
    user_states[call.message.chat.id]['step'] = STEP_PROCESS_DATA

    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    try:
        response = httpx.post(f"{FASTAPI_URL}habit_completed",
                              params={"user_id": call.message.chat.id,
                                      "habit_title": habit_title})
        response.raise_for_status()
        if response.json()["message"] == "Habit completed successfully":
            bot.send_message(call.message.chat.id, phrase_dict[lang]['habit_completed_21'])
        else:
            bot.send_message(call.message.chat.id, phrase_dict[lang]['habit_completed'])
    except httpx.RequestError as e:
        bot.send_message(call.message.chat.id, f"Ошибка соединения с сервером: {e}")
    except httpx.HTTPStatusError as e:
        bot.send_message(call.message.chat.id, f"Ошибка сервера: {e.response.text}")


def send_reminder(user_id, habit_title):
    bot.send_message(user_id, f"Это ваше напоминание! Не забудьте обновить свои привычки. {habit_title} 🌟")


scheduler.start()
schedule_user_reminders()
# TODO после ввода названия привычки запрашивать время напоминания
# TODO прописать логику получения всего списка привычек
# TODO добавить возможность изменения напоминания времени
# TODO обновлять задачи в кронтабе только у одной привычки, а не проходится по всем привычкам
# TODO откорректировать send_reminder
