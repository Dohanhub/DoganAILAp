# API Client & Config Pack - Extended Data Architecture

## Overview
Comprehensive API client configuration for DoganAI Compliance Kit with extended data sources covering compliance, governance, market benchmarks, and regulatory intelligence for KSA and target regions.

---

This pack includes:
- `.env.example` for all external services
- TypeScript **typed API client** with retries, timeouts, and schema validation
- JSON Schemas for Compliance, Benchmarks, Regulations
- Healthcheck helpers
- Example integration into your existing React simulator
- Docker Compose healthchecks snippet
- **Extended Data Architecture** for compliance, governance, benchmarks, and regulatory intelligence

---

## 🏛️ Extended Data Architecture Specification

### 1) Compliance & Governance

#### **Policies & Controls**
```typescript
interface PolicyControl {
  policy_id: string;
  title: string;
  version: string;
  status: 'draft' | 'active' | 'deprecated' | 'under_review';
  owner: string;
  last_review_at: Date;
  control_refs: string[];
  created_at: Date;
  updated_at: Date;
}
```
**Sync Cadence**: Initial load + refresh every 15–30 minutes; webhook for real-time updates
**Endpoint**: `/api/compliance/policies`
**Priority**: High (Critical for compliance operations)

#### **Control Frameworks**
```typescript
interface ControlFramework {
  framework: string; // e.g., 'ISO27001', 'NIST', 'SOX', 'GDPR'
  section: string;
  control_id: string;
  evidence_required: string[];
  implementation_guidance: string;
  maturity_level: 1 | 2 | 3 | 4 | 5;
  last_updated: Date;
}
```
**Sync Cadence**: Weekly sync or triggered by changes
**Endpoint**: `/api/compliance/frameworks`
**Priority**: Medium (Framework updates are less frequent)

#### **Evidence Status**
```typescript
interface EvidenceStatus {
  evidence_id: string;
  control_id: string;
  source: string;
  status: 'pending' | 'submitted' | 'approved' | 'rejected' | 'expired';
  expires_at: Date;
  submitted_by: string;
  reviewed_by?: string;
  file_references: string[];
  last_updated: Date;
}
```
**Sync Cadence**: Near-real-time via webhook or 5–10 minute polling
**Endpoint**: `/api/compliance/evidence`
**Priority**: Critical (Real-time compliance monitoring)

#### **Risk Register**
```typescript
interface RiskRegister {
  risk_id: string;
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  likelihood: 'rare' | 'unlikely' | 'possible' | 'likely' | 'almost_certain';
  mitigation: string;
  due_date: Date;
  owner: string;
  status: 'open' | 'in_progress' | 'mitigated' | 'accepted';
  impact_areas: string[];
  last_assessed: Date;
}
```
**Sync Cadence**: Refresh every 30–60 minutes
**Endpoint**: `/api/compliance/risks`
**Priority**: High (Risk management is critical)

---

### 2) Market & Sector Benchmarks

#### **Industry KPIs**
```typescript
interface IndustryKPI {
  kpi: string;
  sector: string; // e.g., 'banking', 'telecom', 'government', 'healthcare'
  p50: number; // 50th percentile
  p95: number; // 95th percentile
  sample_size: number;
  region: string; // e.g., 'KSA', 'GCC', 'MENA', 'Global'
  measurement_unit: string;
  data_source: string;
  collection_date: Date;
  validity_period: string; // ISO 8601 duration
}
```
**Sync Cadence**: Daily or weekly updates
**Endpoint**: `/api/benchmarks/industry-kpis`
**Priority**: Medium (Market intelligence)

#### **Peer Thresholds**
```typescript
interface PeerThreshold {
  metric: string;
  tier: 'tier1' | 'tier2' | 'tier3' | 'emerging';
  min: number;
  max: number;
  source: string;
  confidence_level: number; // 0-100
  peer_count: number;
  region: string;
  last_updated: Date;
  methodology: string;
}
```
**Sync Cadence**: Weekly or monthly sync
**Endpoint**: `/api/benchmarks/peer-thresholds`
**Priority**: Low (Strategic planning data)

---

### 3) Local Regulatory Intelligence (KSA + Target Regions)

