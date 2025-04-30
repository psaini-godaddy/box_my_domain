import React from 'react';
import { Box, Typography } from '@mui/material';

const DomainListCard = ({ domains = [] }) => {
  return (
      <Box className="modal list-modal">
          <Box style={{ display: 'flex', marginTop: '-30px' }}>
              <Typography variant="h3" align="center">
                  Congratulations 🎉 <br/>
                  <Typography variant="h4" align="center">
                      Enjoy your new domain and make the most of it 🚀
                  </Typography>
              </Typography>

          </Box>
          {domains.map((domain, index) => (
              <Typography variant="h6" style={{ fontSize: '70px' , fontWeight: '600' }}>
                  {domain}
              </Typography>
          ))}
      </Box>
  );
};

export default DomainListCard;