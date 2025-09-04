'use client';

import { useState, useEffect, useRef, ReactNode } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Box, 
  IconButton, 
  Tooltip, 
  Fab, 
  Dialog, 
  DialogTitle, 
  DialogContent,
  DialogActions,
  Button,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Typography,
  Avatar,
  TextField,
  Divider
} from '@mui/material';
import {
  Mic as MicIcon,
  MicOff as MicOffIcon,
  SmartToy as AiIcon,
  Gesture as GestureIcon,
  TouchApp as TouchIcon,
  VolumeUp as VolumeIcon,
  Settings as SettingsIcon,
  Close as CloseIcon,
  Send as SendIcon,
  KeyboardVoice as VoiceIcon,
  Swipe as SwipeIcon,
  ZoomIn as ZoomIcon,
  PanTool as PanIcon,
} from '@mui/icons-material';

// Gesture recognition system
export const GestureSystem = {
  // Swipe navigation hook
  useSwipeNavigation: () => {
    const [swipeDirection, setSwipeDirection] = useState<string | null>(null);
    const [isListening, setIsListening] = useState(false);
    const touchStart = useRef<{ x: number; y: number } | null>(null);
    const touchEnd = useRef<{ x: number; y: number } | null>(null);
    
    const minSwipeDistance = 50;
    
    const onTouchStart = (e: React.TouchEvent) => {
      touchEnd.current = null;
      touchStart.current = {
        x: e.targetTouches[0].clientX,
        y: e.targetTouches[0].clientY,
      };
    };
    
    const onTouchMove = (e: React.TouchEvent) => {
      touchEnd.current = {
        x: e.targetTouches[0].clientX,
        y: e.targetTouches[0].clientY,
      };
    };
    
    const onTouchEnd = () => {
      if (!touchStart.current || !touchEnd.current) return;
      
      const distanceX = touchStart.current.x - touchEnd.current.x;
      const distanceY = touchStart.current.y - touchEnd.current.y;
      const isHorizontalSwipe = Math.abs(distanceX) > Math.abs(distanceY);
      
      if (isHorizontalSwipe) {
        if (Math.abs(distanceX) > minSwipeDistance) {
          const direction = distanceX > 0 ? 'left' : 'right';
          setSwipeDirection(direction);
          handleSwipe(direction);
        }
      } else {
        if (Math.abs(distanceY) > minSwipeDistance) {
          const direction = distanceY > 0 ? 'up' : 'down';
          setSwipeDirection(direction);
          handleSwipe(direction);
        }
      }
      
      // Reset after a short delay
      setTimeout(() => setSwipeDirection(null), 500);
    };
    
    const handleSwipe = (direction: string) => {
      console.log(`Swipe detected: ${direction}`);
      // Implement navigation logic here
      switch(direction) {
        case 'left':
          // Navigate to next tab/section
          break;
        case 'right':
          // Navigate to previous tab/section
          break;
        case 'up':
          // Expand current section
          break;
        case 'down':
          // Collapse current section
          break;
      }
    };
    
    return {
      swipeDirection,
      isListening,
      setIsListening,
      onTouchStart,
      onTouchMove,
      onTouchEnd,
    };
  },
  
  // Pinch to zoom hook
  usePinchZoom: (elementRef: React.RefObject<HTMLElement>) => {
    const [scale, setScale] = useState(1);
    const [isZooming, setIsZooming] = useState(false);
    
    useEffect(() => {
      const element = elementRef.current;
      if (!element) return;
      
      let initialDistance = 0;
      let initialScale = 1;
      
      const handleTouchStart = (e: TouchEvent) => {
        if (e.touches.length === 2) {
          setIsZooming(true);
          initialDistance = Math.hypot(
            e.touches[0].clientX - e.touches[1].clientX,
            e.touches[0].clientY - e.touches[1].clientY
          );
          initialScale = scale;
        }
      };
      
      const handleTouchMove = (e: TouchEvent) => {
        if (e.touches.length === 2 && isZooming) {
          e.preventDefault();
          
          const currentDistance = Math.hypot(
            e.touches[0].clientX - e.touches[1].clientX,
            e.touches[0].clientY - e.touches[1].clientY
          );
          
          const newScale = Math.max(0.5, Math.min(3, initialScale * (currentDistance / initialDistance)));
          setScale(newScale);
        }
      };
      
      const handleTouchEnd = () => {
        setIsZooming(false);
      };
      
      element.addEventListener('touchstart', handleTouchStart);
      element.addEventListener('touchmove', handleTouchMove, { passive: false });
      element.addEventListener('touchend', handleTouchEnd);
      
      return () => {
        element.removeEventListener('touchstart', handleTouchStart);
        element.removeEventListener('touchmove', handleTouchMove);
        element.removeEventListener('touchend', handleTouchEnd);
      };
    }, [elementRef, scale, isZooming]);
    
    return { scale, isZooming, setScale };
  }
};

