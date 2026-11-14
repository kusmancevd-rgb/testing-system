from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user
from datetime import datetime
from utils import *


app = Flask(__name__)
app.secret_key = 'ddsdsaddfsadddssdfssdcsddsdsassfdfsacfsfdsdsffsssdsfsdfssdssmmssdfdsvcbssgcdddgddddfoddsdccvc'

login_manager = LoginManager()
login_manager.init_app(app)


@app.after_request
def add_headers_and_inject_script(response):
    # 1. Запрещаем кеширование (заголовки)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'

    # 2. Автоматически вставляем скрипт в HTML
    # Проверяем, что сервер возвращает именно HTML-страницу (а не JSON или картинку)
    if response.content_type.startswith('text/html') and not response.direct_passthrough:
        # Наш код для защиты от кнопки "Назад"
        script = b"""
        <script>
            window.addEventListener('pageshow', function (event) {
                if (event.persisted) {
                    window.location.reload();
                }
            });
        </script>
        """
        # Ищем закрывающий тег </body> и вставляем скрипт прямо перед ним
        response.data = response.data.replace(b'</body>', script + b'</body>')

    return response


class User(UserMixin):
    def __init__(self, username, password, role, name, familia, grade):
        self.username = username
        self.password = password
        self.role = role
        self.name = name
        self.familia = familia
        self.grade = grade

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
        if current_user.is_authenticated:
            if current_user.role == 'teacher':
                return redirect(url_for('teacher_page'))
            if current_user.role == 'student':
                return redirect(url_for('student_page'))

        if not current_user.is_authenticated:
            return render_template('login.html')

    if request.method == 'POST':
        if current_user.is_authenticated:
            if current_user.role == 'teacher':
                return jsonify({'type': 'Redirect', 'url': '/teacher'})
            if current_user.role == 'student':
                return jsonify({'type': 'Redirect', 'url': '/student'})

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
        if current_user.is_authenticated:
            if current_user.role == 'teacher':
                return redirect(url_for('teacher_page'))
            if current_user.role == 'student':
                return redirect(url_for('student_page'))

        if not current_user.is_authenticated:
            return render_template('register.html')

    if request.method == 'POST':
        if current_user.is_authenticated:
            if current_user.role == 'teacher':
                return jsonify({'type': 'Redirect', 'url': '/teacher'})
            if current_user.role == 'student':
                return jsonify({'type': 'Redirect', 'url': '/student'})

        data = request.get_json()
        username = data['username']
        password = data['password']
        repeatpassword = data['repearpassword']
        role = data['role']
        name = data['name']
        familia = data['familia']
        grade = data.get('grade', '')

        if load_user(username):
            return jsonify({'type': "IncorData", 'html': "Данный username уже занят"})
        if password != repeatpassword:
            return jsonify({'type': "IncorData", 'html': "Пароли не совпадают"})
        if role not in ['teacher', 'student']:
            return jsonify({'type': 'IncorData', 'html': "Некорректная роль"})
        if not (password and username and name and familia):
            return jsonify({'type': 'IncorData', 'html': "Заполните все поля"})
        if role != 'teacher':
            if not grade:
                grade = 1
            elif not check_if_grade_exists(grade):
                return jsonify({'type': 'IncorData', 'html': "Класса с таким ID не существует"})

        insert_user(username, password, role, name, familia, grade)
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

        if req['type'] == 'send_class':
            req = request.get_json()
            class_name = req['name']

            if not class_name:
                return jsonify({'type': 'incorData', 'error_message': 'Заполните все поля'})
            if class_already_exists_for_teacher(current_user.username, class_name):
                return jsonify({'type': 'incorData', 'error_message': 'Такой класс уже существует'})

            add_class_to_db(current_user.username, class_name)
            class_id = get_id_of_class(current_user.username, class_name)

            return jsonify({'type': 'success', 'class_id': class_id})


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
    if not get_param_of_test(test_id):
        return "No such test"
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

        if req['type'] == 'send_class_assignment':
            class_id = req['class_id']

            if not check_if_grade_exists(class_id):
                return jsonify({'type': 'incorData', 'error_message': 'Этого класса не существует'})
            if check_if_assignment_exists(test_id, class_id):
                return jsonify({'type': 'incorData', 'error_message': 'Вы уже назначили этот тест этому классу'})
            if get_creator_of_class(class_id) != current_user.username:
                return jsonify({'type': 'incorData', 'error_message': 'У вас нет доступа к этому классу'})

            add_testAssignmentToClass_to_db(test_id, class_id)

            return jsonify({'type': 'success'})


