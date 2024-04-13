import requests


def create_new_token():
    """Создание нового токена"""
    metadata_url = "http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token"
    headers = {"Metadata-Flavor": "Google"}
    response = requests.get(metadata_url, headers=headers)
    return response.json()


from threading import Timer


def repeater(interval, function):
    Timer(interval, repeater, [interval, function]).start()
    function()


# Пример использования: функция `my_task` будет вызываться каждые 2 секунды.
def my_task():
    IAM_token = create_new_token()
    return IAM_token



