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

def load_param_of_test(id):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    resp = cursor.execute("SELECT * FROM test WHERE id=?", (id, )).fetchone()
    conn.close()

    return resp


def load_solutions(test_id):
    '''
    test_id -> [{name:, mark:, cheated_chance:, time:}, {}, ...]
    '''

    '''solution:
    'question-1: [ans1, ans2, ...], question-2: [ans1, ans2, ...]...'
    '''
    mx_score = calculate_max_ball(test_id)

    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    resp = cursor.execute('SELECT * FROM test_solved_by_student WHERE test_id=?', (test_id, )).fetchall()

    result = []

    for solution in resp:
        student_id = solution[2]
        student_data = cursor.execute('SELECT * FROM user WHERE username=?', (student_id, )).fetchone()
        name = student_data[3] + ' ' + student_data[4]

        mark = calculate_mark(json.loads(solution[3]), test_id)
        cheated_chance = solution[5]
        time = solution[4]

        result.append({
            'id': solution[0],
            'name': name,
            'score': f'{mark}/{mx_score}',
            'cheated': cheated_chance,
            'time': time
        })

    conn.close()

    return result


def calculate_mark(solution, test_id):
    '''solution:
        'question-1: [ans1, ans2, ...], question-2: [ans1, ans2, ...]...'
    '''

    '''questions
     {question-1: {......, answers: {answer-1: {}, answer-2: {}}}, question-2: {......, answers: {answer-1: {}, answer-2: {}}}}
     '''

    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    questions = cursor.execute('SELECT * FROM test where id=?', (test_id, )).fetchone()

    questions = json.loads(questions[5])

    score = 0

    for question_key, question in questions.items():
        incorrect_answers = []
        correct_answers = []
        all_answers = []
        answers = question['answers']
        for key, value in answers.items():
            answer_id = int(key[7:])
            is_correct = int(value['is_correct'])
            if not is_correct:
                incorrect_answers.append(answer_id)
            else:
                correct_answers.append(answer_id)
            all_answers.append(answer_id)

        user_answers = solution[question_key]
        user_answers = [int(elem) for elem in user_answers]

        score_for_question = calculate_corectness(all_answers, incorrect_answers, correct_answers, user_answers)

        score += score_for_question * int(question['max_score'])

    conn.close()

    return score


def calculate_corectness(all_answers, incorrect_answers, correct_answers, user_answers):
    print(all_answers, incorrect_answers, correct_answers, user_answers)
    score = len(correct_answers)

    for answer in all_answers:
        if (answer in correct_answers and answer not in user_answers) or (answer in incorrect_answers and answer in user_answers):
            score -= 1

    if len(correct_answers) == 0:
        if len(user_answers) == 0:
            return 1
        return 0

    score = score / len(correct_answers)

    return max(score, 0)


def calculate_max_ball(test_id):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    test_info = cursor.execute('SELECT * FROM test WHERE id=?', (test_id, )).fetchone()[5]
    test_info = json.loads(test_info)

    mx_score = 0
    for key, value in test_info.items():
        mx_score += int(value['max_score'])

    conn.close()

    return mx_score


def get_answers(solution_id):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    res = cursor.execute('SELECT * FROM test_solved_by_student WHERE id=?', (solution_id, )).fetchone()
    student_solutions = json.loads(res[3])

    test_id = res[1]

    test_info = cursor.execute('SELECT * FROM test WHERE id=?', (test_id, )).fetchone()
    questions = json.loads(test_info[5])

    result = {}

    for question_key, question_value in questions.items():
        correct_answers = []
        answers = question_value['answers']
        for key, value in answers.items():
            if value['is_correct']:
                correct_answers.append(key[7:])

        result[question_key] = {'correct': correct_answers,
                                    'student': student_solutions[question_key]}

    conn.close()
    return result


def get_creator_of_solution(solution_id):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    res = cursor.execute('SELECT * FROM test WHERE test.id in (SELECT test_id from test_solved_by_student WHERE test_solved_by_student.id=?)',
                         (solution_id, )).fetchone()

    conn.close()
    return res[1]


def get_test_id(solution_id):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    res = cursor.execute(
        'SELECT * FROM test_solved_by_student WHERE id=?', (solution_id,)).fetchone()

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


def calculate_mark_of_solution_by_id(solution_id):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    res = cursor.execute('SELECT * FROM test_solved_by_student WHERE id=?', (solution_id, )).fetchone()

    solution = json.loads(res[3])
    test_id = res[1]

    conn.close()
    return calculate_mark(solution, test_id)
