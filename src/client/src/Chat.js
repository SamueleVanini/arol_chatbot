import React from 'react';
import './Chat.css';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';

function Chat() {

  const [data, setData] = useState(null);
  const location = useLocation();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const requestId = uuidv4(); // Genera un ID univoco per la richiesta
        console.log(`Request ID: ${requestId}`); // Stampa l'ID della richiesta per il debug

        const response = await axios.get('http://127.0.0.1:5000/api/chat', {
          headers: {
            'X-Request-ID': requestId // Invia l'ID univoco come intestazione
          }
        });
        setData(response.data);
      } catch (error) {
        console.error('There was an error fetching the data!', error);
      }
    };

    fetchData();
  }, [location.pathname]);

  return (
    <div className="chat-container">
      <div className="list-container">
        <h2 className='history'>HISTORY</h2>
        <ul>
          <li>Item 1</li>
          <li>Item 2</li>
          <li>Item 3</li>
        </ul>
      </div> 
      <div className="image-container">
          <img src="th.jpeg" alt="AROL" className="image2" />
        </div>
        
    <div className="chat">
      
      <div className="border-chat"> 
        
        <div className="chatBot">
          
          <ul className="chatbox">
            <li className="chat-incoming chat">
              <p>Hey! How can I assist you today?</p>
            </li>
            <li className="chat-incoming chat">
              <p>Hi, talk about cats</p>
            </li>
            <li className="chat-incoming chat">
              <p>The cat (Felis catus), also referred to as domestic cat or house cat, is a small domesticated carnivorous mammal. It is the only domesticated species of the family Felidae. Advances in archaeology and genetics have shown that the domestication of the cat occurred in the Near East around 7500 BC. It is commonly kept as a house pet and farm cat, but also ranges freely as a feral cat avoiding human contact. Valued by humans for companionship and its ability to kill vermin, the cat's retractable claws are adapted to killing small prey like mice and rats. It has a strong, flexible body, quick reflexes, and sharp teeth, and its night vision and sense of smell are well developed. It is a social species, but a solitary hunter and a crepuscular predator. Cat communication includes vocalizations like meowing, purring, trilling, hissing, growling, and grunting as well as cat body language. It can hear sounds too faint or too high in frequency for human ears, such as those made by small mammals. It secretes and perceives pheromones.</p>
            </li>
          </ul>
          <div className="chat-input">
            <textarea className="text" rows="0" cols="17" placeholder="Enter a message..."></textarea>
            <button id="sendBTN">Send</button>
          </div>
        </div>
      </div>
    </div>
    </div>
  );
}

export default Chat;