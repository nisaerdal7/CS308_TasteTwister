import React, { useState, useEffect } from 'react';
import Sidebar from './Sidebar';
import RatingChart from './RatingChart';
import './Statistics.css';

const mockData = [
  { date: '2023-12-01', rating: 4 },
  { date: '2023-12-02', rating: 3.5 },
  { date: '2023-12-03', rating: 4.2 },
  { date: '2023-12-04', rating: 3.8 },
  { date: '2023-12-05', rating: 4.5 },
];

const StatsPage = () => {
  const [selectedTab, setSelectedTab] = useState('last-24-hours');
  const [selectedCategory, setSelectedCategory] = useState('songs');
  const [data, setData] = useState({
    songs: [],
    artists: [],
    albums: [],
  });
  const [ratingData, setRatingData] = useState([]);
  const username = localStorage.getItem('username');
  const fetchChartData = async () => {
    try {
      const response = await fetch(`http://127.0.0.1:5000/stats/mean/all-time`, {
        method: 'GET',
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const result = await response.json();

      // Format the data for RatingChart
      const formattedData = Object.entries(result.daily_average_ratings).map(([date, rating]) => ({
        date,
        rating,
      }));

      setRatingData(formattedData);
    } catch (error) {
      console.error('Error fetching data:', error.message);
    }
  };
  useEffect(() => {
    // Fetch data from the backend when the component mounts
    fetchData();
  }, [selectedTab, selectedCategory]);

  const fetchData = async () => {
    try {
      const response = await fetch(`http://127.0.0.1:5000/stats/${selectedTab}/${username}`, {
        method: 'GET',
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const result = await response.json();

      setData({
        songs: result.top_songs || [],
        artists: result.top_performers || [],
        albums: result.top_albums || [],
      });
    } catch (error) {
      console.error('Error fetching data:', error.message);
    }
  };

  const handleTabChange = (tab) => {
    setSelectedTab(tab);
  };

  const handleCategoryChange = (category) => {
    setSelectedCategory(category);
  };

  const renderTableData = () => {
    const selectedData = data[selectedCategory] || [];

    return selectedData.map((item, index) => (
      <tr key={index}>
        <td>{item.track_name || item.performer || item.album}</td>
        <td>{item.rating || item.average_rating}</td>
      </tr>
    ));
  };

  return (
    <div className="stats-container">
      {/* Background Image */}
      <Sidebar />

      {/* Black Transparent Grid */}
      <div className="grid-container">
        {/* Flex container for tabs and dropdown */}
        <div className="stats-flex-container">
          {/* Tabs */}
          <div className="stats-tabs-container">
            <div
              className={`stats-tab ${selectedTab === 'last-24-hours' ? 'active' : ''}`}
              onClick={() => handleTabChange('last-24-hours')}
            >
              Last 24 Hours
            </div>
            <div
              className={`stats-tab ${selectedTab === 'last-7-days' ? 'active' : ''}`}
              onClick={() => handleTabChange('last-7-days')}
            >
              Last Week
            </div>
            <div
              className={`stats-tab ${selectedTab === 'all-time' ? 'active' : ''}`}
              onClick={() => handleTabChange('all-time')}
            >
              All Time
            </div>
            <div
              className={`stats-tab ${selectedTab === 'chart' ? 'active' : ''}`}
              onClick={() => {handleTabChange('chart'); fetchChartData();}}
            >
              Rating Chart
            </div>
          </div>

          {/* Dropdown Menu */}
          <select
            onChange={(e) => handleCategoryChange(e.target.value)}
            value={selectedCategory}
            className="select-dropdown"
          >
            <option value="songs">Songs</option>
            <option value="artists">Artists</option>
            <option value="albums">Albums</option>
          </select>
        </div>

        {/* Conditionally render dark grid for RatingChart */}
        {selectedTab === 'chart' && (
          <div className="dark-grid-container">
            <RatingChart data={ratingData} />
          </div>
        )}

        {/* Conditionally render Table of Top Items */}
        {selectedTab !== 'chart' && (
          <table className="data-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Rating</th>
              </tr>
            </thead>
            <tbody>{renderTableData()}</tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default StatsPage;
