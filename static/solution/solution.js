async function loadAnswers() {
    let resp = await fetch(window.location.href,
        {
        method: "POST", 
        body: JSON.stringify({'type': 'get_answers'}),
        headers: {
        'Content-Type': 'application/json'
        }, 
    }
    );

    resp = await resp.json();

    if (resp['type'] != 'success') {
        return;
    }

    let table = `<table class='table'>
                    <tr>
                        <th>Номер</th>
                        <th>Ответы ученика</th>
                        <th>Правильные ответы</th>
                    </tr>`;

    let answers = resp['answers'];

    for (let question of Object.keys(answers)) {
        let correct_answers = answers[question]['correct'];
        let student_answers = answers[question]['student'];

        table += `
        <tr>
          <td>${question.slice(9)}</td>
          <td>${student_answers.join(', ')}</td>
          <td>${correct_answers.join(', ')}</td>
        </tr>
        `;
    }

    document.querySelector('.answers').insertAdjacentHTML('afterbegin', table);
}


loadAnswers();
