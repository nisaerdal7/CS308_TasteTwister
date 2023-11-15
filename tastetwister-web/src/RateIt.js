import React, { useState, useEffect} from 'react';
import './RateIt.css';
import editIcon from './images/edit-icon.png'; // Adjust the path based on your project structure



function RateIt() {
  const [searchTerm, setSearchTerm] = useState('');
  const [songs, setSongs] = useState([]);


  const fetchSongs = () => {
    const storedUsername = localStorage.getItem('username');
    console.log(storedUsername);
    
    return fetch('http://127.0.0.1:5000/songs?username=' + storedUsername, {
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
        setSongs(data);
        console.log(songs);
      });
  }, []);

  

  const filteredSongs = songs.filter(
    (song) =>
      `${song.track_name} ${song.performer} ${song.album}`.toLowerCase().includes(searchTerm.toLowerCase())
  );

 return (
    <div className="rate-it-container">
      <div className="search-bar">
        <input
          type="text"
          placeholder="Search for songs"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      <div className="rate-it">
  <table>
    <thead>
      <tr>
        <th className="title-column">Title</th>
        <th className="column">Artist</th>
        <th className="column">Album</th>
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
          <td className="actions-column"></td>

        </tr>
      ))}
    </tbody>
  </table>
</div>
      
    </div>
  );
}

export default RateIt;
