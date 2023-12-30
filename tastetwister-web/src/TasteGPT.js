import React, { useState, useEffect } from 'react';
import './TasteGPT.css'; // Updated import
import saveIcon from './images/save-icon.png';



function TasteGPT() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedGenre, setSelectedGenre] = useState('');
  const [selectedEra, setSelectedEra] = useState('');
  const [playlist, setPlaylist] = useState([]);
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

  
  const filteredSongs = playlist.filter(
    (song) =>
      `${song.track_name} ${song.performer} ${song.album}`.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const [isLoading, setIsLoading] = useState(false); // New state for loading indicator
  const handleSubmit = () => {

    setIsLoading(true); // Set loading state to true before making the request
    // Call the function to handle the submission
    handleSubmitGenreEra();
  };

  const handleSubmitGenreEra = () => {
    const storedUsername = localStorage.getItem('username');
    const username = storedUsername;
    const storedToken = localStorage.getItem('token');
    
    if (!storedToken) {
      setIsLoading(false); // Set loading state to false in case of an error
      // Handle the case where the token is not available
      alert("User not authenticated. Please log in.");
      return;
    }

    // Prepare the URL for the backend endpoint
    const apiUrl = `http://127.0.0.1:5000/ai_song_suggestions_by_era_genre/${username}?era=${selectedEra}&genre=${selectedGenre}`;

    // Make a GET request to the backend
    fetch(apiUrl, {
      method: 'GET',
      headers: {
        'Authorization': storedToken,
      },
    })
    .then(response => response.json())
    .then(data => {
      // Handle the response from the backend
      setPlaylist(data); // Assuming the response from the backend is an array of songs
    })
    .catch(error => {
      console.error('Error fetching song suggestions:', error);
      // Handle the error, such as displaying an alert or updating state
    }).finally(() => {
      setIsLoading(false); // Set loading state to false after the request is complete
    });
  };

  return (
    
    <div className="taste-gpt-container">
    
    {/* Genres Dropdown */}
    <div className="dropdown-container">
    <select
        className="gpt-dropdown black-transparent-background"
        value={selectedGenre}
        onChange={(e) => setSelectedGenre(e.target.value)}
      >
        <option value="" >Select Genre...</option>
        <option value="rock">Rock</option>
        <option value="pop">Pop</option>
        <option value="indie">Indie</option>
        <option value="jazz">Jazz</option>
        <option value="hiphop">Hip Hop</option>
        <option value="metal">Metal</option>
      </select>

      {/* Eras Dropdown */}
      <select
        className="gpt-dropdown black-transparent-background"
        value={selectedEra}
        onChange={(e) => setSelectedEra(e.target.value)}
      >
        <option value="" >Select Era...</option>
        <option value="70s">70s</option>
        <option value="80s">80s</option>
        <option value="90s">90s</option>
        <option value="00s">00s</option>
        <option value="10s">10s</option>
        <option value="20s">20s</option>
      </select>
      <button
        className='gpt-submit-button'
        style={{ background: '#329374', color: '#fff' }}
        onClick={handleSubmit}
      >
        Submit
      </button>
      {isLoading && (
        <div className="loader-container">
          <div className="loader"></div>
        </div>
      )}
      </div>
      <div className="gpt-search-bar">
        <input
        type="text"
        placeholder="Search for Songs"  /* Updated placeholder text */
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
    />
    </div>

    <div className="taste-gpt-list">
    <table>
        <thead>
        <tr>
            <th className="gpt-title-column">Title</th>
            <th className="gpt-artist-column">Artist</th>
            <th className="gpt-album-column">Album</th>
            <th className="gpt-saved-column">Saved</th>
        </tr>
        </thead>
        <tbody>
        {filteredSongs.map((song, index) => (
            <tr key={index}>
            <td className="gpt-title-column">{song.track_name}</td>
            <td className="gpt-artist-column">{song.performer}</td>
            <td className="gpt-album-column">{song.album}</td>
            <td className="gpt-saved-column">
                <span
                onClick={() => SaveSong(song)} // Call a function for edit action
                style={{ cursor: 'pointer', marginLeft: '45px' }}
                >
                <img
                    src={saveIcon}
                    alt="Save Icon"
                    onClick={() => console.log(song)}
                    style={{ width: '22px', height: '22px' }} // Adjust the size as needed
                />
                </span>
            </td>
            </tr>
        ))}
        </tbody>
    </table>
    </div>
    </div>
    );
}

export default TasteGPT;