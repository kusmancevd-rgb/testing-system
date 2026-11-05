import sqlite3
import json


def get_user(username):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    resp = cursor.execute('SELECT * FROM user WHERE username=?', (username, )).fetchone()
    conn.close()
    return resp


def insert_user(username, password, role, name, familia):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO user (username, password, role, name, familia) '
                   'VALUES (?, ?, ?, ?, ?)', (username, password, role, name, familia))
    conn.commit()
    conn.close()


def load_params_of_test_created_by_username(username, *params):
    '''Возвращает короткую информацию (столбцы params) о всех тестах, сделанных username'''

    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    resp = cursor.execute(f'SELECT {", ".join(params)} FROM test where username_of_creator=?', (username, )).fetchall()
    conn.close()

    # Преобразование [(..., ..., ...), (..., ..., ...)] в [{name: ..., description: ..., date: ...}, {...}]
    lst = []
    for i in range(len(resp)):
        lst.append({})
        for j in range(len(params)):
            lst[i][params[j]] = resp[i][j]

    return lst


def add_test_to_db(dct, username, date):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    cursor.execute('INSERT INTO test (username_of_creator, date_of_creation, name, description, questions) VALUES (?, ?, ?, ?, ?)',
                   (username, date.strftime('%Y-%m-%d %H%M'), dct['name'], dct['description'], json.dumps(dict(list(dct.items())[2:]))))

    conn.commit()
    conn.close()

def get_param_of_test(id):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    resp = cursor.execute("SELECT * FROM test WHERE id=?", (id, )).fetchone()
    conn.close()

    return resp


def get_creator_of_solution(solution_id):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    res = cursor.execute('SELECT * FROM test WHERE test.id in (SELECT test_id from test_solved_by_student WHERE test_solved_by_student.id=?)',
                         (solution_id, )).fetchone()

    conn.close()
    return res[1]


def get_info_of_solution(solution_id):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    res = cursor.execute('SELECT * FROM test_solved_by_student WHERE id=?', (solution_id, )).fetchone()

    conn.close()
    return res


def get_creator_of_test(test_id):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    res = cursor.execute('SELECT * FROM test WHERE id=?', (test_id, )).fetchone()

    conn.close()
    return res[1]


def get_solution_info_by_test_id(test_id):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    res = cursor.execute("SELECT * FROM test_solved_by_student WHERE test_id=?", (test_id, )).fetchall()

    conn.close()

    return res
