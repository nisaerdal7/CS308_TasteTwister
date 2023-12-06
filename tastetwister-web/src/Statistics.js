// StatsPage.js
import React, { useState } from 'react';
import Sidebar from './Sidebar';
import './Statistics.css';

const StatsPage = () => {
  const [selectedTab, setSelectedTab] = useState('last24');
  const [selectedCategory, setSelectedCategory] = useState('songs');

  // Mock data
  const data = {
    last24: [
      { name: 'Song 1', artist: 'Artist 1', plays: 50 },
      // Add more data as needed
    ],
    lastWeek: [
      { name: 'Song 2', artist: 'Artist 2', plays: 40 },
      // Add more data as needed
    ],
    allTime: [
      { name: 'Song 3', artist: 'Artist 3', plays: 100 },
      // Add more data as needed
    ],
  };

  const handleTabChange = (tab) => {
    setSelectedTab(tab);
  };

  const handleCategoryChange = (category) => {
    setSelectedCategory(category);
  };

  return (
    <div className="stats-container">
      {/* Background Image */}
      <Sidebar />
      
      {/* Black Transparent Grid */}
      <div className="grid-container">
        {/* Dropdown Menu */}
        <select onChange={(e) => handleCategoryChange(e.target.value)} value={selectedCategory} className="select-dropdown">
          <option value="songs">Songs</option>
          <option value="artists">Artists</option>
          <option value="albums">Albums</option>
        </select>

        {/* Tabs */}
        <div className="stats-tabs-container">
          <div
            className={`stats-tab ${selectedTab === 'last24' ? 'active' : ''}`}
            onClick={() => handleTabChange('last24')}
          >
            Last 24 Hours
          </div>
          <div
            className={`stats-tab ${selectedTab === 'lastWeek' ? 'active' : ''}`}
            onClick={() => handleTabChange('lastWeek')}
          >
            Last Week
          </div>
          <div
            className={`stats-tab ${selectedTab === 'allTime' ? 'active' : ''}`}
            onClick={() => handleTabChange('allTime')}
          >
            All Time
          </div>
        </div>

        {/* Table of Top 10 Items */}
        <table className="data-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Artist</th>
              <th>Album</th>
            </tr>
          </thead>
          <tbody>
            {data[selectedTab].map((item, index) => (
              <tr key={index}>
                <td>{item.name}</td>
                <td>{item.artist}</td>
                <td>{item.plays}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default StatsPage;
