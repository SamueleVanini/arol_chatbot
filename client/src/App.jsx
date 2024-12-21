import React from 'react';
import Homepage from './components/Homepage.jsx';
import Chat from './components/Chat';
import {BrowserRouter as Router, Routes, Route} from 'react-router-dom';
import Register from "./components/Register.jsx";
import Login from "./components/Login.jsx";
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import {Container} from "react-bootstrap";


function App() {

    const handleShowError = (message) => {
        toast.error(message ? message : "An Error happened!", {
            position: "top-right",
            autoClose: 2000,
            hideProgressBar: false,
            closeOnClick: true,
            pauseOnHover: false,
            draggable: true,
            progress: undefined,
        });
    };

    return (
        <Container fluid className="flex-grow-1 d-flex flex-column">
            <ToastContainer/>
            <Router>
                <Routes>
                    <Route path="/" element={<Homepage/>}/>
                    <Route path="/register" element={<Register/>}/>
                    <Route path="/login" element={<Login showError={handleShowError}/>}/>
                    <Route path="/chat" element={<Chat/>}/>
                </Routes>
            </Router>
        </Container>
    );
}

export default App;