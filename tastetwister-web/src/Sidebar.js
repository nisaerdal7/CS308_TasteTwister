// Sidebar.js

import React from 'react';
import './Sidebar.css';

const Sidebar = () => {
  return (
    <div className="sidebar">
      <ul>
        <li>Home</li>
        <li>Dashboard</li>
        <li>Profile</li>
        {/* Add more entries as needed */}
      </ul>
    </div>
  );
}

export default Sidebar;
