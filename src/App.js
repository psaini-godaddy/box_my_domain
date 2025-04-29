import React, { useState } from 'react';
import { Modal, Box, Typography, CircularProgress } from '@mui/material';
import {Button, Input, Divider} from '@mui/joy';
import AddAPhotoOutlinedIcon from '@mui/icons-material/AddAPhotoOutlined';
import { useSpring, animated } from '@react-spring/web';
import axios from 'axios';
import LoadingPage from './LoadingPage';
import './App.css';
import TipsAndUpdatesTwoToneIcon from '@mui/icons-material/TipsAndUpdatesTwoTone';
import ListCard from './ListCard';
import InstagramIcon from '@mui/icons-material/Instagram';
import PinterestIcon from '@mui/icons-material/Pinterest';

const ImageUploadCard = ({ imageData, handleDrop, handleImageSubmit, handleQuestion }) => (
  <Box className="modal">
    <Box className="image-title">
      <h3>Upload Your Image</h3>
      <p>Please upload an image or skip this step</p>
    </Box>
    <Box
      className="drag-drop-area"
      onDragOver={(e) => e.preventDefault()}
      onDrop={handleDrop}
    >
      {imageData ? (
        <img src={imageData} alt="Preview" className='uploaded-image' />
      ) : (
        <p style={{ fontSize: '30px'}}>
        <AddAPhotoOutlinedIcon style={{ fontSize: '40px', }}/> Drag and drop an image here, or click to upload
        </p>
      )}
    </Box>
    <Divider orientation="horizontal">OR </Divider>
    <Box className='image-text'>
      <Input placeholder="Paste your image link" variant="soft" size="lg" style ={{ height: '50px', marginTop: '20px'}}>
      </Input>
      <Box style={{marginTop:'20px', textAlign:'right'}}>
      <button className='hidden'><InstagramIcon style={{ fontSize: '40px', color: '#000'}}/></button>
      <button className='hidden'><PinterestIcon style={{ fontSize: '40px', color: '#000'}}/></button>
      </Box>
      </Box>
    <Box className='footer'>
      <button className='button image-button' style={{ float: "right" }} onClick={handleQuestion}>
        Skip
      </button>
      <button className='button image-button' style={{ float: "right" }} onClick={handleImageSubmit}>
        Next
      </button>
    </Box>
  </Box>
);

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

const DomainTestCard = ({handleQuestion, handleClose}) => (
  <Box className='modal'>
    <Box className='question-title'>
      <p>Do you want to take a quick domainality test?</p>
    </Box>
    <Box className='footer'>
      <button className='button' onClick={handleQuestion}>Start Test</button>
      <button className='button' onClick={handleClose}>Next Time</button>
    </Box>
  </Box>
);

  const UserInput = ({ handleSend }) => {
  const [message, setMessage] = useState('');

  const handleInputChange = (event) => {
    setMessage(event.target.value);
  };

  const handleSendClick = () => {
    handleSend(message);
    setMessage('');
  };

  return (
    <Box className='modal'>
      <Box className='text-title'>
      <img src="/pic.png" className="info-icon" />
      </Box>
      <Box className='input-container'>
        <input
          type='text'
          value={message}
          onChange={handleInputChange}
          placeholder=' Spill the tea—why are you here?'
          className='text-input'/>
        <div>
        <button
          className="button text-button"
          onClick={handleSendClick}
        >
          Send
        </button>
      </div>
      </Box>
      <Box className='footer'>
      
      </Box>
    </Box>
  );
};

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
  const questionCardAnimation = useSpring({
    opacity: loading,
    transform: loading ? 'translateY(-20px)' : 'translateY(0)',
    config: { duration: 500 },
  });
  const [userOption, setUserOption] = useState(null);

  const handleOpen = async () => {
    document.querySelector('#merrywrap img').src = '/gold_box_after.webp';
    setTimeout(() => {
      setOpen(true);
    }, 300);

  };

  const handleClose = () => {
    setOpen(false);
    window.location.reload();
    const response = axios.post('http://localhost:5000/reset', {
    }, { withCredentials: true });
  };
  const handleSendMessage = async (text) => {
    setUserInput(false);
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:5000/chat', {
        message: userOption,
        textInput: text
      }, { withCredentials: true });

      const data = response.data;
      if (data.content.options && typeof data.content.options === 'object') {
        console.log('Options:', data.content.options);
        data.content.options = Object.entries(data.content.options).map(([key, value]) => `${value}`);
      }
      setData(data.content);
      console.log('Response:', data);
    } catch (error) {
      console.error('Error sending message:', error);
    }
    setLoading(false);
    setIsLast(false);
    setUserInput(false);
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
      setIsLast(data.isLast);
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
        <div id="merrywrap" className="merrywrap">
          <img src="/gold_box_before.webp" alt="Gold Box Before" onClick={handleOpen}/>
        </div>

        <Modal open={open} onClose={handleClose} className='modal-container'>
                  {image ? (
                      <ImageUploadCard imageData={imageData} handleDrop={handleDrop}
                                       handleImageSubmit={handleImageSubmit} handleQuestion={handleQuestion}/>
                  ) : userInput ? (
                          <UserInput handleSend={handleSendMessage}/>
                      )
                      : loading ? (
                          <LoadingPage/>
                      ) : data ? (
                          data.recommended_domains ? (
                              <ListCard guesses={data.recommended_domains}/>
                          ) : (
                              <animated.div style={questionCardAnimation}>
                                  <QuestionCard
                                      question={data.chat}
                                      options={data.options}
                                      handleOptionClick={handleOptionClick}
                                      progress={progress}
                                  />
                              </animated.div>
                          )
                      ) : showDomainTestPopup ? (
                          <DomainTestCard handleClose={handleClose} handleQuestion={handleQuestion}/>
                      ) : (
                          <Typography>Loading...</Typography>
                      )}
              </Modal>
          </div>
          );
          };

          export default App;
