# Technical Specification: Agent Architecture, APIs, and Video Metadata ERD

**Feature**: 1-add-agent-stories
**Created**: 2026-02-06
**Status**: Draft

## 1. Agent Roles

- Super-Orchestrator
  - Human role with final management-by-exception authority.
  - Responsibilities: approve high-risk publishes, perform emergency interventions, ratify high-risk specs, review audit trails.

- Manager Agent (multiple, role-based)
  - Long-running AI agents responsible for domain-level decision making, policy enforcement, and orchestration of worker swarms.
  - Responsibilities: schedule trend ingestion, select ideas for production, coordinate safety reviews, request publish actions via MCP, escalate to Super-Orchestrator.

- Worker Agent (swarms)
  - Short-lived or task-scoped agents that perform specific tasks: trend parsing, idea generation, asset production, metrics ingestion, remediation.
  - Responsibilities: execute work items, emit events/results, retry on transient failures, tag outputs with `specRef` and `planRef`.

## 2. Communication & Coordination Patterns

- Message Bus (internal): Agents communicate via an internal message bus (pub/sub + durable queues). Message types: Commands, Events, Queries.
  - Commands: single-consumer tasks (e.g., `ProduceAssetCommand`).
  - Events: multi-consumer broadcasts (e.g., `TrendDetectedEvent`, `AssetProducedEvent`).
  - Queries/Replies: request-scoped responses (e.g., `SafetyReviewQuery` -> `SafetyReviewResponse`).

- Coordination Patterns:
  - Manager Agents issue commands to Worker Swarms and subscribe to lifecycle events.
  - Worker Agents ACK/NACK commands; implement exponential backoff + retry policy for transient failures.
  - Saga/Orchestration pattern for multi-step flows (idea → asset → safety → publish) with compensating actions for failures.
  - Idempotency: All commands include an `idempotencyKey` to prevent duplicated effects.
  - Spec/Plan Linking: Every command/event must include `specRef` and optional `planRef` for auditability.

- External interactions (publishing, external ingestion) MUST go through MCP adapter/service. MCP acts as a gateway and enforcer for external network calls.

## 3. Conceptual API Contracts (JSON inputs/outputs)

Notes:

- These are conceptual message schemas used between agents (internal RPC/events) and for MCP-facing actions. All messages include `traceId`, `specRef`, and `createdBy` for traceability.
- Timestamps are ISO 8601 strings.

Common envelope fields (present on all messages):
{
"traceId": "string (uuid)",
"specRef": "string",
"planRef": "string | null",
"createdBy": { "agentId": "string", "agentType": "string" },
"timestamp": "string (ISO 8601)"
}

### 3.1 Trend Ingest

- TrendIngestRequest (Manager -> TrendWorker)
  {
  "source": "string", // e.g. twitter, reddit, analytics
  "since": "string (ISO) | null",
  "limit": "integer | null",
  "filters": { "languages": ["en"], "regions": ["us"] }
  }

- TrendIngestResponse
  {
  "topics": [
  { "topicId": "string", "topic": "string", "confidence": 0.0, "provenance": ["url"], "sampleSignals": [] }
  ],
  "warnings": ["string"]
  }

### 3.2 Idea Generation

- IdeaGenerationRequest (Manager -> IdeaWorker)
  {
  "topicId": "string",
  "objective": "string", // e.g. "drive awareness"
  "constraints": { "safetyLevel": "low|medium|high" },
  "seed": { /_ optional context _/ }
  }

- IdeaGenerationResponse
  {
  "ideas": [
  { "ideaId": "string", "title": "string", "summary": "string", "estimatedSignals": {"score": 0.0}, "confidence": 0.0 }
  ]
  }

### 3.3 Asset Production

- AssetProductionRequest (Manager -> ProducerWorker)
  {
  "ideaId": "string",
  "assetTypes": ["text","image","video"],
  "metadata": { "tone": "string", "length": "short|medium|long" },
  "outputConfig": { "formats": ["mp4","webp"], "resolution": "1080p" }
  }

