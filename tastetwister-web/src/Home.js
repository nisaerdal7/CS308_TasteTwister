import React, { useState } from 'react';
import './Home.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import SongList from './SongList';
import Sidebar from './Sidebar';


function Home() {
    return (
      <div className="home-container">
        <Sidebar/>
        <h1>Welcome to TasteTwister</h1>
        <p>This is our home page.</p>
        <SongList/>
      </div>
    );
  }
  
export default Home;