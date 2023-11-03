import React, { useState, useEffect} from 'react';
import './SongList.css';

function SongList() {
  const [searchTerm, setSearchTerm] = useState('');
  const [songs, setSongs] = useState([]);

  useEffect(() => {
    //Make a GET request to fetch the list of songs from your backend API.
    fetch('http://127.0.0.1:5000/songs')
      .then((response) => response.json())
      .then((data) => {
        console.log(data);
    })
      .catch((error) => console.error('Error fetching songs:', error));
      
  }, []);

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
        <button className="add-button">ADD</button> {/* Added "ADD" button */}
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
    </div>
  );
}

export default SongList;
