// Notification.js

import React, { useState, useEffect } from 'react';
import './Notification.css'; // Import the corresponding CSS file
import bellIcon from './images/bell-icon3.png'; // Import your bell icon image

const Notification = () => {
  const [showNotifications, setShowNotifications] = useState(false);
  const [notifications, setNotifications] = useState([]);

  const fetchUnheardArtists = async () => {
    try {
      const storedToken = localStorage.getItem('token');
      const response = await fetch('http://127.0.0.1:5000/unheard_artists', {
        method: 'GET',
        headers: {
          "Authorization": storedToken,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorMessage = await response.text();
        throw new Error(`Failed to fetch unheard artists: ${errorMessage}`);
      }

      const data = await response.json();

      if (data.artist && data.song) {
        setNotifications([
          `You haven't added a new song from ${data.artist} for a while! Check out ${data.song} from ${data.artist}!`,
          // Add more notifications if needed
        ]);
      }
    } catch (error) {
      console.error('Error:', error.message);
    }
  };

  const handleNotificationClick = () => {
    setShowNotifications(!showNotifications);
    // Fetch new notifications when the panel is opened
    if (!showNotifications) {
      fetchUnheardArtists();
    }
  };

  useEffect(() => {
    // Close the notifications panel when clicking outside of it
    const handleClickOutside = (event) => {
      if (showNotifications && !event.target.closest('.notification-panel')) {
        setShowNotifications(false);
      }
    };

    document.addEventListener('click', handleClickOutside);

    return () => {
      document.removeEventListener('click', handleClickOutside);
    };
  }, [showNotifications]);

  return (
    <div className="notification-container">
      
        <img src={bellIcon} alt="Bell Icon" className='bell-icon' onClick={handleNotificationClick} />
      
      {showNotifications && (
        <div className="notification-panel">
          {notifications.map((notification, index) => (
            <div key={index} className="notification-message">
              {notification}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Notification;
