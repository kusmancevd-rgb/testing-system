async function loadQuestions() {
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
            let is_checked = ''
            if (question['answers'][answer]['is_correct'] == "1") {
                is_checked = 'checked';
            }

            s += `<input type="checkbox" value=${question['answers'][answer]['is_correct']} ${is_checked} style="pointer-events: none;">`;
            s += `<span class=answer>${question['answers'][answer]['answer']}</span>`;
            s += "<br>";
        }

        result += s;
        result += '</div>';
    }

    document.querySelector('.questions').insertAdjacentHTML('afterbegin', result);
}


loadQuestions();
