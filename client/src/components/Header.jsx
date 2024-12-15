import React from 'react';
import '../Default.css';
import {useNavigate} from "react-router-dom"; // Import the CSS file for styling

function Header() {
    const navigate = useNavigate()
    return (
        <header className="header">
            <img
                src="logo.png"
                alt="Site Logo"
                className="logo"
                onClick={() => navigate("/")}
            />
        </header>
    );
}

export default Header;
