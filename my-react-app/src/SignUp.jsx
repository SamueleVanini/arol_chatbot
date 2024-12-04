import "./SignUp.css";
import React from "react";

function SignUp() {
    return (
            <div className="text-container">
            <form className="input-form">
                <input type="text" placeholder="Email" className="input-field" />
                <input type="text" placeholder="Password" className="input-field" />
                <button type="submit" className="submit-button">Sign Up</button>
            </form>
            </div>
    );
    }

export default SignUp;