// Voice interaction system
export const VoiceSystem = {
  // Voice commands hook
  useVoiceCommands: () => {
    const [isListening, setIsListening] = useState(false);
    const [transcript, setTranscript] = useState('');
    const [isSupported, setIsSupported] = useState(false);
    const recognitionRef = useRef<any>(null);
    
    useEffect(() => {
      // Check if speech recognition is supported
      if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        setIsSupported(true);
        const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
        recognitionRef.current = new SpeechRecognition();
        
        recognitionRef.current.continuous = true;
        recognitionRef.current.interimResults = true;
        recognitionRef.current.lang = 'en-US';
        
        recognitionRef.current.onresult = (event: any) => {
          let finalTranscript = '';
          for (let i = event.resultIndex; i < event.results.length; i++) {
            if (event.results[i].isFinal) {
              finalTranscript += event.results[i][0].transcript;
            }
          }
          if (finalTranscript) {
            setTranscript(finalTranscript);
            processVoiceCommand(finalTranscript.toLowerCase());
          }
        };
        
        recognitionRef.current.onerror = (event: any) => {
          console.error('Speech recognition error:', event.error);
          setIsListening(false);
        };
        
        recognitionRef.current.onend = () => {
          setIsListening(false);
        };
      }
    }, []);
    
    const commands = {
      'show dashboard': () => {
        console.log('Navigating to dashboard');
        // Implement navigation
      },
      'open compliance': () => {
        console.log('Opening compliance section');
        // Implement navigation
      },
      'refresh data': () => {
        console.log('Refreshing data');
        // Implement data refresh
      },
      'export report': () => {
        console.log('Exporting report');
        // Implement export
      },
      'switch language': () => {
        console.log('Switching language');
        // Implement language switch
      },
      'help': () => {
        console.log('Showing help');
        // Show help dialog
      },
    };
    
    const processVoiceCommand = (command: string) => {
      for (const [key, action] of Object.entries(commands)) {
        if (command.includes(key)) {
          action();
          break;
        }
      }
    };
    
    const startListening = () => {
      if (recognitionRef.current && isSupported) {
        recognitionRef.current.start();
        setIsListening(true);
      }
    };
    
    const stopListening = () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
        setIsListening(false);
      }
    };
    
    const toggleListening = () => {
      if (isListening) {
        stopListening();
      } else {
        startListening();
      }
    };
    
    return {
      isListening,
      transcript,
      isSupported,
      startListening,
      stopListening,
      toggleListening,
    };
  },
  
  // Voice command button component
  VoiceCommandButton: () => {
    const { isListening, isSupported, toggleListening } = VoiceSystem.useVoiceCommands();
    
    if (!isSupported) {
      return null;
    }
    
    return (
      <Tooltip title={isListening ? "Stop listening" : "Start voice commands"}>
        <Fab
          color={isListening ? "secondary" : "primary"}
          size="medium"
          onClick={toggleListening}
          sx={{
            position: 'fixed',
            bottom: 100,
            right: 24,
            zIndex: 1000,
          }}
        >
          <motion.div
            animate={isListening ? { scale: [1, 1.2, 1] } : {}}
            transition={{ duration: 1, repeat: Infinity }}
          >
            {isListening ? <MicOffIcon /> : <MicIcon />}
          </motion.div>
        </Fab>
      </Tooltip>
    );
  }
};

