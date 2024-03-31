import config_template
import telebot, logging
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from main_template import ask_gpt, create_system_prompt, do_not_add_users, count_tokens
from datetime import datetime

bot = telebot.TeleBot(config_template.TOKEN)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%d.%m.%Y, %H:%M:%S',
    filename='logs_file.txt',
    filemode='w'
)

users_sessions = {}


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
    bot.send_message(m.chat.id, 'Чтобы начать творческую работу, нажми /create',
                     reply_markup=create_keyboard(['/create']))


user_data = {}
user_collection = {}


@bot.message_handler(commands=['create'])
def create(m):
    if not do_not_add_users(users_sessions):
        user_id = m.from_user.id
        bot.send_message(m.chat.id, "Для начала напиши жанр, в котором хочешь составить сценарий: ")
        user_data[user_id] = {}
        user_collection[user_id] = []
        if user_id not in users_sessions:
            users_sessions[user_id] = {'session': 1, 'tokens': 0}
            bot.register_next_step_handler(m, user_genre)
        else:
            if not users_sessions[user_id]['session'] == 3:
                users_sessions[user_id]['session'] += 1
                users_sessions[user_id]['tokens'] = 0
                bot.register_next_step_handler(m, user_genre)
            else:
                bot.send_message(m.chat.id, 'Извините, у вас закончились сессии.')
                logging.info(f'Пользователь {m.from_user.first_name} с id {user_id} истратил все сессии')
    else:
        bot.send_message(m.chat.id, 'Бот не работает, вакантные места кончились.')
        logging.info('Пользователи закончились, бот отключился.')


def user_genre(m):
    genre = m.text
    user_id = m.from_user.id
    user_data[user_id]['genre'] = genre
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
    SYSTEM = create_system_prompt(user_data, user_id)
    user_collection[user_id].append({'role': 'system', 'content': SYSTEM})
    users_sessions[user_id]['tokens'] += count_tokens(SYSTEM)
    bot.register_next_step_handler(m, story)


def story(m):
    user_id = m.from_user.id
    if m.text != '/end':
        user_content = m.text
        users_sessions[user_id]['tokens'] += count_tokens(user_content)
        user_collection[user_id].append({'role': 'user', 'content': user_content})
        if users_sessions[user_id]['tokens'] < 1000:
            assistant_content = ask_gpt(user_collection[user_id])
            users_sessions[user_id]['tokens'] += count_tokens(assistant_content)
            bot.send_message(m.chat.id, 'YandexGPT: ' + assistant_content)
            bot.send_message(m.chat.id, 'Напиши продолжение истории. Чтобы закончить, введи /end.')
            bot.register_next_step_handler(m, story)
        else:
            bot.send_message(m.chat.id, 'Извините, у вас закончились токены.')
            all_text = ''
            for one_mess in user_collection[user_id]:
                if one_mess['role'] != 'system':
                    all_text += '\n' + one_mess['content']
            bot.send_message(m.chat.id, all_text + '\n\nКонец...')
            logging.info(f'Пользователь {m.from_user.first_name} с id {user_id} истратил логины, '
                         f'сессия {users_sessions[user_id]["session"]}')
    else:
        assistant_content = ask_gpt(user_collection[user_id], 'end')
        users_sessions[user_id]['tokens'] += count_tokens(assistant_content)
        user_collection[user_id].append({'role': 'assistant', 'content': assistant_content})
        bot.send_message(m.chat.id, 'Вот, что у нас получилось:')
        all_text = ''
        for one_mess in user_collection[user_id]:
            if one_mess['role'] != 'system':
                all_text += '\n' + one_mess['content']
        bot.send_message(m.chat.id, all_text + '\n\nКонец...')
        print(f'Потрачено {users_sessions[user_id]["tokens"]} токенов.')


bot.polling()
