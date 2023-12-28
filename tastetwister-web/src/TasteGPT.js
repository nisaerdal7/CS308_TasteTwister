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

  return (
    
    <div className="taste-gpt-container">
    
    {/* Genres Dropdown */}
    <div className="dropdown-container">
    <select
        className="gpt-dropdown black-transparent-background"
        value={selectedGenre}
        onChange={(e) => setSelectedGenre(e.target.value)}
      >
        <option value="" disabled>Select Genre...</option>
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
        <option value="" disabled>Select Era...</option>
        <option value="70s">70s</option>
        <option value="80s">80s</option>
        <option value="90s">90s</option>
        <option value="00s">00s</option>
        <option value="10s">10s</option>
        <option value="20s">20s</option>
      </select>
      <button className='gpt-submit-button'
              
              style={{ background: '#329374', color: '#fff' }}
            >
              Submit 
            </button>
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