#### **Regulation Catalog**
```typescript
interface RegulationCatalog {
  reg_id: string;
  jurisdiction: string; // e.g., 'KSA', 'UAE', 'Qatar', 'Bahrain', 'Kuwait', 'Oman'
  authority: string; // e.g., 'SAMA', 'CMA', 'CITC', 'NCA'
  title: string;
  effective_date: Date;
  links: {
    official_text: string;
    summary: string;
    guidance?: string;
  }[];
  summary: string;
  impact_assessment: string;
  compliance_deadline?: Date;
  status: 'proposed' | 'enacted' | 'effective' | 'superseded';
  tags: string[];
}
```
**Sync Cadence**: Weekly updates; urgent webhook for new/changed laws
**Endpoint**: `/api/regulatory/catalog`
**Priority**: Critical (Regulatory compliance is mandatory)

#### **Obligations Mapping**
```typescript
interface ObligationMapping {
  obligation_id: string;
  reg_id: string;
  category: string; // e.g., 'reporting', 'governance', 'risk_management', 'data_protection'
  control_mapping: {
    framework: string;
    control_id: string;
    mapping_confidence: number; // 0-100
  }[];
  deadline: Date;
  penalty_severity: 'administrative' | 'financial' | 'criminal';
  implementation_guidance: string;
  responsible_department: string;
  status: 'identified' | 'mapped' | 'implemented' | 'verified';
}
```
**Sync Cadence**: Triggered by regulatory changes
**Endpoint**: `/api/regulatory/obligations`
**Priority**: Critical (Direct compliance impact)

#### **Sanctions/Enforcement Updates**
```typescript
interface EnforcementUpdate {
  case_id: string;
  authority: string;
  violation: string;
  fine_amount: number;
  currency: string;
  date: Date;
  organization_type: string;
  organization_size: 'small' | 'medium' | 'large' | 'enterprise';
  violation_category: string;
  precedent_value: 'low' | 'medium' | 'high';
  public_disclosure: boolean;
  lessons_learned: string;
  related_regulations: string[];
}
```
**Sync Cadence**: Weekly refresh
**Endpoint**: `/api/regulatory/enforcement`
**Priority**: Medium (Intelligence and trend analysis)

---

### 4) Auth & Identity Integration Points

#### **Service Authentication**
```typescript
interface ServiceAuth {
  service_id: string;
  auth_method: 'api_key' | 'oauth2' | 'jwt' | 'mutual_tls';
  credentials: {
    api_key?: string;
    client_id?: string;
    client_secret?: string;
    token_endpoint?: string;
    scope?: string[];
  };
  rate_limits: {
    requests_per_minute: number;
    burst_limit: number;
  };
  retry_policy: {
    max_retries: number;
    backoff_strategy: 'linear' | 'exponential';
    base_delay_ms: number;
  };
}
```

#### **User Context**
```typescript
interface UserContext {
  user_id: string;
  organization_id: string;
  roles: string[];
  permissions: string[];
  data_access_level: 'public' | 'internal' | 'confidential' | 'restricted';
  region_access: string[];
  session_id: string;
  expires_at: Date;
}
```

---

---

