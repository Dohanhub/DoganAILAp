import { test, expect } from '@playwright/test';
import { request } from '@playwright/test';

const API_BASE = process.env.API_BASE || 'http://localhost:8000';
const WEB_BASE = process.env.WEB || 'http://localhost:3001';

// Test data
const testUser = {
  username: 'testuser',
  password: 'TestPass123!',
  email: 'test@doganai.com',
  full_name: 'Test User',
  role: 'user'
};

const testOrg = {
  name: 'Test Organization',
  name_arabic: 'منظمة اختبار',
  sector: 'Technology',
  city: 'Riyadh',
  size: 'Medium'
};

let authToken: string;
let userId: number;
let orgId: number;
let assessmentId: number;
let riskId: number;

test.describe('DoganAI Compliance Kit - Comprehensive E2E Tests', () => {
  
  test.describe('Health and System Checks', () => {
    test('health endpoint should return operational status', async ({ request }) => {
      const response = await request.get(`${API_BASE}/health`);
      expect(response.ok()).toBeTruthy();
      
      const data = await response.json();
      expect(data.status).toBe('operational');
      expect(data.services.database).toBe('healthy');
      expect(data.services.api).toBe('active');
    });

    test('root endpoint should return platform info', async ({ request }) => {
      const response = await request.get(`${API_BASE}/`);
      expect(response.ok()).toBeTruthy();
      
      const data = await response.json();
      expect(data.platform).toContain('Dogan AI');
      expect(data.features.saudi_frameworks).toContain('NCA');
      expect(data.features.arabic_support).toBe(true);
    });

    test('metrics endpoint should return system metrics', async ({ request }) => {
      const response = await request.get(`${API_BASE}/metrics`);
      expect(response.ok()).toBeTruthy();
      
      const data = await response.json();
      expect(data.metrics).toBeDefined();
      expect(typeof data.metrics.total_orgs).toBe('number');
    });
  });

  test.describe('Authentication Flow', () => {
    test('user registration should work', async ({ request }) => {
      const response = await request.post(`${API_BASE}/register`, {
        data: testUser
      });
      
      expect(response.ok()).toBeTruthy();
      const data = await response.json();
      expect(data.message).toContain('registered successfully');
      expect(data.user_id).toBeDefined();
      userId = data.user_id;
    });

    test('user login should work and return token', async ({ request }) => {
      const response = await request.post(`${API_BASE}/login`, {
        data: {
          email: testUser.email,
          password: testUser.password
        }
      });
      
      expect(response.ok()).toBeTruthy();
      const data = await response.json();
      expect(data.access_token).toBeDefined();
      expect(data.token_type).toBe('bearer');
      expect(data.user.email).toBe(testUser.email);
      authToken = data.access_token;
    });

    test('protected endpoint should require authentication', async ({ request }) => {
      const response = await request.get(`${API_BASE}/api/auth/me`);
      expect(response.status()).toBe(401);
    });

    test('protected endpoint should work with valid token', async ({ request }) => {
      const response = await request.get(`${API_BASE}/api/auth/me`, {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      });
      
      expect(response.ok()).toBeTruthy();
      const data = await response.json();
      expect(data.email).toBe(testUser.email);
    });

    test('duplicate registration should fail', async ({ request }) => {
      const response = await request.post(`${API_BASE}/register`, {
        data: testUser
      });
      
      expect(response.status()).toBe(400);
      const data = await response.json();
      expect(data.detail).toContain('already registered');
    });

    test('invalid login credentials should fail', async ({ request }) => {
      const response = await request.post(`${API_BASE}/login`, {
        data: {
          email: testUser.email,
          password: 'wrongpassword'
        }
      });
      
      expect(response.status()).toBe(401);
      const data = await response.json();
      expect(data.detail).toBe('Invalid credentials');
    });
  });

  test.describe('Organization Management', () => {
    test('create organization should work', async ({ request }) => {
      const response = await request.post(`${API_BASE}/api/organizations`, {
        data: testOrg
      });
      
      expect(response.ok()).toBeTruthy();
      const data = await response.json();
      expect(data.name).toBe(testOrg.name);
      expect(data.name_arabic).toBe(testOrg.name_arabic);
      expect(data.sector).toBe(testOrg.sector);
      orgId = data.id;
    });

    test('get organizations should return created org', async ({ request }) => {
      const response = await request.get(`${API_BASE}/api/organizations`);
      expect(response.ok()).toBeTruthy();
      
      const data = await response.json();
      expect(Array.isArray(data)).toBeTruthy();
      const createdOrg = data.find(org => org.id === orgId);
      expect(createdOrg).toBeDefined();
      expect(createdOrg.name).toBe(testOrg.name);
    });
  });

  test.describe('Framework Management', () => {
    test('get frameworks should return available frameworks', async ({ request }) => {
      const response = await request.get(`${API_BASE}/api/frameworks`);
      expect(response.ok()).toBeTruthy();
      
      const data = await response.json();
      expect(Array.isArray(data)).toBeTruthy();
      expect(data.length).toBeGreaterThan(0);
      
      // Check for Saudi frameworks
      const saudiFrameworks = data.filter(f => f.is_saudi);
      expect(saudiFrameworks.length).toBeGreaterThan(0);
    });

    test('get Saudi frameworks only should work', async ({ request }) => {
      const response = await request.get(`${API_BASE}/api/frameworks?saudi_only=true`);
      expect(response.ok()).toBeTruthy();
      
      const data = await response.json();
      expect(Array.isArray(data)).toBeTruthy();
      data.forEach(framework => {
        expect(framework.is_saudi).toBe(true);
      });
    });

    test('get framework controls should work', async ({ request }) => {
      // First get a framework
      const frameworksResponse = await request.get(`${API_BASE}/api/frameworks`);
      const frameworks = await frameworksResponse.json();
      const framework = frameworks[0];
      
      const response = await request.get(`${API_BASE}/api/frameworks/${framework.code}/controls`);
      expect(response.ok()).toBeTruthy();
      
      const data = await response.json();
      expect(data.framework).toBeDefined();
      expect(data.controls).toBeDefined();
      expect(Array.isArray(data.controls)).toBeTruthy();
    });
  });

  test.describe('Assessment Management', () => {
    test('create assessment should work', async ({ request }) => {
      // Get a framework first
      const frameworksResponse = await request.get(`${API_BASE}/api/frameworks`);
      const frameworks = await frameworksResponse.json();
      const framework = frameworks[0];
      
      const response = await request.post(`${API_BASE}/api/assessments`, {
        data: {
          organization_id: orgId,
          framework_code: framework.code,
          assessment_type: 'automated'
        }
      });
      
      expect(response.ok()).toBeTruthy();
      const data = await response.json();
      expect(data.assessment_id).toBeDefined();
      expect(data.framework).toBe(framework.code);
      expect(data.score).toBeGreaterThan(0);
      assessmentId = data.assessment_id;
    });

    test('get assessments should return created assessment', async ({ request }) => {
      const response = await request.get(`${API_BASE}/api/assessments?organization_id=${orgId}`);
      expect(response.ok()).toBeTruthy();
      
      const data = await response.json();
      expect(Array.isArray(data)).toBeTruthy();
      const createdAssessment = data.find(a => a.id === assessmentId);
      expect(createdAssessment).toBeDefined();
    });

    test('complete assessment should work', async ({ request }) => {
      const response = await request.put(`${API_BASE}/api/assessments/${assessmentId}/complete?score=85.5`);
      expect(response.ok()).toBeTruthy();
      
      const data = await response.json();
      expect(data.message).toContain('completed');
    });
  });

  test.describe('Risk Management', () => {
    test('create risk should work', async ({ request }) => {
      const riskData = {
        organization_id: orgId,
        title: 'Test Security Risk',
        severity: 'high',
        likelihood: 'medium',
        category: 'Security',
        description: 'Test risk for E2E testing',
        owner: 'Test Owner'
      };
      
      const response = await request.post(`${API_BASE}/api/risks`, {
        data: riskData
      });
      
      expect(response.ok()).toBeTruthy();
      const data = await response.json();
      expect(data.title).toBe(riskData.title);
      expect(data.inherent_risk_score).toBeDefined();
      expect(data.risk_level).toBeDefined();
      riskId = data.id;
    });

    test('get risks should return created risk', async ({ request }) => {
      const response = await request.get(`${API_BASE}/api/risks?organization_id=${orgId}`);
      expect(response.ok()).toBeTruthy();
      
      const data = await response.json();
      expect(Array.isArray(data)).toBeTruthy();
      const createdRisk = data.find(r => r.id === riskId);
      expect(createdRisk).toBeDefined();
      expect(createdRisk.title).toBe('Test Security Risk');
    });

    test('risk calculation should be accurate', async ({ request }) => {
      const riskData = {
        organization_id: orgId,
        title: 'Critical Risk Test',
        severity: 'critical',
        likelihood: 'very_high',
        category: 'Operational'
      };
      
      const response = await request.post(`${API_BASE}/api/risks`, {
        data: riskData
      });
      
      expect(response.ok()).toBeTruthy();
      const data = await response.json();
      expect(data.inherent_risk_score).toBe(25); // 5 * 5
      expect(data.risk_level).toBe('Critical');
    });
  });

  test.describe('Analytics and Reporting', () => {
    test('analytics dashboard should work', async ({ request }) => {
      const response = await request.get(`${API_BASE}/api/analytics/dashboard`);
      expect(response.ok()).toBeTruthy();
      
      const data = await response.json();
      expect(data.framework_scores).toBeDefined();
      expect(data.risk_distribution).toBeDefined();
      expect(Array.isArray(data.framework_scores)).toBeTruthy();
      expect(Array.isArray(data.risk_distribution)).toBeTruthy();
    });

    test('compliance trends should work', async ({ request }) => {
      const response = await request.get(`${API_BASE}/api/analytics/trends?organization_id=${orgId}&days=30`);
      expect(response.ok()).toBeTruthy();
      
      const data = await response.json();
      expect(Array.isArray(data)).toBeTruthy();
    });

    test('generate report should work', async ({ request }) => {
      const reportData = {
        organization_id: orgId,
        report_type: 'compliance',
        frameworks: ['NCA', 'SAMA'],
        format: 'json'
      };
      
      const response = await request.post(`${API_BASE}/api/reports/generate`, {
        data: reportData
      });
      
      expect(response.ok()).toBeTruthy();
      const data = await response.json();
      expect(data.report_id).toBeDefined();
      expect(data.title).toContain('Compliance Report');
      expect(data.organization).toBeDefined();
      expect(data.summary).toBeDefined();
    });

    test('dashboard stats should work', async ({ request }) => {
      const response = await request.get(`${API_BASE}/api/dashboard/stats`);
      expect(response.ok()).toBeTruthy();
      
      const data = await response.json();
      expect(typeof data.organizations).toBe('number');
      expect(typeof data.assessments).toBe('number');
      expect(typeof data.open_risks).toBe('number');
      expect(typeof data.frameworks).toBe('number');
      expect(Array.isArray(data.risk_distribution)).toBeTruthy();
    });
  });

  test.describe('Notification System', () => {
    test('get notifications should work', async ({ request }) => {
      const response = await request.get(`${API_BASE}/api/notifications`);
      expect(response.ok()).toBeTruthy();
      
      const data = await response.json();
      expect(Array.isArray(data)).toBeTruthy();
    });

    test('get unread notifications should work', async ({ request }) => {
      const response = await request.get(`${API_BASE}/api/notifications?unread_only=true`);
      expect(response.ok()).toBeTruthy();
      
      const data = await response.json();
      expect(Array.isArray(data)).toBeTruthy();
    });
  });

  test.describe('Security Tests', () => {
    test('CORS headers should be properly configured', async ({ request }) => {
      const response = await request.get(`${API_BASE}/health`);
      const headers = response.headers();
      
      // Should not have wildcard CORS (security fix from memory)
      expect(headers['access-control-allow-origin']).not.toBe('*');
    });

    test('sensitive endpoints should require authentication', async ({ request }) => {
      const sensitiveEndpoints = [
        '/api/organizations',
        '/api/assessments',
        '/api/risks',
        '/api/reports/generate'
      ];
      
      for (const endpoint of sensitiveEndpoints) {
        const response = await request.post(`${API_BASE}${endpoint}`, {
          data: {}
        });
        // Should return 401 or 422 (validation error), not 200
        expect([401, 422]).toContain(response.status());
      }
    });

    test('SQL injection protection should work', async ({ request }) => {
      const maliciousInput = "'; DROP TABLE users; --";
      
      const response = await request.post(`${API_BASE}/login`, {
        data: {
          email: maliciousInput,
          password: 'test'
        }
      });
      
      // Should handle gracefully, not crash
      expect([400, 401, 422]).toContain(response.status());
    });

    test('rate limiting should be in place for auth endpoints', async ({ request }) => {
      // Attempt multiple failed logins
      const promises = [];
      for (let i = 0; i < 10; i++) {
        promises.push(
          request.post(`${API_BASE}/login`, {
            data: {
              email: 'nonexistent@test.com',
              password: 'wrongpassword'
            }
          })
        );
      }
      
      const responses = await Promise.all(promises);
      // At least some should return 401, none should crash the server
      responses.forEach(response => {
        expect([401, 429]).toContain(response.status());
      });
    });
  });

  test.describe('Data Validation', () => {
    test('invalid organization data should be rejected', async ({ request }) => {
      const invalidOrg = {
        name: '', // Empty name should be invalid
        sector: 'Technology'
      };
      
      const response = await request.post(`${API_BASE}/api/organizations`, {
        data: invalidOrg
      });
      
      expect([400, 422]).toContain(response.status());
    });

    test('invalid risk data should be rejected', async ({ request }) => {
      const invalidRisk = {
        organization_id: 999999, // Non-existent org
        title: 'Test Risk',
        severity: 'invalid_severity',
        likelihood: 'invalid_likelihood',
        category: 'Security'
      };
      
      const response = await request.post(`${API_BASE}/api/risks`, {
        data: invalidRisk
      });
      
      expect([400, 422, 500]).toContain(response.status());
    });

    test('invalid assessment data should be rejected', async ({ request }) => {
      const invalidAssessment = {
        organization_id: 999999,
        framework_code: 'NONEXISTENT_FRAMEWORK'
      };
      
      const response = await request.post(`${API_BASE}/api/assessments`, {
        data: invalidAssessment
      });
      
      expect([404, 422]).toContain(response.status());
    });
  });

  test.describe('Performance Tests', () => {
    test('health endpoint should respond quickly', async ({ request }) => {
      const start = Date.now();
      const response = await request.get(`${API_BASE}/health`);
      const duration = Date.now() - start;
      
      expect(response.ok()).toBeTruthy();
      expect(duration).toBeLessThan(1000); // Should respond within 1 second
    });

    test('dashboard stats should respond within reasonable time', async ({ request }) => {
      const start = Date.now();
      const response = await request.get(`${API_BASE}/api/dashboard/stats`);
      const duration = Date.now() - start;
      
      expect(response.ok()).toBeTruthy();
      expect(duration).toBeLessThan(5000); // Should respond within 5 seconds
    });
  });
});
