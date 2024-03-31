import sqlite3
import config_template
from datetime import datetime
from pprint import pprint


def execute_query(sql_query, data=None):
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    if data:
        cursor.execute(sql_query, data)
    else:
        cursor.execute(sql_query)

    connection.commit()
    connection.close()


def execute_selection_query(sql_query, data=None):
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()

    if data:
        cursor.execute(sql_query, data)
    else:
        cursor.execute(sql_query)
    rows = cursor.fetchall()
    connection.close()
    return rows


def clean_table():
    # TODO: Требуется написать код для удаления всех записей таблицы
    sql = 'DELETE FROM users'
    execute_query(sql)


def create_table(table_name):
    sql_query = (f'CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY, '
                 f'user_id INTEGER, '
                 f'role TEXT, '
                 f'content TEXT, '
                 f'date DATETIME, '
                 f'token INTEGER, '
                 f'session INTEGER);')
    execute_query(sql_query)


def delete_data(user_id: int):
    sql = f'DELETE FROM users WHERE user_id = {user_id}'
    execute_query(sql)


def get_all_tokens():
    sql = f'SELECT DISTINCT user_id, session from users;'
    result = execute_selection_query(sql)
    answer = []
    for i in result:
        answer.append(i)
    return answer






# # TODO: Подсчёт всех токенов за всё время
def get_tokens():
    sql1 = f'SELECT DISTINCT session FROM users ORDER BY date DESC'
    res_session = execute_selection_query(sql1)
    all_tokens = 0
    for ell in res_session:
        sql2 = f"SELECT token FROM users WHERE session={ell[0]}"
        res_count = 0
        res_tokens = execute_selection_query(sql2)
        for ell2 in res_tokens:
            res_count += ell2[0]
            all_tokens += ell2[0]

        print(f'За сессию {ell[0]} было потрачено: {res_count} токенов')
    print(f'Всего потрачено {all_tokens} токенов')
get_tokens()
# create_table('users')

def get_data_for_user(user_id):
    # TODO: Здесь вам нужно добавить код для выполнения запроса и записи в логи
    sql = f'SELECT * FROM users WHERE user_id={user_id};'
    result = execute_selection_query(sql)
    answer = []
    for i in result:
        answer.append(i)
    return answer[0]


def get_last_session_id(user_id):
    sql = f'SELECT session FROM users WHERE user_id={user_id} ORDER BY date DESC LIMIT 1'
    result = execute_selection_query(sql)
    answer = []
    for i in result:
        answer.append(i)
    return result[0]


# Функция, возвращающая размер указанной сессии в токенах
def get_session_size(user_id, session_id):
    sql = f'SELECT token FROM users WHERE user_id={user_id} and session={session_id} ORDER BY date DESC LIMIT 1;'
    result = execute_selection_query(sql)
    answer = []
    for i in result:
        answer.append(i)
    return result[0]


def is_limit_users():
    connection = sqlite3.connect('users.db')

    cursor = connection.cursor()
    result = cursor.execute('SELECT DISTINCT user_id FROM users;')

    count = 0  # количество пользователей
    for i in result:  # считаем количество полученных строк
        count += 1  # одна строка == один пользователь
    connection.close()
    return count >= config_template.MAX_USERS
# Если функция возвращает False, то можно добавлять пользователей


def insert_row(values):
    # TODO: Требуется написать код для вставки новой строки в таблицу
    data = values
    sql = f'INSERT INTO users (user_id, role, content, date, token, session) VALUES (?, ?, ?, ?, ?, ?);'
    execute_query(sql, data)


def is_value_in_table(column_name, value):
    # TODO: Требуется написать код для проверки есть ли запись в таблице
    # Создаёт запрос SELECT колонка FROM имя_таблицы WHERE колонка == значение LIMIT 1
    sql = f'SELECT {column_name} FROM users WHERE {column_name}="{value}" LIMIT 1;'
    result = execute_selection_query(sql)
    if result:
        answer = []
        for i in result:
            answer.append(i)
        return result[0]
    else:
        return False


def update_data(user_id: int, column: str, new_value: str):
    sql = f'UPDATE users SET {column} = "{new_value}" WHERE user_id = {user_id};'
    execute_query(sql)


# insert_row([8, 'test_7', 'апрtafar ', datetime.now(), 345, 5])
# print(is_limit_users())
# print(get_session_size(3,7))
# print(get_data_for_user(1))
# delete_data(8)
# print(get_last_session_id(2))
# print(is_value_in_table('token', 100))
# print(get_all_tokens())