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

async function fetchSession(token) {

    return await fetch(`${SERVER_URL}/user/session`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        }
    })
        .then(handleInvalidResponse)
        .then(response => response.json())
}


async function makeQuery(activeSessionId, userInput, token) {
    return await fetch(`${SERVER_URL}/query`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({session_id: activeSessionId, input: userInput})
    })
        .then(handleInvalidResponse)
        .then(response => response.json())
}

async function fetchChatHistory(token) {
    return await fetch(`${SERVER_URL}/user/session/all`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        }
    })
        .then(handleInvalidResponse)
        .then(response => response.json())
        .then(response => response.session_ids)
}

async function fetchSessionHistory(session_id, token) {
    return await fetch(`${SERVER_URL}/user/session/${session_id}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        }
    })
        .then(handleInvalidResponse)
        .then(response => response.json())
        .then(response => response.history.sort((a, b) => a.timestamp - b.timestamp))
}

const logout = () => {
    // Clear the token from local storage or any other storage mechanism
    localStorage.removeItem('token');
    // Optionally, you can also clear other user-related data
    localStorage.removeItem('user');
    // Redirect to login page or home page
    window.location.href = '/login';
}

function handleInvalidResponse(response) {
    if (!response.ok) {
        return response.json().then(errorData => {
            throw new Error(errorData.detail);
        });
    }
    return response;
}


const API = {register, login, logout, fetchSession, makeQuery, fetchChatHistory, fetchSessionHistory};
export default API;