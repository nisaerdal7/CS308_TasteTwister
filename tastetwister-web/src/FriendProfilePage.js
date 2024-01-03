// FriendProfilePage.js
import React from 'react';
import './FriendProfilePage.css';
import Sidebar from './Sidebar';
import FriendProfile from './FriendProfile';
import { useParams } from 'react-router-dom';

const FriendProfilePage = () => {
  const { friendName } = useParams();

  return (
    <div className="friend-page">
    <Sidebar />
      <h2>{`Profile Page for ${friendName || 'Unknown Friend'}`}</h2>
      {/* Add your customized content based on the friend's name */}
      <FriendProfile username={friendName}/>
    </div>
  );
};

export default FriendProfilePage;


