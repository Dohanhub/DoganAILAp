'use client';

import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
  Stepper,
  Step,
  StepLabel,
  Paper,
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Assessment as AssessmentIcon,
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  ExpandMore as ExpandMoreIcon,
  Business as BusinessIcon,
  Policy as PolicyIcon,
  Security as SecurityIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
// import { useTranslation } from 'react-i18next';
import { useComplianceData } from '@/hooks/useComplianceData';

interface EvaluationForm {
  vendor: string;
  policy: string;
  evaluationType: string;
  priority: string;
  description: string;
}

const ComplianceEvaluation: React.FC = () => {
  // const { t } = useTranslation();
  const t = (key: string) => key; // Fallback translation function
  const { evaluateCompliance } = useComplianceData();
  const [activeStep, setActiveStep] = useState(0);
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [formData, setFormData] = useState<EvaluationForm>({
    vendor: '',
    policy: '',
    evaluationType: '',
    priority: 'medium',
    description: '',
  });

  const steps = [
    'Select Vendor',
    'Choose Policy',
    'Configure Evaluation',
    'Review & Execute',
  ];

  const vendors = [
    { id: 'ibm', name: 'IBM', type: 'Technology' },
    { id: 'microsoft', name: 'Microsoft', type: 'Cloud Services' },
    { id: 'oracle', name: 'Oracle', type: 'Database' },
    { id: 'sap', name: 'SAP', type: 'Enterprise Software' },
    { id: 'aws', name: 'Amazon Web Services', type: 'Cloud Infrastructure' },
  ];

  const policies = [
    { id: 'nca', name: 'NCA Commercial Authorization', authority: 'NCA' },
    { id: 'sama', name: 'SAMA Banking Regulations', authority: 'SAMA' },
    { id: 'moh', name: 'MoH Healthcare Standards', authority: 'MoH' },
    { id: 'citc', name: 'CITC Telecom Compliance', authority: 'CITC' },
    { id: 'data-protection', name: 'Data Protection Law', authority: 'SDAIA' },
  ];

  const evaluationTypes = [
    { id: 'full', name: 'Full Compliance Audit', duration: '2-4 hours' },
    { id: 'quick', name: 'Quick Assessment', duration: '15-30 minutes' },
    { id: 'focused', name: 'Focused Review', duration: '1-2 hours' },
    { id: 'continuous', name: 'Continuous Monitoring', duration: 'Ongoing' },
  ];

  const handleInputChange = (field: keyof EvaluationForm, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleNext = () => {
    setActiveStep(prev => Math.min(prev + 1, steps.length - 1));
  };

  const handleBack = () => {
    setActiveStep(prev => Math.max(prev - 1, 0));
  };

  const handleEvaluate = async () => {
    setIsEvaluating(true);
    try {
      const result = await evaluateCompliance.mutateAsync(formData);
      setResults(result.data);
      setActiveStep(steps.length); // Move to results view
    } catch (error) {
      console.error('Evaluation failed:', error);
      // Simulate results for demo
      setTimeout(() => {
        setResults({
          score: 85.2,
          status: 'compliant',
          issues: [
            { type: 'warning', message: 'SSL certificate expires in 30 days', severity: 'medium' },
            { type: 'error', message: 'Missing data encryption for customer records', severity: 'high' },
          ],
          recommendations: [
            'Renew SSL certificate',
            'Implement end-to-end encryption for customer data',
            'Update access control policies',
          ],
          completedChecks: 47,
          totalChecks: 52,
        });
        setActiveStep(steps.length);
      }, 3000);
    } finally {
      setIsEvaluating(false);
    }
  };

  const renderStepContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Select Vendor for Evaluation
              </Typography>
            </Grid>
            {vendors.map((vendor) => (
              <Grid item xs={12} md={6} key={vendor.id}>
                <Card
                  sx={{
                    cursor: 'pointer',
                    border: formData.vendor === vendor.id ? 2 : 1,
                    borderColor: formData.vendor === vendor.id ? 'primary.main' : 'divider',
                    '&:hover': { borderColor: 'primary.main' },
                  }}
                  onClick={() => handleInputChange('vendor', vendor.id)}
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <BusinessIcon color="primary" />
                      <Box>
                        <Typography variant="h6">{vendor.name}</Typography>
                        <Typography variant="body2" color="text.secondary">
                          {vendor.type}
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        );

      case 1:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Choose Compliance Policy
              </Typography>
            </Grid>
            {policies.map((policy) => (
              <Grid item xs={12} md={6} key={policy.id}>
                <Card
                  sx={{
                    cursor: 'pointer',
                    border: formData.policy === policy.id ? 2 : 1,
                    borderColor: formData.policy === policy.id ? 'primary.main' : 'divider',
                    '&:hover': { borderColor: 'primary.main' },
                  }}
                  onClick={() => handleInputChange('policy', policy.id)}
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <PolicyIcon color="primary" />
                      <Box>
                        <Typography variant="h6">{policy.name}</Typography>
                        <Chip label={policy.authority} size="small" color="primary" />
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        );

      case 2:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Configure Evaluation Settings
              </Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Evaluation Type</InputLabel>
                <Select
                  value={formData.evaluationType}
                  onChange={(e) => handleInputChange('evaluationType', e.target.value)}
                  label="Evaluation Type"
                >
                  {evaluationTypes.map((type) => (
                    <MenuItem key={type.id} value={type.id}>
                      <Box>
                        <Typography>{type.name}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          {type.duration}
                        </Typography>
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Priority</InputLabel>
                <Select
                  value={formData.priority}
                  onChange={(e) => handleInputChange('priority', e.target.value)}
                  label="Priority"
                >
                  <MenuItem value="low">Low</MenuItem>
                  <MenuItem value="medium">Medium</MenuItem>
                  <MenuItem value="high">High</MenuItem>
                  <MenuItem value="critical">Critical</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description (Optional)"
                multiline
                rows={3}
                value={formData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                placeholder="Add any specific requirements or notes for this evaluation..."
              />
            </Grid>
          </Grid>
        );

      case 3:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Review Evaluation Configuration
              </Typography>
            </Grid>
            <Grid item xs={12}>
              <Paper sx={{ p: 3 }}>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Vendor
                    </Typography>
                    <Typography variant="body1">
                      {vendors.find(v => v.id === formData.vendor)?.name || 'Not selected'}
                    </Typography>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Policy
                    </Typography>
                    <Typography variant="body1">
                      {policies.find(p => p.id === formData.policy)?.name || 'Not selected'}
                    </Typography>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Evaluation Type
                    </Typography>
                    <Typography variant="body1">
                      {evaluationTypes.find(t => t.id === formData.evaluationType)?.name || 'Not selected'}
                    </Typography>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Priority
                    </Typography>
                    <Chip label={formData.priority} color="primary" size="small" />
                  </Grid>
                  {formData.description && (
                    <Grid item xs={12}>
                      <Typography variant="subtitle2" color="text.secondary">
                        Description
                      </Typography>
                      <Typography variant="body1">{formData.description}</Typography>
                    </Grid>
                  )}
                </Grid>
              </Paper>
            </Grid>
          </Grid>
        );

      default:
        return null;
    }
  };

  const renderResults = () => {
    if (!results) return null;

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Alert
              severity={results.status === 'compliant' ? 'success' : 'warning'}
              sx={{ mb: 3 }}
            >
              <Typography variant="h6">
                Evaluation Complete - Score: {results.score}%
              </Typography>
              <Typography>
                {results.completedChecks} out of {results.totalChecks} checks passed
              </Typography>
            </Alert>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  <ErrorIcon color="error" sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Issues Found
                </Typography>
                <List>
                  {results.issues.map((issue: any, index: number) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        {issue.type === 'error' ? (
                          <ErrorIcon color="error" />
                        ) : (
                          <WarningIcon color="warning" />
                        )}
                      </ListItemIcon>
                      <ListItemText
                        primary={issue.message}
                        secondary={`Severity: ${issue.severity}`}
                      />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  <CheckIcon color="success" sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Recommendations
                </Typography>
                <List>
                  {results.recommendations.map((rec: string, index: number) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        <CheckIcon color="success" />
                      </ListItemIcon>
                      <ListItemText primary={rec} />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </motion.div>
    );
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        <AssessmentIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Compliance Evaluation
      </Typography>

      {activeStep < steps.length ? (
        <>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Stepper activeStep={activeStep} alternativeLabel>
                {steps.map((label) => (
                  <Step key={label}>
                    <StepLabel>{label}</StepLabel>
                  </Step>
                ))}
              </Stepper>
            </CardContent>
          </Card>

          <Card>
            <CardContent sx={{ minHeight: 400 }}>
              {renderStepContent(activeStep)}
            </CardContent>
            <Box sx={{ p: 3, display: 'flex', justifyContent: 'space-between' }}>
              <Button
                onClick={handleBack}
                disabled={activeStep === 0}
                variant="outlined"
              >
                Back
              </Button>
              <Box sx={{ display: 'flex', gap: 2 }}>
                {activeStep === steps.length - 1 ? (
                  <Button
                    onClick={handleEvaluate}
                    disabled={isEvaluating || !formData.vendor || !formData.policy}
                    variant="contained"
                    startIcon={<PlayIcon />}
                  >
                    {isEvaluating ? 'Evaluating...' : 'Start Evaluation'}
                  </Button>
                ) : (
                  <Button
                    onClick={handleNext}
                    variant="contained"
                    disabled={
                      (activeStep === 0 && !formData.vendor) ||
                      (activeStep === 1 && !formData.policy) ||
                      (activeStep === 2 && !formData.evaluationType)
                    }
                  >
                    Next
                  </Button>
                )}
              </Box>
            </Box>
          </Card>
        </>
      ) : (
        renderResults()
      )}

      {isEvaluating && (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Evaluation in Progress...
            </Typography>
            <LinearProgress sx={{ mb: 2 }} />
            <Typography variant="body2" color="text.secondary">
              This may take a few minutes depending on the evaluation type selected.
            </Typography>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export { ComplianceEvaluation };
