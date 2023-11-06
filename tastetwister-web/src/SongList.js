import React, { useState, useEffect} from 'react';
import './SongList.css';

function SongList() {
  const [searchTerm, setSearchTerm] = useState('');
  //const [songs, setSongs] = useState([]);

  /*useEffect(() => {
    //Make a GET request to fetch the list of songs from your backend API.
    fetch('http://127.0.0.1:5000/songs')
      .then((response) => response.json())
      .then((data) => {
        console.log(data);
    })
      .catch((error) => console.error('Error fetching songs:', error));
      
  }, []);*/
  const [songs, setSongs] = useState([
    { title: 'Cant Remember to Forget You', artist: 'Rihanna', album: 'Shakira. (Expanded Edition)',
     rating: '4' },
    { title: 'Waka Waka (This Time for Africa)', artist: 'Shakira', 
    album: 'Waka Waka (This Time for Africa)', rating: '5' },
    { title: 'Cant Remember to Forget You', artist: 'Rihanna', album: 'Shakira. (Expanded Edition)',
     rating: '4' },
    { title: 'Waka Waka (This Time for Africa)', artist: 'Shakira', 
    album: 'Waka Waka (This Time for Africa)', rating: '5' },
    { title: 'Cant Remember to Forget You', artist: 'Rihanna', album: 'Shakira. (Expanded Edition)',
     rating: '4' },
    { title: 'Waka Waka (This Time for Africa)', artist: 'Shakira', 
    album: 'Waka Waka (This Time for Africa)', rating: '5' },
    { title: 'Cant Remember to Forget You', artist: 'Rihanna', album: 'Shakira. (Expanded Edition)',
     rating: '4' },
    { title: 'Waka Waka (This Time for Africa)', artist: 'Shakira', 
    album: 'Waka Waka (This Time for Africa)', rating: '5' },
    { title: 'Cant Remember to Forget You', artist: 'Rihanna', album: 'Shakira. (Expanded Edition)',
     rating: '4' },
    { title: 'Waka Waka (This Time for Africa)', artist: 'Shakira', 
    album: 'Waka Waka (This Time for Africa)', rating: '5' },
    { title: 'Cant Remember to Forget You', artist: 'Rihanna', album: 'Shakira. (Expanded Edition)',
     rating: '4' },
    { title: 'Waka Waka (This Time for Africa)', artist: 'Shakira', 
    album: 'Waka Waka (This Time for Africa)', rating: '5' },
    
  ]);

  const [isPopupVisible, setPopupVisible] = useState(false);
  const showPopup = () => {
    setPopupVisible(true);
  };

  const hidePopup = () => {
    setPopupVisible(false);
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      // You can now work with the selected file (e.g., upload it to the server or process it)
      console.log('Selected file:', file);
    }
  };

  const filteredSongs = songs.filter(
    (song) =>
      `${song.title} ${song.artist} ${song.album}`.toLowerCase().includes(searchTerm.toLowerCase())
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
        <button className="add-button" onClick={showPopup}>+</button>
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
                <td className="title-column">{song.title}</td>
                <td className="column">{song.artist}</td>
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
            style={{ display: 'none' }}
            onChange={handleFileUpload}
          />
        </div>
            <button>Manual Enter</button>
    </div>
)}

    </div>
  );
}

export default SongList;
