import telebot
from telebot.types import Message, Dict, InlineKeyboardMarkup, InlineKeyboardButton, BotCommand, CallbackQuery

from config import BOT_TOKEN
from phrase import phrase_dict
from models import User
from database import session

bot = telebot.TeleBot(BOT_TOKEN)

# creating user states
user_states: Dict[int, Dict[str, str]] = {}
STEP_ASK_TOKEN = "ask_token"
STEP_ASK_CURRENCY = "ask_currency"
STEP_PROCESS_DATA = "process_data"

# creating hint for bot command
commands_eng = [
    BotCommand("/add_new_habit", "Send to add new habit"),
    BotCommand("/help", "Show help message"),
]

commands_rus = [
    BotCommand("/add_new_habit", "Отправьте для добавления новой привычки"),
    BotCommand("/help", "Показать справку"),
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

    user = User(
        user_id=call.from_user.id,
        username=call.from_user.username,
        first_name=call.from_user.first_name,
        last_name=call.from_user.last_name,
        language=call.data
    )

    session.merge(user)
    session.commit()

