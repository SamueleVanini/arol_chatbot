import React, {useState} from 'react';
import {useNavigate} from 'react-router-dom';
import './default.css';
import Header from "./Header.jsx";

const Register = () => {

    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');

    const navigate = useNavigate();


    const handleSignUp = async () => {
        if (password !== confirmPassword) {
            alert("Passwords do not match!");
            return;
        }
        const response = await fetch('http://127.0.0.1:80/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({username: username, password: password, password_confirm: confirmPassword})
        });

        if (response.ok) {
            navigate('/login')
        } else {
            const errorData = await response.json();
            alert(`Registration failed: ${errorData.detail}`);
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
                <input
                    type="password"
                    placeholder="Confirm Password"
                    className="input-field"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                />


                <button type="button" className="submit-button" onClick={handleSignUp}>
                    Sign Up
                </button>
            </form>
        </div>


    );
};

export default Register;