import telebot
from telebot.types import Message, Dict, InlineKeyboardMarkup, InlineKeyboardButton, BotCommand

from config import BOT_TOKEN

bot = telebot.TeleBot(BOT_TOKEN)

# creating user states
user_states: Dict[int, Dict[str, str]] = {}
STEP_ASK_TOKEN = "ask_token"
STEP_ASK_CURRENCY = "ask_currency"
STEP_PROCESS_DATA = "process_data"

# creating hint for bot commands
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
