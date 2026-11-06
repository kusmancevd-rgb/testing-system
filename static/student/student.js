async function handleInput(event) {
    event.preventDefault()

    let resp = await sendResponse();

    if (resp['type'] == 'success') {
        window.location.href = resp['url'];
        return;
    }

    if (resp['type'] == 'alreadyCompleted') {
        let error_message = document.querySelector('.error');

        if (error_message) {
            error_message.remove();
        }

        document.querySelector('.input_test').insertAdjacentHTML('afterend',
            `<p class="error">Вы уше прошли этот тест!</p>`
        );
    }

    if (resp['type'] == 'nan') {
        let error_message = document.querySelector('.error');

        if (error_message) {
            error_message.remove();
        }

        document.querySelector('.input_test').insertAdjacentHTML('afterend',
            `<p class="error">Введите верный номер теста</p>`
        );
    }
}


async function sendResponse() {
    let value = document.querySelector('.input').value;

    let resp = await fetch('http://127.0.0.1:5000/student', {
        method: "POST", 
        body: JSON.stringify(
            {'type': 'load_test',
             'id': value}
            ),
        headers: {
        'Content-Type': 'application/json'
        }, 
    }
    );
    resp = await resp.json();

    return resp;
}


document.querySelector('.input_test').addEventListener('submit', (event) => handleInput(event))
