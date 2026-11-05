from database import *
import json


def load_solutions(test_id):
    '''
    test_id -> [{name:, mark:, cheated_chance:, time:}, {}, ...]
    '''

    '''solution:
    'question-1: [ans1, ans2, ...], question-2: [ans1, ans2, ...]...'
    '''
    mx_score = calculate_max_ball(test_id)

    resp = get_solution_info_by_test_id(test_id)

    result = []

    for solution in resp:
        student_id = solution[2]
        student_data = get_user(student_id)
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

    return result


def calculate_mark(solution, test_id):
    '''solution:
        'question-1: [ans1, ans2, ...], question-2: [ans1, ans2, ...]...'
    '''

    '''questions
     {question-1: {......, answers: {answer-1: {}, answer-2: {}}}, question-2: {......, answers: {answer-1: {}, answer-2: {}}}}
     '''

    questions = get_param_of_test(test_id)

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
    test_info = get_param_of_test(test_id)[5]
    test_info = json.loads(test_info)

    mx_score = 0
    for key, value in test_info.items():
        mx_score += int(value['max_score'])

    return mx_score


def get_answers(solution_id):
    '''
    solution_id ->
    {question-1: {correct: [], student: []}, question-2: {...}, ...}
    '''
    res = get_info_of_solution(solution_id)
    student_solutions = json.loads(res[3])

    test_id = res[1]

    test_info = get_param_of_test(test_id)
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

    return result


def calculate_mark_of_solution_by_id(solution_id):
    res = get_info_of_solution(solution_id)

    solution = json.loads(res[3])
    test_id = res[1]

    return calculate_mark(solution, test_id)