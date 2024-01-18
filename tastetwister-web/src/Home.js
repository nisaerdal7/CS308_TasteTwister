import React, { useState } from 'react';
import './Home.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import SongList from './SongList';
import Sidebar from './Sidebar';
import Notification from './Notification';


function Home() {
    return (
      <div className="home-container">
        <Sidebar/>
        <h3>Welcome to TasteTwister!</h3>
        <SongList/>
       <div className="home-notification-container">
       <Notification/>
        </div> 
      </div>
    );
  }
  
export default Home;