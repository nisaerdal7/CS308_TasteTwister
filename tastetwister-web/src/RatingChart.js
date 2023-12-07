import React from 'react';

import { Chart, registerables} from 'chart.js';
import { Line } from "react-chartjs-2";


Chart.register(...registerables);

const RatingChart = ({ data }) => {
  
  const chartData = {
    labels: data.map((entry) => entry.date),
    datasets: [
      {
        label: 'Daily Average Rating',
        fill: false,
        lineTension: 0.1,
        backgroundColor: 'rgba(75,192,192,0.4)',
        borderColor: 'rgba(75,192,192,1)',
        data: data.map((entry) => entry.rating),
      },
    ],
  };

  const chartOptions = {
    scales: {
      x: {
        type: 'category',
        labels: data.map((entry) => entry.date),
        grid: {
          color: 'rgba(255, 255, 255, 0.1)', // Customize x-axis grid color
        },
        ticks: {
          color: 'rgba(255, 255, 255, 0.8)', // Customize x-axis tick color
        },
      },
      y: {
        beginAtZero: true,
        max: 5,
        grid: {
          color: 'rgba(255, 255, 255, 0.1)', // Customize y-axis grid color
        },
        ticks: {
          color: 'rgba(255, 255, 255, 0.8)', // Customize y-axis tick color
        },
      },
    },
    plugins: {
      legend: {
        labels: {
          color: 'rgba(255, 255, 255, 0.8)', // Customize legend label color
        },
      },
    },
  };
  
  

  return <Line data={chartData} options={chartOptions} />;
};

export default RatingChart;
