import './Homepage.css';

function Homepage() {
    return (
      <div className="homepage">
        <div className="border-homepage">
            <img src="/th.jpeg" alt="AROL" className="welcome-image" />
          <div className="text-container">
          <form className="input-form">
          <input type="text" placeholder="Email" className="input-field" />
          <input type="password" placeholder="Password" className="input-field" />
          <button type="button" className="submit-button">Sign In</button>
          <button type="button" className="submit-button">Sign Up</button>
            </form>
          </div>
        </div>
      </div>
    );
  }

export default Homepage;