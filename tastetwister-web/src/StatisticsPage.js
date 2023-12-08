import React from 'react';
import './StatisticsPage.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import StatsPage from './Statistics';
import Sidebar from './Sidebar';

function StatisticsPage() {
  return (
    <div className="taste-twist-page">
      <Sidebar />
      <StatsPage />
    </div>
  );
}

export default StatisticsPage;