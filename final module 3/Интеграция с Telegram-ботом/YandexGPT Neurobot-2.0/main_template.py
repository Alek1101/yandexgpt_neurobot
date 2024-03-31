import requests
from config_template import IAM_TOKEN, FOLDER_ID, GPT_MODEL, CONTINUE_STORY, END_STORY, SYSTEM_PROMPT
from pprint import pprint
import time


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


# def main(user_id=123321):
#     print("Привет! Я помогу тебе составить классный сценарий!")
#     genre = input("Для начала напиши жанр, в котором хочешь составить сценарий: ")
#     user_id = 123321
#     # TODO: 'INSERT INTO users (user_id, genre) VALUE (?, ?)'
#     character = input("Теперь опиши персонажа, который будет главным героем: ")
#     # TODO: 'INSERT INTO users (user_id, character) VALUE (?, ?)'
#     setting = input("И последнее. Напиши сеттинг, в котором будет жить главный герой: ")
#
#     # Запиши полученную информацию в user_data
#
#     user_data = {123321: {
#         'genre': genre,
#         'character': character,
#         'setting': setting
#     }}
#
#     # Запиши системный промт, созданный на основе полученной информации от пользователя, в user_collection
#
#     user_collection = {
#         123321: [
#             {'role': 'system', 'content': create_system_prompt(user_data, 123321)},
#
#         ]
#     }
#
#     user_content = input('Напиши начало истории: \n')
#     while user_content.lower() != 'end':
#         # Запиши user_content в user_collection
#         user_collection[123321].append({'role': 'user', 'content': user_content})
#         assistant_content = ask_gpt(user_collection[123321])
#
#         # Запиши assistant_content в user_collection
#
#         print('YandexGPT: ', assistant_content)
#         user_content = input('Напиши продолжение истории. Чтобы закончить введи end: \n')
#
#     assistant_content = ask_gpt(user_collection[user_id], 'end')
#
#     # Запиши assistant_content в user_collection
#     user_collection[123321].append({'role': 'assistant', 'content': assistant_content})
#
#     print('\nВот, что у нас получилось:\n')
#
#     # Напиши красивый вывод получившейся истории
#     # print(f'{user_collection=}\n\n{user_data=}')
#     # print('******----*********')
#
#     for one_mess in user_collection[123321]:
#         print(one_mess['content'])
#
#     input('\nКонец... ')
#
#
# if __name__ == "__main__":
#     main()

# create_new_token()