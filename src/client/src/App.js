import './App.css';
import React from 'react';
import Homepage from './Homepage';
import SignUp from './SignUp';
import Chat from './Chat';
import { Routes, Route } from 'react-router-dom';
import axios from 'axios';


function App() {
  

  return (
    <Routes>
          <Route path="/" element={<Homepage />} />
          <Route path="/signup" element={<SignUp />} />
          <Route path="/chat" element={<Chat />} />
    </Routes>
  );
}

export default App;

