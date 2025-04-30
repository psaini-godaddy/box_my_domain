import React from 'react';
import { Box, Typography } from '@mui/material';

const DomainListCard = ({ domains = [] }) => {
  return (
      <Box className="modal list-modal">
        <Box className="list-card">
          <Box style={{ display: 'flex', justifyContent: 'center', margin: '40px 0px' }}>
            <Typography variant="h4">
              🎈 Big reveal! These domains are all about you!
            </Typography>
          </Box>
          {domains.map((domain, index) => (
              <Box
                  key={index}
                  className="list-item"
                  style={{
                    padding: '15px',
                    border: '1px solid #ccc',
                    borderRadius: '8px',
                    marginBottom: '20px',
                  }}
              >
                <Typography variant="h6" style={{ fontSize: '20px' }}>
                  {domain}
                </Typography>
              </Box>
          ))}
        </Box>
      </Box>
  );
};

export default DomainListCard;