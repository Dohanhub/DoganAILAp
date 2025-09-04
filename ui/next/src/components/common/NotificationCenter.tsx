'use client';

import React, { useState } from 'react';
import {
  IconButton,
  Badge,
  Menu,
  MenuItem,
  Typography,
  Box,
  Divider,
  Button,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  Avatar,
  Tooltip,
} from '@mui/material';
import {
  Notifications as NotificationsIcon,
  NotificationsNone as NotificationsNoneIcon,
  Security as SecurityIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  CheckCircle as CheckIcon,
  MarkEmailRead as MarkReadIcon,
  DeleteSweep as ClearAllIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { useGlobalStore } from '@/stores/GlobalStore';

interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'info' | 'warning' | 'error' | 'success';
  timestamp: Date;
  read: boolean;
  action?: {
    label: string;
    onClick: () => void;
  };
}

const NotificationCenter: React.FC = () => {
  const { notifications } = useGlobalStore();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [notificationList, setNotificationList] = useState<Notification[]>([
    {
      id: '1',
      title: 'NCA Policy Update',
      message: 'New commercial authorization requirements have been published',
      type: 'info',
      timestamp: new Date(Date.now() - 5 * 60 * 1000),
      read: false,
    },
    {
      id: '2',
      title: 'Security Alert',
      message: 'Multiple failed login attempts detected from IP 192.168.1.100',
      type: 'warning',
      timestamp: new Date(Date.now() - 15 * 60 * 1000),
      read: false,
    },
    {
      id: '3',
      title: 'Compliance Check Complete',
      message: 'IBM vendor evaluation completed successfully with 95% compliance score',
      type: 'success',
      timestamp: new Date(Date.now() - 30 * 60 * 1000),
      read: true,
    },
    {
      id: '4',
      title: 'Critical Violation',
      message: 'Data protection policy violation detected in Oracle database configuration',
      type: 'error',
      timestamp: new Date(Date.now() - 60 * 60 * 1000),
      read: false,
    },
    {
      id: '5',
      title: 'System Maintenance',
      message: 'Scheduled maintenance will begin at 2:00 AM UTC tonight',
      type: 'info',
      timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
      read: true,
    },
  ]);

  const unreadCount = notificationList.filter(n => !n.read).length;

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleMarkAsRead = (notificationId: string) => {
    setNotificationList(prev =>
      prev.map(notification =>
        notification.id === notificationId
          ? { ...notification, read: true }
          : notification
      )
    );
  };

  const handleMarkAllAsRead = () => {
    setNotificationList(prev =>
      prev.map(notification => ({ ...notification, read: true }))
    );
  };

  const handleClearAll = () => {
    setNotificationList([]);
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'warning':
        return <WarningIcon color="warning" />;
      case 'error':
        return <SecurityIcon color="error" />;
      case 'success':
        return <CheckIcon color="success" />;
      default:
        return <InfoIcon color="info" />;
    }
  };

  const getNotificationColor = (type: string) => {
    switch (type) {
      case 'warning':
        return 'warning';
      case 'error':
        return 'error';
      case 'success':
        return 'success';
      default:
        return 'info';
    }
  };

  const formatTimestamp = (date: Date) => {
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
    
    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    
    const diffInHours = Math.floor(diffInMinutes / 60);
    if (diffInHours < 24) return `${diffInHours}h ago`;
    
    const diffInDays = Math.floor(diffInHours / 24);
    return `${diffInDays}d ago`;
  };

  return (
    <>
      <Tooltip title="Notifications">
        <IconButton onClick={handleClick} color="inherit">
          <Badge badgeContent={unreadCount} color="error">
            {unreadCount > 0 ? <NotificationsIcon /> : <NotificationsNoneIcon />}
          </Badge>
        </IconButton>
      </Tooltip>
      
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        PaperProps={{
          sx: { width: 400, maxHeight: 500 }
        }}
      >
        {/* Header */}
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">
              Notifications
            </Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
              {unreadCount > 0 && (
                <Tooltip title="Mark all as read">
                  <IconButton size="small" onClick={handleMarkAllAsRead}>
                    <MarkReadIcon />
                  </IconButton>
                </Tooltip>
              )}
              <Tooltip title="Clear all">
                <IconButton size="small" onClick={handleClearAll}>
                  <ClearAllIcon />
                </IconButton>
              </Tooltip>
            </Box>
          </Box>
          
          {unreadCount > 0 && (
            <Typography variant="body2" color="text.secondary">
              You have {unreadCount} unread notification{unreadCount !== 1 ? 's' : ''}
            </Typography>
          )}
        </Box>

        {/* Notifications List */}
        <List sx={{ p: 0, maxHeight: 400, overflow: 'auto' }}>
          <AnimatePresence>
            {notificationList.length === 0 ? (
              <Box sx={{ p: 3, textAlign: 'center' }}>
                <NotificationsNoneIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
                <Typography variant="body2" color="text.secondary">
                  No notifications
                </Typography>
              </Box>
            ) : (
              notificationList.map((notification, index) => (
                <motion.div
                  key={notification.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <ListItem
                    sx={{
                      bgcolor: notification.read ? 'transparent' : 'action.hover',
                      borderLeft: 4,
                      borderLeftColor: `${getNotificationColor(notification.type)}.main`,
                      cursor: 'pointer',
                      '&:hover': { bgcolor: 'action.selected' },
                    }}
                    onClick={() => !notification.read && handleMarkAsRead(notification.id)}
                  >
                    <ListItemIcon>
                      <Avatar
                        sx={{
                          bgcolor: `${getNotificationColor(notification.type)}.light`,
                          color: `${getNotificationColor(notification.type)}.main`,
                          width: 32,
                          height: 32,
                        }}
                      >
                        {getNotificationIcon(notification.type)}
                      </Avatar>
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                          <Typography
                            variant="body2"
                            fontWeight={notification.read ? 'normal' : 'bold'}
                            sx={{ flexGrow: 1 }}
                          >
                            {notification.title}
                          </Typography>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, ml: 1 }}>
                            <Typography variant="caption" color="text.secondary">
                              {formatTimestamp(notification.timestamp)}
                            </Typography>
                            {!notification.read && (
                              <Box
                                sx={{
                                  width: 8,
                                  height: 8,
                                  borderRadius: '50%',
                                  bgcolor: 'primary.main',
                                }}
                              />
                            )}
                          </Box>
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                            {notification.message}
                          </Typography>
                          {notification.action && (
                            <Button
                              size="small"
                              onClick={(e) => {
                                e.stopPropagation();
                                notification.action!.onClick();
                              }}
                              sx={{ mt: 1 }}
                            >
                              {notification.action.label}
                            </Button>
                          )}
                        </Box>
                      }
                    />
                  </ListItem>
                  <Divider />
                </motion.div>
              ))
            )}
          </AnimatePresence>
        </List>

        {/* Footer */}
        {notificationList.length > 0 && (
          <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider', textAlign: 'center' }}>
            <Button size="small" variant="text" onClick={handleClose}>
              View All Notifications
            </Button>
          </Box>
        )}
      </Menu>
    </>
  );
};

export { NotificationCenter };
