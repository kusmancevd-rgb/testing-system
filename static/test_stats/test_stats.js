let all_solutions;


async function loadSolutions() {
    let resp = await fetch(
        window.location.href,
        {
            method: 'POST',
            body: JSON.stringify({'type': 'load_solutions'}),
            headers: {
                'Content-Type': 'application/json'
        }
        }

    );

    resp = await resp.json();
    
    if (resp['type'] != 'success') {
        return;
    }

    let solutions = resp['solutions'];

    all_solutions = solutions;

    insertGrades();
    renderSolutions(solutions);
}


function renderSolutions(solutions) {
    let result;

    if (solutions.length == 0) {
        result = 'У этого теста пока нету решений';
    } else {
        result = `<table class='table'>
                    <tr>
                        <th>Класс</th>
                        <th>Имя</th>
                        <th>Балл</th>
                        <th>Списано</th>
                        <th>Время выполнения</th>
                    </tr>`;
        
        
        for (let solution of solutions) {
            result += `<tr>
                        <td>${solution['grade']}</td>
                        <td><a href="/teacher/solution/${solution['id']}">${solution['name']}</a></td>
                        <td>${solution['score']}</td>
                        <td>${solution['cheated']}</td>
                        <td>${solution['time']}</td>
                    </tr>`;
        }
        
        result += '</table>';
    }

    let solutions_div = document.querySelector('.solutions');
    solutions_div.innerHTML = result;
}


function onGradeChange(grade) {
    let result = [];

    if (grade == 'all') {
        result = all_solutions;
    } else {
        for (let solution of all_solutions) {
            if (solution['grade'] == grade) {
                result.push(solution);
            }
        }
    }
    renderSolutions(result);
}


function insertGrades() {
    let selector = document.querySelector('.grade');
    let added_grades = [];

    for (let solution of all_solutions) {
        let grade = solution['grade']
        if (!added_grades.includes(grade)) {
            added_grades.push(grade);
            selector.insertAdjacentHTML('beforeend',
                `<option value="${grade}">${grade}</option>`
            );
        }
    }
}


loadSolutions();
document.querySelector('.grade').addEventListener('change', (event) => onGradeChange(event.target.value));
