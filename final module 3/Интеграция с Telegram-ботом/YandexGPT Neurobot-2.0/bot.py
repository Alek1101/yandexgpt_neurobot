import config_template
import telebot, logging
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from main_template import ask_gpt, create_system_prompt
import database

bot = telebot.TeleBot(config_template.TOKEN)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%d.%m.%Y, %H:%M:%S',
    filename='logs_file.txt',
    filemode='w'
)


def create_keyboard(options):
    buttons = (KeyboardButton(text=option) for option in options)
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*buttons)
    return keyboard


@bot.message_handler(commands=['debug'])
def debug(m):
    try:
        with open('logs_file.txt', 'r') as f:
            bot.send_document(m.chat.id, f)
    except:
        bot.send_message(m.chat.id, 'Не удалось прислать файл с логами')
        logging.warning('Не удалось отправить документ с логами')


@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, 'Привет, этот бот вместе с пользователем пишет тексты.')
    bot.send_message(m.chat.id, 'Чтобы начать творческую работу, нажми /create', reply_markup=create_keyboard(['/create']))


user_data = {}
user_collection = {}


@bot.message_handler(commands=['create'])
def create(m):
    database.create_table('users')
    user_id = m.from_user.id
    bot.send_message(m.chat.id, "Для начала напиши жанр, в котором хочешь составить сценарий: ")
    user_data[user_id] = {}
    user_collection[user_id] = []
    bot.register_next_step_handler(m, user_genre)


def user_genre(m):
    genre = m.text
    user_id = m.from_user.id
    user_data[user_id]['genre'] = genre
    print(user_data)
    bot.send_message(m.chat.id, 'Теперь опиши персонажа, который будет главным героем: ')
    bot.register_next_step_handler(m, user_character)


def user_character(m):
    character = m.text
    user_id = m.from_user.id
    user_data[user_id]['character'] = character
    bot.send_message(m.chat.id, 'И последнее. Напиши сеттинг, в котором будет жить главный герой: ')
    bot.register_next_step_handler(m, user_setting)


def user_setting(m):
    setting = m.text
    user_id = m.from_user.id
    user_data[user_id]['setting'] = setting
    bot.send_message(m.chat.id, 'Напиши начало истории: ')
    bot.register_next_step_handler(m, story)


def story(m):
    user_id = m.from_user.id
    if m.text != '/end':
        user_collection[user_id].append({'role': 'system', 'content': create_system_prompt(user_data, user_id)})
        user_content = m.text
        assistant_content = ask_gpt(user_collection[user_id])
        bot.send_message(m.chat.id, '')



    else:

        bot.send_message(m.chat.id, 'Вот, что у нас получилось: ')


bot.polling()