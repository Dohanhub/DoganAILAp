CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE TABLE IF NOT EXISTS policy_control(
  regulator TEXT, control_id TEXT, version TEXT,
  title_ar TEXT, title_en TEXT, requirement_ar TEXT, requirement_en TEXT,
  category TEXT, severity TEXT, residency_required BOOLEAN DEFAULT FALSE,
  PRIMARY KEY(regulator, control_id, version)
);
CREATE TABLE IF NOT EXISTS vendor_capability(
  vendor_id TEXT, solution TEXT, control_id TEXT, version TEXT,
  evidence TEXT, scope TEXT, notes TEXT,
  PRIMARY KEY(vendor_id, solution, control_id, version)
);
CREATE TABLE IF NOT EXISTS mapping(
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT, policy_ref TEXT, vendor_files TEXT[], sector TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE IF NOT EXISTS compliance_result(
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  mapping_id UUID, status TEXT,
  required JSONB, provided JSONB, missing JSONB, notes JSONB,
  created_at TIMESTAMPTZ DEFAULT now(), hash TEXT
);
CREATE TABLE IF NOT EXISTS kpi_snapshot(
  ts DATE, sector TEXT, metric TEXT, value NUMERIC, source TEXT,
  PRIMARY KEY(ts, sector, metric)
);
CREATE TABLE IF NOT EXISTS audit_log(
  ts TIMESTAMPTZ DEFAULT now(), actor TEXT, action TEXT, object_type TEXT,
  object_id TEXT, before JSONB, after JSONB, sig TEXT
);
