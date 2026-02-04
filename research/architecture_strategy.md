# Project Chimera – Architecture Strategy

## 1. Agent Orchestration Pattern

- Selected Pattern: Hierarchical Swarm

Project Chimera adopts a Hierarchical Swarm architecture, where:

- A single Human Super-Orchestrator governs intent and policy.
- AI Manager Agents translate intent into executable plans.
- Specialized Worker Swarms execute tasks in parallel.

**Reasoning**:

- This pattern allows for scalable coordination of multiple agents while maintaining human oversight and control.
- This pattern avoids chaos of linear chains and ungoverned swarms.

## 2. Human-in-the-Loop Safety Layer (Human Reviewers (HITL Moderators))

- Humans approve policies, constraints, and specs, not individual actions.
- Interaction: They utilize a streamlined Review Interface (part of the Dashboard) to quickly Approve, Reject, or Edit agent-generated content.
- They receive escalated tasks from the Judge Agents—content that is flagged as low-confidence, sensitive, or high-risk.
- If a Worker proposes a transaction that exceeds the limit or matches a suspicious pattern, the CFO Judge strictly REJECTS the task and flags it for human review

## 3. Data & Storage Strategy (Video Metadata)

**Primary Store: Relational (SQL) Database**: Well-suited for structured metadata and lifecycle state.
**Supplementary Storage**: Object storage for media assets and event logs for observability and replay.
