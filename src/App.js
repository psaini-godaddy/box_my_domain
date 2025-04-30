import React, { useState } from 'react';
import { Modal, Box, Typography, Dialog, DialogTitle, DialogContent, DialogActions, CircularProgress } from '@mui/material';
import {Button, Input, Divider} from '@mui/joy';
import AddAPhotoOutlinedIcon from '@mui/icons-material/AddAPhotoOutlined';
import { useSpring, animated } from '@react-spring/web';
import axios from 'axios';
import LoadingPage from './LoadingPage';
import './App.css';
import TipsAndUpdatesTwoToneIcon from '@mui/icons-material/TipsAndUpdatesTwoTone';
import DomainListCard from './DomainListCard';
import InstagramIcon from '@mui/icons-material/Instagram';
import PinterestIcon from '@mui/icons-material/Pinterest';
import confetti from 'canvas-confetti';

let confettiInstance;

export function initConfettiCanvas() {
  const canvas = document.createElement('canvas');
  canvas.id = 'confetti-canvas';
  canvas.style.position = 'fixed';
  canvas.style.top = 0;
  canvas.style.left = 0;
  canvas.style.width = '100vw';
  canvas.style.height = '100vh';
  canvas.style.zIndex = '99999'; // super high
  canvas.style.pointerEvents = 'none';
  document.body.appendChild(canvas);

  confettiInstance = confetti.create(canvas, { resize: true, useWorker: true });
}

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
    const [loading, setLoading] = useState(false);
    const [optionClicked, setOptionClicked] = useState(0);
    const [totalQuestions, setTotalQuestions] = useState(5);
    const [imageData, setImageData] = useState(null);
    const [showDomainTestPopup, setShowDomainTestPopup] = useState(false);
    const [image, setImage] = useState(true);
    const [userInput, setUserInput] = useState(false);
    const [isLast, setIsLast] = useState(false);
    const [imageRaw, setImageRaw] = useState(null);
    const [imageFlag, setImageFlag] = useState(false);
    const [price, setPrice] = useState(null);
    const [openConfirm, setOpenConfirm] = useState(false);
    const [keyword, setKeyword] = useState('');

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
    setOpenConfirm(true);
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
              <Box style={{display: 'flex', gap: '40px'}}>
                  <button
                      className="button price-button"
                      onClick={() => handlePriceSelect(15)}
                      style={priceButtonStyle}
                      style={{
                          fontSize: '30px',
                          marginTop: '10px',
                          borderRadius: '12px'
                      }}
                  >
                      $15
                  </button>

                  <button
                      className="button price-button"
                      onClick={() => handlePriceSelect(25)}
                      style={priceButtonStyle}
                      style={{
                          fontSize: '30px',
                          marginTop: '10px',
                          borderRadius: '12px'
                      }}
                  >
                      $25
                  </button>

                  <button
                      className="button price-button"
                      onClick={() => handlePriceSelect(35)}
                      style={priceButtonStyle}
                      style={{
                          fontSize: '30px',
                          marginTop: '10px',
                          borderRadius: '12px'
                      }}
                  >
                      $35
                  </button>
              </Box>
          </Box>

      </Box>
    <Dialog className="dialog" open={openConfirm} onClose={handleCancel}>
        <DialogTitle>Confirm Payment</DialogTitle>
        <DialogContent>
            <Typography>Unlock your surprise for ${price} + domain registration (1 year).</Typography>
        </DialogContent>
        <DialogActions>
            <Button onClick={handleCancel} color="secondary">Cancel</Button>
            <Button onClick={handleConfirm} color="primary">Confirm</Button>
        </DialogActions>
    </Dialog>
    </div>
  );
};

