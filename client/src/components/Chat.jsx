import React, { useState, useEffect, useRef } from 'react';
import './Chat.css';
import API from '../API';


function Chat() {
    const [input, setInput] = useState('');
    const [sessionId, setSessionId] = useState(null);
    const [response, setResponse] = useState('');
    const [currentChat, setCurrentChat] = useState([]);
    const [chatHistory, setChatHistory] = useState([]);
    const [pendingInput, setPendingInput] = useState(null);
    const [menuOpen, setMenuOpen] = useState(false);
    const [errorText, setErrorText] = useState('');
    const [isLoading, setIsLoading] = useState(false); 
    const token = localStorage.getItem('token');
    const editableRef = useRef(null);

    const toggleMenu = () => {
        setMenuOpen(!menuOpen);
    };

   

    const fetchSessionId = async () => {
        try {
            const sessionId = await API.fetchSession(token);
            setSessionId(sessionId);
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
        setIsLoading(true);
        try{
                const result = await API.makeQueryAPI(activeSessionId, userInput, token);
                const newMessage = { type: 'outgoing', data: { content: userInput } };
                const newResponse = { type: 'incoming', data: { content: result.answer } };
                setCurrentChat((prevChat) => [...prevChat, newMessage, newResponse]);
                setResponse(result.answer);
        
        } catch (error) {
            console.error('There was an error!', error);
        }finally {
            editableRef.current.innerText = ''; 
            setIsLoading(false);
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
                const sessionIds = await API.fetchChatHistoryAPI(token);
                setChatHistory(sessionIds);
            } catch (error) {
                console.error('Error fetching chat history:', error);
                setErrorText('Error fetching chat history');
            }
        };

        fetchChatHistory();
    }, [token]);

    const fetchSessionHistory = async (session_id) => {
        try {
                const history = await API.fetchSessionHistoryAPI(session_id, token);
                setSessionId(session_id);
                setCurrentChat(history);
        } catch (error) {
            console.error('Error fetching session history:', error);
            setErrorText('Error fetching session history');
        }
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
                    {(chat.type === 'incoming' || chat.type === 'ai') && <img src={"/public/image.png"} alt="Chat Icon" className="chat-icon" />}
                    <p>{chat.data.content}</p>
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
                    <button className="button_chat" type="button" id="sendBTN" onClick={handleSubmit} disabled={isLoading}>
                        {isLoading ? <div class="spinner"></div> : <i className="bi bi-send"></i>}
                    </button>
                </div>
                
            </div>
            <div className='logout-container'>
  <button className="logout-button" onClick={API.logout}>
                Logout
            </button>
            </div>
        </div>
    );
}

export default Chat;


