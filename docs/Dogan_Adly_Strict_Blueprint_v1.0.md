# Dogan Compliance — **Adly Strict™** Refactor Blueprint (v1.0)
_Last updated: 2025-08-30 04:19:57_

> One-of-a-kind compliance tech — opinionated, verifiable, tamper-evident. No vibes, just receipts.

## 0) Executive Summary
Refactor the Dogan compliance app into a **policy-driven, evidence-first platform** with **Adly Strict™** guardrails:
- **Policy-as-Code** (domain DSL compiled to WASM) with unit tests and golden snapshots.
- **Evidence Graph** (normalized, immutable) + **Attestation Service** (Ed25519-signed, Merkle-chained).
- **Append-only Audit Log** with cryptographic anchoring (optional off-chain or external anchor).
- **Data-Minimization & Tokenization** (zero-PII-by-default); **field-level encryption**; **KMS-backed keys**.
- **Deterministic Reports**: regulator-ready exports with provenance hashes.
- **Fail-Closed** runtime: if policy/evidence missing → block, alert, and open investigation.

This blueprint gives Replit a clear target: an MVP that is unique, rigorous, and demo-ready for IBM/IPM and Saudi governance use cases.

---

## 1) **Adly Strict™ Principles**
1. **Determinism over heroics**: same input → same verdict; logs prove it.
2. **Everything is Evidence**: configs, scans, approvals, waivers, runbooks, artifacts.
3. **Tamper-evidence by default**: Merkle chain + signed attestations.
4. **Zero PII unless justified**: default deny; tokenization + reversible only with legal key split.
5. **Human-in-the-loop with dual control**: sensitive actions require quorum.
6. **Time-boxed waivers**: expiries enforced in code; auto-revoke.
7. **Minimal blast radius**: per-tenant crypto isolation; least privilege IAM.
8. **Explainability**: every decision links to policy rule, inputs, and evidence hashes.
9. **Fail closed**: on ambiguity → safe stop + incident workflow.
10. **Portability**: policy/attestations are portable assets (archivable & verifiable).

---

## 2) Target Architecture (High Level)
- **Policy Engine** (`policy-engine/`): Adly-DSL → IR → WASM; verifier; rule coverage.
- **Evidence Collector** (`services/evidence-collector/`): connectors (Git, CI, SAST, DAST, SBOM, cloud configs); normalizer.
- **Attestation Service** (`services/attestation/`): Ed25519 signing, Merkle chaining, optional external anchor.
- **Audit Log** (`services/audit-log/`): append-only, content-addressed, queryable.
- **Workflow Orchestrator** (`services/workflow/`): state machines (SLA, escalation, waivers).
- **Reporting & Exporter** (`services/reporting/`): regulator templates (CSV/PDF/JSON) with provenance.
- **API Gateway** (`api/`): REST + GraphQL; OIDC; scoped tokens per tenant.
- **UI Console** (`ui/`): dashboards, evidence viewer, policy editor with tests, waiver console.
- **Privacy Layer** (`packages/privacy/`): tokenization, FLE, PII scanners, redaction.
- **Key Mgmt** (`infra/kms/`): envelope encryption via cloud KMS; HSM optional.
- **Observability** (`infra/obs/`): structured logs (OTel), metrics, traces; redaction hooks.
- **Storage**: PostgreSQL (OLTP), object store (evidence artifacts), columnar (analytics).

---

## 3) Policy-as-Code (Adly-DSL)
- **Shape**: declarative, versioned; rule sets per domain (data, infra, SDLC, vendor, privacy).
- **Compilation**: DSL → IR → WASM module; deterministic runtime + pure functions.
- **Testing**: golden snapshots; mutation testing; coverage by rule and branch.
- **Example (toy syntax):**
```adly
rule DataExportMustBeEncrypted when export.service == "s3" {{ 
  require export.kms_key_id != null
  require export.encryption == "AES256" or export.encryption == "aws:kms"
}}

rule WaiverTimebox {{ require now() < waiver.expires_at }}
```
- **Interfaces**: `evaluate(policy_package, context_json) -> decision {{allow|deny|warn, reasons[], evidence_refs[]}}`

---

## 4) Evidence Graph
- **Normalized Types**: `Scan`, `Config`, `Artifact`, `Approval`, `Waiver`, `VendorAttestation`, `RuntimeEvent`.
- **Identity**: content-addressed (SHA-256) + signed by Attestation Service.
- **Lineage**: edges: `produced_by`, `verifies`, `supersedes`, `depends_on`.
- **Retention**: WORM with legal holds; redactions leave tombstones with reason codes.
- **Query**: `evidence.where(type="Scan" and severity>=HIGH).since(90d)`

