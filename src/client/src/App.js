import './App.css';
import React from 'react';
import Homepage from './Homepage';
import SignUp from './SignUp';
import Chat from './Chat';
import { Routes, Route } from 'react-router-dom';
import axios from 'axios';


function App() {

  const [data, setData] = useState(null);


  useEffect(() => {
    axios.get('http://127.0.0.1:5000/api/data')
      .then(response => {
        setData(response.data);
      })
      .catch(error => {
        console.error('There was an error fetching the data!', error);
      });
  }, []);

  return (
    <Routes>
          <Route path="/" element={<Homepage />} />
          <Route path="/signup" element={<SignUp />} />
          <Route path="/chat" element={<Chat />} />
    </Routes>
  );
}

export default App;

