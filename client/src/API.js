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

const logout = () => {
    // Clear the token from local storage or any other storage mechanism
    localStorage.removeItem('token');
    // Optionally, you can also clear other user-related data
    localStorage.removeItem('user');
    // Redirect to login page or home page
    window.location.href = '/login';
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

export const fetchSession = async (token) => {
    try {
        const response = await fetch(`${SERVER_URL}/user/session`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });
        const data = await response.json();
        return data.session_id;
    } catch (error) {
        console.error('Error fetching session ID:', error);
        throw error;
    }
};

export const makeQueryAPI = async (activeSessionId, userInput, token) => {
    try {
        const response = await fetch(`${SERVER_URL}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ session_id: activeSessionId, input: userInput })
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Network response was not ok: ${response.status} - ${errorText}`);
        } else {
            const result = await response.json();
            return result;
        }
    } catch (error) {
        console.error('There was an error!', error);
        throw error;
    }
};

export const fetchChatHistoryAPI = async (token) => {
    try {
        const response = await fetch(`${SERVER_URL}/user/session/all`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });
        const data = await response.json();
        return data.session_ids;
    } catch (error) {
        console.error('Error fetching chat history:', error);
        throw error;
    }
};

export const fetchSessionHistoryAPI = async (session_id, token) => {
    try {
        const response = await fetch(`${SERVER_URL}/user/session/${session_id}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });
        const data = await response.json();
        return data.history.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
    } catch (error) {
        console.error('Error fetching session history:', error);
        throw error;
    }
};

const API = {register, login, logout, fetchSession, makeQueryAPI, fetchChatHistoryAPI, fetchSessionHistoryAPI};
export default API;