// AI Assistant component
interface AIAssistantProps {
  isOpen: boolean;
  onClose: () => void;
}

export const AIAssistant: React.FC<AIAssistantProps> = ({ isOpen, onClose }) => {
  const [messages, setMessages] = useState<Array<{ id: string; text: string; isUser: boolean; timestamp: Date }>>([
    {
      id: '1',
      text: 'Hello! I\'m your AI assistant. How can I help you with compliance today?',
      isUser: false,
      timestamp: new Date(),
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  
  const handleSendMessage = async () => {
    if (!inputText.trim()) return;
    
    const userMessage = {
      id: Date.now().toString(),
      text: inputText,
      isUser: true,
      timestamp: new Date(),
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsTyping(true);
    
    // Simulate AI response
    setTimeout(() => {
      const aiResponse = {
        id: (Date.now() + 1).toString(),
        text: generateAIResponse(inputText),
        isUser: false,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, aiResponse]);
      setIsTyping(false);
    }, 1000 + Math.random() * 2000);
  };
  
  const generateAIResponse = (userInput: string): string => {
    const responses = [
      "I can help you with that! Let me analyze your compliance requirements.",
      "Based on your input, I recommend checking the NCA v2.0 guidelines.",
      "I've found some relevant compliance patterns for your use case.",
      "Let me generate a compliance report for you.",
      "I can assist with automating your compliance checks.",
      "Would you like me to explain the SAMA CSF requirements?",
    ];
    
    return responses[Math.floor(Math.random() * responses.length)];
  };
  
  return (
    <Dialog
      open={isOpen}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 3,
          height: '80vh',
          maxHeight: 600,
        }
      }}
    >
      <DialogTitle sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: 2,
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white'
      }}>
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
        >
          <AiIcon />
        </motion.div>
        <Typography variant="h6">AI Assistant</Typography>
        <IconButton
          onClick={onClose}
          sx={{ color: 'white', ml: 'auto' }}
        >
          <CloseIcon />
        </IconButton>
      </DialogTitle>
      
      <DialogContent sx={{ p: 0, display: 'flex', flexDirection: 'column' }}>
        <Box sx={{ 
          flex: 1, 
          overflow: 'auto', 
          p: 2,
          background: '#f8f9fa'
        }}>
          <List>
            {messages.map((message) => (
              <ListItem
                key={message.id}
                sx={{
                  flexDirection: 'column',
                  alignItems: message.isUser ? 'flex-end' : 'flex-start',
                  p: 1,
                }}
              >
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: 1,
                    maxWidth: '80%',
                  }}
                >
                  {!message.isUser && (
                    <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main' }}>
                      <AiIcon fontSize="small" />
                    </Avatar>
                  )}
                  <Box
                    sx={{
                      background: message.isUser 
                        ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                        : 'white',
                      color: message.isUser ? 'white' : 'text.primary',
                      p: 2,
                      borderRadius: 3,
                      boxShadow: 1,
                      maxWidth: '100%',
                    }}
                  >
                    <Typography variant="body2">
                      {message.text}
                    </Typography>
                    <Typography 
                      variant="caption" 
                      sx={{ 
                        opacity: 0.7,
                        display: 'block',
                        mt: 0.5
                      }}
                    >
                      {message.timestamp.toLocaleTimeString()}
                    </Typography>
                  </Box>
                  {message.isUser && (
                    <Avatar sx={{ width: 32, height: 32, bgcolor: 'secondary.main' }}>
                      U
                    </Avatar>
                  )}
                </Box>
              </ListItem>
            ))}
            {isTyping && (
              <ListItem sx={{ justifyContent: 'flex-start' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main' }}>
                    <AiIcon fontSize="small" />
                  </Avatar>
                  <Box sx={{ display: 'flex', gap: 0.5 }}>
                    {[0, 1, 2].map((i) => (
                      <motion.div
                        key={i}
                        animate={{ y: [0, -10, 0] }}
                        transition={{
                          duration: 0.6,
                          repeat: Infinity,
                          delay: i * 0.2,
                        }}
                        style={{
                          width: 8,
                          height: 8,
                          borderRadius: '50%',
                          backgroundColor: '#667eea',
                        }}
                      />
                    ))}
                  </Box>
                </Box>
              </ListItem>
            )}
          </List>
        </Box>
        
        <Divider />
        
        <Box sx={{ p: 2, display: 'flex', gap: 1 }}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Type your message..."
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            size="small"
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: 3,
              }
            }}
          />
          <IconButton
            onClick={handleSendMessage}
            disabled={!inputText.trim()}
            sx={{
              bgcolor: 'primary.main',
              color: 'white',
              '&:hover': {
                bgcolor: 'primary.dark',
              },
              '&:disabled': {
                bgcolor: 'grey.300',
              }
            }}
          >
            <SendIcon />
          </IconButton>
        </Box>
      </DialogContent>
    </Dialog>
  );
};