---

## 5) Attestation & Audit
- **Attestation**: Ed25519; bundle includes payload hash, subject, issuer, timestamp, policy hash.
- **Merkle Log**: each event batched into a tree; roots chained; root hash anchored (optional external anchor or notarization).
- **Verification API**: `GET /attestations/{{id}}/verify` → returns chain proof + signatures.
- **Clock discipline**: RFC 3339 timestamps; NTP drift guards.

---

## 6) Privacy & Crypto
- **Data-Minimization**: deny by default; explicit allowlists.
- **Tokenization**: irreversible tokens for analytics; reversible with split-knowledge keys.
- **Field-Level Encryption**: per tenant, per column; rotate keys; kms: envelope.
- **PII Scanning**: inbound/outbound; block on discover unless policy allows.
- **Audit Redaction**: policy-governed, tombstoned, attestable.

---

## 7) API & UI
- **REST/GraphQL** with strict scopes (`tenant:read`, `evidence:write`, `policy:admin`).
- **Rate limits** per token; mTLS for service-to-service.
- **UI** priorities: evidence explorer, policy editor with tests, waiver workflow, report builder.
- **Accessibility**: WCAG 2.2 AA; keyboard-first flows.

---

## 8) Non-Functionals & SLOs
- **Availability**: 99.9% (MVP) → 99.95% (Phase 2).
- **Latency**: p95 policy eval < 50ms; report gen 1k findings < 30s.
- **Security**: CIS Benchmarks for infra; SDLC with SAST/DAST/SBOM gates.
- **Compliance**: SOC2-ready logging; ISO 27001 controls mapping exported.

---

## 9) Threat Model (abridged)
- **T1** log tampering → Merkle + signatures + external anchor.
- **T2** policy bypass → gateway harden + fail-closed + mandatory attestations.
- **T3** key exposure → envelope keys + HSM/KMS + rotation + scoped KMS IAM.
- **T4** PII leak via logs → redaction hooks + privacy layer.
- **T5** connector supply-chain → pin versions + integrity checks + sandboxing.

---

## 10) DevEx, CI/CD, and Quality Gates
- **Trunk-based**; conventional commits; preview envs.
- **Pipelines**: lint → unit → policy-tests → mutation tests → integ → security gates → sign artifacts → deploy.
- **Quality Bars**: 90% rule-coverage; zero critical vulns; SLA monitors green.

---

## 11) Acceptance Criteria (MVP)
1. Policy engine runs WASM policies deterministically with golden tests.
2. Evidence ingested from at least 3 connectors (Git, CI, Cloud config).
3. Every decision links to evidence hashes and policy rule IDs.
4. Audit log is append-only; Merkle proofs verifiable via API.
5. Attestations signed with per-tenant keys; rotation documented.
6. Waiver workflow with expiry + dual approval.
7. Privacy layer tokenizes PII fields; reversible only via quorum.
8. Reports export with provenance hash attached and verifiable.
9. Observability: structured logs, metrics, traces; PII guard active.
10. Disaster recovery runbook + backup/restore validated.
11. RBAC scopes enforced end-to-end; least privilege checks.
12. One-click demo path for IBM/IPM with sample policies + dataset.

---

## 12) Delivery Plan (suggested)
- **Sprint 1**: policy engine, DSL skeleton, evidence schema, base connectors.
- **Sprint 2**: attestation + Merkle log, API skeleton, UI console beta.
- **Sprint 3**: privacy layer, waiver workflow, reports v1, observability.
- **Sprint 4**: hardening, performance, DR runbook, demo packaging.

---

## 13) Repository Layout (proposed)
```
policy-engine/
  src/ …
  tests/
services/
  evidence-collector/
  attestation/
  audit-log/
  workflow/
  reporting/
api/
  gateway/
ui/
  console/
packages/
  privacy/
infra/
  kms/
  db/
  obs/
docs/
  blueprint.md
tests/
  e2e/
```
---

## 14) Handoff Deliverables
- Architecture diagram, ADRs, threat model, runbooks.
- Policy packs (SDLC, Data, Vendor, Privacy) with tests.
- Demo kit (scripts + seeded evidence + sample policies).
- Compliance mapping (SOC2/ISO/Local regs) crosswalk.

---

**Definition of Done**: all Acceptance Criteria met, demo kit green, external verification endpoint returns valid proofs for a sample report.
