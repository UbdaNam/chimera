# MCP Servers: Developer & Runtime (Project Chimera)

**Feature**: 1-add-agent-stories
**Created**: 2026-02-06

This document lists Model Context Protocol (MCP) servers used by Project Chimera and separates developer-facing MCPs (governance, versioning, observability) from runtime MCPs (agent-facing gateways to external systems). Each entry includes Purpose, Who can use it, Allowed actions, and Security & Audit considerations.

---

## Developer MCPs

### MCP-Governance

- Purpose: Centralized policy, role, and approval service. Enforces constitution rules (e.g., Super-Orchestrator approvals), records approvals, and manages RBAC for agents and humans.
- Who can use it: Human Super-Orchestrator, authorized Manager Agents, governance tools.
- Allowed to do: Query and enforce policy decisions, record approvals/rejections, require human sign-off on high-risk actions, attach policy metadata to specs and plans.
- Security & audit: Strong authentication (mTLS + RBAC), immutable approval records, tamper-evident audit logs, mandatory `specRef` on decisions. All approvals include approverId, timestamp, and reasoning.

### MCP-VersionControl

- Purpose: Mediated access to repository operations (spec storage, immutable spec snapshots, spec-version linking). Provides programmatic, auditable commits/tags for specs and plans.
- Who can use it: Manager Agents (limited ops), trusted automation, human maintainers.
- Allowed to do: Read spec artifacts, propose spec changes (creating draft refs), tag approved specs, create signed snapshots; write operations require governance policy checks.
- Security & audit: Commits and snapshots are signed; write operations require policy validation and are recorded with `traceId` and `agentId`. Direct pushes restricted; MCP enforces branch protection.

### MCP-Observability

- Purpose: Centralized telemetry ingestion and query for traces, metrics, and structured logs (for dashboards and forensic analysis).
- Who can use it: Operators, Manager Agents (read), authorized analytics workers.
- Allowed to do: Ingest structured telemetry, query dashboards, export audit slices. Does NOT perform external network calls on behalf of agents.
- Security & audit: Immutable retention options for audit logs, access controls for sensitive logs, redaction for PII, all telemetry tagged with `traceId` and `specRef`.

---

## Runtime MCPs

### MCP-PublishGateway

- Purpose: Mediates all outbound publishing interactions to external channels (social, video platforms, blogs) per the constitution's "no direct external calls" rule.
- Who can use it: Manager Agents via authenticated MCP calls only.
- Allowed to do: Queue and deliver publish requests, manage credentials (secure vault), return publish receipts, and throttle/rate-limit per-channel policies.
- Security & audit: Enforces credential vault access controls, signs receipts, stores publish receipts immutably, logs `traceId`, `specRef`, channelId, and result metadata. Rate-limiting and content-safety checks upstream required before publish.

### MCP-IngestGateway

- Purpose: Mediates ingestion of external signals (trends, metrics) into the internal message bus; provides sanitization and schema validation.
- Who can use it: External data providers (via managed connectors) and MCP adapters.
- Allowed to do: Accept inbound feeds, normalize schemas, validate provenance, produce `TrendDetectedEvent`/`EngagementIngest` entries.
- Security & audit: Source authentication (API keys, signing), ingest validation logs, quarantine of malformed data, all ingested batches tagged with provenance and `traceId`.

### MCP-StorageGateway

- Purpose: Secure storage adapter for large assets (media files, model artifacts) and signed location references returned to agents.
- Who can use it: Producer Worker Agents (via Manager commands) and MCP-PublishGateway.
- Allowed to do: Store and retrieve blobs, generate short-lived signed URLs, enforce access policies.
- Security & audit: Blob immutability options, access logs, signed URL expiration, content-hash integrity checks, and `specRef` metadata attached to stored objects.

### MCP-Auth (Identity)

- Purpose: Centralized identity and credential service for agents and humans; issues short-lived tokens for runtime MCPs.
- Who can use it: All agents and human users (subject to RBAC rules).
- Allowed to do: Issue/refresh tokens, validate identities, map agent roles to permissions.
- Security & audit: Token issuance logged, refresh attempts monitored, token revocation supported, and all auth events include `agentId`, `role`, and `traceId`.

---

## Cross-cutting Security & Audit Considerations

- All MCP servers MUST record `traceId`, `specRef`, `agentId`, and timestamp for every request and response to enable end-to-end traceability.
- Developer MCPs require stronger write-guarding: any mutation that affects specs, approvals, or policies requires an auditable approval workflow recorded in MCP-Governance.
- Runtime MCPs enforce least privilege: agents receive scoped credentials/tokens with limited lifetime and scope; secrets are never stored in plain text by agents.
- Immutable audit sink: key events (safety verdicts, publish receipts, governance approvals, failure escalations) must be forwarded to an append-only audit store for forensics.
- Data residency & retention: MCPs must support configurable retention policies and redaction for PII; audit logs must be tamper-evident.

---

## Traceability & Usage Guidance

- Every MCP call should include `specRef` and `planRef` when available. `traceId` must be generated at the user-facing command boundary (Manager Agent) and propagated across MCPs and worker swarms.
- High-risk operations routed via MCP-Governance for approval checks before the runtime MCPs perform side-effecting actions (e.g., `MCP-PublishGateway`).