// Interactive features container
interface InteractiveFeaturesProps {
  children: ReactNode;
}

export const InteractiveFeatures: React.FC<InteractiveFeaturesProps> = ({ children }) => {
  const { onTouchStart, onTouchMove, onTouchEnd } = GestureSystem.useSwipeNavigation();
  const [showAIAssistant, setShowAIAssistant] = useState(false);
  
  return (
    <Box
      onTouchStart={onTouchStart}
      onTouchMove={onTouchMove}
      onTouchEnd={onTouchEnd}
      sx={{ position: 'relative' }}
    >
      {children}
      
      {/* AI Assistant FAB */}
      <Tooltip title="AI Assistant">
        <Fab
          color="primary"
          size="large"
          onClick={() => setShowAIAssistant(true)}
          sx={{
            position: 'fixed',
            bottom: 24,
            right: 24,
            zIndex: 1000,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          }}
        >
          <motion.div
            animate={{ 
              scale: [1, 1.1, 1],
              rotate: [0, 5, -5, 0]
            }}
            transition={{ 
              duration: 2, 
              repeat: Infinity,
              ease: "easeInOut"
            }}
          >
            <AiIcon />
          </motion.div>
        </Fab>
      </Tooltip>
      
      {/* Voice Command Button */}
      <VoiceSystem.VoiceCommandButton />
      
      {/* AI Assistant Dialog */}
      <AIAssistant 
        isOpen={showAIAssistant} 
        onClose={() => setShowAIAssistant(false)} 
      />
    </Box>
  );
};

// Gesture indicator component
export const GestureIndicator: React.FC = () => {
  const [showIndicator, setShowIndicator] = useState(false);
  const [gestureType, setGestureType] = useState('');
  
  useEffect(() => {
    const handleGesture = (e: any) => {
      setGestureType(e.detail.type);
      setShowIndicator(true);
      setTimeout(() => setShowIndicator(false), 2000);
    };
    
    window.addEventListener('gesture', handleGesture);
    return () => window.removeEventListener('gesture', handleGesture);
  }, []);
  
  if (!showIndicator) return null;
  
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0 }}
      style={{
        position: 'fixed',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        background: 'rgba(0, 0, 0, 0.8)',
        color: 'white',
        padding: '16px 24px',
        borderRadius: '12px',
        zIndex: 2000,
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
      }}
    >
      <GestureIcon />
      <Typography variant="body1">
        {gestureType} gesture detected
      </Typography>
    </motion.div>
  );
};

export default {
  GestureSystem,
  VoiceSystem,
  AIAssistant,
  InteractiveFeatures,
  GestureIndicator,
};
