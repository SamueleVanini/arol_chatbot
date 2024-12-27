import React from 'react';
import './default.css'; // Import the CSS file for styling

function VideoSection() {
  return (
    <div className="video-container">
      <video
        className="background-video"
        src="arol_splash.mp4" // Replace with the actual path to your video file
        type="video/mp4"
        autoPlay
        loop
        muted
        playsInline
      />
    </div>
  );
}

export default VideoSection;
