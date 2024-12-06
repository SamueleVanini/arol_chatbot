import React from 'react';
import Homepage from './Homepage';
import Chat from './Chat';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';



function App() {
  

  return (
    <Router>
    <Routes>
          <Route path="/" element={<Homepage />} />
          <Route path="/chat" element={<Chat />} />
    </Routes>
    </Router>
  );
}

export default App;