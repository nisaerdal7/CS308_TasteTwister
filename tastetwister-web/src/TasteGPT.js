import React, { useState } from 'react';
import './TasteGPT.css'; // Updated import
import saveIcon from './images/save-icon.png';

function TasteGPT() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedGenre, setSelectedGenre] = useState('');
  const [selectedEra, setSelectedEra] = useState('');
  const [selectedTimeframe, setSelectedTimeframe] = useState('last-24-hours'); // Default value for timeframe
  const [activeTab, setActiveTab] = useState('yourTaste'); // Default tab
  const [playlist, setPlaylist] = useState([]);
  const [isLoading, setIsLoading] = useState(false); // New state for loading indicator
  const SaveSong = (song) => {
    // Your SaveSong function logic
    const storedToken = localStorage.getItem('token');
    console.log(storedToken);
    console.log(song);
    song.rating = '';
    fetch('http://127.0.0.1:5000/songs', {
      method: 'POST',
      headers: {
        Authorization: storedToken,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(song),
      credentials: 'include',
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.message === 'Song added or updated!') {
          alert('Song added or updated successfully!');
        }
      })
      .catch((error) => {
        console.error('Error uploading song:', error);
      });
  };

  const handleSubmitTimeframe = () => {
    setIsLoading(true); 
    // Handle submission based on the selected timeframe
    const storedToken = localStorage.getItem('token');
    const username = localStorage.getItem('username'); // Replace with the actual username

    
      // Based on your taste tab
      fetch(`http://127.0.0.1:5000/ai_song_suggestions/${selectedTimeframe}/${username}`, {
        method: 'GET',
        headers: {
          Authorization: storedToken,
        },
        credentials: 'include',
      })
        .then((response) => response.json())
        .then((data) => {
          // Handle the data as needed
          setPlaylist(data)
          console.log('AI Song Suggestions:', data);
        })
        .catch(error => {
          console.error('Error fetching song suggestions:', error);
          // Handle the error, such as displaying an alert or updating state
        }).finally(() => {
          setIsLoading(false); // Set loading state to false after the request is complete
        });
    
  };

  const handleSubmitGenreEra = () => {
    setIsLoading(true);
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

  const handleSubmit = () => {

    setIsLoading(true); // Set loading state to true before making the request
    // Call the function to handle the submission
    handleSubmitGenreEra();
  };

  const handleTabChange = (tab) => {
    setPlaylist([]);
    setActiveTab(tab);
  };

  const handleGenreChange = (e) => {
    setSelectedGenre(e.target.value);
  };

  const handleEraChange = (e) => {
    setSelectedEra(e.target.value);
  };


  const filteredSongs = playlist.filter(
    (song) =>
      `${song.track_name} ${song.performer} ${song.album}`.toLowerCase().includes(searchTerm.toLowerCase())
  );
  return (
    <div className="taste-gpt-container">
      <div className="tab-container">
        <div
          className={`tab ${activeTab === 'yourTaste' ? 'active' : ''}`}
          onClick={() => handleTabChange('yourTaste')}
        >
          Based on your taste!
        </div>
        <div
          className={`tab ${activeTab === 'genresEras' ? 'active' : ''}`}
          onClick={() => handleTabChange('genresEras')}
        >
          Based on genres & eras
        </div>
      </div>

      {activeTab === 'yourTaste' ? (
        <div className="dropdown-container">
          <select
            className="gpt-dropdown black-transparent-background"
            value={selectedTimeframe}
            onChange={(e) => setSelectedTimeframe(e.target.value)}
          >
            <option value="last-24-hours">Last 24 hours</option>
            <option value="last-7-days">Last week</option>
            <option value="all-time">All time</option>
          </select>
          <button
        className='gpt-submit-button'
        style={{ background: '#329374', color: '#fff' }}
        onClick={handleSubmitTimeframe}
      >
        Submit
      </button>
      {isLoading && (
        <div className="loader-container">
          <div className="loader"></div>
        </div>
      )}
        </div>
      ) : (
        <div className="dropdown-container">
          <select
            className="gpt-dropdown black-transparent-background"
            value={selectedGenre}
            onChange={handleGenreChange}
          >
            <option value="" >
              Select Genre...
            </option>
            <option value="rock">Rock</option>
            <option value="pop">Pop</option>
            <option value="indie">Indie</option>
            <option value="jazz">Jazz</option>
            <option value="hiphop">Hip Hop</option>
            <option value="metal">Metal</option>
          </select>

          <select
            className="gpt-dropdown black-transparent-background"
            value={selectedEra}
            onChange={handleEraChange}
          >
            <option value="" >
              Select Era...
            </option>
            <option value="70s">70s</option>
            <option value="80s">80s</option>
            <option value="90s">90s</option>
            <option value="00s">00s</option>
            <option value="2010s">2010s</option>
            <option value="2020s">2020s</option>
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
      )}

      <div className="gpt-search-bar">
        <input
          type="text"
          placeholder="Search for Songs"
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
    </div>
  );
}

export default TasteGPT;
