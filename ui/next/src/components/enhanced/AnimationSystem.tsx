'use client';

import { motion, AnimatePresence, Variants } from 'framer-motion';
import { ReactNode, useState, useEffect } from 'react';
import { Box, Skeleton, CircularProgress } from '@mui/material';

// Enhanced animation variants for unforgettable UX
export const animationVariants = {
  // Page transitions with depth
  pageTransition: {
    initial: { 
      opacity: 0, 
      y: 20, 
      scale: 0.98,
      filter: 'blur(4px)'
    },
    animate: { 
      opacity: 1, 
      y: 0, 
      scale: 1,
      filter: 'blur(0px)'
    },
    exit: { 
      opacity: 0, 
      y: -20, 
      scale: 0.98,
      filter: 'blur(4px)'
    },
    transition: { 
      duration: 0.4, 
      ease: [0.4, 0, 0.2, 1],
      staggerChildren: 0.1
    }
  },
  
  // Card interactions with premium feel
  cardHover: {
    initial: { scale: 1, y: 0, rotateX: 0 },
    hover: { 
      scale: 1.02, 
      y: -8,
      rotateX: 2,
      transition: { 
        duration: 0.2, 
        ease: "easeOut",
        type: "spring",
        stiffness: 300
      }
    },
    tap: { 
      scale: 0.98,
      transition: { duration: 0.1 }
    }
  },
  
  // Advanced loading states
  shimmer: {
    initial: { x: '-100%' },
    animate: { 
      x: '100%',
      transition: { 
        duration: 1.5, 
        repeat: Infinity, 
        ease: "linear",
        repeatDelay: 0.5
      }
    }
  },
  
  // Success animations with celebration
  successPulse: {
    initial: { scale: 0.8, opacity: 0, rotate: -10 },
    animate: { 
      scale: [0.8, 1.2, 1], 
      opacity: [0, 1, 1],
      rotate: [-10, 5, 0],
      transition: { 
        duration: 0.6, 
        ease: "easeOut",
        times: [0, 0.6, 1]
      }
    }
  },
  
  // Error animations with attention
  errorShake: {
    initial: { x: 0 },
    animate: { 
      x: [-10, 10, -10, 10, 0],
      transition: { 
        duration: 0.5,
        ease: "easeInOut"
      }
    }
  },
  
  // Stagger children animations
  staggerContainer: {
    animate: {
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2
      }
    }
  },
  
  staggerItem: {
    initial: { opacity: 0, y: 20 },
    animate: { 
      opacity: 1, 
      y: 0,
      transition: { 
        duration: 0.4,
        ease: "easeOut"
      }
    }
  },
  
  // Floating animation for attention
  float: {
    animate: {
      y: [0, -10, 0],
      transition: {
        duration: 2,
        repeat: Infinity,
        ease: "easeInOut"
      }
    }
  },
  
  // Pulse animation for notifications
  pulse: {
    animate: {
      scale: [1, 1.05, 1],
      transition: {
        duration: 1,
        repeat: Infinity,
        ease: "easeInOut"
      }
    }
  },
  
  // Slide in from different directions
  slideInLeft: {
    initial: { x: -100, opacity: 0 },
    animate: { x: 0, opacity: 1 },
    exit: { x: -100, opacity: 0 },
    transition: { duration: 0.3, ease: "easeOut" }
  },
  
  slideInRight: {
    initial: { x: 100, opacity: 0 },
    animate: { x: 0, opacity: 1 },
    exit: { x: 100, opacity: 0 },
    transition: { duration: 0.3, ease: "easeOut" }
  },
  
  slideInUp: {
    initial: { y: 100, opacity: 0 },
    animate: { y: 0, opacity: 1 },
    exit: { y: 100, opacity: 0 },
    transition: { duration: 0.3, ease: "easeOut" }
  },
  
  slideInDown: {
    initial: { y: -100, opacity: 0 },
    animate: { y: 0, opacity: 1 },
    exit: { y: -100, opacity: 0 },
    transition: { duration: 0.3, ease: "easeOut" }
  },
  
  // Scale animations
  scaleIn: {
    initial: { scale: 0, opacity: 0 },
    animate: { scale: 1, opacity: 1 },
    exit: { scale: 0, opacity: 0 },
    transition: { duration: 0.3, ease: "backOut" }
  },
  
  // Fade animations
  fadeIn: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    exit: { opacity: 0 },
    transition: { duration: 0.3 }
  },
  
  // Rotate animations
  rotateIn: {
    initial: { rotate: -180, opacity: 0 },
    animate: { rotate: 0, opacity: 1 },
    exit: { rotate: 180, opacity: 0 },
    transition: { duration: 0.5, ease: "easeOut" }
  },
  
  // Bounce animations
  bounce: {
    animate: {
      y: [0, -20, 0],
      transition: {
        duration: 0.6,
        ease: "easeInOut"
      }
    }
  },
  
  // Morphing animations
  morph: {
    animate: {
      borderRadius: ["20%", "50%", "20%"],
      transition: {
        duration: 2,
        repeat: Infinity,
        ease: "easeInOut"
      }
    }
  }
};

