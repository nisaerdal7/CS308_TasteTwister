// FriendProfile.js
import React, { useState, useEffect } from 'react';
import './FriendProfile.css'; // Add styling for the friend profile
import * as icons from './images'; // Update this path accordingly


const FriendProfile = ({ username }) => {
  const [topSongs, setTopSongs] = useState([]);
  const [myProfileIcon, setProfileIcon] = useState('');
  const storedToken = localStorage.getItem('token');

  const fetchSongs = () => {
    
    return fetch('http://127.0.0.1:5000/songs?username=' + username, {
      headers:{
        "Authorization": storedToken
      },
      method: 'GET',
      credentials: 'include'
    })
    .then((response) => response.json())
    .catch((error) => {
      console.error('Error fetching songs:', error);
      throw error; // propagate the error
    });
  };
  
  useEffect(() => {
    // Fetch the user's songs when the component mounts
    fetchSongs()
      .then((data) => {
        setTopSongs(data);
        console.log(topSongs);
      });
    fetchProfileIcon();
  }, []);

  const filteredSongs = topSongs.filter(
    (song) =>
      `${song.track_name} ${song.performer} ${song.album}`.toLowerCase()
  );

  const fetchProfileIcon = () => {
    const storedToken = localStorage.getItem('token');

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

  return (
    <div className="friend-profile-container">
        <div className="favorite-songs-container">
          <h2>
            <img
              src={myProfileIcon ? getProfileImage(myProfileIcon) : null}
              alt="Profile Icon"
              className="my-profile-icon"
              style={{ width: '57px', height: '57px' }}
            />
            {`${username}'s Songs`}
          </h2>
          
          <table className="friend-song-table">
            <thead>
              <tr>
                <th className= "title-column">Title</th>
                <th className= "column">Artist</th>
                <th className= "column">Album</th>
                <th className="rating-column">Rating</th>
                
              </tr>
            </thead>
            <tbody>
              {filteredSongs.map((song, index) => (
                <tr key={index}>
                  <td className="title-column">{song.track_name}</td>
                  <td className="column">{song.performer}</td>
                  <td className="column">{song.album}</td>
                  <td className="rating-column">{song.rating}</td>
                  
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    
  );
};

export default FriendProfile;

