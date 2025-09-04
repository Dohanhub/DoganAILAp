-- DoganAI Compliance Kit - RLS Policies (Simplified)
-- Version: 2.0.0
-- Description: Row Level Security policies for tenant isolation
-- This file must be run after V1__doganai_core_simple.sql

-- =============================================================================
-- RLS FUNCTION: CURRENT TENANT
-- =============================================================================

-- RLS function: current tenant
CREATE OR REPLACE FUNCTION app_tenant_id() RETURNS uuid AS $$
  SELECT current_setting('app.current_tenant_id', true)::uuid
$$ LANGUAGE sql STABLE;

-- =============================================================================
-- ENABLE RLS ON ALL TABLES
-- =============================================================================

-- Enable RLS on all tenant-scoped tables
DO $$
DECLARE
  t text;
BEGIN
  FOR t IN SELECT unnest(ARRAY[
    'tenants','users','api_keys','projects','datasets','documents',
    'models','jobs','inference_runs','consents','data_access_requests',
    'data_retention_policies','integrations','webhooks','events'
  ])
  LOOP
    EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY;', t);
  END LOOP;
END $$;

-- =============================================================================
-- TENANT ISOLATION POLICIES
-- =============================================================================

-- Tenants table - users can only see their own tenant
CREATE POLICY tenant_tenants ON tenants
  USING (id = app_tenant_id())
  WITH CHECK (id = app_tenant_id());

-- Users table - users can only see users in their tenant
CREATE POLICY tenant_rw_users ON users
  USING (tenant_id = app_tenant_id())
  WITH CHECK (tenant_id = app_tenant_id());

-- API keys table - users can only see API keys in their tenant
CREATE POLICY tenant_rw_api_keys ON api_keys
  USING (user_id IN (SELECT id FROM users WHERE tenant_id = app_tenant_id()))
  WITH CHECK (user_id IN (SELECT id FROM users WHERE tenant_id = app_tenant_id()));

-- Projects table - users can only see projects in their tenant
CREATE POLICY tenant_rw_projects ON projects
  USING (tenant_id = app_tenant_id())
  WITH CHECK (tenant_id = app_tenant_id());

-- Datasets table - users can only see datasets in their tenant
CREATE POLICY tenant_rw_datasets ON datasets
  USING (project_id IN (SELECT id FROM projects WHERE tenant_id = app_tenant_id()))
  WITH CHECK (project_id IN (SELECT id FROM projects WHERE tenant_id = app_tenant_id()));

-- Documents table - users can only see documents in their tenant
CREATE POLICY tenant_rw_documents ON documents
  USING (dataset_id IN (SELECT id FROM datasets WHERE project_id IN (SELECT id FROM projects WHERE tenant_id = app_tenant_id())))
  WITH CHECK (dataset_id IN (SELECT id FROM datasets WHERE project_id IN (SELECT id FROM projects WHERE tenant_id = app_tenant_id())));

-- Models table - users can only see models in their tenant
CREATE POLICY tenant_rw_models ON models
  USING (tenant_id = app_tenant_id())
  WITH CHECK (tenant_id = app_tenant_id());

-- Jobs table - users can only see jobs in their tenant
CREATE POLICY tenant_rw_jobs ON jobs
  USING (tenant_id = app_tenant_id())
  WITH CHECK (tenant_id = app_tenant_id());

-- Inference runs table - users can only see inference runs in their tenant
CREATE POLICY tenant_rw_inference_runs ON inference_runs
  USING (model_id IN (SELECT id FROM models WHERE tenant_id = app_tenant_id()))
  WITH CHECK (model_id IN (SELECT id FROM models WHERE tenant_id = app_tenant_id()));

-- Consents table - users can only see consents in their tenant
CREATE POLICY tenant_rw_consents ON consents
  USING (user_id IN (SELECT id FROM users WHERE tenant_id = app_tenant_id()))
  WITH CHECK (user_id IN (SELECT id FROM users WHERE tenant_id = app_tenant_id()));

-- Data access requests table - users can only see data access requests in their tenant
CREATE POLICY tenant_rw_data_access_requests ON data_access_requests
  USING (user_id IN (SELECT id FROM users WHERE tenant_id = app_tenant_id()))
  WITH CHECK (user_id IN (SELECT id FROM users WHERE tenant_id = app_tenant_id()));

-- Data retention policies table - users can only see data retention policies in their tenant
CREATE POLICY tenant_rw_data_retention_policies ON data_retention_policies
  USING (tenant_id = app_tenant_id())
  WITH CHECK (tenant_id = app_tenant_id());

