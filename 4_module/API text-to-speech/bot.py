import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from config import TOKEN, MAX_USER_TTS_SYMBOLS, MAX_TTS_SYMBOLS
from database import count_all_symbol, insert_row
from speech_kit import text_to_speech
from time import sleep

bot = telebot.TeleBot(TOKEN)


def is_tts_symbol_limit(message, text):
    user_id = message.from_user.id
    text_symbols = len(text)

    # Функция из БД для подсчёта всех потраченных пользователем символов
    all_symbols = count_all_symbol(user_id) + text_symbols

    # Сравниваем all_symbols с количеством доступных пользователю символов
    if all_symbols >= MAX_USER_TTS_SYMBOLS:
        msg = f"Превышен общий лимит SpeechKit TTS {MAX_USER_TTS_SYMBOLS}. Использовано: {all_symbols} символов. Доступно: {MAX_USER_TTS_SYMBOLS - all_symbols}"
        bot.send_message(user_id, msg)
        return None

    # Сравниваем количество символов в тексте с максимальным количеством символов в тексте
    if text_symbols >= MAX_TTS_SYMBOLS:
        msg = f"Превышен лимит SpeechKit TTS на запрос {MAX_TTS_SYMBOLS}, в сообщении {text_symbols} символов"
        bot.send_message(user_id, msg)
        return None
    return len(text)


def create_keyboard(options):
    buttons = (KeyboardButton(text=option) for option in options)
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*buttons)
    return keyboard


@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, 'Привет! Я умею озвучивать текст.')
    bot.send_message(m.chat.id, 'Чтобы озвучить текст, напиши команду /speech.',
                     reply_markup=create_keyboard(['/speech']))


@bot.message_handler(commands=['speech'])
def speech_message(m):
    bot.send_message(m.chat.id, 'Отправьте текстовое сообщение, которое нужно озвучить.')
    bot.register_next_step_handler(m, speech_voice)


def speech_voice(m):
    user_id = m.from_user.id
    text = m.text
    if m.content_type != 'text':
        bot.send_message(m.chat.id,'Отправьте текстовое сообщение.')
        return
    text_symbol = is_tts_symbol_limit(m, text)
    if text_symbol is None:
        return

    insert_row(user_id, text, text_symbol)
    status, content = text_to_speech(text)
    if status:

        bot.send_voice(m.chat.id, content)
    else:
        bot.send_message(m.chat.id, content)
    sleep(5)
    bot.send_message(m.chat.id, 'Желаете продолжить озвучку сообщений?',
                     reply_markup=create_keyboard(['Да', 'Нет']))


def message_choice(m):
    ans = m.text
    if ans.lower() == 'Да':
        bot.send_message(m.chat.id, 'Отправьте текстовое сообщение, которое нужно озвучить.')
        bot.register_next_step_handler(m, speech_voice)
    elif ans.lower() == 'Нет':
        bot.send_message(m.chat.id, 'До скорой встречи!')
    else:
        bot.send_message(m.chat.id, 'Желаете продолжить озвучку сообщений?',
                         reply_markup=create_keyboard(['Да', 'Нет']))
        bot.register_next_step_handler(m, message_choice)


bot.polling()