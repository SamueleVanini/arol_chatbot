import React, { useState, useEffect } from 'react'; 
import './Chat.css';

function Chat() {
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [response, setResponse] = useState('');
  const [currentChat, setCurrentChat] = useState([
    { type: 'incoming', message: 'Hello! How can I help you today?' },
    { type: 'outgoing', message: 'I need help for my company' },
    { type: 'incoming', message: 'Ok, tell me more details' },
    { type: 'outgoing', message: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam sed nulla sed turpis dignissim accumsan in ac justo. Sed eget dolor et erat fermentum sodales lacinia quis arcu. Donec consequat leo vel rhoncus blandit. Nullam lectus justo, maximus in sapien vitae, tristique bibendum mauris. In est quam, auctor ac sapien at, blandit fermentum elit. In ultricies massa in viverra consectetur. Curabitur ut est enim. Mauris semper erat est, nec condimentum eros consequat sed. Sed in auctor quam. Nullam condimentum ultricies turpis auctor molestie. Nulla blandit lorem mi, nec finibus est fringilla eget.' },
  ]);
  const [chatHistory, setChatHistory] = useState([
    {  message: 'Example' },
    {message: 'Example' },
    { message: 'Example' },
    {  message: 'Example' }
]);

const [menuOpen, setMenuOpen] = useState(false);

const toggleMenu = () => {
  setMenuOpen(!menuOpen);
};
  
useEffect(() => {
  const fetchSessionId = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/user/session');
      const data = await response.json();
      setSessionId(data.session_id);
    } catch (error) {
      console.error('Error fetching session ID:', error);
    }
  };

  fetchSessionId();
}, []);

const handleSubmit = async (e) => {
  e.preventDefault();
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
            <button className="menu-button" onClick={toggleMenu}>
            <i className="bi bi-clock-history"></i>
      </button>
      {menuOpen && (
        <div className="side-menu open">
           <button className="close-button" onClick={toggleMenu}>
           <i class="bi bi-backspace"></i>
        </button>
          <ul className="menu-list">
          {chatHistory.map((chat, index) => (
            <li key={index} className={chat.type}>
              {chat.message}
            </li>
          ))}
          </ul>
        </div>
      )}
          <ul className={"chatbox"}>
              {currentChat.map((chat, index) => (
                <li key={chat.type + index} className={chat.type}>
                    <p className='chat-message'>{chat.message}</p>
                </li>
              ))}
            </ul>
            <div className={`chat-input`}>
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

