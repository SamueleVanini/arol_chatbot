import React, { useState, useEffect } from 'react';
import './Chat.css';

function Chat() {
    const [input, setInput] = useState('');
    const [sessionId, setSessionId] = useState(null);
    const [response, setResponse] = useState('');
    const [currentChat, setCurrentChat] = useState([]);
    const [chatHistory, setChatHistory] = useState([]);
    const [pendingInput, setPendingInput] = useState(null);
    const [menuOpen, setMenuOpen] = useState(false);
    const [errorText, setErrorText] = useState('');
    const token = localStorage.getItem('token');

    const toggleMenu = () => {
        setMenuOpen(!menuOpen);
    };

    const fetchSessionId = async () => {
        try {
            const response = await fetch('http://127.0.0.1:80/user/session', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application',
                    'Authorization': `Bearer ${token}`
                }
            });
            const data = await response.json();
            setSessionId(data.session_id);
        } catch (error) {
            console.error('Error fetching session ID:', error);
        }
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
        try {
            const response = await fetch('http://127.0.0.1:80/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ session_id: activeSessionId, input: userInput })
            });
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Network response was not ok: ${response.status} - ${errorText}`);
            } else {
                const result = await response.json();
                const newMessage = { type: 'outgoing', data: { content: userInput } };
                const newResponse = { type: 'incoming', data: { content: result.answer } };
                setCurrentChat((prevChat) => [...prevChat, newMessage, newResponse]);
                setResponse(result.answer);
            }
        } catch (error) {
            console.error('There was an error!', error);
        }
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
        const fetchChatHistory = async () => {
            try {
                const response = await fetch('http://127.0.0.1:80/user/session/all', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    }
                });
                const data = await response.json();
                setChatHistory(data.session_ids);
            } catch (error) {
                console.error('Error fetching chat history:', error);
                setErrorText('Error fetching chat history');
            }
        };

        fetchChatHistory();
    }, [token]);

    const fetchSessionHistory = async (session_id) => {
        try {
            const response = await fetch(`http://127.0.0.1:80/user/session/${session_id}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                }
            });
            const data = await response.json();
            setSessionId(session_id);
            setCurrentChat(data.history.sort((a, b) => a.timestamp - b.timestamp));
        } catch (error) {
            console.error('Error fetching session history:', error);
            setErrorText('Error fetching session history');
        }
    };

    const handleNewChat = () => {
        setCurrentChat([]);
        fetchSessionId();
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
                <button className="menu-button" onClick={toggleMenu}>
                    <i className="bi bi-clock-history"></i>
                </button>
            )}

            <div className="chat-container">
                <ul className="chatbox">
                    {currentChat && currentChat.map((chat, index) => (
                        <li key={chat.type + index} className={chat.type}>
                            <p className='chat-message'>{chat.data.content}</p>
                        </li>
                    ))}
                </ul>
                <div className="chat-input">
                    <div
                        contentEditable="true"
                        className="text editable-rectangle"
                        onInput={(e) => setInput(e.target.innerText)}
                    ></div>
                    <button className="button_chat" type="button" id="sendBTN" onClick={handleSubmit}>
                        <i className="bi bi-send"></i>
                    </button>
                </div>
            </div>
        </div>
    );
}

export default Chat;