// Styling for the Price Buttons
    const priceButtonStyle = {
        background: 'black',
        color: 'white',
        border: 'none',
        borderRadius: '10px',
        padding: '10px 20px',
        fontSize: '18px',
        cursor: 'pointer',
        transition: 'transform 0.2s ease, background 0.3s ease',
    };

    const surpriseButtonStyle = {
        backgroundColor: '#20c997',
        color: 'white',
        border: 'none',
        borderRadius: '10px',
        fontSize: '18px',
        // padding: '12px 30px',
        cursor: 'pointer',
        transition: 'transform 0.3s ease, background-color 0.3s ease',
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

const QuestionCard = ({ question, options, handleOptionClick, progress}) => (
    <Box className='modal question-card'>
      <Box className='progress-bar-container'>
        <CircularProgress
            variant="determinate"
            value={progress}
            size={150}
            thickness={3}
            sx={{
              strokeColor: 'gray',
              color: '#01a4a6', // Set the custom color here
            }}
            style={{ margin: '0 auto', display: 'block' }}
        />
        <Typography
            variant="caption"
            component="div"
            color="textSecondary"
            style={{
              position: 'absolute',
              top: '125px',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              fontSize: '30px',
            }}
        >
          {`${Math.round(progress)}%`}
        </Typography>
      </Box>
      <Box className='question-title-container'>
        <Box className='question-title'>
          {question}</Box>
      </Box>
      <Box className='grid-container'>
        {options.map((option, index) => (
            <Box key={index} className='option-button' onClick={() => handleOptionClick(option)}>
              {option}
            </Box>
        ))}
      </Box>
    </Box>
);

// const DomainTestCard = ({handleQuestion, handleClose}) => (
//     <Box className='modal'>
//       <Box className='question-title'>
//         <p>Do you want to take a quick domainality test?</p>
//       </Box>
//       <Box className='footer'>
//         <button className='button' onClick={handleQuestion}>Start Test</button>
//         <button className='button' onClick={handleClose}>Next Time</button>
//       </Box>
//     </Box>
// );

const handleConfirm = () => {
    console.log('Payment confirmed!');
    console.log(`Price selected: $${price}`);
    launchFireworks();
    setOpenConfirm(false);
    handleSendMessage(price, keyword);

};
const handleCancel = () => {
    setOpenConfirm(false);
    setImage(false); // Hide the PriceSelectionCard
};

  const questionCardAnimation = useSpring({
    opacity: loading,
    transform: loading ? 'translateY(-20px)' : 'translateY(0)',
    config: { duration: 500 },
  });
  const [userOption, setUserOption] = useState(null);

  const handleOpen = async () => {
    document.querySelector('#mysteryBox img').src = '/gold_box_after.png';
    setTimeout(() => {
      setOpen(true);
    }, 900);

  };

  const handleClose = () => {
    setOpen(false);
    window.location.reload();
    const response = axios.post('http://localhost:5000/reset', {
    }, { withCredentials: true });
  };
  const handleSendMessage = async (price, keyword) => {
    setLoading(true);
    try {
        const response = await axios.get('http://localhost:8001/domain_draw', {
          params: {
            price,
            search_query: keyword
          }
        }, { withCredentials: true });

       // const response = { data: { content: { chat: "Dummy question?", options: ["Option 1", "Option 2"], recommended_domains: null }, isLast: false } };
        //print response
        console.log('Raw Response:', response);
        const data = response.data.result.map(item => item.domain);
        setData(data);
        console.log('Response:', data);
    } catch (error) {
      console.error('Error sending message:', error);
    }
    setLoading(false);
    setImage(false);
  };

  const fetchQuestion = async (selectedOption) => {
    setLoading(true);
    if (imageFlag) {
      setTotalQuestions(2);
      console.log('Fetching question with image...', selectedOption);
      const formData = new FormData();
      formData.append('image', imageRaw);
      const response = await fetch(`http://localhost:5001/image?message=${encodeURIComponent(selectedOption)}`, {
        method: 'POST',
        body: formData, // FormData automatically sets the correct headers
        credentials: 'include',
      });
      const data = await response.json();
      console.log('Raw Response:', data);
      if (data.content.options && typeof data.content.options === 'object') {
        console.log('Options:', data.content.options);
        data.content.options = Object.entries(data.content.options).map(([key, value]) => `${value}`);
      }
      setData(data.content);
      setLoading(false);
      return;
    }
    if (isLast) {
      setUserInput(true);
      return;
    }
    console.log('Fetching question...', selectedOption);
    try {
      const response = await axios.post('http://localhost:5000/chat', {
        message: selectedOption // Send the selected option as a JSON object
      },{ withCredentials: true });

      // Process options if they are an object
      const data = response.data;
      console.log('Raw Response:', data);
      if (data.content.options && typeof data.content.options === 'object') {
        console.log('Options:', data.content.options);
        data.content.options = Object.entries(data.content.options).map(([key, value]) => `${value}`);
      }
      setData(data.content); // Update the state with the processed data
      console.log('Processed Response:', data);
    } catch (error) {
      console.error('Error fetching question:', error);
    }
    setLoading(false);
  };

  const progress = (optionClicked / totalQuestions) * 100;

  const handleDrop = (event) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    const reader = new FileReader();
    setImageRaw(file);
    reader.onload = (e) => {
      setImageData(e.target.result); // Base64 encoded image data
    };
    reader.readAsDataURL(file);
  };

  const handleImageSubmit = async () => {
    setLoading(true);
    setImage(false);
    if (imageRaw) {
      // Create a FormData object to hold the image data
      const formData = new FormData();
      formData.append('image', imageRaw); // 'image' is the key expected by the Flask backend
      console.log(imageRaw instanceof File);
      try {
        // Send the image data to the Flask backend
        const response = await fetch('http://localhost:5001/image', {
          method: 'POST',
          body: formData, // FormData automatically sets the correct headers
          credentials: 'include',
        });


        if (!response.ok) {
          console.error('Failed to send image data');
          console.log(await response.json()); // Log the backend response for debugging
          return;
        }
        const data = await response.json();
        console.log(data);
        if (data.content.options && typeof data.content.options === 'object') {
          console.log('Options:', data.content.options);
          data.content.options = Object.entries(data.content.options).map(([key, value]) => `${value}`);
        }
        console.log(data.content);
        setData(data.content);
        setImageFlag(true);
        setLoading(false);
        console.log(data)
        console.log('Image successfully sent');
      } catch (error) {
        console.error('Error sending image data:', error);
      }
    }
  };

  const handleOptionClick = async (option) => {
    setUserOption(option);
    setOptionClicked((prev) => prev + 1);
    if (option !== null && option !== undefined) {
      console.log(`Option selected: ${option}`);
      await fetchQuestion(option); // Proceed to the next step only if option is valid
    } else {
      console.log(`Option selected: ${option}`);
      await fetchQuestion();
    }
  };

  const handleQuestion = async () => {
    setImage(false);
    setShowDomainTestPopup(false);
    await fetchQuestion('start');
    // setUserInput(true);
  };



  return (
      <div style={{textAlign: 'center', marginTop: '50px'}}>
          <div id="mysteryBox" className="mysteryBox">
              <img src="/white_box.png" alt="White Box" className="background-box"/>
              <img src="/gold_box_8.png" alt="Mystery Box" className="foreground-box" onClick={handleOpen}/>
          </div>

          <Modal open={open} onClose={handleClose} className='modal-container'>
              {image ? (
                  <PriceSelectionCard handlePriceSelect={handlePriceSelect}/>
              ) : loading ? (
                  <LoadingPage/>
              ) : data ? (
                  <DomainListCard domains={data}/>
              ) : (
                  <Typography>Loading...</Typography>
              )}
          </Modal>
      </div>
  );
};

export default App;