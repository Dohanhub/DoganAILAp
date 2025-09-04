'use client';

import React from 'react';
import {
  IconButton,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Tooltip,
} from '@mui/material';
import {
  Language as LanguageIcon,
  Translate as TranslateIcon,
} from '@mui/icons-material';
import { useGlobalStore } from '@/stores/GlobalStore';

const LanguageSwitch: React.FC = () => {
  const { language, setLanguage } = useGlobalStore();
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);

  const languages = [
    { code: 'ar', name: 'العربية', flag: '🇸🇦' },
    { code: 'en', name: 'English', flag: '🇺🇸' },
  ];

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLanguageChange = (langCode: 'ar' | 'en') => {
    setLanguage(langCode);
    handleClose();
  };

  const currentLanguage = languages.find(lang => lang.code === language);

  return (
    <>
      <Tooltip title="Change Language">
        <IconButton onClick={handleClick} color="inherit">
          <LanguageIcon />
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
      >
        {languages.map((lang) => (
          <MenuItem
            key={lang.code}
            onClick={() => handleLanguageChange(lang.code as 'ar' | 'en')}
            selected={language === lang.code}
          >
            <ListItemIcon>
              <span style={{ fontSize: '1.2em' }}>{lang.flag}</span>
            </ListItemIcon>
            <ListItemText>
              {lang.name}
            </ListItemText>
          </MenuItem>
        ))}
      </Menu>
    </>
  );
};

export { LanguageSwitch };