- AssetProductionResponse
  {
  "assetPackageId": "string",
  "assets": [ { "assetId": "string", "type": "string", "locationRef": "string" } ],
  "specRef": "string",
  "warnings": []
  }

### 3.4 Safety Review

- SafetyReviewRequest (Manager -> SafetyWorker)
  {
  "assetPackageId": "string",
  "riskProfile": "low|medium|high",
  "policyHints": ["policyA","policyB"]
  }

- SafetyReviewResponse
  {
  "assetPackageId": "string",
  "verdict": "approve|reject|modify",
  "confidence": 0.0,
  "issues": [ { "code": "string", "message": "string", "severity": "low|high" } ],
  "requiredApprovalBy": { "role": "Super-Orchestrator", "reason": "string" } | null
  }

### 3.5 Publish (Manager -> MCP Adapter)

- PublishRequest
  {
  "assetPackageId": "string",
  "channels": [ { "channelId": "string", "channelType": "social|video|blog" } ],
  "scheduledAt": "ISO 8601 | null",
  "credentialsRef": "string" // MCP uses stored credentials
  }

- PublishResponse
  {
  "publishId": "string",
  "assetPackageId": "string",
  "results": [ { "channelId": "string", "status": "queued|success|failed", "externalRef": "string | null", "message": "string | null" } ]
  }

### 3.6 Engagement Metrics Ingest

- EngagementIngestRequest (MCP/ingest -> MetricsWorker)
  {
  "contentId": "string",
  "channelId": "string",
  "metrics": { "impressions": 0, "clicks": 0, "shares": 0, "comments": 0 },
  "timestampRange": { "from": "ISO", "to": "ISO" }
  }

- EngagementIngestResponse
  {
  "status": "accepted|rejected",
  "contentId": "string",
  "errors": []
  }

### 3.7 Failure & Retry Events

- FailureEvent (emitted on persistent failures)
  {
  "actionId": "string",
  "actionType": "string",
  "error": { "code": "string", "message": "string" },
  "attempts": 3,
  "status": "escalated|resolved|pending",
  "escalatedTo": { "agentId": "string", "role": "Manager" } | null
  }

### 3.8 Health & Status

- HealthReportRequest
  {
  "requestedBy": { "agentId": "string", "role": "Super-Orchestrator" },
  "period": { "from": "ISO", "to": "ISO" },
  "scope": ["ingest","safety","publish","metrics"]
  }

- HealthReportResponse
  {
  "reportId": "string",
  "summary": { "ingestSuccessRate": 0.0, "publishSuccessRate": 0.0, "openFailures": 0 },
  "links": { "auditLog": "string", "relatedSpecs": ["string"] }
  }

## 4. Database Schema: Video Metadata (ERD)

Overview: primary entity is `Video` (content asset). The schema stores metadata, provenance, publish records, and aggregated engagement metrics. All tables include `specRef` and `createdBy` for traceability.

Entities and key fields:

- Video
  - id (uuid, PK)
  - assetId (string, unique)
  - title (string)
  - durationSeconds (int)
  - contentType (enum: video|short|clip)
  - resolution (string)
  - format (string)
  - locationRef (string) -- storage or URL
  - specRef (string)
  - ideaId (uuid) FK -> ContentIdea(id)
  - createdAt (timestamp)
  - updatedAt (timestamp)

- ContentIdea
  - id (uuid, PK)
  - title (string)
  - summary (text)
  - trendId (string)
  - createdByAgent (string)
  - createdAt (timestamp)

- AssetPackage
  - id (uuid, PK)
  - packageRef (string)
  - assets (jsonb) // optional denormalized list
  - specRef (string)
  - createdAt