## 1) `.env.example`
```env
# =============================================================================
# CORE SERVICE URLs
# =============================================================================
COMPLIANCE_URL=http://localhost:7001
BENCHMARKS_URL=http://localhost:7002
REGULATIONS_URL=http://localhost:7009
AUTH_URL=http://localhost:7005
INTEGRATIONS_URL=http://localhost:7004
AI_ML_URL=http://localhost:7003
AI_AGENT_URL=http://localhost:7006
AUTOTEST_URL=http://localhost:7007
PAYMENTS_URL=http://localhost:7010
I18N_URL=http://localhost:7011

# =============================================================================
# EXTENDED DATA SOURCES - COMPLIANCE & GOVERNANCE
# =============================================================================
POLICIES_API_URL=http://localhost:7012
CONTROL_FRAMEWORKS_API_URL=http://localhost:7013
EVIDENCE_API_URL=http://localhost:7014
RISK_REGISTER_API_URL=http://localhost:7015

# =============================================================================
# MARKET & SECTOR BENCHMARKS
# =============================================================================
INDUSTRY_KPI_API_URL=http://localhost:7016
PEER_THRESHOLDS_API_URL=http://localhost:7017
MARKET_INTELLIGENCE_API_URL=http://localhost:7018

# =============================================================================
# REGULATORY INTELLIGENCE (KSA + REGIONS)
# =============================================================================
REGULATORY_CATALOG_API_URL=http://localhost:7019
OBLIGATIONS_API_URL=http://localhost:7020
ENFORCEMENT_API_URL=http://localhost:7021
SANCTIONS_API_URL=http://localhost:7022

# Regional Regulatory Authorities
SAMA_API_URL=https://api.sama.gov.sa
CMA_API_URL=https://api.cma.org.sa
CITC_API_URL=https://api.citc.gov.sa
NCA_API_URL=https://api.nca.gov.sa

# GCC Regulatory APIs
UAE_CENTRAL_BANK_API_URL=https://api.centralbank.ae
QATAR_CENTRAL_BANK_API_URL=https://api.qcb.gov.qa
BAHRAIN_CENTRAL_BANK_API_URL=https://api.cbb.gov.bh
KUWAIT_CENTRAL_BANK_API_URL=https://api.cbk.gov.kw
OMAN_CENTRAL_BANK_API_URL=https://api.cbo.gov.om

# =============================================================================
# AUTHENTICATION & SECURITY
# =============================================================================
API_TOKEN=
JWT_SECRET=your-jwt-secret-here
OAUTH_CLIENT_ID=your-oauth-client-id
OAUTH_CLIENT_SECRET=your-oauth-client-secret
OAUTH_TOKEN_ENDPOINT=https://auth.example.com/oauth/token

# Service-specific API keys
COMPLIANCE_API_KEY=compliance-api-key
REGULATORY_API_KEY=regulatory-api-key
BENCHMARKS_API_KEY=benchmarks-api-key
MARKET_DATA_API_KEY=market-data-api-key

# =============================================================================
# SYNC CADENCES & INTERVALS (in seconds)
# =============================================================================
# Compliance & Governance
POLICIES_SYNC_INTERVAL=900          # 15 minutes
CONTROL_FRAMEWORKS_SYNC_INTERVAL=604800  # 1 week
EVIDENCE_SYNC_INTERVAL=300          # 5 minutes
RISK_REGISTER_SYNC_INTERVAL=1800    # 30 minutes

# Market & Benchmarks
INDUSTRY_KPI_SYNC_INTERVAL=86400    # 1 day
PEER_THRESHOLDS_SYNC_INTERVAL=604800 # 1 week

# Regulatory Intelligence
REGULATORY_CATALOG_SYNC_INTERVAL=604800  # 1 week
OBLIGATIONS_SYNC_INTERVAL=0         # Event-driven
ENFORCEMENT_SYNC_INTERVAL=604800    # 1 week

# =============================================================================
# WEBHOOK CONFIGURATIONS
# =============================================================================
WEBHOOK_SECRET=your-webhook-secret
WEBHOOK_TIMEOUT=30000
WEBHOOK_RETRY_ATTEMPTS=3

# Webhook endpoints for real-time updates
POLICIES_WEBHOOK_URL=/webhooks/policies
EVIDENCE_WEBHOOK_URL=/webhooks/evidence
REGULATORY_WEBHOOK_URL=/webhooks/regulatory
RISK_WEBHOOK_URL=/webhooks/risks

# =============================================================================
# RATE LIMITING & PERFORMANCE
# =============================================================================
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
RATE_LIMIT_BURST=150

# Service-specific rate limits
REGULATORY_RATE_LIMIT=50
COMPLIANCE_RATE_LIMIT=200
BENCHMARKS_RATE_LIMIT=100

# =============================================================================
# RETRY CONFIGURATION
# =============================================================================
MAX_RETRIES=3
RETRY_DELAY=1000
RETRY_BACKOFF=exponential
RETRY_MAX_DELAY=30000

# Critical data retry settings
CRITICAL_DATA_MAX_RETRIES=5
CRITICAL_DATA_RETRY_DELAY=500

# =============================================================================
# HEALTH CHECK CONFIGURATION
# =============================================================================
HEALTH_CHECK_INTERVAL=30000
HEALTH_CHECK_TIMEOUT=5000
HEALTH_CHECK_RETRIES=3

# Extended health checks
DEEP_HEALTH_CHECK_INTERVAL=300000   # 5 minutes
DATA_FRESHNESS_THRESHOLD=3600       # 1 hour

# =============================================================================
# DATA QUALITY & VALIDATION
# =============================================================================
DATA_VALIDATION_ENABLED=true
SCHEMA_VALIDATION_STRICT=true
DATA_INTEGRITY_CHECKS=true

# =============================================================================
# CACHING CONFIGURATION
# =============================================================================
CACHE_TTL_POLICIES=1800             # 30 minutes
CACHE_TTL_FRAMEWORKS=86400          # 24 hours
CACHE_TTL_EVIDENCE=300              # 5 minutes
CACHE_TTL_RISKS=3600                # 1 hour
CACHE_TTL_BENCHMARKS=86400          # 24 hours
CACHE_TTL_REGULATORY=43200          # 12 hours

# =============================================================================
# MONITORING & ALERTING
# =============================================================================
MONITORING_ENABLED=true
ALERT_WEBHOOK_URL=https://alerts.example.com/webhook
SLACK_WEBHOOK_URL=https://hooks.slack.com/your-webhook
EMAIL_ALERTS_ENABLED=true
SMS_ALERTS_ENABLED=false

# =============================================================================
# REGIONAL SETTINGS
# =============================================================================
DEFAULT_REGION=KSA
SUPPORTED_REGIONS=KSA,UAE,Qatar,Bahrain,Kuwait,Oman
DEFAULT_TIMEZONE=Asia/Riyadh
DEFAULT_CURRENCY=SAR
DEFAULT_LANGUAGE=en

# =============================================================================
# COMPLIANCE SETTINGS
# =============================================================================
DATA_RETENTION_DAYS=2555            # 7 years
AUDIT_LOG_RETENTION_DAYS=3650       # 10 years
ENCRYPTION_ENABLED=true
DATA_CLASSIFICATION_REQUIRED=true

# =============================================================================
# DEVELOPMENT & DEBUGGING
# =============================================================================
DEBUG_MODE=false
LOG_LEVEL=INFO
API_DOCS_ENABLED=true
CORS_ENABLED=true
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

> Copy to `.env` (frontend: use `VITE_` or `NEXT_PUBLIC_` prefixes as needed, e.g. `VITE_COMPLIANCE_URL`).

---

## 2) `src/api/types.ts`
```ts
export type PolicyStatus = "draft" | "active" | "retired";

