'use client';

import { createTheme, ThemeProvider } from '@mui/material/styles';
import { ReactNode } from 'react';

// Enhanced color palette with Saudi Arabia branding
const enhancedColors = {
  primary: {
    main: '#1a365d', // Deep Saudi Blue
    light: '#3182ce',
    dark: '#0f2027',
    gradient: 'linear-gradient(135deg, #1a365d 0%, #3182ce 100%)',
    contrastText: '#ffffff',
  },
  secondary: {
    main: '#d69e2e', // Saudi Gold
    light: '#f6e05e',
    dark: '#b7791f',
    gradient: 'linear-gradient(135deg, #d69e2e 0%, #f6e05e 100%)',
    contrastText: '#1a202c',
  },
  success: {
    main: '#38a169', // Emerald Green
    light: '#48bb78',
    dark: '#2f855a',
    gradient: 'linear-gradient(135deg, #38a169 0%, #48bb78 100%)',
    contrastText: '#ffffff',
  },
  warning: {
    main: '#ed8936', // Vibrant Orange
    light: '#f56565',
    dark: '#c05621',
    gradient: 'linear-gradient(135deg, #ed8936 0%, #f56565 100%)',
    contrastText: '#ffffff',
  },
  error: {
    main: '#e53e3e', // Rich Red
    light: '#fc8181',
    dark: '#c53030',
    gradient: 'linear-gradient(135deg, #e53e3e 0%, #fc8181 100%)',
    contrastText: '#ffffff',
  },
  info: {
    main: '#3182ce', // Bright Blue
    light: '#63b3ed',
    dark: '#2c5282',
    gradient: 'linear-gradient(135deg, #3182ce 0%, #63b3ed 100%)',
    contrastText: '#ffffff',
  },
  // Custom gradients for premium feel
  gradients: {
    primary: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    success: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
    warning: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    dark: 'linear-gradient(135deg, #2c3e50 0%, #3498db 100%)',
    sunset: 'linear-gradient(135deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%)',
    ocean: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    forest: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
    fire: 'linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%)',
  },
  // Neutral colors
  grey: {
    50: '#f7fafc',
    100: '#edf2f7',
    200: '#e2e8f0',
    300: '#cbd5e0',
    400: '#a0aec0',
    500: '#718096',
    600: '#4a5568',
    700: '#2d3748',
    800: '#1a202c',
    900: '#171923',
  },
  // Background colors
  background: {
    default: '#f7fafc',
    paper: '#ffffff',
    gradient: 'linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%)',
    dark: 'linear-gradient(135deg, #1a202c 0%, #2d3748 100%)',
  },
  // Text colors
  text: {
    primary: '#1a202c',
    secondary: '#4a5568',
    disabled: '#a0aec0',
    hint: '#718096',
  },
};

// Enhanced typography system
const enhancedTypography = {
  fontFamily: {
    primary: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    arabic: 'Noto Sans Arabic, Tahoma, Arial, sans-serif',
    display: 'Poppins, Inter, sans-serif', // For headings
    mono: 'JetBrains Mono, Fira Code, "Courier New", monospace', // For code/data
    serif: 'Georgia, "Times New Roman", serif', // For special content
  },
  fontSize: {
    xs: '0.75rem',    // 12px
    sm: '0.875rem',   // 14px
    base: '1rem',     // 16px
    lg: '1.125rem',   // 18px
    xl: '1.25rem',    // 20px
    '2xl': '1.5rem',  // 24px
    '3xl': '1.875rem', // 30px
    '4xl': '2.25rem',  // 36px
    '5xl': '3rem',     // 48px
    '6xl': '3.75rem',  // 60px
    '7xl': '4.5rem',   // 72px
    '8xl': '6rem',     // 96px
    '9xl': '8rem',     // 128px
  },
  fontWeight: {
    thin: 100,
    light: 300,
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
    extrabold: 800,
    black: 900,
  },
  lineHeight: {
    none: 1,
    tight: 1.25,
    snug: 1.375,
    normal: 1.5,
    relaxed: 1.625,
    loose: 2,
  },
  letterSpacing: {
    tighter: '-0.05em',
    tight: '-0.025em',
    normal: '0em',
    wide: '0.025em',
    wider: '0.05em',
    widest: '0.1em',
  },
};

