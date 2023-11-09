import React, { useState } from 'react';
import './Home.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import { useUser } from './UserContext';
import SongList from './SongList';


function Home() {
  const { user } = useUser();
  console.log(user);
  const username = user;
    return (
      <div className="home-container">
        <h1>Welcome to TasteTwister</h1>
        <p>This is our home page.</p>
        <SongList user={username}/>
      </div>
    );
  }
  
export default Home;