export interface CompliancePolicy {
  policy_id: string;
  title: string;
  version: string;
  status: PolicyStatus;
  owner?: string;
  last_review_at?: string; // ISO datetime
  control_refs: string[];
}

export interface ComplianceSummary {
  complianceRate: number; // 0..100
  activePoliciesCount: number;
  policies: CompliancePolicy[];
}

export interface BenchmarkKPI {
  kpi: string; // e.g., "deflection", "csat"
  sector: string; // e.g., "gov", "telecom"
  p50?: number;
  p95: number;
  sample_size: number;
  region?: string; // e.g., "KSA"
  as_of: string; // ISO datetime
}

export interface RegulationDoc {
  reg_id: string;
  jurisdiction: string; // e.g., "KSA"
  title: string;
  effective_date: string; // ISO date
  links?: string[];
  summary?: string;
}

export interface EvidenceSummary {
  evidence_id: string;
  control_id: string;
  source: string;
  status: "missing" | "pending" | "verified";
  expires_at?: string;
}

export interface MetricsSummary {
  model: string;
  p50?: number;
  p95?: number;
  err_rate?: number;
  rpm?: number;
  tpm?: number;
  cost_estimate?: number;
}

export interface ConversationSummary {
  conv_id: string;
  user_id?: string;
  summary: string;
  resolution?: string;
  handoff?: boolean;
  created_at?: string;
}
```

---

## 3) `src/api/schemas.ts` (JSON Schemas as JS objects)
```ts
export const CompliancePolicySchema = {
  type: "object",
  required: ["policy_id", "title", "version", "status", "control_refs"],
  properties: {
    policy_id: { type: "string" },
    title: { type: "string" },
    version: { type: "string" },
    status: { enum: ["draft", "active", "retired"] },
    owner: { type: "string" },
    last_review_at: { type: "string" },
    control_refs: { type: "array", items: { type: "string" } },
  },
} as const;

