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

    let result;

    if (solutions.length == 0) {
        result = 'У этого теста пока нету решений';
    } else {
        result = `<table class='table'>
                    <tr>
                        <th>Имя</th>
                        <th>Балл</th>
                        <th>Списано</th>
                        <th>Время выполнения</th>
                    </tr>`;
        
        
        for (let solution of solutions) {
            result += `<tr>
                        <td><a href="/teacher/solution/${solution['id']}">${solution['name']}</a></td>
                        <td>${solution['score']}</td>
                        <td>${solution['cheated']}</td>
                        <td>${solution['time']}</td>
                    </tr>`;
        }
        
        result += '</table>';
    }

    document.querySelector('.solutions').insertAdjacentHTML('afterbegin', result);
}


loadSolutions();
