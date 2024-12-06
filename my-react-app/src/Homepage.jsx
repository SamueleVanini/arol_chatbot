import React, { useState } from 'react';
import './Homepage.css';

const Homepage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleSignIn = async () => {
    const response = await fetch('http://localhost:3001/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ username: email, password: password })
    });

    if (response.ok) {
      const data = await response.json();
      alert('Login successful! Token: ' + data.access_token);
    } else {
      alert('Login failed: ' + response.statusText);
    }
  };

  const handleSignUp = async () => {
    const response = await fetch('http://localhost:3001/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ username: username, password: password })
    });

    if (response.ok) {
      alert('Registration successful! You can now log in.');
    } else {
      alert('Registration failed: ' + response.statusText);
    }
  };


  return (

      <form className="input-form" onSubmit={(e) => e.preventDefault()}>
        <input
          type="text"
          placeholder="Email"
          className="input-field"
          value={email}
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
        <button type="button" className="submit-button" onClick={handleSignUp}>
          Sign Up
        </button>
      </form>

  );
};

export default Homepage;