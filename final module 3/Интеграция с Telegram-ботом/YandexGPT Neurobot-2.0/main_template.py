import requests
from config_template import IAM_TOKEN, FOLDER_ID, GPT_MODEL, CONTINUE_STORY, END_STORY, SYSTEM_PROMPT
from pprint import pprint
from time import sleep


def do_not_add_users(data: dict):
    if len(data) == 5:
        return True
    else:
        return False













# Подсчитывает количество токенов в тексте
def count_tokens(text):
    headers = { # заголовок запроса, в котором передаем IAM-токен
        'Authorization': f'Bearer {IAM_TOKEN}', # token - наш IAM-токен
        'Content-Type': 'application/json'
    }
    data = {
       "modelUri": f"gpt://{FOLDER_ID}/yandexgpt/latest", # указываем folder_id
       "maxTokens": 100,
       "text": text # text - тот текст, в котором мы хотим посчитать токены
    }
    return len(
        requests.post(
            "https://llm.api.cloud.yandex.net/foundationModels/v1/tokenize",
            json=data,
            headers=headers
        ).json()['tokens']
    ) # здесь, после выполнения запроса, функция возвращает количество токенов в text



def create_new_token():
    """Создание нового токена"""
    metadata_url = "http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token"
    headers = {"Metadata-Flavor": "Google"}
    response = requests.get(metadata_url, headers=headers)
    return response.json()


def ask_gpt(collection, mode='continue'):
    url = f"https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        'Authorization': f'Bearer {IAM_TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {
        "modelUri": f"gpt://{FOLDER_ID}/{GPT_MODEL}/latest",
        "completionOptions": {
            "stream": False,
            "temperature": 0.6,
            "maxTokens": 100
        },
        "messages": []
    }

    for row in collection:
        content = row['content']

        # Добавь дополнительный текст к сообщению пользователя в зависимости от режима
        if mode == 'continue' and row['role'] == 'user':
            content += f'\n{CONTINUE_STORY}'
        elif mode == 'end' and row['role'] == 'user':
            content += f'\n{END_STORY}'

        data["messages"].append(
            {
                "role": row["role"],
                "text": content
            }
        )

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code != 200:
            result = f"Status code {response.status_code}"
            return result
        result = response.json()['result']['alternatives'][0]['message']['text']
    except Exception as e:
        result = "Произошла непредвиденная ошибка. Подробности см. в журнале."
    return result


def create_system_prompt(data, user_id):
    prompt = SYSTEM_PROMPT
    prompt += (f'Напиши  историю в жанре {data[user_id]["genre"]}'
               f' с главным героем {data[user_id]["character"]}. '
               f'Дело происходит в {data[user_id]["setting"]}.')
    return prompt


def time_token():
    a = 0
    while True:
        a += 1
        sleep(5)
        return a
