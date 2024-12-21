import React, {useState, useEffect, useRef} from 'react';
import './Chat.css';
import API from '../API';
import {useAuth} from "./AuthContext.jsx";


function Chat({showError}) {
    const [input, setInput] = useState('');
    const [sessionId, setSessionId] = useState(null);
    const [response, setResponse] = useState('');
    const [currentChat, setCurrentChat] = useState([]);
    const [chatHistory, setChatHistory] = useState([]);
    const [pendingInput, setPendingInput] = useState(null);
    const [menuOpen, setMenuOpen] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const token = localStorage.getItem('token');
    const editableRef = useRef(null);
    const {logout} = useAuth();

    const toggleMenu = () => {
        setMenuOpen(!menuOpen);
    };


    const fetchSessionId = async () => {
        API.fetchSession(token)
            .then(response => setSessionId(response.session_id))
            .catch(e => {
                showError(e.message)
            })
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        // If it's the first message in a new chat, we need a sessionId first
        if (!currentChat || currentChat.length === 0) {
            // Set the pending input and fetch the sessionId
            setPendingInput(input);
            await fetchSessionId();
            setInput(''); // Clear input field
        } else {
            // If we already have a sessionId, just make the query call directly
            await makeQuery(sessionId, input);
            setInput(''); // Clear input field
        }
    };

    const makeQuery = async (activeSessionId, userInput) => {
        setIsLoading(true);
        API.makeQuery(activeSessionId, userInput, token)
            .then((result) => {
                const newMessage = {type: 'outgoing', data: {content: userInput}};
                const newResponse = {type: 'incoming', data: {content: result.answer}};
                setCurrentChat((prevChat) => [...prevChat, newMessage, newResponse]);
                setResponse(result.answer);
                editableRef.current.innerText = '';
                setIsLoading(false);
            })
            .catch((e) => showError(e.message))

    };

    const fetchChatHistory = async () => {
        API.fetchChatHistory(token)
            .then(sessionIds => {
                setChatHistory(sessionIds)
            })
            .catch(e => showError(e.message))
    };

    // useEffect to process pendingInput once sessionId is set
    useEffect(() => {
        if (sessionId && pendingInput) {
            // Now we have both a sessionId and a pending input, we can send the query
            makeQuery(sessionId, pendingInput);
            setPendingInput(null);
        }
    }, [sessionId, pendingInput]);

    useEffect(() => {

        fetchChatHistory();
    }, [token]);

    const fetchSessionHistory = async (session_id) => {
        API.fetchSessionHistory(session_id, token)
            .then(history => {
                setSessionId(session_id);
                setCurrentChat(history);
            })
            .catch(e => showError(e.message))
    };

    const handleNewChat = () => {
        if (currentChat.length > 0) {
            setCurrentChat([]);
        }
    };

    return (
        <div className="chatBot">
            {menuOpen ? (
                <div className="side-menu-container">
                    <div className="side-menu open">
                        <ul className="menu-list">
                            <button className="menu-button" onClick={toggleMenu}>
                                <i className="bi bi-backspace"></i>
                            </button>
                            <li className="menu-item" onClick={handleNewChat}> New Chat</li>
                            {chatHistory && chatHistory.slice().reverse().map((chat, index) => (
                                <li key={index} className={chat.type} onClick={() => fetchSessionHistory(chat)}>
                                    {"Chat " + (chatHistory.length - 1 - index)}
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>
            ) : (
                <div className="side-menu-closed">
                    <button className="menu-button" onClick={toggleMenu}>
                        <i className="bi bi-clock-history"></i>
                    </button>

                </div>
            )}

            <div className="chat-container">
                <ul className="chatbox">
                    {currentChat && currentChat.map((chat, index) => (
                        <li key={chat.type + index} className={chat.type}>
                            <div key={index} className={`chat-message ${chat.type}`}>
                                {(chat.type === 'incoming' || chat.type === 'ai') &&
                                    <div className="circular-container">
                                        <img src="/favicon.png" className="circular-image" alt="Circular profile"/>
                                    </div>}
                                <div style={{whiteSpace: 'pre-wrap'}}>
                                    {chat.data.content}
                                </div>
                            </div>
                        </li>
                    ))}

                </ul>

                <div className="chat-input">

                    <div
                        ref={editableRef}
                        contentEditable="true"
                        className="text editable-rectangle"
                        onInput={(e) => setInput(e.target.innerText)}
                    ></div>
                    <button className="button_chat" type="button" id="sendBTN" onClick={handleSubmit}
                            disabled={isLoading}>
                        {isLoading ? <div class="spinner"></div> : <i className="bi bi-send"></i>}
                    </button>
                </div>

            </div>
            <div className='logout-container'>
                <button className="logout-button" onClick={logout}>
                    Logout
                </button>
            </div>
        </div>
    );
}

export default Chat;


