<!--
Sync Impact Report
- Version change: none -> 1.0.0
- Modified principles: added all core principles for Project Chimera
- Added sections: Mission, Non-Negotiable Principles, Safety & Governance, Operational Assumptions
- Removed sections: template placeholders
- Templates requiring updates: ✅ .specify/templates/plan-template.md
- Follow-up TODOs: None
-->

# Project Chimera High-level vision and Constraints.

## Mission and Long-Term Intent

Mission: Project Chimera is an Autonomous Influencer Network of persistent, goal-directed AI agents operating under a hierarchical swarm model. The system's long-term intent is to reliably pursue defined objectives while preserving human-aligned governance, auditability, and safe operation.

The mission is primary and immutable: all project activities MUST serve the stated objectives and uphold the constraints in this constitution.

## Non-Negotiable Architectural Principles

1. Spec-Driven Development (MANDATORY)

- Every change or capability MUST originate as a written specification. Specifications are the authoritative source of truth for requirements, success criteria, and acceptance tests.

2. Hierarchical Swarm Orchestration (MANDATORY)

- Agent behavior MUST follow a hierarchical swarm model: responsibilities, authority, and escalation paths are defined in specifications and enforced at runtime.

3. Single Human Super-Orchestrator (MANDATORY)

- There MUST be exactly one human Super-Orchestrator with final management-by-exception authority for any given operational domain. This role is responsible for emergency intervention, policy overrides, and certifying high-risk operations.

4. Mandatory Use of MCP for External Interactions (MANDATORY)

- All interactions with external systems, networks, or third parties MUST be mediated through the MCP interface. Direct external access by internal agents is forbidden.

5. Separation of Phases (MANDATORY)

- Specification, Planning, and Implementation phases MUST be strictly separated. No implementation activity may commence until specifications are ratified and planning phase outputs (tasks, success criteria, test harnesses) are complete.

## Safety, Governance, Auditability, and Traceability (MANDATORY REQUIREMENTS)

- Immutable Specifications: All specifications and approved amendments MUST be stored immutably and versioned.
- Audit Trails: Every decision, plan, task assignment, and external interaction MUST be recorded with sufficient context to reproduce the decision path and actor (agent id or human id).
- Human Oversight: The Super-Orchestrator MUST have timely visibility into audit logs and the ability to pause or halt swarm operations.
- Management-by-Exception: Routine operations may be automated; any deviation from expected behavior or failed safety checks MUST escalate to the Super-Orchestrator.
- Traceability: Implementations MUST include links to the originating specification and plan for every delivered artifact or behavior.
- Required Reviews: High-risk specifications (as defined by risk classification in the spec) MUST require explicit human approval from the Super-Orchestrator before execution.

## Operational Assumptions

- Agents-as-Implementers: The constitution assumes AI agents (not humans) will perform the majority of implementation work. This is a governance assumption and not a technical mandate.
- Role Clarity: Agents, planners, and verifiers MUST have clearly defined roles; agents MAY propose plans but MAY NOT execute outside approved plans without Super-Orchestrator approval.

## Constraints and Prohibitions (EXPLICIT RULES)

- No More Than One Super-Orchestrator: At any time there MUST be one, and only one, human Super-Orchestrator per operational domain.
- No Direct External Calls: Agents MUST NOT call external services except through MCP.
- No Implementation During Specification: Implementation work MUST NOT begin until the specification and planning phases are complete and ratified.
- Immutable Record Linking: Every runtime action that affects system state MUST reference originating spec and plan identifiers.

## Governance and Amendment Procedure

- Supremacy: This constitution supersedes other project documents in cases of conflict.
- Amendments: Amendments to this constitution MUST be proposed as a specification, include rationale and migration plan, and be ratified by the Super-Orchestrator and a two-thirds quorum of the governance committee (unless the Super-Orchestrator invokes emergency amendment authority).
- Versioning: Constitution versions follow semantic versioning. Non-breaking clarifications use patch bumps; additions of principles use minor bumps; removal or redefinition of principles use major bumps.

## Compliance and Enforcement

- All project artifacts (specs, plans, tasks, and code) MUST include a compliance matrix that maps items to constitution principles.
- Automated gates in the planning workflow MUST enforce constitution checks before entering implementation.

**Version**: 1.0.0 | **Ratified**: 2026-02-06 | **Last Amended**: 2026-02-06
