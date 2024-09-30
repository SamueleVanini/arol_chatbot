import React, { useState } from 'react'; 
import './Chat.css';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';

function Chat() {
  const [input, setInput] = useState('');
  const [response, setResponse] = useState(null);
  const [chatHistory, setChatHistory] = useState([
    { type: 'past', message: 'dogs' }, 
    { type: 'past', message: 'cats' }, 
  ]);
  const [currentChat, setCurrentChat] = useState([
    { type: 'incoming', message: 'Hi, how can I help you today?' }
  ]);
  const handleSubmit = async (e) => {
    e.preventDefault();
    const sessionId = uuidv4(); // Genera un ID univoco per la sessione

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
      setInput(''); // Resetta il campo di input
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
            <li key={index} className={`chat-${chat.type}`}>
              <p>{chat.message}</p>
            </li>
          ))}
        </ul>
      </div> 
      <div className="image-container">
        <img src="th.jpeg" alt="AROL" className="image2" />
      </div>

      <div className="chat">
        <div className="border-chat"> 
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
              <form onSubmit={handleSubmit}>
                <textarea
                  className="text"
                  rows="1"
                  cols="17"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Enter a message..."
                ></textarea>
                <button type="submit" id="sendBTN">Send</button>
              </form>
              {response && <p>Response: {response}</p>}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Chat;