// Enhanced spacing system
const enhancedSpacing = {
  xs: '0.25rem',   // 4px
  sm: '0.5rem',    // 8px
  md: '1rem',      // 16px
  lg: '1.5rem',    // 24px
  xl: '2rem',      // 32px
  '2xl': '3rem',   // 48px
  '3xl': '4rem',   // 64px
  '4xl': '6rem',   // 96px
  '5xl': '8rem',   // 128px
};

// Enhanced border radius system
const enhancedBorderRadius = {
  none: '0',
  sm: '0.125rem',   // 2px
  base: '0.25rem',  // 4px
  md: '0.375rem',   // 6px
  lg: '0.5rem',     // 8px
  xl: '0.75rem',    // 12px
  '2xl': '1rem',    // 16px
  '3xl': '1.5rem',  // 24px
  full: '9999px',
};

// Enhanced shadows system
const enhancedShadows = {
  none: 'none',
  sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  base: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
  '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
  inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
  // Custom shadows for premium feel
  glow: {
    primary: '0 0 20px rgba(26, 54, 93, 0.3)',
    success: '0 0 20px rgba(56, 161, 105, 0.3)',
    warning: '0 0 20px rgba(237, 137, 54, 0.3)',
    error: '0 0 20px rgba(229, 62, 62, 0.3)',
  },
};

