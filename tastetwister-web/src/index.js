import React from 'react';
import ReactDOM from 'react-dom';

import LoginForm from './Login';
import reportWebVitals from './reportWebVitals';
import Home from './Home';
import Profile from './Profile';
import RateItPage from './RateItPage';
import StatisticsPage from './StatisticsPage';
import {BrowserRouter, Route, Routes } from 'react-router-dom';
import TasteTwistPage from './TasteTwistPage';
import TasteGPTPage from './TasteGPTPage';
import FriendProfilePage from './FriendProfilePage';
ReactDOM.render(
  
  <BrowserRouter>
    <div>
    
      <Routes> 
    
        <Route exact path="/home" element={<Home />} />
        <Route exact path="/rateitpage" element={<RateItPage />} />
        <Route exact path="/" element={<LoginForm />} />
        <Route exact path="/profile" element={<Profile />} />
        <Route exact path="/tasteit" element={<TasteTwistPage />} />
        <Route exact path="/tastegpt" element={<TasteGPTPage />} />
        <Route exact path="/statistics" element={<StatisticsPage />} />
        <Route path="/friend/:friendName" element={<FriendProfilePage />} />
        </Routes>
    
    </div>
  </BrowserRouter>,
  document.getElementById('root')
);

reportWebVitals();

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals


