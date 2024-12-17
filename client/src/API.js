const SERVER_URL = 'http://localhost:80';

async function register(username, password, confirmPassword) {
    return await fetch(SERVER_URL + '/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({username: username, password: password, password_confirm: confirmPassword})
    })
        .then(handleInvalidResponse)
        .then(response => response.json());

}

async function login(username, password) {
    return await fetch(SERVER_URL + '/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({username: username, password: password})
    })
        .then(handleInvalidResponse)
        .then(response => response.json());
}

function handleInvalidResponse(response) {
    console.log(response.ok)
    if (!response.ok) {
        throw Error(response.json().detail)
    }
    // let type = response.headers.get('Content-Type');
    // if (type !== null && type.indexOf('application/json') === -1) {
    //     throw new TypeError(`Expected JSON, got ${type}`)
    // }
    return response;
}



const API = {register, login};
export default API;