// Create enhanced theme
const createEnhancedTheme = (mode: 'light' | 'dark' = 'light') => {
  const isDark = mode === 'dark';
  
  return createTheme({
    palette: {
      mode,
      primary: enhancedColors.primary,
      secondary: enhancedColors.secondary,
      success: enhancedColors.success,
      warning: enhancedColors.warning,
      error: enhancedColors.error,
      info: enhancedColors.info,
      grey: enhancedColors.grey,
      background: {
        default: isDark ? enhancedColors.grey[900] : enhancedColors.background.default,
        paper: isDark ? enhancedColors.grey[800] : enhancedColors.background.paper,
      },
      text: {
        primary: isDark ? enhancedColors.grey[100] : enhancedColors.text.primary,
        secondary: isDark ? enhancedColors.grey[300] : enhancedColors.text.secondary,
      },
    },
    typography: {
      fontFamily: enhancedTypography.fontFamily.primary,
      h1: {
        fontFamily: enhancedTypography.fontFamily.display,
        fontSize: enhancedTypography.fontSize['4xl'],
        fontWeight: enhancedTypography.fontWeight.bold,
        lineHeight: enhancedTypography.lineHeight.tight,
        letterSpacing: enhancedTypography.letterSpacing.tight,
      },
      h2: {
        fontFamily: enhancedTypography.fontFamily.display,
        fontSize: enhancedTypography.fontSize['3xl'],
        fontWeight: enhancedTypography.fontWeight.semibold,
        lineHeight: enhancedTypography.lineHeight.tight,
      },
      h3: {
        fontFamily: enhancedTypography.fontFamily.display,
        fontSize: enhancedTypography.fontSize['2xl'],
        fontWeight: enhancedTypography.fontWeight.semibold,
        lineHeight: enhancedTypography.lineHeight.snug,
      },
      h4: {
        fontSize: enhancedTypography.fontSize.xl,
        fontWeight: enhancedTypography.fontWeight.semibold,
        lineHeight: enhancedTypography.lineHeight.snug,
      },
      h5: {
        fontSize: enhancedTypography.fontSize.lg,
        fontWeight: enhancedTypography.fontWeight.medium,
        lineHeight: enhancedTypography.lineHeight.normal,
      },
      h6: {
        fontSize: enhancedTypography.fontSize.base,
        fontWeight: enhancedTypography.fontWeight.medium,
        lineHeight: enhancedTypography.lineHeight.normal,
      },
      body1: {
        fontSize: enhancedTypography.fontSize.base,
        lineHeight: enhancedTypography.lineHeight.relaxed,
      },
      body2: {
        fontSize: enhancedTypography.fontSize.sm,
        lineHeight: enhancedTypography.lineHeight.relaxed,
      },
      button: {
        fontWeight: enhancedTypography.fontWeight.semibold,
        textTransform: 'none',
        letterSpacing: enhancedTypography.letterSpacing.wide,
      },
      caption: {
        fontSize: enhancedTypography.fontSize.xs,
        lineHeight: enhancedTypography.lineHeight.normal,
      },
      overline: {
        fontSize: enhancedTypography.fontSize.xs,
        fontWeight: enhancedTypography.fontWeight.medium,
        letterSpacing: enhancedTypography.letterSpacing.wider,
        textTransform: 'uppercase',
      },
    },
    shape: {
      borderRadius: parseInt(enhancedBorderRadius.lg),
    },
    spacing: 8,
    components: {
      MuiButton: {
        styleOverrides: {
          root: {
            borderRadius: enhancedBorderRadius.lg,
            textTransform: 'none',
            fontWeight: enhancedTypography.fontWeight.semibold,
            padding: '12px 24px',
            transition: 'all 0.2s ease-in-out',
            '&:hover': {
              transform: 'translateY(-2px)',
              boxShadow: enhancedShadows.lg,
            },
          },
          contained: {
            background: enhancedColors.primary.gradient,
            '&:hover': {
              background: enhancedColors.primary.gradient,
              filter: 'brightness(1.1)',
            },
          },
          outlined: {
            borderWidth: '2px',
            '&:hover': {
              borderWidth: '2px',
              transform: 'translateY(-2px)',
            },
          },
        },
      },
      MuiCard: {
        styleOverrides: {
          root: {
            borderRadius: enhancedBorderRadius.xl,
            boxShadow: enhancedShadows.base,
            border: `1px solid ${isDark ? enhancedColors.grey[700] : enhancedColors.grey[200]}`,
            transition: 'all 0.3s ease-in-out',
            '&:hover': {
              boxShadow: enhancedShadows.lg,
              transform: 'translateY(-4px)',
            },
          },
        },
      },
      MuiPaper: {
        styleOverrides: {
          root: {
            borderRadius: enhancedBorderRadius.lg,
          },
        },
      },
      MuiChip: {
        styleOverrides: {
          root: {
            borderRadius: enhancedBorderRadius.full,
            fontWeight: enhancedTypography.fontWeight.medium,
          },
        },
      },
      MuiTextField: {
        styleOverrides: {
          root: {
            '& .MuiOutlinedInput-root': {
              borderRadius: enhancedBorderRadius.lg,
              '&:hover .MuiOutlinedInput-notchedOutline': {
                borderColor: enhancedColors.primary.main,
              },
              '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                borderColor: enhancedColors.primary.main,
                borderWidth: '2px',
              },
            },
          },
        },
      },
      MuiAppBar: {
        styleOverrides: {
          root: {
            background: isDark 
              ? enhancedColors.background.dark 
              : enhancedColors.background.gradient,
            backdropFilter: 'blur(10px)',
            borderBottom: `1px solid ${isDark ? enhancedColors.grey[700] : enhancedColors.grey[200]}`,
          },
        },
      },
      MuiDrawer: {
        styleOverrides: {
          paper: {
            background: isDark 
              ? enhancedColors.background.dark 
              : enhancedColors.background.gradient,
            borderRight: `1px solid ${isDark ? enhancedColors.grey[700] : enhancedColors.grey[200]}`,
          },
        },
      },
    },
  });
};

// Enhanced theme provider component
interface EnhancedThemeProviderProps {
  children: ReactNode;
  mode?: 'light' | 'dark';
}

export const EnhancedThemeProvider: React.FC<EnhancedThemeProviderProps> = ({
  children,
  mode = 'light',
}) => {
  const theme = createEnhancedTheme(mode);
  
  return (
    <ThemeProvider theme={theme}>
      {children}
    </ThemeProvider>
  );
};

// Export theme utilities
export const themeUtils = {
  colors: enhancedColors,
  typography: enhancedTypography,
  spacing: enhancedSpacing,
  borderRadius: enhancedBorderRadius,
  shadows: enhancedShadows,
  createTheme: createEnhancedTheme,
};

export default EnhancedThemeProvider;
