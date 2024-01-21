import React from 'react';
import './StatisticsPage.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import StatsPage from './Statistics';
import Sidebar from './Sidebar';

function StatisticsPage() {
  return (
    <div className="taste-twist-page">
      <Sidebar />
      <h5 >Your statistics!</h5>
      <StatsPage />
    </div>
  );
}

export default StatisticsPage;