- PublishRecord
  - id (uuid, PK)
  - publishId (string)
  - videoId (uuid) FK -> Video(id)
  - channelId (string)
  - channelType (string)
  - status (enum)
  - externalRef (string)
  - mcpReceipt (jsonb)
  - attemptedAt (timestamp)

- EngagementMetrics (time-series / aggregated)
  - id (uuid, PK)
  - videoId (uuid) FK -> Video(id)
  - channelId (string)
  - periodStart (timestamp)
  - periodEnd (timestamp)
  - impressions (bigint)
  - clicks (bigint)
  - shares (bigint)
  - comments (bigint)
  - createdAt (timestamp)

- FailureEvent
  - id (uuid, PK)
  - actionId (string)
  - actionType (string)
  - errorCode (string)
  - errorMessage (text)
  - attempts (int)
  - escalatedTo (string)
  - status (string)
  - createdAt (timestamp)

- AgentState
  - agentId (string, PK)
  - agentType (string)
  - lastSeen (timestamp)
  - status (string)
  - metadata (jsonb)

Relationships (ERD summary):

- Video 1---\* PublishRecord
- Video 1---\* EngagementMetrics
- ContentIdea 1---\* Video
- AssetPackage 1---\* Video (via asset references)
- FailureEvent linked to any action via actionId

### Example SQL (Video table)

CREATE TABLE Video (
id uuid PRIMARY KEY,
assetId text UNIQUE NOT NULL,
title text,
durationSeconds int,
contentType text,
resolution text,
format text,
locationRef text,
specRef text NOT NULL,
ideaId uuid,
createdAt timestamptz DEFAULT now(),
updatedAt timestamptz DEFAULT now()
);

## 5. Data Responsibilities

- Agent State
  - Stored in `AgentState`; ephemeral runtime state stored in in-memory caches but persisted to DB for audit and recovery.
  - Responsibility: Manager Agents own long-lived coordination state; Worker Agents own transient task state (persisted on failure or completion).

- Content Metadata
  - Stored in `ContentIdea`, `AssetPackage`, `Video`, `PublishRecord` tables.
  - Responsibility: Producer Workers write artifacts; Manager Agents authorize and link artifacts to specs and plans.

- Logs & Audit
  - Immutable audit trail must record all decision points: command issuance, safety verdicts, publish receipts, failure escalations.
  - Store logs in an append-only store (e.g., log storage with immutability guarantees) and index events with `traceId`, `specRef`, `agentId`.

- Metrics
  - Stored in `EngagementMetrics`; aggregated into weekly/monthly rollups for reports.

## 6. Governance, Observability & Traceability

- Governance
  - All actions MUST include `specRef` and, where applicable, `planRef`.
  - High-risk verdicts require explicit Super-Orchestrator approval; safety review responses include `requiredApprovalBy` when applicable.
  - Access control: Role-based access control (RBAC) for agents and human users. Super-Orchestrator role enforced by policy service.

- Observability
  - Telemetry: Traces (distributed tracing), metrics (Prometheus-style), and logs (structured JSON). All include `traceId`.
  - Dashboards: Key dashboards for ingest success, safety verdict rates, publish success rates, open failure events, and agent health.
  - Alerts: Threshold-based alerts for failure rates, safety rejections, publish failures, and abnormal engagement spikes.

- Traceability
  - Immutable linkbacks: Every artifact (idea, asset, publish record, metrics snapshot) must include `specRef` and `traceId`.
  - Audit storage: Append-only audit sink that stores full event payloads for forensic review.
  - Drill-down: Health reports include links to relevant audit log entries and the originating spec/plan files.

## 7. Operational Notes

- Idempotency and de-duplication: All externally visible operations must be idempotent; agents must use `idempotencyKey` for retries.
- Retry policy: Exponential backoff with jitter; persistent failures after N attempts generate `FailureEvent` and escalate.
- Privacy & retention: Metadata retention policies apply; PII must not be stored unless permitted and must be redacted in audit logs.
