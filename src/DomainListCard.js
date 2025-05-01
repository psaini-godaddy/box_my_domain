import React from 'react';
import {Box, Button, Typography} from '@mui/material';

const DomainListCard = ({ domains = [] , confirmDomain}) => {
  return (
      <Box className="modal list-modal">
          <Box style={{display: 'flex', marginTop: '-30px'}}>
              <Typography variant="h3" align="center">
                  Congratulations 🎉 <br/>
                  <Typography variant="h4" align="center">
                      Enjoy your new domain and make the most of it 🚀
                  </Typography>
              </Typography>

          </Box>
          {domains.map((domain, index) => (
              <Typography variant="h6" style={{fontSize: '70px', fontWeight: '600'}}>
                  {domain}
              </Typography>
          ))}
          <Box style={{display: 'column', marginTop: '100px'}}>
              <Button
                  variant="contained"
                  sx={{ backgroundColor: 'teal', textTransform: 'none', px: 3 , fontSize:'30px', marginRight: '300px'}}
                  onClick={confirmDomain}
              >
                  Love It!
              </Button>
              <Button
                  variant="contained"
                  sx={{ backgroundColor: 'teal', textTransform: 'none', px: 3 , fontSize:'30px'}}
              >
                  Play Again!
              </Button>
          </Box>

      </Box>
  );
};

export default DomainListCard;