@app.route('/teacher/solution/<solution_id>', methods=['GET', 'POST'])
@login_required
def solution(solution_id):
    if not get_info_of_solution(solution_id):
        return "NO such solution"
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
    if not get_param_of_test(test_id):
        return "No such test"
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


@app.route('/teacher/my_classes', methods=['GET', 'POST'])
@login_required
def my_classes():
    if request.method == 'GET':
        return render_template('my_classes.html',
                               name=f"{current_user.familia.capitalize()} {current_user.name[0].upper()}")

    if request.method == 'POST':
        req = request.get_json()

        if req['type'] == 'get_my_classes':
            return jsonify({'type': 'success', 'classes': load_classes(current_user.username)})

        if req['type'] == 'delete_class':
            class_id = req['class_id']

            if not check_if_grade_exists(class_id):
                return jsonify({'type': 'error'})
            if get_creator_of_class(class_id) != current_user.username:
                return jsonify({'type': 'error'})

            delete_class(class_id)

            return jsonify({'type': 'success'})

        if req['type'] == 'delete_user_from_class':
            student_id = req['student_id']
            class_id = req['class_id']
            if get_creator_of_class(class_id) == current_user.username and int(get_user(student_id)[5]) == int(class_id):
                remove_user_from_class(student_id)

                return jsonify({'type': 'success'})

            return jsonify({'type': 'error'})


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

            if student_already_started_test(current_user.username, test_id):
                return jsonify({'type': 'alreadyCompleted'})

            if not test_id_is_valid(test_id):
                return jsonify({'type': 'nan'})

            return jsonify({'type': 'success', 'url': f'/student/test/{test_id}'})

        if req['type'] == 'load_class_assignment':
            class_id = get_user(current_user.username)[5]

            assignments = load_assignments(current_user.username, class_id)
            return jsonify({'type': 'success', 'assignments': assignments})


@app.route('/student/test/<test_id>', methods=['GET', 'POST'])
@login_required
def student_test(test_id):
    if current_user.role != 'student':
        return "No permission"
    if not get_param_of_test(test_id):
        return "No such test"

    if request.method == 'GET':
        if student_already_started_test(current_user.username, test_id):
            return 'Error'

        add_test_to_started(current_user.username, test_id, datetime.now())
        return render_template('test_for_student.html',
                               name=f"{current_user.familia.capitalize()} {current_user.name[0].upper()}",
                               test_name=get_param_of_test(test_id)[3],
                               test_description=get_param_of_test(test_id)[4])

    if request.method == 'POST':
        req = request.get_json()

        if student_already_completed_test(current_user.username, test_id):
            return jsonify({'type': 'error'})

        if req['type'] == 'get_test_info':
            return jsonify({'type': 'success', 'test': get_param_of_test(test_id)[5], 'max_time': get_param_of_test(test_id)[6]})

        if req['type'] == 'send_test':
            time_now = datetime.now()

            time_started = get_start_time(current_user.username, test_id)
            time_started = datetime.strptime(time_started, '%Y-%m-%d %H:%M:%S')

            time_for_solving = (time_now - time_started).total_seconds() / 60

            cheated_chance = req['cheated_chance']
            max_time = get_param_of_test(test_id)[6]

            if time_for_solving > max_time + 1:
                cheated_chance = 1

            add_solution_to_db(current_user.username, test_id, json.dumps(req['test']), f'{time_for_solving} мин', cheated_chance)

            return jsonify({'type': 'success', 'url': '/student'})


app.run()
