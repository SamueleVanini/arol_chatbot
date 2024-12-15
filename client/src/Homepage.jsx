import React, {useState} from 'react';
import {useNavigate} from 'react-router-dom';
import './default.css';
import Header from "./components/Header.jsx";
import VideoSection from "./components/VideoSection.jsx";

const Homepage = () => {


    const navigate = useNavigate();

    return (
        <div>
            <Header/>
            <VideoSection/>
            <div className="button-overlay">
                <button className="overlay-button"
                        onClick={()=>{navigate("login")}}
                >
                    Start Chatting with our AI Assistant
                </button>
            </div>
        </div>

    );
}

export default Homepage;