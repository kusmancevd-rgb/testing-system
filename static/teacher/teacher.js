let all_tests;


async function loadMyTests() {
    let resp = await fetch('http://127.0.0.1:5000/teacher', {
        method: "POST", 
        body: JSON.stringify({'type': 'get_my_tests'}),
        headers: {
        'Content-Type': 'application/json'
        }, 
    }
    );
    resp = await resp.json();
    all_tests = resp;
    

    renderTest(resp);
}


function redirectToPage(page) {
    window.location.href = `http://127.0.0.1:5000/${page}`;
    return;

}


function renderTest(resp) {
    let s = '';

    for (let i in resp) {
        test = resp[i];

        s += `<a href='/teacher/test_stats/${test['id']}'>
                <div>
                    ${test['name']}
                    <br>
                    ${test['description']}
                    <br>
                    ${test['date_of_creation']}
                </div>
            </a>`;
    }

    if (resp.length == 0) {
        s = "<div class='no_tests'>У вас пока что нет созданных тестов или поиск ничего не нашёл</div>";
    }

    document.querySelector(".my_tests").innerHTML = s;
}


function testInputHandler(text) {
    let obj = [];
    for (let test of all_tests) {
        if (test['name'].includes(text)) {
            obj.push(test);
        }
    }

    renderTest(obj);
}


function createClass() {
    removeSuccessMessageIfExists();

    let div_content = document.querySelector('.grade').innerHTML;
    if (!div_content) {
        addClassCreation();
    }
    if (div_content) {
        removeClassCreation();
    }
}


function addClassCreation() {
    document.querySelector('.create_class').innerHTML = 'Отменить';


    let elem = document.querySelector('.grade');
    elem.insertAdjacentHTML('afterbegin', `
        <input class='class_name'>
        <button class='submit_class'>Выложить класс</button>`)
    document.querySelector('.submit_class').addEventListener('click', sendClass);
}


function removeClassCreation() {
    document.querySelector('.create_class').innerHTML = 'Создать класс';

    document.querySelector('.grade').innerHTML = '';
}


async function sendClass() {
    let class_name = document.querySelector('.class_name').value;

    let resp = await fetch(window.location.href, {
    method: "POST", 
    body: JSON.stringify({
        'type': 'send_class',
        'name': class_name}),
    headers: {
    'Content-Type': 'application/json'
    }, 
    }
    );
    resp = await resp.json();
    if (resp['type'] == 'incorData') {
        let error_msg = resp['error_message'];
        let error_p = document.querySelector('.error_message');
        if (error_p) {
            error_p.remove();
        }
        document.querySelector('.grade').insertAdjacentHTML('beforeend', `
            <p class='error_message'>${error_msg}</p>`
        );
    }
    if (resp['type'] == 'success') {
        document.querySelector('.grade').insertAdjacentHTML('beforebegin',
            `<p class='success_message'>Класс с айди ${resp['class_id']} был успешно добавлен</p>` 
        )
        removeClassCreation();
    }
}


function removeSuccessMessageIfExists() {
    let msg = document.querySelector('.success_message')
    if (msg) {
        msg.remove();
    }
}


document.querySelector('.create_test').addEventListener('click', () => redirectToPage('teacher/create_test'));
document.querySelector('.test_input').addEventListener('input', (event) => testInputHandler(event.target.value));
document.querySelector('.create_class').addEventListener('click', createClass);
loadMyTests();
