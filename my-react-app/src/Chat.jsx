import React, { useState, useEffect } from 'react'; 
import './Chat.css';

function Chat() {
  const [input, setInput] = useState('');
  const [response, setResponse] = useState('');
  const [currentChat, setCurrentChat] = useState([
    { type: 'incoming', message: 'Hello! How can I help you today?' },
    { type: 'outgoing', message: 'I need help for my company' }
  ]);
  const [chatHistory, setChatHistory] = useState([
    { type: 'incoming', message: 'Example' }
]);

const [menuOpen, setMenuOpen] = useState(false);

const toggleMenu = () => {
  setMenuOpen(!menuOpen);
};

  // Generate a simpler session ID
  const generateSessionId = () => {
      return Math.random().toString(36).substr(2, 9);
  };

  // Initialize sessionId state
  const [sessionId, setSessionId] = useState(generateSessionId());

  useEffect(() => {
      // If you need to perform any side effects with sessionId, do it here
      console.log('Session ID:', sessionId);
  }, [sessionId]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    // Use the sessionId from state
    try {
        const response = await fetch('http://127.0.0.1:80/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: sessionId,
                input: input
            })
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Network response was not ok: ${response.status} - ${errorText}`);
        }

        const result = await response.json();
        const newMessage = { type: 'outgoing', message: input };
        const newResponse = { type: 'incoming', message: result.answer };
        setCurrentChat([...currentChat, newMessage, newResponse]);
        setResponse(result.answer);
        setInput(''); // Reset the input field
    } catch (error) {
        console.error('There was an error!', error);
    }
};


  return (
          <div className="chatBot">
          <ul className="chatbox">
              {currentChat.map((chat, index) => (
                <li key={chat.type + index} className={chat.type}>
                  <div className="chat-bubble">
                    <p className='chat-message'>{chat.message}</p>
                  </div>
                </li>
              ))}
            </ul>
            <div className="chat-input">
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

