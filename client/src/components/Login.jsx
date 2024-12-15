import React, {useState} from 'react';
import {useNavigate} from 'react-router-dom';
import './default.css';
import Header from "./Header.jsx";

const Login = () => {

    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');


    const navigate = useNavigate();


    const handleSignIn = async () => {
        const response = await fetch('http://127.0.0.1:80/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({username: username, password: password})
            });

            if (response.ok) {
                const data = await response.json();
                localStorage.setItem('token', data.access_token); // Store the token
                navigate('/chat');
            } else {
                alert('Login failed: ' + response.statusText);
            }
    };


    return (
        <div>
            <Header/>
            <form className="input-form" onSubmit={(e) => e.preventDefault()}>
                <input
                    type="text"
                    placeholder="Username"
                    className="input-field"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                />
                <input
                    type="password"
                    placeholder="Password"
                    className="input-field"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                />

                <button type="button" className="submit-button" onClick={handleSignIn}>
                    Sign In
                </button>
                <span
                    className="clickable-text"
                    onClick={() => navigate("/register")}> Don't have an account yet? Click to register now!</span>

            </form>
        </div>


    );
};

export default Login;