// Enhanced loading components
export const LoadingComponents = {
  // Skeleton with shimmer effect
  SkeletonCard: ({ height = 200, width = '100%' }) => (
    <motion.div
      className="skeleton-card"
      variants={animationVariants.shimmer}
      initial="initial"
      animate="animate"
      style={{
        position: 'relative',
        overflow: 'hidden',
        borderRadius: '12px',
        background: 'linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)',
        backgroundSize: '200px 100%',
        height,
        width,
      }}
    >
      <motion.div
        className="skeleton-shimmer"
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent)',
          backgroundSize: '200px 100%',
        }}
        animate={{
          x: ['-100%', '100%']
        }}
        transition={{
          duration: 1.5,
          repeat: Infinity,
          ease: "linear"
        }}
      />
    </motion.div>
  ),
  
  // Circular progress with custom animation
  CircularProgress: ({ value = 0, size = 60, thickness = 4, color = 'primary' }) => (
    <motion.div
      className="circular-progress-container"
      initial={{ scale: 0, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ duration: 0.3, ease: "backOut" }}
    >
      <CircularProgress
        variant="determinate"
        value={value}
        size={size}
        thickness={thickness}
        color={color as any}
        sx={{
          '& .MuiCircularProgress-circle': {
            strokeLinecap: 'round',
          }
        }}
      />
      <motion.div
        className="progress-text"
        style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          fontSize: `${size * 0.2}px`,
          fontWeight: 'bold',
        }}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        {Math.round(value)}%
      </motion.div>
    </motion.div>
  ),
  
  // Spinning loader
  Spinner: ({ size = 40, color = 'primary' }) => (
    <motion.div
      className="spinner"
      animate={{ rotate: 360 }}
      transition={{ 
        duration: 1, 
        repeat: Infinity, 
        ease: "linear" 
      }}
      style={{
        width: size,
        height: size,
        border: `3px solid rgba(0,0,0,0.1)`,
        borderTop: `3px solid ${color === 'primary' ? '#1976d2' : color}`,
        borderRadius: '50%',
      }}
    />
  ),
  
  // Dots loader
  DotsLoader: () => (
    <motion.div
      className="dots-loader"
      style={{ display: 'flex', gap: '8px' }}
    >
      {[0, 1, 2].map((index) => (
        <motion.div
          key={index}
          style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            backgroundColor: '#1976d2',
          }}
          animate={{
            scale: [1, 1.5, 1],
            opacity: [0.5, 1, 0.5],
          }}
          transition={{
            duration: 1,
            repeat: Infinity,
            delay: index * 0.2,
            ease: "easeInOut"
          }}
        />
      ))}
    </motion.div>
  ),
  
  // Pulse loader
  PulseLoader: ({ size = 40, color = 'primary' }) => (
    <motion.div
      className="pulse-loader"
      animate={{
        scale: [1, 1.2, 1],
        opacity: [0.5, 1, 0.5],
      }}
      transition={{
        duration: 1.5,
        repeat: Infinity,
        ease: "easeInOut"
      }}
      style={{
        width: size,
        height: size,
        borderRadius: '50%',
        backgroundColor: color === 'primary' ? '#1976d2' : color,
      }}
    />
  )
};

// Animated page wrapper
interface AnimatedPageProps {
  children: ReactNode;
  className?: string;
}

export const AnimatedPage: React.FC<AnimatedPageProps> = ({ children, className }) => (
  <motion.div
    className={className}
    variants={animationVariants.pageTransition}
    initial="initial"
    animate="animate"
    exit="exit"
  >
    {children}
  </motion.div>
);

// Animated card component
interface AnimatedCardProps {
  children: ReactNode;
  className?: string;
  onClick?: () => void;
  disabled?: boolean;
}

export const AnimatedCard: React.FC<AnimatedCardProps> = ({ 
  children, 
  className, 
  onClick, 
  disabled = false 
}) => (
  <motion.div
    className={className}
    variants={animationVariants.cardHover}
    initial="initial"
    whileHover={!disabled ? "hover" : undefined}
    whileTap={!disabled ? "tap" : undefined}
    onClick={onClick}
    style={{ cursor: disabled ? 'default' : 'pointer' }}
  >
    {children}
  </motion.div>
);

