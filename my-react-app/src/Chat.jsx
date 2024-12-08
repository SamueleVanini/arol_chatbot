import React, { useState, useEffect } from 'react';
import './Chat.css';

function Chat() {
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [response, setResponse] = useState('');
  const [currentChat, setCurrentChat] = useState([]);
  const [chatHistory, setChatHistory] = useState([]);
  const token = localStorage.getItem('token');


  const [menuOpen, setMenuOpen] = useState(false);

  const toggleMenu = () => {
    setMenuOpen(!menuOpen);
  };

  useEffect(() => {

    fetchSessionId();
  }, []);

  const fetchSessionId = async () => {
    try {
      const response = await fetch('http://0.0.0.0:80/user/session', {
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
    try {

      const response = await fetch('http://0.0.0.0:80/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ session_id: sessionId, input: input })
      });
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Network response was not ok: ${response.status} - ${errorText}`);
      } else {
        const result = await response.json();
        const newMessage = { type: 'outgoing' , data: {content: input }};
        const newResponse = { type: 'incoming', data: {content: result.answer} };
        setCurrentChat([...currentChat, newMessage, newResponse]);
        setResponse(result.answer);
        setInput(''); // Reset the input field
      }
    } catch (error) {
      console.error('There was an error!', error);
    }
  };

  useEffect(() => {
    const fetchChatHistory = async () => {
      try {
        const response = await fetch('http://0.0.0.0:80/user/session/all', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          }
        });
        const data = await response.json();
        console.log(data);
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
      const response = await fetch(`http://0.0.0.0:80/user/session/${session_id}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });
      const data = await response.json();
      console.log(data.history);
      setSessionId(session_id);
      setCurrentChat(data.history);
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
      <button className="menu-button" onClick={toggleMenu}>
        <i className="bi bi-clock-history"></i>
      </button>
      {menuOpen && (
        <div className="side-menu open">
          <button className="close-button" onClick={toggleMenu}>
            <i class="bi bi-backspace"></i>
          </button>
          <ul className="menu-list">
            <li className="menu-item" onClick={handleNewChat}> New Chat</li>
            {chatHistory && chatHistory.map((chat, index) => (
              <li key={index} className={chat.type} onClick={() => fetchSessionHistory(chat)}>
                {"Chat " + index}
              </li>
            ))}
          </ul>
        </div>
      )}
      <ul className={`chatbox${menuOpen ? '-menu-open' : ''}`}>
        {currentChat && currentChat.map((chat, index) => (
          <li key={chat.type + index} className={chat.type}>
            <p className='chat-message'>{chat.data.content}</p>
          </li>
        ))}
      </ul>
      <div className={`chat-input${menuOpen ? '-menu-open' : ''}`}>
        <textarea
          className="text"
          rows="1"
          cols="17"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Enter a message..."
        ></textarea>
        <button className="button_chat" type="button" id="sendBTN" onClick={handleSubmit}>{'>'}</button>
      </div>
    </div>
  );
}

export default Chat;

