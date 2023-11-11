// Sidebar.js

import React from 'react';
import './Sidebar.css';
import homeIcon from './images/homeicon.png';
import profileIcon from './images/profileicon.jpeg';
import twistIcon from './images/twisticon.png';
import logoutIcon from './images/logout-icon.png';
import heartIcon from './images/hearticon.png';
import statisticsIcon from './images/statistics-icon.png';
import { useNavigate } from "react-router-dom";

function Sidebar() {
  const navigate = useNavigate();
  const handleLogout = () => {
    // Perform logout actions (e.g., clear user session)
    // ...

    // Redirect to the login page
    navigate('/')
  };
  return (
    <div className="sidebar">
      <a href="#home"><img src={homeIcon} alt="Home Icon" className="icon"/>Home</a>
      <a href="#profile"><img src={profileIcon} alt="Profile Icon" className="profile-icon" />  My Profile</a>
      <a href="#tastetwist"><img src={twistIcon} alt="Twist Icon" className="icon"/>TasteTwist!</a>
      <a href="#rate"><img src={heartIcon} alt="Heart Icon" className="icon"/>Rate It!</a>
      <a href="#saved"><img src={statisticsIcon} alt="Statistics Icon" className="icon"/>Statistics</a>
      {/* Add more links as needed */}
     
      <div className="logout-button" onClick={handleLogout}>
          <img src={logoutIcon} alt="Logout" className="logout-icon" />
          <span className="logout-text">   Logout</span>
      </div>
    </div>
  );
}

export default Sidebar;
