import React, {useState} from 'react';
import {useNavigate} from 'react-router-dom';
import './default.css';
import Header from "./Header.jsx";
import API from "../API.js";
import "./Login.css";

const Login = () => {

    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [errorMessage, setErrorMessage] = useState('');
    const [showError, setShowError] = useState(false);


    const navigate = useNavigate();


    const handleSignIn = async () => {
        API.login(username, password)
            .then(response => {
                localStorage.setItem('token', response.access_token); // Store the token
                navigate('/chat');
            })
            .catch(e => {
                setErrorMessage('Login failed: ' + e.message);
                setShowError(true); // Mostra il pop-up
            })
    };

    const closeErrorPopup = () => {
        setShowError(false); // Chiude il pop-up
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

            
            {showError && (
                <div className="error-popup">
                    <span>{errorMessage}</span>
                    <button className="close-btn" onClick={closeErrorPopup}>Close</button>
                </div>
            )}
        </div>


    );
};

export default Login;