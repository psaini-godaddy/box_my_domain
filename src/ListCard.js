import React, { useEffect, useRef, useState } from 'react';
import { Box, Typography } from '@mui/material';
import Chart from 'chart.js/auto';
import AddShoppingCartIcon from '@mui/icons-material/AddShoppingCart';
import './App.css';
const ListCard = ({ guesses = {} }) => {
  const chartRefs = useRef({});
  const [expandedCard, setExpandedCard] = useState(0); // Store index of expanded card

  const guessesArray = Object.entries(guesses).map(([domain, details]) => ({
    domain,
    ...details,
  }));

  useEffect(() => {
    guessesArray.forEach((item, index) => {
      if (expandedCard === index) { // Only render chart for the expanded card
        const canvasId = `radar-chart-${index}`;
        const ctx = document.getElementById(canvasId)?.getContext('2d');
        if (!ctx) return;

        if (chartRefs.current[canvasId]) {
          chartRefs.current[canvasId].destroy();
        }
        chartRefs.current[canvasId] = new Chart(ctx, {
          type: 'radar',
          data: {
            labels: Object.keys(item.score),
            datasets: [
              {
                label: item.domain,
                data: Object.values(item.score),
                backgroundColor: 'rgba(54, 162, 235, 0.4)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1,
              },
            ],
          },
          options: {
            maintainAspectRatio: false,
            responsive: true,
            plugins: {
              legend: { display: false },
            },
            scales: {
              r: {
                pointLabels: {
                  font: { size: 12, weight: 'bold' },
                  padding: 3,
                },
                ticks: { beginAtZero: true, display: false},
                grid: { lineWidth: 2 },
              },
            },
          },
        });
      }
    });

    return () => {
      Object.values(chartRefs.current).forEach((chart) => chart.destroy());
    };
  }, [guessesArray, expandedCard]);

  const toggleCardVisibility = (index) => {
    setExpandedCard((prevIndex) => (prevIndex === index ? null : index)); // Expand or collapse the clicked card
  };

  if (guessesArray.length === 0) {
    return (
      <Box className="list-card">
        <Typography variant="h6">No guesses available</Typography>
      </Box>
    );
  }

  return (
    <Box className="modal list-modal">
      <Box className="list-card">
        <Box style={{ display: 'flex', justifyContent: 'center', margin: '40px 0px' }}>
          <Typography variant="h4">
          <p>🎈 Big reveal! These domains are all about you!</p>
          </Typography>
        </Box>
        {guessesArray.map((item, index) => (
          <Box
            key={index}
            className="list-item"
            onClick={() => toggleCardVisibility(index)} // Make the entire card clickable
            style={{
              cursor: 'pointer', // Indicate clickability
              padding: '15px',
              border: '1px solid #ccc',
              borderRadius: '8px',
              marginBottom: '20px',
              overflow: 'hidden', // Ensure content doesn't overflow during animation
              transition: 'max-height 0.3s ease-in-out', // Smooth expansion/collapse
              maxHeight: expandedCard === index ? '500px' : '60px', // Adjust max height dynamically
            }}
          >
            {/* Domain and Price */}
            <Box
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
            >
              <Typography variant="h6" style={{ marginLeft: '20px', fontSize: '25px' }}>
                <strong>{item.domain}</strong>
              </Typography>
              <Box
                style={{
                  display: 'flex',
                  alignItems: 'center',
                }}
              >
                <Typography
                  variant="body1"
                  style={{
                    fontSize: '20px',
                    marginRight: `${Math.max(10 - item.price.toString().length, 0) * 8}px`, // Adjust spacing dynamically
                  }}
                >
                  <strong>Price: ${(Math.round(item.price * 100) / 100).toFixed(2)}</strong>
                </Typography>
                <AddShoppingCartIcon fontSize="large" />
              </Box>
            </Box>

            {/* Card Content */}
            <Box
              style={{
                marginTop: '15px',
                visibility: expandedCard === index ? 'visible' : 'hidden', // Prevent content flicker
              }}
            >
              <Box>
                {/* Radar Graph */}
                <canvas
                  id={`radar-chart-${index}`}
                  width="600"
                  height="600"
                  style={{
                    width: '600px',
                    height: '300px',
                    margin: '0 auto',
                  }}
                ></canvas>
              </Box>
            </Box>
          </Box>
        ))}
      </Box>
    </Box>
  );
};

export default ListCard;
