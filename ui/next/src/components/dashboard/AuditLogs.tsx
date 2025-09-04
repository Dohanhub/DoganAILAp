'use client';

import React, { useState, useMemo } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Paper,
  IconButton,
  Tooltip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Skeleton,
} from '@mui/material';
import {
  History as HistoryIcon,
  Visibility as ViewIcon,
  Download as DownloadIcon,
  FilterList as FilterIcon,
  Search as SearchIcon,
  Security as SecurityIcon,
  Person as PersonIcon,
  Business as BusinessIcon,
  Policy as PolicyIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
// import { useTranslation } from 'react-i18next';
import { useQuery } from 'react-query';
import { apiClient } from '@/lib/api';

interface AuditLog {
  id: string;
  timestamp: string;
  user: string;
  action: string;
  resource: string;
  vendor?: string;
  policy?: string;
  status: 'success' | 'warning' | 'error';
  details: string;
  ipAddress: string;
  userAgent: string;
  sessionId: string;
}

const AuditLogs: React.FC = () => {
  // const { t } = useTranslation();
  const t = (key: string) => key; // Fallback translation function
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [actionFilter, setActionFilter] = useState('all');
  const [selectedLog, setSelectedLog] = useState<AuditLog | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);

  // Fetch audit logs
  const { data: auditLogs, isLoading, error } = useQuery<AuditLog[]>(
    ['audit-logs', { page, rowsPerPage, searchTerm, statusFilter, actionFilter }],
    async () => {
      try {
        const response = await apiClient.audit.logs({
          page: page + 1,
          limit: rowsPerPage,
          search: searchTerm,
          status: statusFilter !== 'all' ? statusFilter : undefined,
          action: actionFilter !== 'all' ? actionFilter : undefined,
        });
        return response.data;
      } catch (error) {
        console.error('Failed to fetch audit logs:', error);
        // Return mock data for demo
        return generateMockLogs();
      }
    },
    {
      staleTime: 30000, // 30 seconds
      refetchInterval: 60000, // 1 minute
    }
  );

  const generateMockLogs = (): AuditLog[] => {
    const actions = ['login', 'logout', 'evaluate_compliance', 'view_report', 'update_policy', 'create_user'];
    const statuses: ('success' | 'warning' | 'error')[] = ['success', 'warning', 'error'];
    const users = ['admin@doganai.com', 'auditor@doganai.com', 'manager@doganai.com'];
    const vendors = ['IBM', 'Microsoft', 'Oracle', 'SAP', 'AWS'];
    const policies = ['NCA Commercial', 'SAMA Banking', 'MoH Healthcare', 'CITC Telecom'];

    return Array.from({ length: 100 }, (_, index) => ({
      id: `log-${index + 1}`,
      timestamp: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
      user: users[Math.floor(Math.random() * users.length)],
      action: actions[Math.floor(Math.random() * actions.length)],
      resource: Math.random() > 0.5 ? `/api/compliance/evaluate` : `/api/vendors/${vendors[Math.floor(Math.random() * vendors.length)]}`,
      vendor: Math.random() > 0.5 ? vendors[Math.floor(Math.random() * vendors.length)] : undefined,
      policy: Math.random() > 0.3 ? policies[Math.floor(Math.random() * policies.length)] : undefined,
      status: statuses[Math.floor(Math.random() * statuses.length)],
      details: `${actions[Math.floor(Math.random() * actions.length)]} operation completed with status ${statuses[Math.floor(Math.random() * statuses.length)]}`,
      ipAddress: `192.168.1.${Math.floor(Math.random() * 255)}`,
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
      sessionId: `sess-${Math.random().toString(36).substr(2, 9)}`,
    }));
  };

  // Filter and search logs
  const filteredLogs = useMemo(() => {
    if (!auditLogs) return [];

    return auditLogs.filter(log => {
      const matchesSearch = searchTerm === '' || 
        log.user.toLowerCase().includes(searchTerm.toLowerCase()) ||
        log.action.toLowerCase().includes(searchTerm.toLowerCase()) ||
        log.resource.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (log.vendor && log.vendor.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (log.policy && log.policy.toLowerCase().includes(searchTerm.toLowerCase()));

      const matchesStatus = statusFilter === 'all' || log.status === statusFilter;
      const matchesAction = actionFilter === 'all' || log.action === actionFilter;

      return matchesSearch && matchesStatus && matchesAction;
    });
  }, [auditLogs, searchTerm, statusFilter, actionFilter]);

  // Paginated logs
  const paginatedLogs = useMemo(() => {
    const startIndex = page * rowsPerPage;
    return filteredLogs.slice(startIndex, startIndex + rowsPerPage);
  }, [filteredLogs, page, rowsPerPage]);

  const handleViewDetails = (log: AuditLog) => {
    setSelectedLog(log);
    setDetailsOpen(true);
  };

  const handleExport = () => {
    const csvContent = [
      ['Timestamp', 'User', 'Action', 'Resource', 'Status', 'IP Address'],
      ...filteredLogs.map(log => [
        log.timestamp,
        log.user,
        log.action,
        log.resource,
        log.status,
        log.ipAddress,
      ])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `audit-logs-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'success';
      case 'warning':
        return 'warning';
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  const getActionIcon = (action: string) => {
    switch (action) {
      case 'login':
      case 'logout':
        return <PersonIcon fontSize="small" />;
      case 'evaluate_compliance':
        return <SecurityIcon fontSize="small" />;
      case 'view_report':
        return <ViewIcon fontSize="small" />;
      case 'update_policy':
        return <PolicyIcon fontSize="small" />;
      default:
        return <BusinessIcon fontSize="small" />;
    }
  };

  if (error) {
    return (
      <Alert severity="error">
        Failed to load audit logs. Please try again later.
      </Alert>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        <HistoryIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Audit Logs
      </Typography>

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={3} alignItems="center">
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Search logs..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />,
                }}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  label="Status"
                >
                  <MenuItem value="all">All Statuses</MenuItem>
                  <MenuItem value="success">Success</MenuItem>
                  <MenuItem value="warning">Warning</MenuItem>
                  <MenuItem value="error">Error</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Action</InputLabel>
                <Select
                  value={actionFilter}
                  onChange={(e) => setActionFilter(e.target.value)}
                  label="Action"
                >
                  <MenuItem value="all">All Actions</MenuItem>
                  <MenuItem value="login">Login</MenuItem>
                  <MenuItem value="logout">Logout</MenuItem>
                  <MenuItem value="evaluate_compliance">Evaluate Compliance</MenuItem>
                  <MenuItem value="view_report">View Report</MenuItem>
                  <MenuItem value="update_policy">Update Policy</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={2}>
              <Button
                fullWidth
                variant="outlined"
                onClick={handleExport}
                startIcon={<DownloadIcon />}
              >
                Export
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Results Summary */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Results Summary
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Showing {paginatedLogs.length} of {filteredLogs.length} audit log entries
            {searchTerm && ` matching "${searchTerm}"`}
          </Typography>
        </CardContent>
      </Card>

      {/* Audit Logs Table */}
      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Timestamp</TableCell>
                <TableCell>User</TableCell>
                <TableCell>Action</TableCell>
                <TableCell>Resource</TableCell>
                <TableCell>Vendor/Policy</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>IP Address</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {isLoading ? (
                Array.from({ length: rowsPerPage }).map((_, index) => (
                  <TableRow key={index}>
                    {Array.from({ length: 8 }).map((_, cellIndex) => (
                      <TableCell key={cellIndex}>
                        <Skeleton variant="text" />
                      </TableCell>
                    ))}
                  </TableRow>
                ))
              ) : (
                paginatedLogs.map((log, index) => (
                  <motion.tr
                    key={log.id}
                    component={TableRow}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                    hover
                  >
                    <TableCell>
                      <Typography variant="body2">
                        {new Date(log.timestamp).toLocaleString()}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <PersonIcon fontSize="small" color="primary" />
                        <Typography variant="body2">{log.user}</Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {getActionIcon(log.action)}
                        <Typography variant="body2">
                          {log.action.replace('_', ' ').toUpperCase()}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.75rem' }}>
                        {log.resource}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                        {log.vendor && (
                          <Chip label={log.vendor} size="small" color="primary" variant="outlined" />
                        )}
                        {log.policy && (
                          <Chip label={log.policy} size="small" color="secondary" variant="outlined" />
                        )}
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={log.status.toUpperCase()}
                        size="small"
                        color={getStatusColor(log.status) as any}
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.75rem' }}>
                        {log.ipAddress}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Tooltip title="View Details">
                        <IconButton
                          size="small"
                          onClick={() => handleViewDetails(log)}
                        >
                          <ViewIcon />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </motion.tr>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[10, 25, 50, 100]}
          component="div"
          count={filteredLogs.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={(_, newPage) => setPage(newPage)}
          onRowsPerPageChange={(e) => {
            setRowsPerPage(parseInt(e.target.value, 10));
            setPage(0);
          }}
        />
      </Card>

      {/* Details Dialog */}
      <Dialog
        open={detailsOpen}
        onClose={() => setDetailsOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Audit Log Details
        </DialogTitle>
        <DialogContent>
          {selectedLog && (
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" color="text.secondary">
                  Timestamp
                </Typography>
                <Typography variant="body1">
                  {new Date(selectedLog.timestamp).toLocaleString()}
                </Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" color="text.secondary">
                  User
                </Typography>
                <Typography variant="body1">{selectedLog.user}</Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" color="text.secondary">
                  Action
                </Typography>
                <Typography variant="body1">{selectedLog.action}</Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" color="text.secondary">
                  Status
                </Typography>
                <Chip
                  label={selectedLog.status.toUpperCase()}
                  color={getStatusColor(selectedLog.status) as any}
                  size="small"
                />
              </Grid>
              <Grid item xs={12}>
                <Typography variant="subtitle2" color="text.secondary">
                  Resource
                </Typography>
                <Typography variant="body1" sx={{ fontFamily: 'monospace' }}>
                  {selectedLog.resource}
                </Typography>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="subtitle2" color="text.secondary">
                  Details
                </Typography>
                <Typography variant="body1">{selectedLog.details}</Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" color="text.secondary">
                  IP Address
                </Typography>
                <Typography variant="body1">{selectedLog.ipAddress}</Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" color="text.secondary">
                  Session ID
                </Typography>
                <Typography variant="body1" sx={{ fontFamily: 'monospace' }}>
                  {selectedLog.sessionId}
                </Typography>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="subtitle2" color="text.secondary">
                  User Agent
                </Typography>
                <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.75rem' }}>
                  {selectedLog.userAgent}
                </Typography>
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailsOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export { AuditLogs };
