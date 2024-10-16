import './Homepage.css';

function Homepage() {
    return (
      <div className="homepage">
        <div className="border-homepage">
          <div className="image-container">
            <img src="/th.jpeg" alt="AROL" className="welcome-image" />
          </div>
          <div className="text-container">
          <h1 className="title">AROL CHATBOT</h1>
          <form className="input-form">
              <input type="text" placeholder="Email" className="input-field" />
              <input type="text" placeholder="Password" className="input-field" />
              <button type="submit" className="submit-button">Sign In</button>
              <button type="submit" className="submit-button">Sign Up</button>
            </form>
          </div>
        </div>
      </div>
    );
  }

export default Homepage;