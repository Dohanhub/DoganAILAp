# DoganAI Compliance Kit - End-to-End Testing

This directory contains comprehensive end-to-end tests for the DoganAI Compliance Kit platform using Playwright.

## Test Coverage

### 🔧 API Tests (`api-comprehensive.spec.ts`)
- **Health & System Checks**: Platform health, metrics, system status
- **Authentication Flow**: Registration, login, token validation, security
- **Organization Management**: CRUD operations, data validation
- **Framework Management**: Saudi & international frameworks, controls
- **Assessment Management**: Create, execute, complete assessments
- **Risk Management**: Risk creation, calculation, scoring
- **Analytics & Reporting**: Dashboard data, trends, report generation
- **Security Tests**: CORS, authentication, SQL injection protection
- **Data Validation**: Input validation, error handling
- **Performance Tests**: Response times, load handling

### 🖥️ UI Tests (`ui-comprehensive.spec.ts`)
- **Landing Page & Navigation**: Homepage, responsive design, navigation
- **Authentication Flow**: Login/register forms, validation, error handling
- **Dashboard & Analytics**: Metrics display, real-time data, charts
- **Organization Management**: Organization CRUD via UI
- **Assessment Management**: Assessment workflow, framework selection
- **Risk Management**: Risk creation and management interface
- **Reporting**: Report generation and download
- **Accessibility**: Arabic support, keyboard navigation, contrast
- **Error Handling**: 404 pages, network errors, form validation
- **Performance**: Page load times, image loading

### 📋 Basic Tests (`basic.spec.ts`)
- Homepage loading
- Login functionality
- Standards page rendering

### 📎 Evidence Tests (`evidence.spec.ts`)
- File upload functionality
- Evidence management

## Setup & Installation

1. **Install Dependencies**:
   ```bash
   cd e2e
   npm install
   npm run install  # Install Playwright browsers
   ```

2. **Environment Setup**:
   Set the following environment variables:
   ```bash
   DATABASE_URL=postgresql://postgres:password@localhost:5432/doganai_test
   SECRET_KEY=test-secret-key-for-e2e-testing-only
   API_BASE=http://localhost:8000
   WEB=http://localhost:3001
   ```

3. **Start Services**:
   The tests will automatically start the backend and frontend services, but you can also run them manually:
   ```bash
   # Backend (in backend/ directory)
   python -m uvicorn server_complete:app --host 0.0.0.0 --port 8000

   # Frontend (in frontend/ directory)
   npm run dev
   ```

## Running Tests

### All Tests
```bash
npm test
```

### Specific Test Suites
```bash
npm run test:api          # API tests only
npm run test:ui-only      # UI tests only
npm run test:basic        # Basic tests only
npm run test:evidence     # Evidence tests only
```

### Interactive Testing
```bash
npm run test:headed       # Run with browser visible
npm run test:ui           # Interactive UI mode
npm run test:debug        # Debug mode
```

### View Reports
```bash
npm run report            # Open HTML report
```

## Test Configuration

- **Browsers**: Chrome, Firefox, Safari, Mobile Chrome, Mobile Safari, Edge
- **Parallel Execution**: Enabled for faster test runs
- **Retries**: 2 retries on CI, 0 locally
- **Timeouts**: 60s test timeout, 30s action timeout
- **Screenshots**: On failure only
- **Videos**: Retained on failure
- **Traces**: On first retry

## Security Testing

The test suite includes comprehensive security validations:

✅ **CORS Configuration**: Validates secure CORS settings (no wildcards)
✅ **Authentication**: Tests protected endpoints require valid tokens
✅ **SQL Injection Protection**: Tests malicious input handling
✅ **Rate Limiting**: Validates auth endpoint protection
✅ **Input Validation**: Tests form validation and data sanitization

## Performance Testing

Performance benchmarks included:
- Health endpoint: < 1 second response
- Dashboard stats: < 5 seconds response
- Page load times: < 5 seconds
- Image loading validation

## Arabic Language Support

Tests validate Arabic language functionality:
- Language switcher functionality
- Arabic text rendering
- RTL layout support
- Bilingual form validation

## Accessibility Testing

Accessibility validations include:
- Keyboard navigation
- Color contrast checks
- Screen reader compatibility
- Focus management

## CI/CD Integration

The test suite is configured for CI/CD with:
- JUnit XML reports for test results
- JSON reports for detailed analysis
- HTML reports for visual review
- Automatic service startup/teardown

## Troubleshooting

### Common Issues

1. **Services not starting**: Check DATABASE_URL and SECRET_KEY environment variables
2. **Port conflicts**: Ensure ports 8000 and 3001 are available
3. **Database connection**: Verify PostgreSQL is running and accessible
4. **Browser installation**: Run `npm run install` to install Playwright browsers

### Debug Mode
```bash
npm run test:debug
```

### Verbose Logging
```bash
DEBUG=pw:api npm test
```

## Test Data

Tests use isolated test data:
- Test user: `e2e-test@doganai.com`
- Test organization: Dynamic names with timestamps
- Test risks: Automated risk scenarios
- Test assessments: Framework-based compliance tests

## Contributing

When adding new tests:
1. Follow existing naming conventions
2. Add appropriate test data cleanup
3. Include both positive and negative test cases
4. Update this README with new test coverage
5. Ensure tests are deterministic and can run in parallel

## Security Compliance

This test suite validates the security remediations mentioned in the project memories:
- ✅ Fixed CORS wildcard vulnerabilities
- ✅ Eliminated hardcoded secrets
- ✅ Environment variable enforcement
- ✅ Kubernetes security configurations
- ✅ Database model security
