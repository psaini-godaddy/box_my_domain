import React, { useState, useEffect, useRef } from 'react';
import { Box, TextField, Button, Typography } from '@mui/material';

const ChatBox = ( { domains = [] }) => {
    const [messages, setMessages] = useState([
        {
            text: `🎉 You just unlocked ${domains.join(', ')}! Wondering how valuable it is? ` +
                "Looking to drive traffic or turn it into profit? " +
                "Just say the word — I'm here to help!",
            sender: 'bot',
        }
    ]);
    const [input, setInput] = useState('');
    const chatEndRef = useRef(null);

    const handleSendMessage = () => {
        if (input.trim() !== '') {
            setMessages(prev => [
                ...prev,
                { text: input, sender: 'user' },
                { text: "Got it! Let me look that up for you... 🔍", sender: 'bot' }
            ]);
            setInput('');
        }
    };

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    return (
        <Box
            sx={{
                position: 'fixed',
                bottom: 20,
                right: 20,
                width: 600,
                height: 500,
                borderRadius: 2,
                boxShadow: 3,
                backgroundColor: '#fff',
                border: '1px solid black',
                display: 'flex',
                flexDirection: 'column',
                zIndex: 1000
            }}
        >
            {/* Header */}
            <Box sx={{ p: 2, backgroundColor: 'teal', color: '#fff', borderTopLeftRadius: 8, borderTopRightRadius: 8 }}>
                <Typography variant="h6">Domain Mystery Box Assistant</Typography>
            </Box>

            {/* Messages */}
            <Box
                sx={{
                    flex: 1,
                    overflowY: 'auto',
                    px: 2,
                    py: 1,
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 1
                }}
            >
                {messages.map((msg, index) => (
                    <Box
                        key={index}
                        sx={{
                            alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                            backgroundColor: msg.sender === 'user' ? '#E6F9EB' : '#F5F5F5',
                            px: 2,
                            py: 1,
                            borderRadius: 2,
                            maxWidth: '75%',
                            fontSize: 14
                        }}
                    >
                        {msg.text}
                    </Box>
                ))}
                <div ref={chatEndRef} />
            </Box>

            {/* Input */}
            <Box sx={{ display: 'flex', p: 2, gap: 1, borderTop: '1px solid #eee' }}>
                <TextField
                    size="small"
                    fullWidth
                    variant="outlined"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                            e.preventDefault(); // Prevents default behavior like adding a new line
                            handleSendMessage();
                        }
                    }}
                    placeholder="Type your message..."
                />
                <Button
                    onClick={handleSendMessage}
                    variant="contained"
                    sx={{ backgroundColor: 'teal', textTransform: 'none', px: 3 }}
                >
                    Send
                </Button>
            </Box>
        </Box>
    );
};

export default ChatBox;