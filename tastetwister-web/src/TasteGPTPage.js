import React from 'react';
import './TasteGPTPage.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import TasteGPT from './TasteGPT';
import Sidebar from './Sidebar';

function TasteGPTPage() { 
  return (
    <div className="taste-gpt-page">
      <Sidebar />
      <h5> Generate specific recommendations with your preferred genre or era with GPT!</h5>
      <TasteGPT />
    </div>
  );
}

export default TasteGPTPage;