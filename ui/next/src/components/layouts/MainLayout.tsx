'use client';

import React, { useState, useEffect } from 'react';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Divider,
  Avatar,
  Menu,
  MenuItem,
  Badge,
  Tooltip,
  useMediaQuery,
  useTheme,
  Breadcrumbs,
  Link,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Close as CloseIcon,
  Dashboard as DashboardIcon,
  Security as SecurityIcon,
  Assessment as AssessmentIcon,
  Timeline as TimelineIcon,
  Settings as SettingsIcon,
  Notifications as NotificationsIcon,
  AccountCircle as AccountIcon,
  Brightness4 as DarkModeIcon,
  Brightness7 as LightModeIcon,
  Language as LanguageIcon,
  ChevronLeft as ChevronLeftIcon,
  Home as HomeIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import { useRouter, usePathname } from 'next/navigation';

import { useGlobalStore } from '@/stores/GlobalStore';
import { SystemHealthIndicator } from '@/components/dashboard/SystemHealthIndicator';

const drawerWidth = 280;

interface NavigationItem {
  id: string;
  label: string;
  icon: React.ReactNode;
  path: string;
  badge?: number;
  children?: NavigationItem[];
}

interface MainLayoutProps {
  children: React.ReactNode;
}

export const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const { t } = useTranslation();
  const theme = useTheme();
  const router = useRouter();
  const pathname = usePathname();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  const { 
    user, 
    notifications, 
    darkMode, 
    toggleDarkMode, 
    language, 
    setLanguage 
  } = useGlobalStore();
  
  const [drawerOpen, setDrawerOpen] = useState(!isMobile);
  const [userMenuAnchor, setUserMenuAnchor] = useState<null | HTMLElement>(null);
  const [languageMenuAnchor, setLanguageMenuAnchor] = useState<null | HTMLElement>(null);

  // Navigation items
  const navigationItems: NavigationItem[] = [
    {
      id: 'overview',
      label: t('navigation.overview'),
      icon: <DashboardIcon />,
      path: '/',
    },
    {
      id: 'compliance',
      label: t('navigation.compliance'),
      icon: <SecurityIcon />,
      path: '/compliance',
      badge: notifications?.compliance || 0,
    },
    {
      id: 'evaluation',
      label: t('navigation.evaluation'),
      icon: <AssessmentIcon />,
      path: '/evaluation',
    },
    {
      id: 'monitoring',
      label: t('navigation.monitoring'),
      icon: <TimelineIcon />,
      path: '/monitoring',
      badge: notifications?.alerts || 0,
    },
    {
      id: 'settings',
      label: t('navigation.settings'),
      icon: <SettingsIcon />,
      path: '/settings',
    },
  ];

  // Handle drawer toggle
  const handleDrawerToggle = () => {
    setDrawerOpen(!drawerOpen);
  };

  // Handle navigation
  const handleNavigate = (path: string) => {
    router.push(path);
    if (isMobile) {
      setDrawerOpen(false);
    }
  };

  // Handle user menu
  const handleUserMenu = (event: React.MouseEvent<HTMLElement>) => {
    setUserMenuAnchor(event.currentTarget);
  };

  const handleUserMenuClose = () => {
    setUserMenuAnchor(null);
  };

  // Handle language menu
  const handleLanguageMenu = (event: React.MouseEvent<HTMLElement>) => {
    setLanguageMenuAnchor(event.currentTarget);
  };

  const handleLanguageMenuClose = () => {
    setLanguageMenuAnchor(null);
  };

  const handleLanguageChange = (lang: string) => {
    setLanguage(lang);
    handleLanguageMenuClose();
  };

  // Breadcrumb generation
  const generateBreadcrumbs = () => {
    const pathSegments = pathname.split('/').filter(Boolean);
    const breadcrumbs = [
      { label: t('navigation.home'), path: '/' }
    ];
    
    let currentPath = '';
    pathSegments.forEach((segment, index) => {
      currentPath += `/${segment}`;
      const item = navigationItems.find(item => item.path === currentPath);
      if (item) {
        breadcrumbs.push({ label: item.label, path: currentPath });
      }
    });
    
    return breadcrumbs;
  };

  // Responsive drawer behavior
  useEffect(() => {
    setDrawerOpen(!isMobile);
  }, [isMobile]);

  // Drawer content
  const drawerContent = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Logo and title */}
      <Box sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
        <Avatar
          sx={{ 
            width: 40, 
            height: 40, 
            bgcolor: 'primary.main',
            fontSize: '1.2rem'
          }}
        >
          🇸🇦
        </Avatar>
        <Box sx={{ flexGrow: 1 }}>
          <Typography variant="h6" fontWeight="bold" noWrap>
            DoganAI
          </Typography>
          <Typography variant="caption" color="text.secondary" noWrap>
            {t('app.subtitle')}
          </Typography>
        </Box>
        {isMobile && (
          <IconButton onClick={handleDrawerToggle} size="small">
            <ChevronLeftIcon />
          </IconButton>
        )}
      </Box>

      <Divider />

      {/* System health indicator */}
      <Box sx={{ p: 2 }}>
        <SystemHealthIndicator compact />
      </Box>

      <Divider />

      {/* Navigation items */}
      <List sx={{ flexGrow: 1, pt: 1 }}>
        {navigationItems.map((item) => (
          <ListItem key={item.id} disablePadding>
            <ListItemButton
              selected={pathname === item.path}
              onClick={() => handleNavigate(item.path)}
              sx={{
                mx: 1,
                mb: 0.5,
                borderRadius: 2,
                '&.Mui-selected': {
                  bgcolor: 'primary.main',
                  color: 'primary.contrastText',
                  '&:hover': {
                    bgcolor: 'primary.dark',
                  },
                  '& .MuiListItemIcon-root': {
                    color: 'primary.contrastText',
                  },
                },
                '&:hover': {
                  bgcolor: 'action.hover',
                },
              }}
            >
              <ListItemIcon
                sx={{
                  minWidth: 40,
                  color: pathname === item.path ? 'inherit' : 'text.secondary',
                }}
              >
                {item.badge ? (
                  <Badge badgeContent={item.badge} color="error">
                    {item.icon}
                  </Badge>
                ) : (
                  item.icon
                )}
              </ListItemIcon>
              <ListItemText 
                primary={item.label}
                primaryTypographyProps={{
                  fontSize: '0.875rem',
                  fontWeight: pathname === item.path ? 600 : 400,
                }}
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>

      <Divider />

      {/* User info */}
      <Box sx={{ p: 2 }}>
        <Box 
          sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: 2,
            p: 1,
            borderRadius: 2,
            bgcolor: 'background.paper',
            cursor: 'pointer',
            '&:hover': {
              bgcolor: 'action.hover',
            },
          }}
          onClick={handleUserMenu}
        >
          <Avatar sx={{ width: 32, height: 32 }}>
            {user?.name?.charAt(0) || 'U'}
          </Avatar>
          <Box sx={{ flexGrow: 1, minWidth: 0 }}>
            <Typography variant="body2" fontWeight="medium" noWrap>
              {user?.name || t('user.guest')}
            </Typography>
            <Typography variant="caption" color="text.secondary" noWrap>
              {user?.role || t('user.viewer')}
            </Typography>
          </Box>
        </Box>
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      {/* App Bar */}
      <AppBar
        position="fixed"
        sx={{
          width: drawerOpen && !isMobile ? `calc(100% - ${drawerWidth}px)` : '100%',
          ml: drawerOpen && !isMobile ? `${drawerWidth}px` : 0,
          transition: theme.transitions.create(['width', 'margin'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
          bgcolor: 'background.paper',
          color: 'text.primary',
          boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
          backdropFilter: 'blur(10px)',
        }}
      >
        <Toolbar>
          {/* Menu button for mobile or when drawer is closed */}
          {(isMobile || !drawerOpen) && (
            <IconButton
              edge="start"
              onClick={handleDrawerToggle}
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
          )}

          {/* Breadcrumbs */}
          <Box sx={{ flexGrow: 1 }}>
            <Breadcrumbs aria-label="breadcrumb">
              {generateBreadcrumbs().map((crumb, index) => (
                <Link
                  key={index}
                  color={index === generateBreadcrumbs().length - 1 ? 'text.primary' : 'inherit'}
                  href={crumb.path}
                  onClick={(e) => {
                    e.preventDefault();
                    handleNavigate(crumb.path);
                  }}
                  sx={{ 
                    textDecoration: 'none',
                    '&:hover': { textDecoration: 'underline' }
                  }}
                >
                  {index === 0 && <HomeIcon sx={{ mr: 0.5 }} fontSize="inherit" />}
                  {crumb.label}
                </Link>
              ))}
            </Breadcrumbs>
          </Box>

          {/* Action buttons */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {/* Language toggle */}
            <Tooltip title={t('app.changeLanguage')}>
              <IconButton onClick={handleLanguageMenu}>
                <LanguageIcon />
              </IconButton>
            </Tooltip>

            {/* Dark mode toggle */}
            <Tooltip title={t('app.toggleTheme')}>
              <IconButton onClick={toggleDarkMode}>
                {darkMode ? <LightModeIcon /> : <DarkModeIcon />}
              </IconButton>
            </Tooltip>

            {/* Notifications */}
            <Tooltip title={t('app.notifications')}>
              <IconButton>
                <Badge 
                  badgeContent={
                    (notifications?.alerts || 0) + (notifications?.compliance || 0)
                  } 
                  color="error"
                >
                  <NotificationsIcon />
                </Badge>
              </IconButton>
            </Tooltip>

            {/* User menu */}
            <Tooltip title={t('app.userMenu')}>
              <IconButton onClick={handleUserMenu}>
                <AccountIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Drawer */}
      <Drawer
        variant={isMobile ? 'temporary' : 'persistent'}
        open={drawerOpen}
        onClose={handleDrawerToggle}
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
            bgcolor: 'background.paper',
            borderRight: `1px solid ${theme.palette.divider}`,
          },
        }}
        ModalProps={{
          keepMounted: true, // Better open performance on mobile
        }}
      >
        {drawerContent}
      </Drawer>

      {/* Main content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: drawerOpen && !isMobile ? `calc(100% - ${drawerWidth}px)` : '100%',
          minHeight: '100vh',
          transition: theme.transitions.create(['width', 'margin'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
        }}
      >
        <Toolbar /> {/* Spacer for fixed AppBar */}
        
        <AnimatePresence mode="wait">
          <motion.div
            key={pathname}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
            style={{ minHeight: 'calc(100vh - 64px)' }}
          >
            {children}
          </motion.div>
        </AnimatePresence>
      </Box>

      {/* User Menu */}
      <Menu
        anchorEl={userMenuAnchor}
        open={Boolean(userMenuAnchor)}
        onClose={handleUserMenuClose}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        <MenuItem onClick={handleUserMenuClose}>
          {t('user.profile')}
        </MenuItem>
        <MenuItem onClick={handleUserMenuClose}>
          {t('user.settings')}
        </MenuItem>
        <Divider />
        <MenuItem onClick={handleUserMenuClose}>
          {t('user.logout')}
        </MenuItem>
      </Menu>

      {/* Language Menu */}
      <Menu
        anchorEl={languageMenuAnchor}
        open={Boolean(languageMenuAnchor)}
        onClose={handleLanguageMenuClose}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        <MenuItem 
          onClick={() => handleLanguageChange('ar')}
          selected={language === 'ar'}
        >
          العربية
        </MenuItem>
        <MenuItem 
          onClick={() => handleLanguageChange('en')}
          selected={language === 'en'}
        >
          English
        </MenuItem>
      </Menu>
    </Box>
  );
};
