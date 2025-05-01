import React, { useState, useEffect, useRef } from 'react';
import { Box, TextField, Button, Typography } from '@mui/material';
import axios from "axios";

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

    const handleSendMessage = async () => {
        if (input.trim() === '') return;

        const userMessage = input.trim();
        const domain = domains[0] || ''; // Fallback if no domain found
        const combined = `${userMessage} ${domain}`;

        setMessages(prev => [...prev, { text: userMessage, sender: 'user' }]);
        setInput('');

        // Temporary loading message
        setMessages(prev => [...prev, { text: 'Got it! Let me look that up for you... 🔍', sender: 'bot' }]);

        try {
            const response = await fetch(
                `http://localhost:8001/get_domain_go_value?domain=${encodeURIComponent(combined)}`
            );

            const data = await response.json();
            const result = data.result?.[0];
            if (!result || !result["Domain Name"]) {
                throw new Error("No domain analysis found.");
            }

            const reply = `
                🔍 Domain Analysis for **${result["Domain Name"]}**:
                
                📈 **Traffic & Engagement**: ${result["Traffic & Engagement"].summary}
                ⭐ Rating: ${result["Traffic & Engagement"].rating}/10
                
                🔑 **Keyword & SEO Value**: ${result["Keyword & SEO Value"].summary}
                ⭐ Rating: ${result["Keyword & SEO Value"].rating}/10
                
                ✍️ **SLD Structure & Length**: ${result["SLD Structure & Length"].summary}
                ⭐ Rating: ${result["SLD Structure & Length"].rating}/10
                
                🎯 **Brandability & Positioning**: ${result["Brandability & Positioning"].summary}
                ⭐ Rating: ${result["Brandability & Positioning"].rating}/10
                
                🔐 **Trustworthiness & TLD**: ${result["Trustworthiness & TLD"].summary}
                ⭐ Rating: ${result["Trustworthiness & TLD"].rating}/10
                `;

            setMessages(prev => {
                const updated = [...prev];
                updated.pop(); // Remove "Thinking..."
                return [...updated, { text: reply, sender: 'bot' }];
            });

        } catch (error) {
            console.error('Error fetching reply:', error);
            setMessages(prev => {
                const updated = [...prev];
                updated.pop();
                return [...updated, { text: "Oops! Something went wrong. Try again later.", sender: 'bot' }];
            });
        }
    };

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    return (
        <Box
            sx={{
                position: 'fixed',
                bottom: 193,
                right: 70,
                width: 750,
                height: 590,
                borderRadius: 5,
                boxShadow: 3,
                backgroundColor: '#fff',
                border: '3px solid black',
                display: 'flex',
                flexDirection: 'column',
                // zIndex: 1000
            }}
        >
            {/* Header */}
            <Box sx={{ p: 2, backgroundColor: 'teal', color: '#fff', borderTopLeftRadius: 15, borderTopRightRadius: 15 }}>
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
                            borderRadius: 5,
                            maxWidth: '75%',
                            fontSize: 14
                        }}
                    >
                        {msg.text.split('\n').map((line, i) => (
                            <div key={i}>{line}</div>
                        ))}
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