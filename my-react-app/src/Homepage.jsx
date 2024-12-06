import React, { useState } from 'react';
import './Homepage.css';

const Homepage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isSignUp, setIsSignUp] = useState(false);


  const handleSignIn = async () => {
    setIsSignUp(false);
    // const response = await fetch('http://localhost:3001/login', {
    //   method: 'POST',
    //   headers: {
    //     'Content-Type': 'application/json'
    //   },
    //   body: JSON.stringify({ username: username, password: password })
    // });

    // if (response.ok) {
    //   const data = await response.json();
    //   alert('Login successful! Token: ' + data.access_token);
    // } else {
    //   alert('Login failed: ' + response.statusText);
    // }
  };

  const handleSignUp = async () => {
    setIsSignUp(true);
    // const response = await fetch('http://localhost:3001/register', {
    //   method: 'POST',
    //   headers: {
    //     'Content-Type': 'application/json'
    //   },
    //   body: JSON.stringify({ username: username, password: password })
    // });

    // if (response.ok) {
    //   alert('Registration successful! You can now log in.');
    // } else {
    //   alert('Registration failed: ' + response.statusText);
    // }
  };

  const handleSubmitSignUp = () => {
    if (password !== confirmPassword) {
      alert("Passwords do not match!");
      return;
    }
    // Handle sign-up logic
  };


  return (

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
         {isSignUp && (
        <input
          type="password"
          placeholder="Confirm Password"
          className="input-field"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
        />
      )}
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