from time import sleep
from main_template import create_new_token


FOLDER_ID = 'b1gg4891rufkm43he5im'
GPT_MODEL = 'yandexgpt-lite'

MAX_PROJECT_TOKENS = 15000  # Макс. Количество токенов на весь проект
MAX_USERS = 5  # Макс. Количество пользователей на весь проект
MAX_SESSIONS = 3  # Макс. Количество сессий у пользователя
MAX_TOKENS_IN_SESSION = 1000

TOKEN = ''

CONTINUE_STORY = 'Продолжи сюжет в 1-3 предложения и оставь интригу. '
END_STORY = 'Напиши завершение истории c неожиданной развязкой.'

# Напиши системный промт, который объяснит нейросети, как правильно писать сценарий вместе с пользователем
SYSTEM_PROMPT = ('Напиши короткую историю вместе с пользователем. Сначала пишет пользователь, потом ты. Не добавляй '
                 'никакой пояснительный текст от себя.')

while True:
    IAM_TOKEN = create_new_token()
    sleep(43200)
