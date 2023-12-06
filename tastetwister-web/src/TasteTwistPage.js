import React from 'react';
import './TasteTwistPage.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import TasteTwist from './TasteTwist';
import Sidebar from './Sidebar';

function TasteTwistPage() {
  return (
    <div className="taste-twist-page">
      <Sidebar />
      <TasteTwist />
    </div>
  );
}

export default TasteTwistPage;

