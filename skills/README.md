# Agent Skill System — Project Chimera

**Feature**: 1-add-agent-stories
**Created**: 2026-02-06

## What a Skill Is

A Skill is a discrete, testable capability an agent can execute to perform a single well-scoped task (for example: fetch trends, generate content, or publish content). A Skill defines a clear input contract, a deterministic output contract, and documented failure modes. Skills are behavioral primitives composed by Manager Agents and orchestrators to build higher-level flows.

## What a Skill Is Not

- A Skill is not implementation code or a runtime library. Do NOT include implementation details, frameworks, or environment-specific instructions in a skill definition.
- A Skill is not an authorization or governance policy; it may require approvals but does not itself define RBAC rules.
- A Skill is not a long-running process with external side effects unless invoked via an orchestration command and recorded with `specRef` and `traceId`.

---

## Common Envelope (present on all skill inputs/outputs)

{
"traceId": "string (uuid)",
"specRef": "string",
"planRef": "string | null",
"createdBy": { "agentId": "string", "agentType": "string" },
"timestamp": "string (ISO 8601)"
}

---

## skill_fetch_trends

- Purpose
  - Ingest external signals and return ranked topics with provenance and confidence to guide idea generation.

- Input contract
  {
  // Envelope fields +
  "source": "string", // e.g. "twitter", "reddit", "analytics"
  "since": "string (ISO) | null",
  "limit": "integer | null",
  "filters": { "languages": ["en"], "regions": ["us"] }
  }

- Output contract
  {
  // Envelope fields +
  "topics": [
  {
  "topicId": "string",
  "topic": "string",
  "confidence": 0.0,
  "provenance": ["string (url or source-id)"],
  "sampleSignals": [ { "signalType": "string", "value": "string|number" } ]
  }
  ],
  "warnings": ["string"]
  }

- Failure conditions
  - Transient network failure to source: return error with retryable=true and include `attempts` and `nextRetryAt` fields.
  - Malformed or unverifiable provenance: return `topics` with empty provenance and a `warnings` entry; quarantined batches logged for manual review.
  - No data found: return empty `topics` and a non-error `warnings` explaining the scope/time window.

---

## skill_generate_content

- Purpose
  - Produce a set of ranked content ideas and associated rationale for a given topic and objective.

- Input contract
  {
  // Envelope fields +
  "topicId": "string",
  "objective": "string", // e.g., "drive awareness"
  "constraints": { "safetyLevel": "low|medium|high" },
  "seedContext": { /_ optional free-form context _/ }
  }

- Output contract
  {
  // Envelope fields +
  "ideas": [
  {
  "ideaId": "string",
  "title": "string",
  "summary": "string",
  "estimatedSignals": { "score": 0.0 },
  "confidence": 0.0
  }
  ],
  "meta": { "generatedBy": "agentId", "modelVersion": "string | null" }
  }

- Failure conditions
  - Safety constraint violation detected (topic or seed flagged): return empty `ideas` and a `meta.reason` with `requiresApproval=true` if Super-Orchestrator review is required.
  - Model generation timeout or resource exhaustion: return error with `retryable=true` and `suggestedBackoffSeconds`.
  - Low-confidence generation (confidence below threshold): return ideas marked with low `confidence` and suggest additional signals or human review.

---

## skill_publish_content

- Purpose
  - Request a publish action for an approved asset package to one or more external channels via the MCP-PublishGateway and return publish receipts.

- Input contract
  {
  // Envelope fields +
  "assetPackageId": "string",
  "channels": [ { "channelId": "string", "channelType": "social|video|blog" } ],
  "scheduledAt": "string (ISO) | null",
  "credentialsRef": "string" // reference to MCP-managed credentials
  }

- Output contract
  {
  // Envelope fields +
  "publishId": "string",
  "assetPackageId": "string",
  "results": [
  { "channelId": "string", "status": "queued|success|failed", "externalRef": "string | null", "message": "string | null" }
  ]
  }

- Failure conditions
  - MCP-PublishGateway authentication failure: return failure with `retryable=false` and escalate to Manager Agent for credential rebind.
  - Channel rate-limit or transient delivery failure: return `status=failed` with `retryable=true` and include `retryPolicy` guidance; system must schedule retries per global retry policy.
  - Safety mismatch (attempt to publish an unapproved or high-risk asset): reject with `status=failed`, include `reason` and set `requiresApproval=true`.

---

## Notes on Failures and Retries

- All failures must include `error.code`, `error.message`, `attempts`, `retryable` (bool), and suggested `nextRetryAt` or `retryPolicy` when applicable.
- Persistent failures after retry budget must emit a `FailureEvent` with escalation metadata linking to `agentId`, `specRef`, and `traceId`.
