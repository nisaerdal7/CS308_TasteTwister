import React, { useState, useEffect} from 'react';
import './SongList.css';
import editIcon from './images/edit-icon.png'; // Adjust the path based on your project structure
import deleteIcon from './images/delete-icon.webp';
import downloadIcon from './images/download-icon.png'; 
import backIcon from './images/back-icon.png';

function SongList() {
  const [searchTerm, setSearchTerm] = useState('');
  const [songs, setSongs] = useState([]);
  const [selectedSongId, setSelectedSongId] = useState(0);
  const [selectedArtist, setSelectedArtist] = useState('');
  const [selectedAlbum, setSelectedAlbum] = useState('');

  const [isPopupVisible, setPopupVisible] = useState(false);
  const [isManualPopupVisible, setManualPopupVisible] = useState(false);
  const [isSpotifyPopupVisible, setSpotifyPopupVisible] = useState(false);
  const [isEditPopupVisible, setEditPopupVisible] = useState(false);
  const [isExportPopupVisible, setExportPopupVisible] = useState(false);
  const [isDeletePopupVisible, setDeletePopupVisible] = useState(false);

  const [songEntry, setSongEntry] = useState({
    track_name: "",
    performer: "",
    album: "",
    rating: "",
  });

  const resetSongEntry = () => {
    setSongEntry({
      track_name: '',
      performer: '',
      album: '',
      rating: ''
    });
  };

  const showPopup = () => {
    resetSongEntry();
    setPopupVisible(true);
    setManualPopupVisible(false); // Hide the manual popup
    setSpotifyPopupVisible(false);
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

  const showSpotifyPopup = () => {
    setRelevantSongs([]); // Clear relevant songs when the popup is opened
    resetSongEntry();
    setPopupVisible(false); // Close the current popup
    setSpotifyPopupVisible(true);
  };

  const showManualPopup = () => {
    resetSongEntry();
    setPopupVisible(false); // Close the current popup
    setManualPopupVisible(true);
  };

  const hideManualPopup = () => {
    setManualPopupVisible(false);
  };

  const hideSpotifyPopup = () => {
    setSpotifyPopupVisible(false);
  };

  const handleDelete = (songId) =>{
    const storedToken = localStorage.getItem('token');
    fetch(`http://127.0.0.1:5000/songs/${songId}/delete`, {
      method: 'POST',
      headers: {
        'Authorization': storedToken,
        'Content-Type': 'application/json', // Specify content type
      },
    })
    .then((response) => response.json())
    .then((data) => {
      //console.log('Response from server:', data);
      if (data.message === 'Song deleted successfully!') {
          alert('Song deleted successfully!');
  
          // Fetch the updated list of songs
          fetchSongs()
          .then((updatedData) => {
              setSongs(updatedData);
              //console.log("Updated songs: ", updatedData);
              setDeletePopupVisible(false);
          })
          .catch((error) => console.error('Error fetching updated songs:', error));
      }
      else {
        alert("The song cannot be deleted!")
      }
      })
  }

  const handleDeleteArtist = (artist) =>{
    const storedToken = localStorage.getItem('token');
    const perf = "One Direction"
    fetch(`http://127.0.0.1:5000/songs/artist/${artist}/delete`, {
      method: 'POST',
      headers: {
        'Authorization': storedToken,
        'Content-Type': 'application/json', // Specify content type
      },
    })
    .then((response) => response.json())
    .then((data) => {
      //console.log('Response from server:', data);
      if (data.message === 'All songs by ' + artist +' deleted successfully!') {
          alert(data.message);
  
          // Fetch the updated list of songs
          fetchSongs()
          .then((updatedData) => {
              setSongs(updatedData);
              //console.log("Updated songs: ", updatedData);
              setDeletePopupVisible(false);
          })
          .catch((error) => console.error('Error fetching updated songs:', error));
      }
      else {
        alert("The songs cannot be deleted!")
      }
      })
  }
  const handleDeleteAlbum = (album) =>{
    const storedToken = localStorage.getItem('token');
    fetch(`http://127.0.0.1:5000/songs/album/${album}/delete`, {
      method: 'POST',
      headers: {
        'Authorization': storedToken,
        'Content-Type': 'application/json', // Specify content type
      },
    })
    .then((response) => response.json())
    .then((data) => {
      //console.log('Response from server:', data);
      if (data.message === 'All songs from the album ' + album +' deleted successfully!') {
          alert(data.message);
  
          // Fetch the updated list of songs
          fetchSongs()
          .then((updatedData) => {
              setSongs(updatedData);
              //console.log("Updated songs: ", updatedData);
              setDeletePopupVisible(false);
          })
          .catch((error) => console.error('Error fetching updated songs:', error));
      }
      else {
        alert("The songs cannot be deleted!")
      }
      })
  }

  


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
  /*const [urlInput, setUrlInput] = useState("");
  //To access the urlInput value later for further use
  const handleUrlInputChange = (e) => {
    setUrlInput(e.target.value); // Update the URL state
  };*/

  const handleSongInputChange = (e, fieldName) => {
    setSongEntry({
      ...songEntry,
      [fieldName]: e.target.value,
    });
  };

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

  const submitSong = () => {
    // Check if any of the fields are empty
    if (!songEntry.track_name || !songEntry.performer || !songEntry.album) {
      // Display a warning message and return early
      alert("All fields are required for submit.");
    
      return;
    }
  
    // Construct the JSON object with user's song entry
    const userSong = {
      ...songEntry,
    };
  
    //console.log("User's Song Entry:", userSong);
    
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
        setSongEntry({
          track_name: '',
          performer: '',
          album: '',
          rating: ''
        });
        setManualPopupVisible(false);
        setPopupVisible(false);
        setSpotifyPopupVisible(false);
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
  const [relevantSongs, setRelevantSongs] = useState([]);
  const submitSpotifySong = () => {
    // Check if any of the fields are empty
    if (!songEntry.track_name && !songEntry.performer && !songEntry.album) {
      // Display a warning message and return early
      alert("At least one field is required for submit.");
      return;
    }
  
    // Construct the JSON object with user's song entry
    const userSong = {
      track_name: songEntry.track_name,
      performer: songEntry.performer,
      album: songEntry.album,
    };
  
    const storedToken = localStorage.getItem('token');
    console.log(storedToken);
  
    fetch('http://127.0.0.1:5000/list_and_add_songs', {
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
        if (data.relevant_songs) {
          setRelevantSongs(data.relevant_songs);
        } else {
          alert("No relevant songs found");
        }
      })
      .catch((error) => {
        console.error('Error listing songs:', error);
      });
  };
  
  const handleExportSubmit = (selectedArtist, selectedRating) => {
    const storedToken = localStorage.getItem('token');
    console.log(storedToken);
  
    // Construct the export URL with selectedArtist and/or selectedRating if provided
    let exportUrl = 'http://127.0.0.1:5000/export_songs';
  
    if (selectedArtist) {
      exportUrl += `?performer=${encodeURIComponent(selectedArtist)}`;
    }
  
    if (selectedRating) {
      exportUrl += `${selectedArtist ? '&' : '?'}rating=${encodeURIComponent(selectedRating)}`;
    }
  
    // Make the fetch request to the backend
    fetch(exportUrl, {
      method: 'GET',
      headers: {
        "Authorization": storedToken,
        'Content-Type': 'application/json',
      },
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.blob();
      })
      .then((blob) => {
        // Create a Blob URL for the blob data
        const url = window.URL.createObjectURL(new Blob([blob]));
  
        // Create a temporary link element and click it to trigger the download
        const a = document.createElement('a');
        a.href = url;
        a.download = 'songs.csv';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
  
        // Revoke the Blob URL to free up resources
        window.URL.revokeObjectURL(url);
      })
      .catch((error) => {
        console.error('Error exporting songs:', error.message);
      });
  };
  
  const [showAddRatingPopup, setShowAddRatingPopup] = useState(false);
  const [selectedAddRating, setSelectedAddRating] = useState('');

  const handleSelectSong = (selectedSong) => {
    // Update the songEntry state with the selected song
    setSongEntry({
      track_name: selectedSong.track_name,
      performer: selectedSong.performer,
      album: selectedSong.album,
      rating: selectedAddRating,
    });
    // Show the rating popup
    setShowAddRatingPopup(true);
  };

  // Add a function to handle the submission of the song and rating
  const handleSongAndRatingSubmit = () => {

    songEntry.rating = selectedAddRating;
    // Submit the song entry with the rating
    submitSong();

    // Close the rating popup
    setShowAddRatingPopup(false);

    // Optionally, you can reset the selected rating state
    setSelectedAddRating('');
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
        <button className="add-button" onClick={()=>setExportPopupVisible(true)}>
        <img
            src={downloadIcon}
            alt="Download Icon"
            style={{ width: '13px', height: '13px' }} // Adjust the size as needed
          />
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
            style={{ cursor: 'pointer', marginLeft: '45px' }}
           >
          <img
            src={editIcon}
            alt="Edit Icon"
            onClick={()=>console.log(song.id)}
            style={{ width: '13px', height: '13px' }} // Adjust the size as needed
          />
            </span>
            <span
            onClick={()=>{setDeletePopupVisible(true);setSelectedSongId(song.id)}}
            style={{ cursor: 'pointer', marginLeft: '10px' }}
           >
          <img
            src={deleteIcon}
            alt="Delete Icon"
            style={{ width: '20px', height: '20px' }} // Adjust the size as needed
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
          <button onClick={showSpotifyPopup}>Spotify Upload</button>
        </div>
      )}

      {isManualPopupVisible && (
        <div className="popup">
          <button className="close-button" onClick={hideManualPopup}>
            X
          </button>
          <div className="song-entry-container">
            <div className="song-entry-row">
              <p></p>
              <p></p>
              <p></p>
              <p></p>
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
          <img
            src={backIcon}
            alt="Back Icon"
            style={{ width: '13px', height: '13px' }} // Adjust the size as needed
          />
          </button>
          <button onClick={submitSong}>Submit</button>
        </div>
      )}

{isSpotifyPopupVisible && (
  <div className="popup">
    <div className="button-row" style={{ marginBottom: '45px' }}>
      <button className="close-button" onClick={hideSpotifyPopup}>
        X
      </button>
      <button className="back-button" onClick={showPopup}>
        <img
          src={backIcon}
          alt="Back Icon"
          style={{ width: '13px', height: '13px' }}
        />
      </button>
    </div>

    <div className="song-entry-container">
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
        <input
          type="text"
          placeholder="Album..."
          value={songEntry.album}
          onChange={(e) => handleSongInputChange(e, "album")}
        />
      </div>

      {relevantSongs.length > 0 && (
        <div className="relevant-songs-container">
          <ul>
            {relevantSongs.map((song, index) => (
              <li key={index} onClick={() => handleSelectSong(song)}>
                <div className="song-info">
                  <p className="song-title">{song.track_name}, {song.album}</p>
                  <p className="song-artist">{song.performer}</p>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      {showAddRatingPopup && (
        <div className="popup">
          <button className="close-button" onClick={() => setShowAddRatingPopup(false)}>
            X
          </button>
          <div className="rating-popup" style={{ background: 'black', color: 'gray', display: 'flex', flexDirection: 'column' }}>
          <select
        className="ratinge-select"
        value={selectedAddRating}
        onChange={(e) => setSelectedAddRating(e.target.value)}
      >
        <option value="" >Select Rating</option>
        {[1, 2, 3, 4, 5].map((ratinge) => (
          <option key={ratinge} value={ratinge}>
            {ratinge}
          </option>
        ))}
      </select>
            <button
              onClick={handleSongAndRatingSubmit}
              style={{ background: '#329374', color: '#fff' }}
            >
              Submit 
            </button>
          </div>
        </div>
      )}

    </div>

    <button onClick={submitSpotifySong}>Submit</button>
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
{isDeletePopupVisible && (
  <div className="popup">
    <button className="close-button" onClick={()=>setDeletePopupVisible(false)}>
      X
    </button>
    <div className="song-entry-row">
       <span 
          style={{marginTop: '20px' }}
          >
            <p></p>
          <p>Delete all songs by the artist</p>
           </span>
       </div>
    <div className="song-entry-row">
      <input
         type="text"
         placeholder="Artist..."
         value={selectedArtist}
         onChange={(e) => setSelectedArtist(e.target.value)}
      />
    </div>
    <button onClick={()=>{handleDeleteArtist(selectedArtist);setSelectedArtist('')}}>Submit</button>
    <div className="song-entry-row">
       <span 
          style={{marginTop: '20px' }}
          >
          <p>Delete all songs by the album</p>
           </span>
       </div>
    <div className="song-entry-row">
      <input
         type="text"
         placeholder="Album..."
         value={selectedAlbum}
         onChange={(e) => setSelectedAlbum(e.target.value)}
      />
    </div>
    <button onClick={()=>{handleDeleteAlbum(selectedAlbum);setSelectedAlbum('')}}>Submit</button>
    <button onClick={()=>handleDelete(selectedSongId)}>Delete the song</button>
  </div>
)}
{isExportPopupVisible && (
  <div className="popup">
    <button className="close-button" onClick={()=>setExportPopupVisible(false)}>
      X
    </button>
    <div className="song-entry-container">
            <div className="song-entry-row">
              <span 
              style={{marginTop: '40px' }}
              >
                <p>Filter by artist or rating!</p>
                </span>
            </div>
            <div className="song-entry-row">
                <input
                type="text"
                placeholder="Artist..."
                value={selectedArtist}
                onChange={(e) => setSelectedArtist(e.target.value)}
                />
            </div>
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
            
  </div>
            
    <button onClick={()=> handleExportSubmit(selectedArtist, selectedRating)}>Submit</button>
    
  </div>
)}

      
    </div>
  );
}

export default SongList;
