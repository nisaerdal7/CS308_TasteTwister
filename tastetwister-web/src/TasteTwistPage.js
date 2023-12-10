import React from 'react';
import './TasteTwistPage.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import TasteTwist from './TasteTwist';
import Sidebar from './Sidebar';

function TasteTwistPage() {
  return (
    <div className="taste-twist-page">
      <Sidebar />
      <h5> Twist tastes to create a song list!</h5>
      <TasteTwist />
    </div>
  );
}

export default TasteTwistPage;

