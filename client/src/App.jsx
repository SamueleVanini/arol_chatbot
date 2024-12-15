import React from 'react';
import Homepage from './Homepage';
import Chat from './Chat';
import {BrowserRouter as Router, Routes, Route} from 'react-router-dom';
import Register from "./Register.jsx";
import Login from "./Login.jsx";


function App() {


    return (
        <Router>
            <Routes>
                <Route path="/" element={<Homepage/>}/>
                <Route path="/register" element={<Register/>}/>
                <Route path="/login" element={<Login/>}/>
                <Route path="/chat" element={<Chat/>}/>
            </Routes>
        </Router>
    );
}

export default App;