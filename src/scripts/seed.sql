-- DoganAI Compliance Kit - Seed Data
-- This script populates the database with initial test data

-- Set the current tenant context
SET LOCAL app.current_tenant_id = '00000000-0000-0000-0000-000000000001';

-- Insert additional tenants for testing
INSERT INTO tenants(id, slug, name, domain, status) VALUES
  ('00000000-0000-0000-0000-000000000002', 'test-tenant', 'Test Tenant', 'test-tenant.com', 'active'),
  ('00000000-0000-0000-0000-000000000003', 'demo-tenant', 'Demo Tenant', 'demo-tenant.com', 'active')
ON CONFLICT (slug) DO NOTHING;

-- Insert additional users for testing
INSERT INTO users(id, tenant_id, email, display_name, password_hash, mfa_enabled) VALUES
  ('00000000-0000-0000-0000-000000000005', '00000000-0000-0000-0000-000000000001', 'vendor@dogan-ai.com', 'Vendor User', crypt('Vendor@123', gen_salt('bf')), false),
  ('00000000-0000-0000-0000-000000000006', '00000000-0000-0000-0000-000000000001', 'customer@dogan-ai.com', 'Customer User', crypt('Customer@123', gen_salt('bf')), false),
  ('00000000-0000-0000-0000-000000000007', '00000000-0000-0000-0000-000000000001', 'analyst@dogan-ai.com', 'Data Analyst', crypt('Analyst@123', gen_salt('bf')), true)
ON CONFLICT (email) DO NOTHING;

-- Insert additional roles
INSERT INTO roles(id, tenant_id, name, description, permissions) VALUES
  ('00000000-0000-0000-0000-000000000008', '00000000-0000-0000-0000-000000000001', 'Vendor', 'Vendor integration access', '["vendor:read", "vendor:write", "integrations:read"]'),
  ('00000000-0000-0000-0000-000000000009', '00000000-0000-0000-0000-000000000001', 'Customer', 'Customer compliance access', '["compliance:read", "reports:read", "projects:read"]'),
  ('00000000-0000-0000-0000-000000000010', '00000000-0000-0000-0000-000000000001', 'Analyst', 'Data analysis access', '["data:read", "analytics:read", "models:read"]')
ON CONFLICT DO NOTHING;

-- Assign roles to users
INSERT INTO user_roles(user_id, role_id) VALUES
  ('00000000-0000-0000-0000-000000000005', '00000000-0000-0000-0000-000000000008'),
  ('00000000-0000-0000-0000-000000000006', '00000000-0000-0000-0000-000000000009'),
  ('00000000-0000-0000-0000-000000000007', '00000000-0000-0000-0000-000000000010')
ON CONFLICT DO NOTHING;

-- Insert additional projects
INSERT INTO projects(id, tenant_id, name, description, compliance_framework, status) VALUES
  ('00000000-0000-0000-0000-000000000011', '00000000-0000-0000-0000-000000000001', 'SAMA Banking Compliance', 'SAMA banking regulations compliance project', 'SAMA', 'active'),
  ('00000000-0000-0000-0000-000000000012', '00000000-0000-0000-0000-000000000001', 'MoH Healthcare Standards', 'Ministry of Health healthcare compliance', 'MoH', 'active'),
  ('00000000-0000-0000-0000-000000000013', '00000000-0000-0000-0000-000000000001', 'Data Governance Framework', 'Data governance and privacy compliance', 'GDPR', 'active')
ON CONFLICT DO NOTHING;

