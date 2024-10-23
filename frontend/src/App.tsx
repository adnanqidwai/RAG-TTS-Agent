import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import {
  Box,
  Typography,
  TextField,
  IconButton,
  Paper,
  List,
  ListItem,
  ListItemText,
  ThemeProvider,
  createTheme,
  CssBaseline,
  GlobalStyles,
  Button,
  ToggleButton,
  ToggleButtonGroup
} from '@mui/material';
import { Send as SendIcon, PlayArrow } from '@mui/icons-material';

interface Message {
  text: string;
  isUser: boolean;
}

const theme = createTheme({
  palette: {
    background: {
      default: '#e8e5dc',
    },
  },
  typography: {
    fontFamily: '"Fantasque Sans Mono", monospace',
    fontWeightBold: 700,
  },
});

const globalStyles = (
  <GlobalStyles
    styles={`
      @import url('https://fontlibrary.org/face/fantasque-sans-mono');
    `}
  />
);

export default function ChatBot() {
  const [query, setQuery] = useState<string>('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [endpoint, setEndpoint] = useState<'agent' | 'rag'>('agent');
  const messagesEndRef = useRef<null | HTMLDivElement>(null);
  const messageToAudio: Record<string, string> = {};

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  useEffect(scrollToBottom, [messages]);

  const handleEndpointChange = (
    event: React.MouseEvent<HTMLElement>,
    newEndpoint: 'agent' | 'rag',
  ) => {
    if (newEndpoint !== null) {
      setEndpoint(newEndpoint);
      setMessages([]);
    }
  };

  const callEndpoint = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setMessages((prev) => [...prev, { text: query, isUser: true }]);
    const currentQuery = query;
    setQuery('');

    try {
      const result = await axios.get(`http://127.0.0.1:8000/${endpoint}`, {
        params: { query: currentQuery },
      });
      const text = result.data.response;

      setMessages((prev) => [...prev, { text, isUser: false }]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        { text: `Error: ${err.message || `Error calling /${endpoint}`}`, isUser: false },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const fetchAudio = async (text: string) => {
    try {
      const ttsResult = await axios.post('http://localhost:8000/tts', { text });
      
      messageToAudio[text.toLowerCase()] = ttsResult.data.response; // cache 

      return ttsResult.data.response; // base64 audio string

    } catch (err) {
      console.error('Error fetching audio:', err);
      return null;
    }
  };

  const playAudio = async (text: string) => {
    if (messageToAudio[text.toLowerCase()]) {
      const audio = new Audio(`data:audio/wav;base64,${messageToAudio[text]}`);
      audio.play();
      return;
    }
    else {
      const audioString = await fetchAudio(text);
      if (audioString) {
        const audio = new Audio(`data:audio/wav;base64,${audioString}`);
        audio.play();
      }
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {globalStyles}
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          height: '100vh',
          bgcolor: 'background.default',
        }}
      >
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Typography variant="h3" align="center">
            Harmony Tutor 🎵
          </Typography>
          <ToggleButtonGroup
            color="primary"
            value={endpoint}
            exclusive
            onChange={handleEndpointChange}
            aria-label="Endpoint"
            sx={{ display: 'flex', justifyContent: 'center', mt: 2, color: '#a18a70', border: "transparent" }}
          >
            <ToggleButton value="agent">Agent Endpoint</ToggleButton>
            <ToggleButton value="rag">RAG Endpoint</ToggleButton>
          </ToggleButtonGroup>
        </Box>
        <List
          sx={{
            flexGrow: 1,
            overflow: 'auto',
            p: 2,
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          {messages.map((message, index) => (
            <ListItem
              key={index}
              sx={{
                justifyContent: message.isUser ? 'flex-end' : 'flex-start',
                mb: 1,
              }}
            >
              <Paper
                elevation={1}
                sx={{
                  p: 2,
                  maxWidth: '70%',
                  bgcolor: message.isUser ? '#fff8c4' : '#f0e2b4',
                  borderRadius: message.isUser ? '20px 20px 0 20px' : '20px 20px 20px 0',
                }}
              >
                <ListItemText
                  primary={message.text}
                  sx={{
                    wordBreak: 'break-word',
                    '& .MuiListItemText-primary': {
                      color: message.isUser ? '#006070' : '#33691e',
                      fontFamily: '"Fantasque Sans Mono", monospace',
                    },
                  }}
                />
              </Paper>
              {!message.isUser && (
                <Button
                  variant="outlined"
                  startIcon={<PlayArrow />}
                  onClick={() => playAudio(message.text)}
                  sx={{ mt: 1, color: '#a18a70', marginLeft: '-10px', marginTop: '-10px', borderColor : 'transparent'}}
                >
                Use Voice
                </Button>
              )}
            </ListItem>
          ))}
          <div ref={messagesEndRef} />
        </List>
        <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Enter your message..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  callEndpoint();
                }
              }}
              sx={{
                mr: 1,
                '& .MuiInputBase-input': {
                  fontFamily: '"Fantasque Sans Mono", monospace',
                },
              }}
            />
            <IconButton
              color="primary"
              onClick={callEndpoint}
              disabled={loading || !query.trim()}
              sx={{ p: '10px' }}
            >
              <SendIcon />
            </IconButton>
          </Box>
        </Box>
      </Box>
    </ThemeProvider>
  );
}