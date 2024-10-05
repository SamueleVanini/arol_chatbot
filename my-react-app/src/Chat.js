import React, { useState, useEffect } from 'react'; 
import './Chat.css';

function Chat() {
  const [input, setInput] = useState('');
  const [response, setResponse] = useState('');
  const [currentChat, setCurrentChat] = useState([
      { type: 'incoming', message: 'Hi, how can I help you today?' }
  ]);
  const [chatHistory, setChatHistory] = useState([
    { type: 'incoming', message: 'Example' }
]);

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
    <div className="chat-container">
      <div className="list-container">
        <h2 className='history'>HISTORY</h2>
        <ul>
          {chatHistory.map((chat, index) => (
            <li key={index} className="past-chat">
              <p>{chat.message}</p>
            </li>
          ))}
        </ul>
      </div> 
      <div className="image-container">
        <img src="th.jpeg" alt="AROL" className="image2" />
      </div>

      <div className="chat">
          <div className="chatBot">
          <ul className="chatbox">
              {currentChat.map((chat, index) => (
                <li key={index} className={`chat-${chat.type} chat`}>
                  <div className="chat-bubble">
                    <p>{chat.message}</p>
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
      </div>
    </div>
  );
}

export default Chat;




/**
 * 
 * import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Chat = () => {
    const [input, setInput] = useState('');
    const [response, setResponse] = useState('');
    const [currentChat, setCurrentChat] = useState([
        { type: 'incoming', message: 'Hi, how can I help you today?' }
    ]);

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
            const result = await axios.post('http://127.0.0.1:80/query', {
                session_id: sessionId,
                input: input
            });
            const newMessage = { type: 'outgoing', message: input };
            const newResponse = { type: 'incoming', message: result.data.answer };
            setCurrentChat([...currentChat, newMessage]);
            setCurrentChat([...currentChat, newResponse]);
            setResponse(result.data.answer);
            setInput(''); // Reset the input field
        } catch (error) {
            console.error('There was an error!', error);
        }
    };

    return (
        <div>
            <p>Session ID: {sessionId}</p>
           
            <form onSubmit={handleSubmit}>
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                />
                <button type="submit">Send</button>
            </form>
            <div>
                {currentChat.map((chat, index) => (
                    <p key={index} className={chat.type}>{chat.message}</p>
                ))}
            </div>
        </div>
    );
};

export default Chat;
 * 
 * 
 * 
 * 
 * 
 */