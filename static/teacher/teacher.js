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

    let s = '';

    for (let test of resp) {
        s += `<a href='/teacher/test_stats/${test['id']}'><div>${test['name']}<br>${test['description']}<br>${test['date_of_creation']}</div></a>`;
    }

    if (resp.length == 0) {
        s = "<div class='no_tests'>У вас пока что нет созданных тестов</div>";
    }

    document.querySelector(".my_tests").insertAdjacentHTML('beforeend', s);
}


function redirectToPage(page) {
    window.location.href = `http://127.0.0.1:5000/${page}`;
    return;

}


document.querySelector('.create_test').addEventListener('click', () => redirectToPage('teacher/create_test'))

loadMyTests();