export const ComplianceSummarySchema = {
  type: "object",
  required: ["complianceRate", "activePoliciesCount", "policies"],
  properties: {
    complianceRate: { type: "number" },
    activePoliciesCount: { type: "number" },
    policies: { type: "array", items: CompliancePolicySchema },
  },
} as const;

export const BenchmarkKPISchema = {
  type: "object",
  required: ["kpi", "sector", "p95", "sample_size", "as_of"],
  properties: {
    kpi: { type: "string" },
    sector: { type: "string" },
    p50: { type: "number" },
    p95: { type: "number" },
    sample_size: { type: "integer" },
    region: { type: "string" },
    as_of: { type: "string" },
  },
} as const;

export const RegulationDocSchema = {
  type: "object",
  required: ["reg_id", "jurisdiction", "title", "effective_date"],
  properties: {
    reg_id: { type: "string" },
    jurisdiction: { type: "string" },
    title: { type: "string" },
    effective_date: { type: "string" },
    links: { type: "array", items: { type: "string" } },
    summary: { type: "string" },
  },
} as const;
```

---

## 4) `src/api/client.ts` (typed client + retries)
```ts
import type { ComplianceSummary, BenchmarkKPI, RegulationDoc, MetricsSummary, ConversationSummary } from "./types";
import { ComplianceSummarySchema, BenchmarkKPISchema, RegulationDocSchema } from "./schemas";

const cfg = {
  compliance: import.meta.env.VITE_COMPLIANCE_URL || process.env.COMPLIANCE_URL,
  benchmarks: import.meta.env.VITE_BENCHMARKS_URL || process.env.BENCHMARKS_URL,
  regulations: import.meta.env.VITE_REGULATIONS_URL || process.env.REGULATIONS_URL,
  ai_ml: import.meta.env.VITE_AI_ML_URL || process.env.AI_ML_URL,
  ai_agent: import.meta.env.VITE_AI_AGENT_URL || process.env.AI_AGENT_URL,
};

const DEFAULT_TIMEOUT = 8000; // ms
const MAX_RETRIES = 2;

async function http<T>(url: string, init: RequestInit = {}, timeout = DEFAULT_TIMEOUT): Promise<T> {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);
  const headers = { ...(init.headers || {}), "Content-Type": "application/json" } as Record<string,string>;
  if (import.meta.env.VITE_API_TOKEN || process.env.API_TOKEN) {
    headers["Authorization"] = `Bearer ${import.meta.env.VITE_API_TOKEN || process.env.API_TOKEN}`;
  }
  let lastErr: any;
  for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
    try {
      const res = await fetch(url, { ...init, headers, signal: controller.signal });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = (await res.json()) as T;
      clearTimeout(id);
      return data;
    } catch (e) {
      lastErr = e;
      await new Promise(r => setTimeout(r, 250 * (attempt + 1)));
    }
  }
  throw lastErr;
}

// Minimal schema validator (runtime guard)
function validate<T>(schema: any, data: any, label: string): T {
  // lightweight checks only; replace with Ajv for production
  if (schema.type === "object") {
    for (const key of (schema.required || [])) {
      if (!(key in data)) throw new Error(`${label} missing required field: ${key}`);
    }
  }
  return data as T;
}

export async function getComplianceSummary(): Promise<ComplianceSummary> {
  const url = `${cfg.compliance}/api/compliance`;
  const raw = await http<any>(url);
  return validate<ComplianceSummary>(ComplianceSummarySchema, raw, "ComplianceSummary");
}

export async function getBenchmarks(sector: string, region = "KSA"): Promise<BenchmarkKPI[]> {
  const url = `${cfg.benchmarks}/api/benchmarks?sector=${encodeURIComponent(sector)}&region=${encodeURIComponent(region)}`;
  const raw = await http<any[]>(url);
  return raw.map((r) => validate<BenchmarkKPI>(BenchmarkKPISchema, r, "BenchmarkKPI"));
}