-- Insert datasets
INSERT INTO datasets(id, tenant_id, project_id, name, description, data_type, size_bytes, record_count, compliance_tags) VALUES
  ('00000000-0000-0000-0000-000000000014', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000004', 'IBM Watson Documents', 'IBM Watson integration documents and specifications', 'documents', 1048576, 150, ARRAY['AI', 'IBM', 'Watson']),
  ('00000000-0000-0000-0000-000000000015', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000011', 'Banking Regulations', 'SAMA banking regulations and compliance documents', 'regulations', 2097152, 300, ARRAY['SAMA', 'Banking', 'Compliance']),
  ('00000000-0000-0000-0000-000000000016', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000012', 'Healthcare Standards', 'MoH healthcare standards and guidelines', 'standards', 1572864, 200, ARRAY['MoH', 'Healthcare', 'Standards'])
ON CONFLICT DO NOTHING;

-- Insert sample documents
INSERT INTO documents(id, tenant_id, dataset_id, title, content, content_hash, file_size, mime_type, compliance_status) VALUES
  ('00000000-0000-0000-0000-000000000017', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000014', 'IBM Watson AI Platform Overview', 'IBM Watson is an AI platform that provides a suite of enterprise-ready AI services, applications, and tooling.', md5('IBM Watson AI Platform Overview'), 2048, 'text/plain', 'compliant'),
  ('00000000-0000-0000-0000-000000000018', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000015', 'SAMA Cybersecurity Framework', 'The SAMA Cybersecurity Framework provides guidelines for financial institutions to protect against cyber threats.', md5('SAMA Cybersecurity Framework'), 3072, 'text/plain', 'pending'),
  ('00000000-0000-0000-0000-000000000019', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000016', 'MoH Data Privacy Guidelines', 'Ministry of Health guidelines for protecting patient data and ensuring privacy compliance.', md5('MoH Data Privacy Guidelines'), 2560, 'text/plain', 'compliant')
ON CONFLICT DO NOTHING;

-- Insert sample embeddings (dummy vectors for testing)
INSERT INTO embeddings(id, tenant_id, document_id, chunk_text, chunk_index, embedding_vector, metadata) VALUES
  ('00000000-0000-0000-0000-000000000020', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000017', 'IBM Watson is an AI platform', 1, '[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]'::vector, '{"chunk_type": "paragraph", "language": "en"}'),
  ('00000000-0000-0000-0000-000000000021', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000018', 'SAMA Cybersecurity Framework guidelines', 1, '[0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,0.1]'::vector, '{"chunk_type": "paragraph", "language": "en"}'),
  ('00000000-0000-0000-0000-000000000022', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000019', 'MoH Data Privacy Guidelines', 1, '[0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,0.1,0.2]'::vector, '{"chunk_type": "paragraph", "language": "en"}')
ON CONFLICT DO NOTHING;

-- Insert sample models
INSERT INTO models(id, tenant_id, name, model_type, version, provider, endpoint_url, settings, status) VALUES
  ('00000000-0000-0000-0000-000000000023', '00000000-0000-0000-0000-000000000001', 'GPT-4 Integration', 'llm', '4.0', 'OpenAI', 'https://api.openai.com/v1/chat/completions', '{"model": "gpt-4", "max_tokens": 4096}', 'active'),
  ('00000000-0000-0000-0000-000000000024', '00000000-0000-0000-0000-000000000001', 'IBM Watson Assistant', 'assistant', '1.0', 'IBM', 'https://api.watson.ai.ibm.com/instances/assistant', '{"assistant_id": "test-assistant"}', 'active'),
  ('00000000-0000-0000-0000-000000000025', '00000000-0000-0000-0000-000000000001', 'Embedding Model', 'embedding', '2.0', 'OpenAI', 'https://api.openai.com/v1/embeddings', '{"model": "text-embedding-ada-002"}', 'active')
ON CONFLICT DO NOTHING;

-- Insert sample jobs
INSERT INTO jobs(id, tenant_id, project_id, name, job_type, status, parameters, result) VALUES
  ('00000000-0000-0000-0000-000000000026', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000004', 'Document Processing Job', 'document_processing', 'completed', '{"batch_size": 100, "chunk_size": 1000}', '{"processed": 150, "failed": 0}'),
  ('00000000-0000-0000-0000-000000000027', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000011', 'Compliance Check Job', 'compliance_check', 'running', '{"framework": "SAMA", "strict_mode": true}', NULL),
  ('00000000-0000-0000-0000-000000000028', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000012', 'Data Analysis Job', 'data_analysis', 'pending', '{"analysis_type": "privacy_impact", "scope": "full"}', NULL)
ON CONFLICT DO NOTHING;

-- Insert sample consents
INSERT INTO consents(id, tenant_id, user_id, consent_type, purpose, granted, granted_at, expires_at) VALUES
  ('00000000-0000-0000-0000-000000000029', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000006', 'data_processing', 'Compliance analysis and reporting', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '1 year'),
  ('00000000-0000-0000-0000-000000000030', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000007', 'ai_analysis', 'AI-powered data analysis and insights', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '6 months')
ON CONFLICT DO NOTHING;

-- Insert sample integrations
INSERT INTO integrations(id, tenant_id, name, integration_type, provider, configuration, status) VALUES
  ('00000000-0000-0000-0000-000000000031', '00000000-0000-0000-0000-000000000001', 'IBM Watson AI Platform', 'ai_platform', 'IBM', '{"api_key": "encrypted_key", "region": "us-south", "services": ["assistant", "discovery", "natural_language_understanding"]}', 'active'),
  ('00000000-0000-0000-0000-000000000032', '00000000-0000-0000-0000-000000000001', 'Microsoft Azure', 'cloud_platform', 'Microsoft', '{"subscription_id": "encrypted_id", "resource_group": "doganai-rg", "services": ["cognitive_services", "machine_learning"]}', 'active'),
  ('00000000-0000-0000-0000-000000000033', '00000000-0000-0000-0000-000000000001', 'Lenovo Hardware', 'hardware', 'Lenovo', '{"server_model": "ThinkSystem SR650", "monitoring": true, "health_checks": true}', 'active')
ON CONFLICT DO NOTHING;

-- Insert sample webhooks
INSERT INTO webhooks(id, tenant_id, name, url, events, secret_hash, status) VALUES
  ('00000000-0000-0000-0000-000000000034', '00000000-0000-0000-0000-000000000001', 'Compliance Alert Webhook', 'https://webhook.site/doganai-compliance', ARRAY['compliance.violation', 'compliance.resolved'], crypt('webhook_secret_123', gen_salt('bf')), 'active'),
  ('00000000-0000-0000-0000-000000000035', '00000000-0000-0000-0000-000000000001', 'AI Model Update Webhook', 'https://webhook.site/doganai-ai-updates', ARRAY['model.updated', 'model.deployed'], crypt('webhook_secret_456', gen_salt('bf')), 'active')
ON CONFLICT DO NOTHING;

-- Insert sample events
INSERT INTO events(id, tenant_id, event_type, actor_id, resource_type, resource_id, details, ip_address) VALUES
  ('00000000-0000-0000-0000-000000000036', '00000000-0000-0000-0000-000000000001', 'user.login', '00000000-0000-0000-0000-000000000002', 'users', '00000000-0000-0000-0000-000000000002', '{"ip": "192.168.1.100", "user_agent": "Mozilla/5.0"}', '192.168.1.100'),
  ('00000000-0000-0000-0000-000000000037', '00000000-0000-0000-0000-000000000001', 'project.created', '00000000-0000-0000-0000-000000000002', 'projects', '00000000-0000-0000-0000-000000000004', '{"project_name": "IBM Watson Integration"}', '192.168.1.100'),
  ('00000000-0000-0000-0000-000000000038', '00000000-0000-0000-0000-000000000001', 'compliance.check.started', '00000000-0000-0000-0000-000000000002', 'jobs', '00000000-0000-0000-0000-000000000027', '{"framework": "SAMA", "strict_mode": true}', '192.168.1.100')
ON CONFLICT DO NOTHING;

-- Insert sample audit logs
INSERT INTO audit_logs(id, tenant_id, user_id, action, resource_type, resource_id, old_values, new_values, ip_address) VALUES
  ('00000000-0000-0000-0000-000000000039', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000002', 'CREATE', 'projects', '00000000-0000-0000-0000-000000000004', NULL, '{"name": "IBM Watson Integration", "compliance_framework": "NCA"}', '192.168.1.100'),
  ('00000000-0000-0000-0000-000000000040', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000002', 'UPDATE', 'users', '00000000-0000-0000-0000-000000000005', '{"mfa_enabled": false}', '{"mfa_enabled": true}', '192.168.1.100'),
  ('00000000-0000-0000-0000-000000000041', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000002', 'DELETE', 'documents', '00000000-0000-0000-0000-000000000017', '{"title": "IBM Watson AI Platform Overview"}', NULL, '192.168.1.100')
ON CONFLICT DO NOTHING;

-- Create audit log partitions for next 3 months
SELECT create_audit_log_partition('2025-09-01'::date);
SELECT create_audit_log_partition('2025-10-01'::date);
SELECT create_audit_log_partition('2025-11-01'::date);

-- Display summary
SELECT 
  'Seed data insertion completed' as status,
  COUNT(*) as total_records,
  'All tables populated with test data' as details
FROM (
  SELECT 1 FROM tenants UNION ALL
  SELECT 1 FROM users UNION ALL
  SELECT 1 FROM roles UNION ALL
  SELECT 1 FROM projects UNION ALL
  SELECT 1 FROM datasets UNION ALL
  SELECT 1 FROM documents UNION ALL
  SELECT 1 FROM embeddings UNION ALL
  SELECT 1 FROM models UNION ALL
  SELECT 1 FROM jobs UNION ALL
  SELECT 1 FROM consents UNION ALL
  SELECT 1 FROM integrations UNION ALL
  SELECT 1 FROM webhooks UNION ALL
  SELECT 1 FROM events UNION ALL
  SELECT 1 FROM audit_logs
) t;
