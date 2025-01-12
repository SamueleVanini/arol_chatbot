import React from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import Homepage from './components/Homepage.jsx';
import Chat from './components/Chat';
import {BrowserRouter as Router, Routes, Route, Navigate} from 'react-router-dom';
import Register from "./components/Register.jsx";
import Login from "./components/Login.jsx";
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import {Container} from "react-bootstrap";
import {Authorization, AuthProvider, useAuth} from "./components/AuthContext.jsx";
import {NotFoundLayout} from "./components/NotFoundLayout.jsx";

function ProtectedRoute({children}) {
    const {authenticatedStatus} = useAuth();
    console.log("this is it = " + authenticatedStatus)
    return (authenticatedStatus === Authorization.Authorized)
        ? children : <Navigate to="/login"/>;
}

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
        <AuthProvider>
            <Container fluid className="flex-grow-1 d-flex flex-column">
                <ToastContainer/>
                <Router>
                    <Routes>
                        <Route path="/" element={<Homepage/>}/>
                        <Route path="/register" element={<Register/>}/>
                        <Route path="/login" element={<Login showError={handleShowError}/>}/>
                        <Route path="/chat" element={<ProtectedRoute><Chat/></ProtectedRoute>}/>
                        <Route path="*" element={<NotFoundLayout/>}/>
                    </Routes>
                </Router>
            </Container>
        </AuthProvider>
    );
}

export default App;