export async function getRegulations(jurisdiction = "KSA"): Promise<RegulationDoc[]> {
  const url = `${cfg.regulations}/api/regulations?jurisdiction=${encodeURIComponent(jurisdiction)}`;
  const raw = await http<any[]>(url);
  return raw.map((r) => validate<RegulationDoc>(RegulationDocSchema, r, "RegulationDoc"));
}

export async function getModelMetrics(): Promise<MetricsSummary[]> {
  const url = `${cfg.ai_ml}/api/metrics/summary`;
  return http<MetricsSummary[]>(url);
}

export async function getConversationSummary(): Promise<ConversationSummary[]> {
  const url = `${cfg.ai_agent}/api/conversations/summary`;
  return http<ConversationSummary[]>(url);
}
```

---

## 5) `src/api/health.ts` (quick health probes)
```ts
const paths = ["/readyz", "/healthz", "/ready", "/health"];

export async function probe(base: string): Promise<{ ok: boolean; path?: string }>{
  for (const p of paths) {
    try {
      const r = await fetch(base + p, { method: "GET" });
      if (r.ok) return { ok: true, path: p };
    } catch {}
  }
  return { ok: false };
}
```

---

## 6) Example: wire into your Simulator (right pane KPIs)
```ts
import { useEffect, useState } from "react";
import { getComplianceSummary, getBenchmarks, getRegulations, getModelMetrics } from "@/api/client";

export function useDashboardData() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<any>({});

  useEffect(() => {
    (async () => {
      try {
        const [comp, bench, regs, metrics] = await Promise.all([
          getComplianceSummary(),
          getBenchmarks("gov", "KSA"),
          getRegulations("KSA"),
          getModelMetrics(),
        ]);
        setData({ comp, bench, regs, metrics });
      } catch (e: any) {
        setError(e.message || String(e));
      } finally { setLoading(false); }
    })();
  }, []);

  return { loading, error, ...data };
}
```
> Then render compliance rate, policy count, top 3 KPIs, and latest regulation titles.

---

## 7) Docker Compose: healthchecks (snippet)
```yaml
services:
  compliance_engine:
    image: your/compliance:latest
    ports: ["7001:7001"]
    healthcheck:
      test: ["CMD", "curl", "-fsS", "http://localhost:7001/readyz"]
      interval: 10s
      timeout: 3s
      retries: 10
      start_period: 20s

  benchmarks:
    image: your/benchmarks:latest
    ports: ["7002:7002"]
    healthcheck:
      test: ["CMD", "curl", "-fsS", "http://localhost:7002/healthz"]
      interval: 10s
      timeout: 3s
      retries: 10
      start_period: 10s

  regulations:
    image: your/regulations:latest
    ports: ["7009:7009"]
    healthcheck:
      test: ["CMD", "curl", "-fsS", "http://localhost:7009/healthz"]
      interval: 10s
      timeout: 3s
      retries: 10
      start_period: 10s
```

---

## 8) Postman/Bruno collection (mini JSON, optional)
```json
{
  "info": { "name": "Dogan Compliance Kit", "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json" },
  "item": [
    { "name": "Compliance Summary", "request": { "method": "GET", "url": "{{COMPLIANCE_URL}}/api/compliance" }},
    { "name": "Benchmarks (KSA/Gov)", "request": { "method": "GET", "url": "{{BENCHMARKS_URL}}/api/benchmarks?sector=gov&region=KSA" }},
    { "name": "Regulations (KSA)", "request": { "method": "GET", "url": "{{REGULATIONS_URL}}/api/regulations?jurisdiction=KSA" }}
  ]
}
```

---

## 9) Quality gates (CI)
- Add schema validation (Ajv) and a smoke job that `curl`s `/readyz` for all services before merging to `main`.
- Fail build if any required env (e.g., `COMPLIANCE_URL`) is missing.

---

### How to use
1. Copy `.env.example` → `.env` (or Frontend env prefix).
2. Drop `src/api/*` files into your app.
3. Import `useDashboardData()` and render the numbers.
4. (Optional) Add Docker healthchecks to your compose.

That’s your full-stack, typed, health-checked fetch layer, ready for the real endpoints when you plug them in. ✅

