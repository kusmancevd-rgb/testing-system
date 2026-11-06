from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user
from datetime import datetime
from utils import *


app = Flask(__name__)
app.secret_key = 'ddddffcfssssgdddgddddfoddcoddddgddd'

login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin):
    def __init__(self, username, password, role, name, familia):
        self.username = username
        self.password = password
        self.role = role
        self.name = name
        self.familia = familia

    def get_id(self):
        return self.username


@login_manager.user_loader
def load_user(username):
    resp = get_user(username)
    if not resp:
        return None
    return User(*resp)


@app.route('/', methods=['GET', 'POST'])
def login_page():
    if request.method == 'GET':
        if not current_user.is_authenticated:
            return render_template('login.html')

        if current_user.role == 'teacher':
            return redirect(url_for('teacher_page'))
        if current_user.role == 'student':
            return redirect(url_for('student_page'))

    if request.method == 'POST':
        data = request.get_json()
        username = data['login']
        password = data['password']

        user = load_user(username)

        if not user:
            return jsonify({'type': 'IncorData', 'html': 'некорректный пользователь'})

        if user.password == password:
            login_user(user, remember=True)
            if user.role == 'teacher':
                return jsonify({'type': 'Redirect', 'url': url_for('teacher_page')})
            if user.role == 'student':
                return jsonify({'type': 'Redirect', 'url': url_for('student_page')})
        else:
            return jsonify({'type': 'IncorData', 'html': 'неверный пароль!'})


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'GET':
        if not current_user.is_authenticated:
            return render_template('register.html')

        if current_user.role == 'teacher':
            return redirect(url_for('teacher_page'))
        if current_user.role == 'student':
            return redirect(url_for('student_page'))

    if request.method == 'POST':
        data = request.get_json()
        username = data['username']
        password = data['password']
        repeatpassword = data['repearpassword']
        role = data['role']
        name = data['name']
        familia = data['familia']

        if load_user(username):
            return jsonify({'type': "IncorData", 'html': "Данный username уже занят"})
        if password != repeatpassword:
            return jsonify({'type': "IncorData", 'html': "Пароли не совпадают"})
        if role not in ['teacher', 'student']:
            return jsonify({'type': 'IncorData', 'html': "Некорректная роль"})
        if not (password and username and name and familia):
            return jsonify({'type': 'IncorData', 'html': "Заполните все поля"})

        insert_user(username, password, role, name, familia)
        user = load_user(username)

        login_user(user, remember=True)

        if user.role == 'teacher':
            return jsonify({'type': 'Redirect', 'url': url_for('teacher_page')})
        if user.role == 'student':
            return jsonify({'type': 'Redirect', 'url': url_for('student_page')})


@app.route('/teacher', methods=['GET', 'POST'])
@login_required
def teacher_page():
    if current_user.role != 'teacher':
        return "No permission"

    if request.method == 'GET':
        return render_template('teacher.html', name=f"{current_user.familia.capitalize()} {current_user.name[0].upper()}")

    if request.method == 'POST':
        req = request.get_json()
        if req['type'] == 'get_my_tests':
            tests = get_param_of_test_created_by_username(current_user.username, 'name', 'description', 'date_of_creation', 'id')
            return jsonify(tests)


@app.route('/teacher/create_test', methods=['GET', 'POST'])
@login_required
def test_creation_page():
    if current_user.role != 'teacher':
        return "No permission"

    if request.method == 'GET':
        return render_template('test_creation.html', name=f"{current_user.familia.capitalize()} {current_user.name[0].upper()}")

    if request.method == 'POST':
        req = request.get_json()
        add_test_to_db(req, username=current_user.username, date=datetime.now())

        print(req)

        return jsonify({'type': 'success', 'url': url_for('teacher_page')})


@app.route('/teacher/test_stats/<test_id>', methods=['GET', 'POST'])
@login_required
def test_stats(test_id):
    if current_user.role != 'teacher':
        return "No permission"
    if get_creator_of_test(test_id) != current_user.username:
        return "No permission"

    if request.method == 'GET':
        test_info = get_param_of_test(test_id)
        test_name = test_info[3]
        return render_template('test_stats.html',
                               name=f"{current_user.familia.capitalize()} {current_user.name[0].upper()}",
                               test_id=test_info[0],
                               test_name=test_name)

    if request.method == 'POST':
        req = request.get_json()
        if req['type'] == 'load_solutions':
            solutions = load_solutions(test_id)
            return jsonify({'type': 'success', 'solutions': solutions})


@app.route('/teacher/solution/<solution_id>', methods=['GET', 'POST'])
@login_required
def solution(solution_id):
    if current_user.role != 'teacher':
        return "NO PERMISSION"
    if get_creator_of_solution(solution_id) != current_user.username:
        return "NO PERMISSION"

    if request.method == 'GET':
        test_info = get_param_of_test(get_info_of_solution(solution_id)[1])
        test_name = test_info[3]
        solution_info = get_info_of_solution(solution_id)
        return render_template('solution.html',
                               name=f"{current_user.familia.capitalize()} {current_user.name[0].upper()}",
                               test_name=test_name,
                               student_name=get_user(solution_info[2])[3] + " " + get_user(solution_info[2])[4],
                               test_id=solution_info[1],
                               cheated_chance=solution_info[5],
                               time=solution_info[4],
                               mark=calculate_mark_of_solution_by_id(solution_id))

    if request.method == 'POST':
        req = request.get_json()
        if req['type'] == 'get_answers':
            answers = get_answers(solution_id)
            return jsonify({'type': 'success', 'answers': answers})


@app.route('/teacher/test/<test_id>', methods=['GET', 'POST'])
@login_required
def teacher_test(test_id):
    if current_user.role != 'teacher':
        return "NO PERMISSION"
    if get_param_of_test(test_id)[1] != current_user.username:
        return "No Permission"

    if request.method == 'GET':
        test_info = get_param_of_test(test_id)

        name = test_info[3]
        description = test_info[4]
        time = test_info[5]

        return render_template('test_for_teacher.html',
                               name=f"{current_user.familia.capitalize()} {current_user.name[0].upper()}",
                               test_name=name,
                               test_description=description,
                               time=time)

    if request.method == 'POST':
        req = request.get_json()

        if req['type'] == 'get_test_info':
            test_info = get_param_of_test(test_id)[5]

            return jsonify({'type': 'success', 'test': test_info})


@app.route('/student', methods=['GET', 'POST'])
@login_required
def student_page():
    if current_user.role != 'student':
        return "No permission"

    if request.method == 'GET':
        return render_template('student.html',
                               name=f"{current_user.familia.capitalize()} {current_user.name[0].upper()}")

    if request.method == 'POST':
        req = request.get_json()

        if req['type'] == 'load_test':
            test_id = req['id']

            if student_already_passed_test(current_user.username, test_id):
                return jsonify({'type': 'alreadyCompleted'})

            if not test_id_is_valid(test_id):
                return jsonify({'type': 'nan'})

            return jsonify({'type': 'success', 'url': '/student/test'})


app.run()
