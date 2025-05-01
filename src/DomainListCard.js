import React from 'react';
import {Box, Button, Typography} from '@mui/material';

const DomainListCard = ({ domains = [] , confirmDomain, onRetry, price, result, fadeOut}) => {
  return (
      <Box
          className="modal list-modal"
          sx={{
              width: fadeOut ? '700px' : '900px',
              height: fadeOut ? '550px' : '600px',
              transform: fadeOut ? 'translate(-420px, 4px)' : 'translate(0, 0)',
              transition: 'width 0.4s ease',
          }}
      >
          <Box style={{display: 'flex'}}>
              <Typography variant="h3" align="center">
                  Congratulations 🎉 <br/>
                  <Typography variant="h4" align="center">
                      Enjoy your new domain and make the most of it 🚀
                  </Typography>
              </Typography>

          </Box>
          {domains.map((domain, index) => (
              <Typography variant="h6" style={{fontSize: '70px', fontWeight: '600', padding: '50px'}}>
                  {domain}
              </Typography>
          ))}
          <Box style={{display: 'column'}}>
              <Button
                  variant="contained"
                  sx={{ backgroundColor: 'teal', textTransform: 'none', px: 3 , fontSize:'30px', marginRight: '100px'}}
                  onClick={confirmDomain}
              >
                  Love It!
              </Button>
              <Button
                  variant="contained"
                  sx={{ backgroundColor: 'teal', textTransform: 'none', px: 3 , fontSize:'30px'}}
                  onClick={() => onRetry(price,'',result.session_id)}
                  disabled={result.remaining_rolls <= 0}
              >Play Again! ({result.remaining_rolls} Reties Left)
              </Button>
          </Box>

      </Box>
  );
};

export default DomainListCard;