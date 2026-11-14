async function loadClasses() {
    let resp = await fetch(
        window.location.href,
        {
            method: 'POST',
            body: JSON.stringify({'type': 'get_my_classes'}),
            headers: {
                'Content-Type': 'application/json'
        }
        }

    );

    resp = await resp.json();

    if (resp['type'] != 'success') {
        return;
    }

    let classes = resp['classes']

    let result = '';

    if (classes.length == 0) {
        result = 'У вас пока нет созданный классов';
    }
    else {

        for (let classs of classes) {
            let s = `<div class="classs">
                    <p>${classs['class_name']}</p>
                    <img src='/static/my_classes/trashbin.png' onclick="removeClass(this, ${classs['class_id']})" width=10>
                    <p>айди ${classs['class_id']}</p>`;
            
            let students = classs['students']

            let table = `<table>
                        <tr>
                            <th>Id</th>
                            <th>Name</th>
                            <th>Familia</th>
                            <th></th>
                        </tr>`
            for (let student of students) {
                table += `<tr>
                            <td>${student['id']}</td>
                            <td>${student['name']}</td>
                            <td>${student['familia']}</td>
                            <td>
                                <img src='/static/my_classes/trashbin.png' onclick="removeStudent(this, '${student['id']}', ${classs['class_id']})" width=10>
                            </td>
                        </tr>`
            }
            
            table += '</table>';

            s += table + '</div>';

            result += s
        }
    }

    document.querySelector('.classes').insertAdjacentHTML('afterbegin', result);
}


async function removeStudent(element, student_id, class_id) {
    let resp = await fetch(
        window.location.href,
        {
            method: 'POST',
            body: JSON.stringify({
                'type': 'delete_user_from_class',
                'student_id': student_id,
                'class_id': class_id
            }),
            headers: {
                'Content-Type': 'application/json'
        }
        }
    );

    resp = await resp.json();

    console.log(resp);

    if (resp['type'] != 'success') {
        return;
    }

    element.closest('tr').remove();
}


async function removeClass(element, class_id) {
    let resp = await fetch(
        window.location.href,
        {
            method: 'POST',
            body: JSON.stringify({
                'type': 'delete_class',
                'class_id': class_id
            }),
            headers: {
                'Content-Type': 'application/json'
        }
        }
    );

    resp = await resp.json();

    console.log(resp);

    if (resp['type'] != 'success') {
        return;
    }

    element.closest('div').remove();
}


loadClasses();