-- Integrations table - users can only see integrations in their tenant
CREATE POLICY tenant_rw_integrations ON integrations
  USING (tenant_id = app_tenant_id())
  WITH CHECK (tenant_id = app_tenant_id());

-- Webhooks table - users can only see webhooks in their tenant
CREATE POLICY tenant_rw_webhooks ON webhooks
  USING (tenant_id = app_tenant_id())
  WITH CHECK (tenant_id = app_tenant_id());

-- Events table - users can only see events in their tenant
CREATE POLICY tenant_rw_events ON events
  USING (tenant_id = app_tenant_id())
  WITH CHECK (tenant_id = app_tenant_id());

-- =============================================================================
-- VALIDATION FUNCTIONS
-- =============================================================================

-- Function to validate tenant isolation
CREATE OR REPLACE FUNCTION validate_tenant_isolation()
RETURNS TABLE(table_name text, rls_enabled boolean, policy_count bigint) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    t.table_name::text,
    t.rls_enabled,
    COALESCE(p.policy_count, 0)::bigint
  FROM (
    SELECT 
      table_name,
      row_security as rls_enabled
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
      AND table_name IN (
        'tenants','users','api_keys','projects','datasets','documents',
        'models','jobs','inference_runs','consents','data_access_requests',
        'data_retention_policies','integrations','webhooks','events'
      )
  ) t
  LEFT JOIN (
    SELECT 
      schemaname,
      tablename,
      COUNT(*) as policy_count
    FROM pg_policies 
    WHERE schemaname = 'public'
    GROUP BY schemaname, tablename
  ) p ON t.table_name = p.tablename
  ORDER BY t.table_name;
END;
$$ LANGUAGE plpgsql;

-- Function to test RLS policies
CREATE OR REPLACE FUNCTION test_rls_policies()
RETURNS TABLE(test_name text, result text) AS $$
BEGIN
  -- Test 1: Check if RLS is enabled on all tables
  IF EXISTS (
    SELECT 1 FROM information_schema.tables 
    WHERE table_schema = 'public' 
      AND table_name IN (
        'tenants','users','api_keys','projects','datasets','documents',
        'models','jobs','inference_runs','consents','data_access_requests',
        'data_retention_policies','integrations','webhooks','events'
      )
      AND row_security = false
  ) THEN
    RETURN QUERY SELECT 'RLS Check'::text, 'FAILED - Some tables do not have RLS enabled'::text;
  ELSE
    RETURN QUERY SELECT 'RLS Check'::text, 'PASSED - All tables have RLS enabled'::text;
  END IF;

  -- Test 2: Check if policies exist
  IF EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE schemaname = 'public' 
      AND tablename IN (
        'tenants','users','api_keys','projects','datasets','documents',
        'models','jobs','inference_runs','consents','data_access_requests',
        'data_retention_policies','integrations','webhooks','events'
      )
  ) THEN
    RETURN QUERY SELECT 'Policy Check'::text, 'PASSED - RLS policies exist'::text;
  ELSE
    RETURN QUERY SELECT 'Policy Check'::text, 'FAILED - No RLS policies found'::text;
  END IF;

  -- Test 3: Check if app_tenant_id function exists
  IF EXISTS (
    SELECT 1 FROM pg_proc 
    WHERE proname = 'app_tenant_id'
  ) THEN
    RETURN QUERY SELECT 'Function Check'::text, 'PASSED - app_tenant_id function exists'::text;
  ELSE
    RETURN QUERY SELECT 'Function Check'::text, 'FAILED - app_tenant_id function not found'::text;
  END IF;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- DOCUMENTATION
-- =============================================================================

COMMENT ON FUNCTION app_tenant_id() IS 'Returns the current tenant ID from session variable app.current_tenant_id';
COMMENT ON FUNCTION validate_tenant_isolation() IS 'Validates that RLS is properly configured for tenant isolation';
COMMENT ON FUNCTION test_rls_policies() IS 'Tests the RLS policy implementation';

-- =============================================================================
-- USAGE INSTRUCTIONS
-- =============================================================================

/*
To use tenant isolation:

1. Set the current tenant ID in your session:
   SET app.current_tenant_id = 'your-tenant-uuid';

2. All queries will automatically filter by tenant_id

3. Validate the setup:
   SELECT * FROM validate_tenant_isolation();
   SELECT * FROM test_rls_policies();

4. Test tenant isolation:
   SET app.current_tenant_id = 'tenant-1-uuid';
   SELECT COUNT(*) FROM users; -- Only shows users from tenant-1
   
   SET app.current_tenant_id = 'tenant-2-uuid';
   SELECT COUNT(*) FROM users; -- Only shows users from tenant-2
*/
