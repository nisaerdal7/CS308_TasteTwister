import React, { useState } from 'react';
import './RateItPage.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import RateIt from './RateIt';
import Sidebar from './Sidebar';


function RateItPage() {
    return (
      <div className="rate-it">
        <Sidebar/>
        <RateIt/>
      </div>
    );
  }
  
export default RateItPage;