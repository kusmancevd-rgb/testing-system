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

    for (let test of resp) {
        s += `<a href='/teacher/test_stats/${test['id']}'><div>${test['name']}<br>${test['description']}<br>${test['date_of_creation']}</div></a>`;
    }

    if (resp.length == 0) {
        s = "<div class='no_tests'>У вас пока что нет созданных тестов или поиск ничего не нашёл</div>";
    }

    document.querySelector(".my_tests").innerHTML = s;
}


function inputHandler(text) {
    obj = [];
    for (let test of all_tests) {
        if (test['name'].includes(text)) {
            obj.push(test);
        }
    }

    renderTest(obj);
}


document.querySelector('.create_test').addEventListener('click', () => redirectToPage('teacher/create_test'));
document.querySelector('.test_input').addEventListener('input', (text) => inputHandler(text.target.value));
loadMyTests();
