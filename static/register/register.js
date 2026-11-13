async function setRegisterData() {
    let obj = {
        'username': document.querySelector('.username').value,
        'password': document.querySelector('.password').value,
        'repearpassword': document.querySelector('.repeatpassword').value,
        'name': document.querySelector('.name').value,
        'familia': document.querySelector('.familia').value,
        'role': document.querySelector('.selectrole').value,
        'grade': document.querySelector('.class')?.value
    };
    obj = JSON.stringify(obj);

    let resp = await fetch(
        'http://127.0.0.1:5000/register',
        {
            method: 'POST',
            body: obj,
            headers: {
                'Content-Type': 'application/json'
        }
        }

    );


    resp = await resp.json();

    let type = resp['type'];
    if (type == 'IncorData'){
        let prev_error = document.querySelector('.errormessage');
        if (prev_error) {
            prev_error.remove()
        }

        document.querySelector('.submit').insertAdjacentHTML('beforebegin', `
            <p class="errormessage">${resp['html']}</p>
        `);
    }
    if (type == 'Redirect') {
        window.location.href = resp['url'];
    }

}


function changeRole(role) {
    if (role == 'teacher') {
        let class_input = document.querySelector('.class');
        if (class_input) {
            class_input.remove();
        }
    }

    if (role == 'student') {
        let prev_class_input = document.querySelector('.class');
        if (prev_class_input) {
            prev_class_input.remove();
        }
        let oporni_elem = document.querySelector('.familia').nextElementSibling;
        oporni_elem.insertAdjacentHTML('afterend',
            `<input class='class' value='Id класса'>`
        );
    }
}


document.querySelector('.submit').addEventListener('click', setRegisterData);
document.querySelector('.selectrole').addEventListener('change', (event) => changeRole(event.target.value));
