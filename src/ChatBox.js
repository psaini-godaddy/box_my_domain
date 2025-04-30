import React, { useState } from 'react';
import { Box, TextField, Button, Typography } from '@mui/material';

const ChatBox = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');

    const handleSendMessage = () => {
        if (input.trim() !== '') {
            setMessages([...messages, { text: input, sender: 'user' }]);
            setInput('');
        }
    };

    return (
        <Box
            style={{
                position: 'fixed',
                bottom: '20px',
                right: '20px',
                width: '480px',
                height: '550px',
                border: '1px solid #ccc',
                borderRadius: '8px',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                padding: '10px',
                backgroundColor: '#f9f9f9',
                boxShadow: '0 4px 8px rgba(0, 0, 0, 0.2)',
            }}
        >
            {/* Chat Messages */}
            <Box
                style={{
                    flex: 1,
                    overflowY: 'auto',
                    marginBottom: '10px',
                }}
            >
                {messages.map((message, index) => (
                    <Typography
                        key={index}
                        style={{
                            textAlign: message.sender === 'user' ? 'right' : 'left',
                            margin: '5px 0',
                            padding: '8px',
                            backgroundColor: message.sender === 'user' ? '#d1e7dd' : '#e9ecef',
                            borderRadius: '8px',
                            display: 'inline-block',
                        }}
                    >
                        {message.text}
                    </Typography>
                ))}
            </Box>

            {/* Input Field */}
            <Box style={{ display: 'flex', gap: '10px' }}>
                <TextField
                    variant="outlined"
                    size="small"
                    fullWidth
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Type your message..."
                />
                <Button
                    variant="contained"
                    color="primary"
                    onClick={handleSendMessage}
                >
                    Send
                </Button>
            </Box>
        </Box>
    );
};

export default ChatBox;