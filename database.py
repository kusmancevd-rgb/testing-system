import sqlite3
import json


def create_tables():
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    conn.execute("PRAGMA foreign_keys = ON")

    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS user
                   (
                       username TEXT PRIMARY KEY,
                       password TEXT,
                       role     TEXT,
                       name     TEXT,
                       familia  TEXT,
                       grade TEXT
                   )
                   ''')

    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS test
                   (
                       id                  INTEGER PRIMARY KEY,
                       username_of_creator TEXT REFERENCES user (username),
                       date_of_creation    TEXT,
                       name                TEXT,
                       description         TEXT,
                       questions           TEXT,
                       max_time INTEGER
                   )
                   ''')

    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS test_solved_by_student
                   (
                       id             INTEGER PRIMARY KEY,
                       test_id        INTEGER REFERENCES test(id),
                       student_id     TEXT REFERENCES user (username),
                       solution       TEXT,
                       time           INTEGER,
                       cheated_chance REAL
                   )
                   ''')

    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS test_started_by_student
                   (
                       id             INTEGER PRIMARY KEY,
                       test_id        INTEGER REFERENCES test (id),
                       student_id     TEXT REFERENCES user (username),
                       time TEXT
                   )
                   ''')

    conn.commit()
    conn.close()


create_tables()


def get_user(username):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    resp = cursor.execute('SELECT * FROM user WHERE username=?', (username, )).fetchone()
    conn.close()
    return resp


def insert_user(username, password, role, name, familia, grade):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO user (username, password, role, name, familia, grade) '
                   'VALUES (?, ?, ?, ?, ?, ?)', (username, password, role, name, familia, grade))
    conn.commit()
    conn.close()


def load_params_of_test_created_by_username(username, *params):
    '''Возвращает короткую информацию (столбцы params) о всех тестах, сделанных username'''

    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    resp = cursor.execute(f'SELECT {", ".join(params)} FROM test where username_of_creator=?', (username, )).fetchall()
    conn.close()

    return resp


def add_test_to_db(dct, username, date):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    cursor.execute('INSERT INTO test (username_of_creator, date_of_creation, name, description, questions, max_time) VALUES (?, ?, ?, ?, ?, ?)',
                   (username, date.strftime('%Y-%m-%d %H:%M:%S'), dct['name'], dct['description'], json.dumps(dict(list(dct.items())[3:])), dct['max_time']))

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


def student_already_started_test(username, test_id):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    res = cursor.execute('SELECT * FROM test_started_by_student WHERE student_id=? and test_id=?', (username, test_id)).fetchall()

    conn.close()

    return len(res) > 0


def test_id_is_valid(test_id):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    res = cursor.execute('SELECT * FROM test WHERE id=?', (test_id, )).fetchall()

    conn.close()

    return len(res) > 0


def add_test_to_started(student_id, test_id, time):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    cursor.execute('INSERT INTO test_started_by_student (test_id, student_id, time) VALUES (?, ?, ?)', (test_id, student_id, time.strftime('%Y-%m-%d %H:%M:%S')))

    conn.commit()
    conn.close()


def get_start_time(student_id, test_id):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    res = cursor.execute('SELECT * FROM test_started_by_student WHERE student_id=? and test_id=?', (student_id, test_id)).fetchone()

    conn.close()
    return res[3]


def add_solution_to_db(student_id, test_id, solution, time, cheated_chance):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    cursor.execute('INSERT INTO test_solved_by_student (student_id, test_id, solution, time, cheated_chance)'
                   'VALUES (?, ?, ?, ?, ?)',
                   (student_id, test_id, solution, time, cheated_chance))

    conn.commit()
    conn.close()


def student_already_completed_test(username, test_id):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    res = cursor.execute('SELECT * FROM test_solved_by_student WHERE student_id=? and test_id=?', (username, test_id)).fetchall()

    conn.close()

    return len(res) > 0
