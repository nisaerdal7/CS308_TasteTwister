import React from 'react';
import ReactDOM from 'react-dom';

import LoginForm from './Login';
import reportWebVitals from './reportWebVitals';
import Home from './Home';
import {BrowserRouter, Route, Routes } from 'react-router-dom';
import{UserProvider} from './UserContext'
ReactDOM.render(
  
  <BrowserRouter>
    <div>
    <UserProvider>
      <Routes> 
    
        <Route exact path="/home" element={<Home />} />
        <Route exact path="/" element={<LoginForm />} />
      
        </Routes>
    </UserProvider>
    </div>
  </BrowserRouter>,
  document.getElementById('root')
);

reportWebVitals();

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals


