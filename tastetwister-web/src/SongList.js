import React, { useState, useEffect} from 'react';
import './SongList.css';
import editIcon from './images/edit-icon.png'; // Adjust the path based on your project structure



function SongList() {
  const [searchTerm, setSearchTerm] = useState('');
  const [songs, setSongs] = useState([]);
  const [selectedSongId, setSelectedSongId] = useState(0);
  

  const [isPopupVisible, setPopupVisible] = useState(false);
  const [isManualPopupVisible, setManualPopupVisible] = useState(false);
  const [isEditPopupVisible, setEditPopupVisible] = useState(false);

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

  const showEditPopup = (songId) => {
    setSelectedSongId(songId);
    setEditPopupVisible(true);
  };  

  const hideEditPopup = () => {
    setEditPopupVisible(false);
  };

  const showManualPopup = () => {
    setPopupVisible(false); // Close the current popup
    setManualPopupVisible(true);
  };

  const hideManualPopup = () => {
    setManualPopupVisible(false);
  };


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
      });
  }, []);
  
  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      //console.log('Selected file:', file);
      const storedToken = localStorage.getItem('token');
      const formData = new FormData();
      formData.append('file', file);
      console.log(storedToken)
      fetch('http://127.0.0.1:5000/upload_songs', {
        method: 'POST',
        headers:{
          "Authorization": storedToken
        },
        body: formData,
        credentials: 'include',
        
      })
      .then((response) => response.json())
      .then((data) => {
        //console.log('Response from server:', data);
        if (data.message === "Songs uploaded successfully!") {
          alert("Songs uploaded successfully!");
  
          // Fetch the updated list of songs
          fetchSongs()
            .then((updatedData) => {
              setSongs(updatedData);
              //console.log("Updated songs: ", updatedData);
            })
            .catch((error) => console.error('Error fetching updated songs:', error));
        }
      })
      .catch((error) => {
        console.error('Error uploading file:', error);
      });
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

  const handleEditRatings = (songId, newRating) => {
    const storedToken = localStorage.getItem('token');
    console.log(selectedRating);
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
              //console.log("Updated songs: ", updatedData);
          })
          .catch((error) => console.error('Error fetching updated songs:', error));
      }
      })

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
    
    const storedToken = localStorage.getItem('token');
    console.log(storedToken);

    fetch('http://127.0.0.1:5000/songs', {
    method: 'POST',
    headers: {
        "Authorization": storedToken,
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(userSong),
    credentials: 'include',
    })
    .then((response) => response.json())
    .then((data) => {
    if (data.message === "Song added or updated!") {
        alert("Song added or updated successfully!");

        // Fetch the updated list of songs
        fetchSongs()
        .then((updatedData) => {
            setSongs(updatedData);
        })
        .catch((error) => console.error('Error fetching updated songs:', error));
    }
    })
    .catch((error) => {
    console.error('Error uploading file:', error);
    });

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
            style={{ cursor: 'pointer', marginLeft: '5px' }}
           >
          <img
            src={editIcon}
            alt="Edit Icon"
            style={{ width: '13px', height: '13px' }} // Adjust the size as needed
          />
            </span>
          </td>

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
                onChange={(e) => handleSongInputChange(e, "track_name")}
                />
                <input
                type="text"
                placeholder="Artist..."
                value={songEntry.performer}
                onChange={(e) => handleSongInputChange(e, "performer")}
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

export default SongList;
