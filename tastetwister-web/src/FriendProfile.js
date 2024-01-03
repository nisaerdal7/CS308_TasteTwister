// FriendProfile.js
import React, { useState, useEffect } from 'react';
import './FriendProfile.css'; // Add styling for the friend profile


const FriendProfile = ({ username }) => {
  const [topSongs, setTopSongs] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`http://127.0.0.1:5000/stats/all-time/${username}`, {
          method: 'GET',
        });

        if (!response.ok) {
          throw new Error('Network response was not ok');
        }

        const result = await response.json();

        setTopSongs(result.top_songs || []);
      } catch (error) {
        console.error('Error fetching data:', error.message);
      }
    };

    fetchData();
  }, [username]);

  const filteredSongs = topSongs.filter(
    (song) =>
      `${song.track_name} ${song.performer} ${song.album}`.toLowerCase()
  );

  return (
    <div className="friend-profile-container">
      
        <div className="favorite-songs-container">
          <h2>{`${username}'s Top Songs`}</h2>
          
          <table className="friend-song-table">
            <thead>
              <tr>
                <th className= "column">Title</th>
                <th className="column">Rating</th>
                
              </tr>
            </thead>
            <tbody>
              {filteredSongs.map((song, index) => (
                <tr key={index}>
                  <td className="column">{song.track_name}</td>
                  <td className="column">{song.rating}</td>
                  
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    
  );
};

export default FriendProfile;

