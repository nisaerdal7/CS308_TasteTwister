import React, { useState, useEffect} from 'react';
import './RateIt.css';
import editIcon from './images/edit-icon.png'; // Adjust the path based on your project structure


function RateIt() {
  const [searchTerm, setSearchTerm] = useState('');
  const [songs, setSongs] = useState([]);
  const [selectedSongId, setSelectedSongId] = useState(0);
  const [isEditPopupVisible, setEditPopupVisible] = useState(false);

  const showEditPopup = (songId) => {
    setSelectedSongId(songId);
    setEditPopupVisible(true);
  };  

  const hideEditPopup = () => {
    setEditPopupVisible(false);
  };

  const fetchSongs = () => {
    const storedUsername = localStorage.getItem('username');
    console.log(storedUsername);
    
    return fetch('http://127.0.0.1:5000/songs/unrated?username=' + storedUsername, {
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
  

  const handleEditRatings = (songId, newRating) => {
    const storedToken = localStorage.getItem('token');
    fetch(`http://127.0.0.1:5000/songs/${songId}/update`, {
      method: 'POST',
      headers: {
        'Authorization': storedToken,
        'Content-Type': 'application/json', // Specify content type
      },
      body: JSON.stringify({ new_rating: newRating }), // Convert data to JSON string
    })
    .then((response) => response.json())
    .then((data) => {
      //console.log('Response from server:', data);
      if (data.message === 'Song rating updated successfully!') {
          alert("Song rating updated successfully!");
  
          // Fetch the updated list of songs
          fetchSongs()
          .then((updatedData) => {
              setSongs(updatedData);
              setSelectedRating('');
              //console.log("Updated songs: ", updatedData);
          })
          .catch((error) => console.error('Error fetching updated songs:', error));
      }
      })

  };

  const filteredSongs = songs.filter(
    (song) =>
      `${song.track_name} ${song.performer} ${song.album}`.toLowerCase().includes(searchTerm.toLowerCase())
  );
  const [selectedRating, setSelectedRating] = useState(0);
 return (
    <div className="song-list-container">
      <div className="search-bar">
        <input
          type="text"
          placeholder="Search for songs"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      <div className="song-list">
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
          <td className="actions-column">
    
            <span
            onClick={()=>showEditPopup(song.id)}// Call a function for edit action
            style={{ cursor: 'pointer', marginLeft: '45px' }}
           >
          <img
            src={editIcon}
            alt="Edit Icon"
            onClick={()=>console.log(song.id)}
            style={{ width: '13px', height: '13px' }} // Adjust the size as needed
          />
            </span>
          </td>

        </tr>
      ))}
    </tbody>
  </table>
</div>

{isEditPopupVisible && (
  <div className="popup">
    <button className="close-button" onClick={hideEditPopup}>
      X
    </button>
    <div className="button-container">
      <select
        className="ratinge-select"
        value={selectedRating}
        onChange={(e) => setSelectedRating(e.target.value)}
      >
        <option value="" >Select Rating</option>
        {[1, 2, 3, 4, 5].map((ratinge) => (
          <option key={ratinge} value={ratinge}>
            {ratinge}
          </option>
        ))}
      </select>
    </div>
    <button onClick={()=> handleEditRatings(selectedSongId, selectedRating)}>Submit</button>
  </div>
)}
    </div>
  );
}

export default RateIt;