import React, { useState, useEffect} from 'react';
import './SongList.css';


function SongList() {
  const [searchTerm, setSearchTerm] = useState('');
  const [songs, setSongs] = useState([]);
  
  useEffect(() => {
    // Fetch the user's songs when the component mounts
    const storedUsername = localStorage.getItem('username');
    console.log(storedUsername)
    fetch('http://127.0.0.1:5000/songs?username='+storedUsername, {
      method: 'GET',
      credentials: 'include'
      
    })
      .then((response) => response.json())
      .then((data) => {
        setSongs(data);
      })
      .catch((error) => console.error('Error fetching songs:', error));
  }, [songs]);

  /*const [songs, setSongs] = useState([
    { title: 'Cant Remember to Forget You', artist: 'Rihanna', album: 'Shakira. (Expanded Edition)',
     rating: '4' },
    { title: 'Waka Waka (This Time for Africa)', artist: 'Shakira', 
    album: 'Waka Waka (This Time for Africa)', rating: '5' },
    
  ]);*/

  const [isPopupVisible, setPopupVisible] = useState(false);
  const [isManualPopupVisible, setManualPopupVisible] = useState(false);

  const [songEntry, setSongEntry] = useState({
    track_name: "",
    performer: "",
    album: "",
    rating: "",
  });

  const showPopup = () => {
    setPopupVisible(true);
    setManualPopupVisible(false); // Hide the manual popup
  };  

  const hidePopup = () => {
    setPopupVisible(false);
  };

  const showManualPopup = () => {
    setPopupVisible(false); // Close the current popup
    setManualPopupVisible(true);
  };

  const hideManualPopup = () => {
    setManualPopupVisible(false);
  };

  // You can work with the selected file (e.g., upload it to the server or process it)
  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      
      console.log('Selected file:', file);
    }
  };

  //TO-DO: URL thing does not work properly yet, waiting for backend implementation.
  const [urlInput, setUrlInput] = useState("");
  //To access the urlInput value later for further use
  const handleUrlInputChange = (e) => {
    setUrlInput(e.target.value); // Update the URL state
  };

  const handleSongInputChange = (e, fieldName) => {
    setSongEntry({
      ...songEntry,
      [fieldName]: e.target.value,
    });
  };

  const submitSong = () => {
    // Check if any of the fields are empty
    if (!songEntry.track_name || !songEntry.performer || !songEntry.album || !songEntry.rating) {
      // Display a warning message and return early
      alert("All fields are required for submit.");
    
      return;
    }
  
    // Construct the JSON object with user's song entry
    const userSong = {
      ...songEntry,
    };
  
    console.log("User's Song Entry:", userSong);
    // You can send this object to the backend later
  };

  const filteredSongs = songs.filter(
    (song) =>
      `${song.track_name} ${song.performer} ${song.album}`.toLowerCase().includes(searchTerm.toLowerCase())
  );

 return (
    <div className="song-list-container">
      <div className="search-bar">
        <input
          type="text"
          placeholder="Search for songs"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        <button className="add-button" onClick={showPopup}>
          +
        </button>
      </div>

      <div className="song-list">
        <table>
          <thead>
            <tr>
              <th className="title-column">Title</th>
              <th className="column">Artist</th>
              <th className="column">Album</th>
              <th className="column">Rating</th>
            </tr>
          </thead>
          <tbody>
          {filteredSongs.map((song, index) => (
              <tr key={index}>
                <td className="title-column">{song.track_name}</td>
                <td className="column">{song.performer}</td>
                <td className="column">{song.album}</td>
                <td className="column">{song.rating}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {isPopupVisible && (
        <div className="popup">
          <button className="close-button" onClick={hidePopup}>
            X
          </button>
          <div className="button-container">
            <label className="upload-button" htmlFor="fileInput">
              File Upload
            </label>
            <input
              type="file"
              id="fileInput"
              accept=".csv"
              style={{ display: "none" }}
              onChange={handleFileUpload}
            />
          </div>
          <button onClick={showManualPopup}>Manual Enter</button>
        </div>
      )}

      {isManualPopupVisible && (
        <div className="popup">
          <button className="close-button" onClick={hideManualPopup}>
            X
          </button>
          <input
            type="text"
            placeholder="URL.."
            className="url-input"
            value={urlInput}
            onChange={handleUrlInputChange}
            />
          <div className="song-entry-container">
            <div className="song-entry-row">
                <p>Enter your song!</p>
            </div>
            <div className="song-entry-row">
                <input
                type="text"
                placeholder="Title..."
                value={songEntry.track_name}
                onChange={(e) => handleSongInputChange(e, "title")}
                />
                <input
                type="text"
                placeholder="Artist..."
                value={songEntry.performer}
                onChange={(e) => handleSongInputChange(e, "artist")}
                />
            </div>
            <div className="song-entry-row">
                <input
                type="text"
                placeholder="Album..."
                value={songEntry.album}
                onChange={(e) => handleSongInputChange(e, "album")}
                />
                <select
                    value={songEntry.rating}
                    onChange={(e) => handleSongInputChange(e, "rating")}
                    className="rating-select"
                    >
                    <option value="">Select Rating</option>
                    {[1, 2, 3, 4, 5].map((rating) => (
                        <option key={rating} value={rating}>
                        {rating}
                        </option>
                    ))}
                    </select>
            </div>
            </div>
          <button className="back-button" onClick={showPopup}>
            Back
          </button>
          <button onClick={submitSong}>Submit</button>
        </div>
      )}
    </div>
  );
}

export default SongList;
