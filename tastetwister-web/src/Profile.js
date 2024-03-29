import React, { useState, useEffect} from 'react';
import { useNavigate } from 'react-router-dom';
import './Profile.css';
import * as icons from './images'; // Update this path accordingly
import editIcon from './images/edit-icon.png';
import Sidebar from './Sidebar';


const Profile = () => {
  const username = localStorage.getItem('username');
  const navigate = useNavigate();
  const [friendsList, setFriendsList] = useState([]);
  const [newFriend, setNewFriend] = useState('');
  const [activeTab, setActiveTab] = useState('received');
  const [incomingRequests, setIncomingRequests] = useState([]);
  const [outgoingRequests, setOutgoingRequests] = useState([]);
  const [showRemoveConfirmation, setShowRemoveConfirmation] = useState(false);
  const [showBlockConfirmation, setShowBlockConfirmation] = useState(false);
  const [selectedFriend, setSelectedFriend] = useState('');
  const [myProfileIcon, setProfileIcon] = useState('');

  useEffect(() => {
    fetchRequests();
    fetchFriends();
   
    fetchBlockedFriends();
    fetchProfileIcon();
  }, []);

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

  const fetchSentRequests = () => {
    const storedToken = localStorage.getItem('token');

    fetch('http://127.0.0.1:5000/outgoing_invites', {
      method: 'GET',
      headers: {
        'Authorization': storedToken,
        'Content-Type': 'application/json',
      },
    })
      .then((response) => response.json())
      .then((data) => {
        setOutgoingRequests(data);
      })
      .catch((error) => console.error('Error fetching outgoing requests:', error));
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
        alert(data.message);
        fetchRequests();
      })
      .catch((error) => console.error('Error sending friend request:', error));

    setNewFriend('');
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
        alert(data.message);
        fetchRequests();
        fetchFriends();
      })
      .catch((error) => console.error('Error responding to friend invite:', error));
  };

  const handleRemoveFriendClick = (friend) => {
    setSelectedFriend(friend);
    setShowRemoveConfirmation(true);
  };

  const handleConfirmation = (confirmed) => {
    if (confirmed) {
      const storedToken = localStorage.getItem('token');

      fetch('http://127.0.0.1:5000/remove_friend', {
        method: 'POST',
        headers: {
          'Authorization': storedToken,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ friend_username: selectedFriend }),
      })
        .then((response) => response.json())
        .then((data) => {
          alert(data.message);
          fetchFriends();
        })
        .catch((error) => console.error('Error removing friend:', error));
    }

    setShowRemoveConfirmation(false);
    setSelectedFriend('');
  };

  const handleBlockConfirmation = (confirmed) => {
    if (confirmed){
    const storedToken = localStorage.getItem('token');
    const username = localStorage.getItem('username');
    fetch('http://127.0.0.1:5000/block_friend', {
      method: 'POST',
      headers: {
        'Authorization': storedToken,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        blocker: username,
        blocked: selectedFriend,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        alert(data.message);
        setShowBlockConfirmation(false);
        fetchBlockedFriends();
        // You may want to update the UI or perform other actions after blocking a friend
      })
      .catch((error) => console.error('Error blocking friend:', error));
    }
    setShowBlockConfirmation(false);
  };

  const handleBlockFriendClick = (friend) => {
    setSelectedFriend(friend);
    setShowBlockConfirmation(true);
  };
  const [blockedFriends, setBlockedFriends] = useState([]);

  useEffect(() => {
    fetchRequests();
    fetchFriends();
    fetchBlockedFriends(); // Fetch blocked friends when component mounts
  }, []);

  const fetchBlockedFriends = () => {
    const storedToken = localStorage.getItem('token');

    fetch('http://127.0.0.1:5000/blocked_friends', {
      method: 'GET',
      headers: {
        'Authorization': storedToken,
        'Content-Type': 'application/json',
      },
    })
      .then((response) => response.json())
      .then((data) => {
        setBlockedFriends(data);
      })
      .catch((error) => console.error('Error fetching blocked friends:', error));
  };

  const handleUnblockFriendClick = (blockedFriend) => {
    const storedToken = localStorage.getItem('token');
    const username = localStorage.getItem('username');

    fetch('http://127.0.0.1:5000/unblock_friend', {
      method: 'POST',
      headers: {
        'Authorization': storedToken,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        blocker: username,
        blocked: blockedFriend.username,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        alert(data.message);
        // Refresh the blocked friends list after unblocking
        fetchBlockedFriends();
      })
      .catch((error) => console.error('Error unblocking friend:', error));
  };

  const handleFriendClick = (friend) => {
    // Use the navigate() function to navigate to another page
    navigate(`/friend/${encodeURIComponent(friend)}`);
  };

  const fetchProfileIcon = () => {
    const storedToken = localStorage.getItem('token');
    const username = localStorage.getItem('username');

    fetch('http://127.0.0.1:5000/get_picture?username=' + username, {
      method: 'GET',
      headers: {
        'Authorization': storedToken,
        'Content-Type': 'application/json',
      },
    })
      .then((response) => response.json())
      .then((data) => {
        setProfileIcon(data.picture);
      })
      .catch((error) => console.error('Error fetching profile icon:', error));
  };

  // Function to get the corresponding image based on the string
  const getProfileImage = (iconString) => {
    switch (iconString) {
      case 'default':
        return icons.DefaultIcon;
      case 'lofigirl':
        return icons.LofiGirlIcon;
      case 'lofiboy':
        return icons.LofiBoyIcon;
      default:
        return icons.DefaultIcon;
    }
  };

  const updatePicture = (selectedOption) => {
    const storedToken = localStorage.getItem('token');
    const username = localStorage.getItem('username');
    fetch('http://127.0.0.1:5000/set_picture?username=' + username, {
      method: 'POST',
      headers: {
        'Authorization': storedToken,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username: username, picture: selectedOption }),
    })
      .then((response) => response.json())
      .then((data) => {
        // Handle the response if needed
        console.log(data);
        fetchProfileIcon();
      })
      .catch((error) => console.error('Error setting picture:', error));
  };
  

  const handleOptionClick = (option) => {
    setPopupOpen(false);
    setSelectedOption(option);
  
    // Call your API to update the picture with the selected option
    updatePicture(option);
  };
  

  const [isPopupOpen, setPopupOpen] = useState(false);
  const [selectedOption, setSelectedOption] = useState(null);


      return (
        <div className="profile-container">
          <Sidebar />
          <div className="left-widget">
            <div className="profile-box">
              <div className="profile-header">
              <img src={myProfileIcon ? getProfileImage(myProfileIcon) : null} alt="Profile Icon" className="my-profile-icon" />
              <img src={editIcon} alt="Edit Icon" className="edit-profile-icon" onClick={() => { console.log('Edit icon clicked'); setPopupOpen(true); }} />

                <h2>{username}'s Friends</h2>
              </div>
              {isPopupOpen && (
                <div className="icon-popup-container">
                  <div className="profile-popup">
                    <p>Choose an icon!</p>
                    <div className="icon-buttons">
                      <button onClick={() => handleOptionClick('default')}>
                        <img src={icons.DefaultIcon} alt="Default Icon" style={{ width: '60px', height: '60px' }} />
                      </button>
                      <button onClick={() => handleOptionClick('lofigirl')}>
                        <img src={icons.LofiGirlIcon} style={{ width: '60px', height: '60px' }} />
                      </button>
                      <button onClick={() => handleOptionClick('lofiboy')}>
                        <img src={icons.LofiBoyIcon} style={{ width: '60px', height: '60px' }} />
                      </button>
                    </div>
                  </div>
                </div>
              )}
              <div className="profile-section">
      <ul>
        {friendsList.map((friend) => (
          <li key={friend} className="friend-item" >
          <div className="friend-options" onClick={() => handleFriendClick(friend)}>
          {friend}
          </div>

            <div className="friend-options">
              <span
                className="remove-icon"
                onClick={() => handleRemoveFriendClick(friend)}
              >
                ❌
              </span>
              <span
            className="icon-space" // Add a class for spacing
          />
              <span
                className="block-icon"
                onClick={() => handleBlockFriendClick(friend)}
              >
                🚫
              </span>
            </div>
          </li>
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
                onClick={() => {
                  setActiveTab('sent');
                  fetchSentRequests(); // Add this line to fetch outgoing requests when the tab is clicked
                }}
              >
                Sent
              </div>
              {/* New tab for "Blocked" */}
              <div
                className={`tab ${activeTab === 'blocked' ? 'active' : ''}`}
                onClick={() => {
                  setActiveTab('blocked');
                  fetchBlockedFriends(); // Fetch blocked friends when the tab is clicked
                }}
              >
                Blocked
              </div>
            </div>
          </div>

          {activeTab === 'received' && (
            <div className="profile-section">
              <h3>Received Requests</h3>
              <ul>
                {Array.isArray(incomingRequests) &&
                  incomingRequests.map((request) => (
                    <li key={request.id}>
                      <span>{request.sender}</span>
                      <div className="request-options">
                        <button onClick={() => handleRespondInvite(request.id, 'accept')}>Accept</button>
                        <button onClick={() => handleRespondInvite(request.id, 'deny')}>Deny</button>
                      </div>
                    </li>
                  ))}
              </ul>
             
            <input
              type="text"
              placeholder="Enter username"
              value={newFriend}
              onChange={(e) => setNewFriend(e.target.value)}
            />
            <button onClick={handleSendRequest} 
            className="send-request-button"
            >Send Request</button>
          </div>
            
          )}

          {activeTab === 'sent' && (
            <div className="profile-section">
              <h3>Sent Requests</h3>
              <ul>
                {Array.isArray(outgoingRequests) && outgoingRequests.map((request) => (
                  <li key={request.id}>
                    <span>{request.receiver}</span>
                    {/* You can add more details or options here if needed */}
                  </li>
                ))}
              </ul>
          
            <input
              type="text"
              placeholder="Enter username"
              value={newFriend}
              onChange={(e) => setNewFriend(e.target.value)}
            />
            <button onClick={handleSendRequest} 
            className="send-request-button"
            >Send Request</button>
          </div>
            
          )}

          {activeTab === 'blocked' && (
            <div className="profile-section">
              <h3>Blocked Users</h3>
              <ul>
                {Array.isArray(blockedFriends) &&
                  blockedFriends.map((blockedFriend) => (
                    <li key={blockedFriend.username}>
                      <span>{blockedFriend.username}</span>
                      <button onClick={() => handleUnblockFriendClick(blockedFriend)}>
                        Unblock
                      </button>
                    </li>
                  ))}
              </ul>
            </div>
          )}

          
        </div>
      </div>

      {showRemoveConfirmation && (
        <div className="popup-container">
          <div className="profile-popup">
            <p>{`Are you sure you want to remove ${selectedFriend} from your friends?`}</p>
            <div className="button-container">
              <button onClick={() => handleConfirmation(true)}>Yes</button>
              <button onClick={() => handleConfirmation(false)}>No</button>
            </div>
          </div>
        </div>
      )}

      {showBlockConfirmation && (
        <div className="popup-container">
          <div className="profile-popup">
            <p>{`Are you sure you want to block ${selectedFriend} from your friends?`}</p>
            <div className="button-container">
              <button onClick={() => handleBlockConfirmation(true)}>Yes</button>
              <button onClick={() => handleBlockConfirmation(false)}>No</button>
            </div>
          </div>
        </div>
      )}

      
    </div>
  );
};

export default Profile;