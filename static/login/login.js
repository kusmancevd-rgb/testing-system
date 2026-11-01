async function sendLoginData() {
    let text = await fetch('http://127.0.0.1:5000/', {
        method: "POST", 
        body: JSON.stringify({'login': document.querySelector('.login').value, 
            'password': document.querySelector('.password').value
        }),
        headers: {
        'Content-Type': 'application/json'
        }, 
    }
    );

    resp = await text.json();

    let type = resp['type'];

    if (type == 'IncorData') {
        let prev_error = document.querySelector('.errormessage');

        if (prev_error) {
            prev_error.remove();
        }

        document.querySelector('.passwordbutton').insertAdjacentHTML('afterend', `
        <p class='errormessage'>${resp['html']}</p>
        `);
        }
    if (type == 'Redirect') {
        window.location.href = resp['url'];
    }
}


document.querySelector('.passwordbutton').addEventListener('click', sendLoginData);