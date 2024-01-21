import React, { useState } from 'react';
import './RateItPage.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import RateIt from './RateIt';
import Sidebar from './Sidebar';


function RateItPage() {
    return (
      <div className="rate-it">
        <Sidebar/>
        <h5> Rate your unrated songs!</h5>
        <RateIt/>
      </div>
    );
  }
  
export default RateItPage;