// Stagger container for lists
interface StaggerContainerProps {
  children: ReactNode;
  className?: string;
}

export const StaggerContainer: React.FC<StaggerContainerProps> = ({ children, className }) => (
  <motion.div
    className={className}
    variants={animationVariants.staggerContainer}
    initial="initial"
    animate="animate"
  >
    {children}
  </motion.div>
);

// Stagger item for list items
interface StaggerItemProps {
  children: ReactNode;
  className?: string;
}

export const StaggerItem: React.FC<StaggerItemProps> = ({ children, className }) => (
  <motion.div
    className={className}
    variants={animationVariants.staggerItem}
  >
    {children}
  </motion.div>
);

// Floating element
interface FloatingElementProps {
  children: ReactNode;
  className?: string;
}

export const FloatingElement: React.FC<FloatingElementProps> = ({ children, className }) => (
  <motion.div
    className={className}
    variants={animationVariants.float}
    animate="animate"
  >
    {children}
  </motion.div>
);

// Pulse element
interface PulseElementProps {
  children: ReactNode;
  className?: string;
}

export const PulseElement: React.FC<PulseElementProps> = ({ children, className }) => (
  <motion.div
    className={className}
    variants={animationVariants.pulse}
    animate="animate"
  >
    {children}
  </motion.div>
);

// Success notification
interface SuccessNotificationProps {
  message: string;
  onComplete?: () => void;
}

export const SuccessNotification: React.FC<SuccessNotificationProps> = ({ 
  message, 
  onComplete 
}) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      onComplete?.();
    }, 3000);
    
    return () => clearTimeout(timer);
  }, [onComplete]);
  
  return (
    <motion.div
      className="success-notification"
      variants={animationVariants.successPulse}
      initial="initial"
      animate="animate"
      style={{
        position: 'fixed',
        top: '20px',
        right: '20px',
        background: 'linear-gradient(135deg, #38a169 0%, #48bb78 100%)',
        color: 'white',
        padding: '16px 24px',
        borderRadius: '12px',
        boxShadow: '0 10px 25px rgba(56, 161, 105, 0.3)',
        zIndex: 1000,
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
      }}
    >
      <motion.div
        animate={{ rotate: [0, 360] }}
        transition={{ duration: 0.5, ease: "easeOut" }}
      >
        ✅
      </motion.div>
      <span style={{ fontWeight: 600 }}>{message}</span>
    </motion.div>
  );
};

// Error notification
interface ErrorNotificationProps {
  message: string;
  onComplete?: () => void;
}

export const ErrorNotification: React.FC<ErrorNotificationProps> = ({ 
  message, 
  onComplete 
}) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      onComplete?.();
    }, 4000);
    
    return () => clearTimeout(timer);
  }, [onComplete]);
  
  return (
    <motion.div
      className="error-notification"
      variants={animationVariants.errorShake}
      initial="initial"
      animate="animate"
      style={{
        position: 'fixed',
        top: '20px',
        right: '20px',
        background: 'linear-gradient(135deg, #e53e3e 0%, #fc8181 100%)',
        color: 'white',
        padding: '16px 24px',
        borderRadius: '12px',
        boxShadow: '0 10px 25px rgba(229, 62, 62, 0.3)',
        zIndex: 1000,
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
      }}
    >
      <motion.div
        animate={{ scale: [1, 1.2, 1] }}
        transition={{ duration: 0.5, ease: "easeInOut" }}
      >
        ❌
      </motion.div>
      <span style={{ fontWeight: 600 }}>{message}</span>
    </motion.div>
  );
};

// Loading overlay
interface LoadingOverlayProps {
  isLoading: boolean;
  children: ReactNode;
  message?: string;
}

export const LoadingOverlay: React.FC<LoadingOverlayProps> = ({ 
  isLoading, 
  children, 
  message = "Loading..." 
}) => (
  <div style={{ position: 'relative' }}>
    {children}
    <AnimatePresence>
      {isLoading && (
        <motion.div
          className="loading-overlay"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(255, 255, 255, 0.9)',
            backdropFilter: 'blur(4px)',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '16px',
            zIndex: 1000,
          }}
        >
          <LoadingComponents.Spinner size={40} />
          <motion.p
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            style={{ 
              margin: 0, 
              color: '#666',
              fontWeight: 500 
            }}
          >
            {message}
          </motion.p>
        </motion.div>
      )}
    </AnimatePresence>
  </div>
);

export default {
  animationVariants,
  LoadingComponents,
  AnimatedPage,
  AnimatedCard,
  StaggerContainer,
  StaggerItem,
  FloatingElement,
  PulseElement,
  SuccessNotification,
  ErrorNotification,
  LoadingOverlay,
};
