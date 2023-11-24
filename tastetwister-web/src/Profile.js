// Profile.js

import React, { useState, useEffect} from 'react';
import './Profile.css';
import myProfileIcon from './images/myprofileicon.jpg';
import Sidebar from './Sidebar';

const Profile = () => {
  // Mock data and actions
  const username = localStorage.getItem('username');
  const [friendsList, setFriendsList] = useState([]);

  const [newFriend, setNewFriend] = useState('');
  const [activeTab, setActiveTab] = useState('received'); // Default to received tab
  const [incomingRequests, setIncomingRequests] = useState([]);

  useEffect(() => {
    fetchRequests();
    fetchFriends();
  }, []); // Fetch requests on component mount

  const fetchRequests = () => {
    const storedToken = localStorage.getItem('token');

    fetch('http://127.0.0.1:5000/incoming_invites', {
      method: 'GET',
      headers: {
        'Authorization': storedToken,
        'Content-Type': 'application/json',
      },
    })
      .then((response) => response.json())
      .then((data) => {
        setIncomingRequests(data);
      })
      .catch((error) => console.error('Error fetching incoming requests:', error));
  };

  const fetchFriends = async () => {
    try {
      const response = await fetch(`http://127.0.0.1:5000/friends/${username}`, {
        method: 'GET',
        headers: {
          'Authorization': localStorage.getItem('token'),
          'Content-Type': 'application/json',
        },
      });
  
      if (response.ok) {
        const friendsData = await response.json();
        setFriendsList(friendsData);
      } else {
        console.error('Error fetching friends:', response.status);
      }
    } catch (error) {
      console.error('Error fetching friends:', error);
    }
  };

  const handleSendRequest = () => {
    const storedToken = localStorage.getItem('token');

    fetch('http://127.0.0.1:5000/send_invite', {
      method: 'POST',
      headers: {
        'Authorization': storedToken,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ receiver: newFriend }),
    })
      .then((response) => response.json())
      .then((data) => {
        alert(data.message); // Display a message, you can replace this with your own logic
        fetchRequests(); // Refresh the requests after sending
        
      })
      .catch((error) => console.error('Error sending friend request:', error));

    setNewFriend(''); // Clear the input after sending
  };

  const handleRespondInvite = (inviteId, response) => {
    const storedToken = localStorage.getItem('token');

    fetch('http://127.0.0.1:5000/respond_invite', {
      method: 'POST',
      headers: {
        'Authorization': storedToken,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        invite_id: inviteId,
        response: response,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        alert(data.message); // Display a message, you can replace this with your own logic
        fetchRequests(); // Refresh the requests after responding
        fetchFriends();
      })
      .catch((error) => console.error('Error responding to friend invite:', error));
  };

  return (
    <div className="profile-container">
      <Sidebar />
      <div className="left-widget">
        <div className="profile-box">
          <div className="profile-header">
            <img src={myProfileIcon} alt="Profile Icon" className="my-profile-icon" />
            <h2>{username}'s Friends</h2>
          </div>

          <div className="profile-section">
          <ul>
          {friendsList.map((friend) => (
            <li key={friend}>{friend}</li>
          ))}
        </ul>
          </div>
        </div>
      </div>

      <div className="right-widget">
        <div className="profile-box">
          <div className="profile-header">
            <div className="tabs">
              <div
                className={`tab ${activeTab === 'received' ? 'active' : ''}`}
                onClick={() => setActiveTab('received')}
              >
                Received
              </div>
              <div
                className={`tab ${activeTab === 'sent' ? 'active' : ''}`}
                onClick={() => setActiveTab('sent')}
              >
                Sent
              </div>
            </div>
          </div>
          {activeTab === 'received' && (
            <div className="profile-section">
            <h3>Received Requests</h3>
            <ul>
              {incomingRequests.map((request) => (
              <li key={request.id}>
                <span>{request.sender}</span>
                 <div className="request-options">
                  <button onClick={() => handleRespondInvite(request.id, 'accept')}>Accept</button>
                  <button onClick={() => handleRespondInvite(request.id, 'deny')}>Deny</button>
                </div>
              </li>
            ))}
            </ul>
        </div>
        )}
          

          {activeTab === 'sent' && (
            <div className="profile-section">
              <h3>Sent Requests</h3>
              {/* Display sent requests content here */}
            </div>
          )}

          <div className="profile-section">
            
            <input
              type="text"
              placeholder="Enter username"
              value={newFriend}
              onChange={(e) => setNewFriend(e.target.value)}
            />
            <button onClick={handleSendRequest}>Send Request</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;

