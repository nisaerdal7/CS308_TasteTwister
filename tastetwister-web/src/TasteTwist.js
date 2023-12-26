import React, { useState, useEffect } from 'react';
import './TasteTwist.css'; // Updated import
import saveIcon from './images/save-icon.png';
import twistIcon from './images/twisticon.png';
import backIcon from './images/back-icon.png';


function TasteTwist() {
  const [searchTerm, setSearchTerm] = useState('');
  const [playlist, setPlaylist] = useState([]);

  const [friendPopupVisible, setFriendPopupVisible] = useState(false);
  const [friendUsername, setFriendUsername] = useState('');

  const showFriendPopup = () => {
    setFriendPopupVisible(true);
  };

  const hideFriendPopup = () => {
    setFriendPopupVisible(false);
  };

  const SaveSong = (song) => {
    const storedToken = localStorage.getItem('token');
    console.log(storedToken);
    console.log(song);
    song.rating = '';
    fetch('http://127.0.0.1:5000/songs', {
    method: 'POST',
    headers: {
        "Authorization": storedToken,
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(song),
    credentials: 'include',
    })
    .then((response) => response.json())
    .then((data) => {
    if (data.message === "Song added or updated!") {
        alert("Song added or updated successfully!");
    }
    })
    .catch((error) => {
    console.error('Error uploading song:', error);
    });
  };

  const submitTasteTwistUsers = async () => {
    try {

        const storedToken = localStorage.getItem('token');
        console.log(storedToken);
      
  
      // Make a request to your Flask backend
      const response = await fetch('http://127.0.0.1:5000/recommend_playlist_all_users', {
        method: 'GET',
        headers: {
            "Authorization": storedToken,
            'Content-Type': 'application/json',
        },
      });
  
      if (!response.ok) {
        // Handle error if the response status is not OK (2xx)
        const errorMessage = await response.text();
        throw new Error(`Failed to fetch playlist: ${errorMessage}`);
      }
  
        // Parse the JSON response
        const fetchedPlaylist = await response.json();
        console.log(fetchedPlaylist);

        // Update the state with the fetched playlist
        setPlaylist(fetchedPlaylist);
      
    } catch (error) {
      console.error('Error:', error.message);
      // Handle error as needed
    }
  };

  const submitTasteTwistFriends = async () => {

    try {

        const storedToken = localStorage.getItem('token');
        console.log(storedToken);
      
  
      // Make a request to your Flask backend
      const response = await fetch('http://127.0.0.1:5000/recommend_playlist_from_all_friends', {
        method: 'GET',
        headers: {
            "Authorization": storedToken,
            'Content-Type': 'application/json',
        },
      });
  
      if (!response.ok) {
        // Handle error if the response status is not OK (2xx)
        const errorMessage = await response.text();
        throw new Error(`Failed to fetch playlist: ${errorMessage}`);
      }
  
        // Parse the JSON response
        const fetchedPlaylist = await response.json();
        console.log(fetchedPlaylist);

        // Update the state with the fetched playlist
        setPlaylist(fetchedPlaylist);
      
    } catch (error) {
      console.error('Error:', error.message);
      // Handle error as needed
    }

  };
  
  const submitTasteTwistFriend = async () => {
    try {
      const storedToken = localStorage.getItem('token');
      console.log(storedToken);
  
      // Check if friendUsername is empty
      if (friendUsername.trim() === '') {
        alert('Username cannot be empty.');
        return; // Don't proceed with the rest of the function
      }
  

      // Make a request to your Flask backend
      const response = await fetch(`http://127.0.0.1:5000/recommend_playlist_friends_duo?friend_username=${friendUsername}`, {
        method: 'GET',
        headers: {
          "Authorization": storedToken,
          'Content-Type': 'application/json',
        },
      });
  
      if (!response.ok) {
        // Handle error if the response status is not OK (2xx)
        alert('User is not found in your friends or blocked you.');
        const errorMessage = await response.text();
        throw new Error(`Failed to fetch playlist: ${errorMessage}`);
      }
  
      hideFriendPopup();
      // Parse the JSON response
      const fetchedPlaylist = await response.json();
      console.log(fetchedPlaylist);
  
      // Update the state with the fetched playlist
      setPlaylist(fetchedPlaylist);
  
    } catch (error) {
      console.error('Error:', error.message);
      // Handle error as needed
    }
  };
  


  const filteredSongs = playlist.filter(
    (song) =>
      `${song.track_name} ${song.performer} ${song.album}`.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    
    <div className="taste-twist-container">
    <div className="button-container">
      <button className="buttonList" onClick={submitTasteTwistUsers}>
        All users!
      </button>
      <button className="buttonList" onClick={submitTasteTwistFriends}>
        All friends!
      </button>
      <button className="buttonList" onClick={showFriendPopup}>
        Specific friend...
      </button>
    </div>
    <div className="twist-search-bar">
    <input
        type="text"
        placeholder="Search for Songs"  /* Updated placeholder text */
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
    />
    </div>

    <div className="taste-twist-list">
    <table>
        <thead>
        <tr>
            <th className="twist-title-column">Title</th>
            <th className="twist-artist-column">Artist</th>
            <th className="twist-album-column">Album</th>
            <th className="twist-saved-column">Saved</th>
        </tr>
        </thead>
        <tbody>
        {filteredSongs.map((song, index) => (
        <tr key={index}>
            <td className="twist-title-column">
                {song.track_name}
                <div className="loves-text">liked by {' '}
                <span className="twist-username">
                {song.username} </span>
            </div>
            </td>
            <td className="twist-artist-column">{song.performer}</td>
            <td className="twist-album-column">{song.album}</td>
            <td className="twist-saved-column">
                <span
                    onClick={() => SaveSong(song)}
                    style={{ cursor: 'pointer', marginLeft: '45px' }}
                >
                    <img
                        src={saveIcon}
                        alt="Save Icon"
                        onClick={() => console.log(song)}
                        style={{ width: '22px', height: '22px' }}
                    />
                </span>
            </td>
        </tr>
    ))}
        </tbody>
    </table>
    </div>

    {friendPopupVisible && (
            <div className="friend-popup">
            <button className="close-button" onClick={hideFriendPopup}>
            X
          </button>
            <input
                type="text"
                placeholder="Enter friend's username"
                className='username-input'
                value={friendUsername}
                onChange={(e) => setFriendUsername(e.target.value)}
            />
            <button className='submit-button' onClick={submitTasteTwistFriend}>
                Submit</button>
            </div>
        )}
    </div>
  );
}

export default TasteTwist;