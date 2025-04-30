import React from 'react';
import { Box, Typography } from '@mui/material';

const DomainListCard = ({ domains = [] }) => {
  return (
      <Box className="modal list-modal">
        <Box className="list-card">
          <Box style={{ display: 'flex', justifyContent: 'center', margin: '40px 0px' }}>
            <Typography variant="h3">
              🎈 Big reveal! These domains are all about you!
            </Typography>
          </Box>
          {domains.map((domain, index) => (
              <Typography variant="h6" style={{ fontSize: '30px' }}>
                  {domain}
              </Typography>
          ))}
        </Box>
      </Box>
  );
};

export default DomainListCard;