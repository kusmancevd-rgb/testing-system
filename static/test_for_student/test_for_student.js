let all_questions;
let cheated_chance = 0;
let time_left;

async function loadQuestions() {
    console.log(window.location.href);
    let resp = await fetch(
        window.location.href,
        {
            method: 'POST',
            body: JSON.stringify({'type': 'get_test_info'}),
            headers: {
                'Content-Type': 'application/json'
        }
        }

    );

    resp = await resp.json();

    if (resp['type'] != 'success') { 
        return;
    }

    let questions = resp['test'];
    questions = JSON.parse(questions);
    all_questions = questions;

    let result = '';

    for (let question_key of Object.keys(questions)) {
        let s = '<div class="question">';

        s += `<span class=number>${question_key.slice(9)}</span>`;
        let question = questions[question_key];

        s += `<span class=question_text>${question['question']}</span>`;
        s += "<br>";

        if (question['image']) {
            s += `<img class='image' src=${question['image']}></img>`;
            s += "<br>";
        }

        for (let answer of Object.keys(question['answers'])) {
            s += `<input type="checkbox" id='answer-${question_key.slice(9)}-${answer.slice(7)}'>`;
            s += `<span class=answer>${question['answers'][answer]['answer']}</span>`;
            s += "<br>";
        }

        result += s;
        result += '</div>';
    }

    let max_time = resp['max_time'];
    time_left = max_time * 60;

    document.querySelector('.testdescription').insertAdjacentHTML('afterend', 
        `<p class="time">${time_left}</p>`
    );

    document.querySelector('.questions').insertAdjacentHTML('afterbegin', result);
}


function createAnswerList() {
    let solutions = {};
    for (let question_key of Object.keys(all_questions)) {
        let student_answers = [];
        let answers = all_questions[question_key]['answers'];
        for (let answer of Object.keys(answers)) {
            let id = `answer-${question_key.slice(9)}-${answer.slice(7)}`;
            let is_checked = document.querySelector('#' + id).checked;
            if (is_checked) {
                student_answers.push(answer.slice(7));
            }
        }
        solutions[question_key] = student_answers;
    }

    return solutions;
}


async function sendTest() {
    let resp = await fetch(
        window.location.href,
        {
            method: 'POST',
            body: JSON.stringify(
                {
                    'type': 'send_test',
                    'test': createAnswerList(),
                    'cheated_chance': cheated_chance
                }
        ),
            headers: {
                'Content-Type': 'application/json'
        }
        }

    );

    resp = await resp.json();

    if (resp['type'] == 'success') {
        window.location.href = resp['url']
        return;
    }
}


async function decreaseTimer() {
    time_left -= 1;

    document.querySelector('.time').innerText = time_left;

    if (time_left == 0) {
        clearInterval(timerId);
        sendTest();
    }

}

loadQuestions();
document.querySelector('.submittest').addEventListener('click', sendTest);
let timerId = setInterval(decreaseTimer, 1000);
