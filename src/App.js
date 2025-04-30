import React, { useState } from 'react';
import { Modal, Box, Typography, Dialog, DialogTitle, DialogContent, DialogActions } from '@mui/material';
import {Button} from '@mui/joy';
import axios from 'axios';
import './App.css';
import DomainListCard from './DomainListCard';
import confetti from 'canvas-confetti';
import ChatBox  from "./ChatBox";

function launchFireworks() {

  const duration = 2 * 1000;
  const animationEnd = Date.now() + duration;
  const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 99999 };

  const interval = setInterval(() => {
    const timeLeft = animationEnd - Date.now();

    if (timeLeft <= 0) {
      clearInterval(interval);
      return;
    }

    const particleCount = 50 * (timeLeft / duration);

    // Launch from random spots
    confetti({
      ...defaults,
      particleCount,
      origin: {
        x: Math.random(),
        y: Math.random() * 0.6
      }
    });
  }, 250);
}
const App = () => {
    const [open, setOpen] = useState(false);
    const [data, setData] = useState(null);
    const [image, setImage] = useState(true);
    const [price, setPrice] = useState(null);
    const [openConfirm, setOpenConfirm] = useState(false);
    const [keyword, setKeyword] = useState('');
    const [changeImage, setChangeImage] = useState(false);
    const [showDomainCard, setShowDomainCard] = useState(true);
    const [showChatBox, setShowChatBox] = useState(false);
    const [fadeOut, setFadeOut] = useState(false);

    // useEffect(() => {
    //     if (showChatBox) {
    //         // Reset default values
    //         setOpen(false);
    //         setImage(true);
    //         setPrice(null);
    //         setOpenConfirm(false);
    //         setKeyword('');
    //         setChangeImage(false);
    //         setShowDomainCard(false);
    //         setFadeOut(false);
    //     }
    // }, [showChatBox]);

const canvas = document.querySelector('canvas');
if (canvas) {
  canvas.style.zIndex = '9999';
  canvas.style.pointerEvents = 'none';
}

const handlePriceSelect = (selectedPrice) => {
    setPrice(selectedPrice); // Set the selected price
    const keywordInput = document.getElementById('textbox');
    if (keywordInput) {
      const inputValue = keywordInput.value;
      setKeyword(inputValue);
      console.log('Selected price:', selectedPrice);
      console.log('Keyword:', inputValue);
    }
    setImage(false); setOpenConfirm(true);
};

const PriceSelectionCard = ({ handleQuestion }) =>{
  // ✅ Dummy handler for now
  return (
      <div>
      <Box
          style={{
            width: '700px',
            height: '700px',
            borderRadius: '15px',
            overflow: 'hidden',
            margin: 'auto',
            marginTop: '100px',
            animation: 'fadeIn 1s ease' // smooth entry animation
          }}
      >
        {/* Top Half - Teal Gradient Background */}
        <Box
            style={{
              background: 'linear-gradient(135deg, #008080, #20c997)',
              height: '30%',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              alignItems: 'center',
              color: 'white',
              padding: '20px',
            }}
        >
          <h3 style={{ fontSize: '38px', fontWeight: '600', marginTop: '50px', justifyContent: 'center' }}> Pick a price to unlock your prize!
          </h3>
          <p style={{ fontSize: '22px', marginTop: '0px' }}>
              Your Mystery Domain Box Awaits 🌟
          </p>
        </Box>

        {/* Bottom Half - White */}
          <Box
              style={{
                  backgroundColor: 'white',
                  height: '30%',
                  padding: '20px',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  borderBottomLeftRadius: '15px',
                  borderBottomRightRadius: '15px',
                  gap: '20px',
                  fontSize: '100px'
              }}
          >
              <input
                  id="textbox"
                  type="text"
                 // value={keyword}
                 // onChange={(e) => setKeyword(e.target.value)}
                  placeholder="What’s your vibe?  e.g. pizza, coffee ☕️"
                  style={{
                      width: '60%',
                      padding: '12px 20px',
                      borderRadius: '12px',
                      border: '1px solid #ccc',
                      fontSize: '16px',
                      backgroundColor: 'white',
                      color: '#333',
                      textAlign: 'center'
                  }}
              />
              {/* Price Buttons */}
              <Box style={{ display: 'flex', gap: '40px' }}>
                  {[15,25,35].map(price => (
                      <button
                          className="button price-button"
                          onClick={() => handlePriceSelect(price)}
                          style={priceButtonStyle}
                      >
                          ${price}
                      </button>
                  ))}
              </Box>
          </Box>

      </Box>
    </div>
  );
};

const ConfirmWindow = () => (
    <Dialog className="dialog" open={openConfirm} onClose={handleCancel}>
        <DialogTitle>Confirm Payment</DialogTitle>
        <DialogContent>
            <Typography>Unlock your surprise for ${price} + standard domain registration fee (1 year).</Typography>
        </DialogContent>
        <DialogActions>
            <Button onClick={handleCancel} color="secondary">Cancel</Button>
            <Button onClick={handleConfirm} color="primary">Confirm</Button>
        </DialogActions>
    </Dialog>
);

// Styling for the Price Buttons
    const priceButtonStyle = {
        background: 'black',
        color: 'white',
        border: 'none',
        padding: '10px 20px',
        cursor: 'pointer',
        transition: 'transform 0.2s ease, background 0.3s ease',
        fontSize: '30px',
        marginTop: '10px',
        borderRadius: '12px'
    };

// Add this CSS into your global styles or inside your file (CSS-in-JS)
const styleSheet = document.createElement("style");
styleSheet.innerText = `
  .button.price-button:hover {
    transform: scale(1.1);
    background: #333;
  }
  
  .button.image-button:hover {
    background-color: #17a2b8;
    transform: scale(1.05);
  }

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
  }
`;
document.head.appendChild(styleSheet);

    const handleConfirm = () => {
        console.log('Payment confirmed!');
        console.log(`Price selected: $${price}`);
        setOpenConfirm(false);
        handleSendMessage(price, keyword);
        setImage(false); // Hide the PriceSelectionCard
    };
    const handleCancel = () => {
        setOpenConfirm(false);
        setImage(true);
    };

  const handleOpen = async () => {
      setChangeImage(true)
    setTimeout(() => {
      setOpen(true);
    }, 900);
  };

  const handleClose = () => {
    setOpen(false);
      setChangeImage(false)
  };
    const handleSendMessage = async (price, keyword) => {
        try {
            const response = await axios.get('http://localhost:8001/domain_draw', {
                params: { price, search_query: keyword }
            }, { withCredentials: true });

            const data = response.data.result.map(item => item.domain);
            setData(data);

            // Start fade-out after short delay
            setTimeout(() => {
                setFadeOut(true);
                setTimeout(() => {
                    setShowDomainCard(false);
                    setShowChatBox(true);
                }, 3000); // Wait for fade animation to complete
            }, 3000); // Show domain card for 3 seconds before fading out
        } catch (error) {
            console.error('Error sending message:', error);
        }
    };

  return (
      <div style={{textAlign: 'center', marginTop: '50px'}}>
          <div id="mysteryBox" className="mysteryBox">
              <img src="/white_box.png" alt="White Box" className="background-box"/>
              <img
                  src={changeImage ? "/gold_box_after.png" : "/gold_box_8.png"}
                  alt="Mystery Box"
                  className={`foreground-box ${changeImage ? "no-wobble" : ""}`}
                  onClick={handleOpen}
              />
          </div>

          <Modal open={open} onClose={handleClose} className='modal-container'>
              {image ? (
                  <PriceSelectionCard handlePriceSelect={handlePriceSelect}/>
              ) : openConfirm ? (
                  <ConfirmWindow/>
              ) : data ? (
                  <>
                      {showDomainCard && (
                          <div className={`fade-wrapper ${fadeOut ? 'fade-out' : ''}`}>
                              <DomainListCard domains={data}/>
                              {launchFireworks()}
                          </div>
                      )}
                      {showChatBox && (
                          <ChatBox domains={data}/>
                      )}
                  </>
              ) : (
                  <Typography>Loading...</Typography>
              )}
          </Modal>
      </div>
  );
};

export default App;