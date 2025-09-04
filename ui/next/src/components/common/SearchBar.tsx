'use client';

import React, { useState } from 'react';
import {
  TextField,
  InputAdornment,
  IconButton,
  Autocomplete,
  Paper,
  Typography,
  Box,
  Chip,
} from '@mui/material';
import {
  Search as SearchIcon,
  Clear as ClearIcon,
  History as HistoryIcon,
  TrendingUp as TrendingIcon,
} from '@mui/icons-material';

interface SearchBarProps {
  placeholder?: string;
  onSearch?: (query: string) => void;
  suggestions?: string[];
}

const SearchBar: React.FC<SearchBarProps> = ({ 
  placeholder = "Search...", 
  onSearch,
  suggestions = []
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchHistory, setSearchHistory] = useState<string[]>([
    'NCA compliance policy',
    'SAMA banking regulations',
    'vendor evaluation report',
    'audit logs',
  ]);

  const popularSearches = [
    'compliance status',
    'security alerts',
    'system health',
    'performance metrics',
  ];

  const allSuggestions = [
    ...searchHistory.map(item => ({ label: item, type: 'history' })),
    ...popularSearches.map(item => ({ label: item, type: 'popular' })),
    ...suggestions.map(item => ({ label: item, type: 'suggestion' })),
  ];

  const handleSearch = (query: string) => {
    if (query.trim()) {
      setSearchQuery(query);
      
      // Add to history if not already present
      if (!searchHistory.includes(query)) {
        setSearchHistory(prev => [query, ...prev.slice(0, 4)]);
      }
      
      onSearch?.(query);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter') {
      handleSearch(searchQuery);
    }
  };

  const handleClear = () => {
    setSearchQuery('');
    onSearch?.('');
  };

  const getOptionIcon = (type: string) => {
    switch (type) {
      case 'history':
        return <HistoryIcon fontSize="small" color="action" />;
      case 'popular':
        return <TrendingIcon fontSize="small" color="action" />;
      default:
        return <SearchIcon fontSize="small" color="action" />;
    }
  };

  return (
    <Autocomplete
      freeSolo
      options={allSuggestions}
      getOptionLabel={(option) => typeof option === 'string' ? option : option.label}
      value={searchQuery}
      onInputChange={(_, newValue) => setSearchQuery(newValue)}
      onChange={(_, value) => {
        if (value) {
          const query = typeof value === 'string' ? value : value.label;
          handleSearch(query);
        }
      }}
      renderInput={(params) => (
        <TextField
          {...params}
          placeholder={placeholder}
          size="small"
          onKeyPress={handleKeyPress}
          InputProps={{
            ...params.InputProps,
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon color="action" />
              </InputAdornment>
            ),
            endAdornment: searchQuery ? (
              <InputAdornment position="end">
                <IconButton size="small" onClick={handleClear}>
                  <ClearIcon />
                </IconButton>
              </InputAdornment>
            ) : null,
          }}
          sx={{
            minWidth: 250,
            '& .MuiOutlinedInput-root': {
              bgcolor: 'background.paper',
            },
          }}
        />
      )}
      renderOption={(props, option) => (
        <li {...props} key={option.label}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
            {getOptionIcon(option.type)}
            <Typography variant="body2" sx={{ flexGrow: 1 }}>
              {option.label}
            </Typography>
            {option.type === 'popular' && (
              <Chip label="Popular" size="small" variant="outlined" />
            )}
          </Box>
        </li>
      )}
      PaperComponent={(props) => (
        <Paper {...props} sx={{ mt: 1 }}>
          {allSuggestions.length > 0 && (
            <Box sx={{ p: 1, borderBottom: 1, borderColor: 'divider' }}>
              <Typography variant="caption" color="text.secondary">
                Recent searches and suggestions
              </Typography>
            </Box>
          )}
          {props.children}
        </Paper>
      )}
    />
  );
};

export { SearchBar };
