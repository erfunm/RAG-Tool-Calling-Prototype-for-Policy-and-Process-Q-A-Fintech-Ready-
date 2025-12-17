# Roadmap to Production

## Latency Targets
- **P50:** < 800 ms for single-turn Q&A with warm cache.
- **P95:** < 1500 ms including retrieval, tool execution, and generation.
- Enable batching for embedding calls and shared vector index for multi-tenant use.

## Permissioning and Access Control
- Integrate with IAM to scope policy visibility by team/role (Compliance, Ops, Risk).
- Enforce row-level filters on retrieval to prevent cross-LOB leakage.
- Sign tool responses with provenance metadata and validate request context (user, case, purpose).

## Evaluation Strategy
- **Golden Q&A set:** curated by Compliance covering onboarding, KYC, fraud escalation, and data retention.
- **Safety regression:** include refusal cases (insufficient evidence, conflicting policy versions, unsupported jurisdictions).
- **Audit replay:** run historical queries through new models to ensure consistent decisions.
- **Offline metrics:** grounding precision/recall and citation accuracy.
- **Online:** guarded canary with error budgets; block release on refusal-rate regression.

## Observability and Auditability
- Centralize JSONL logs to SIEM; attach correlation IDs per request.
- Track retrieval scores, tool calls, and response provenance.
- Emit structured safety outcomes (answered/refused/escalated) for dashboards.

## Tooling Hardening
- Move tools behind service layer with auth + rate limits.
- Add schema validation and contract tests for tool payloads.
- Support sandbox vs. production endpoints.

## RAG Improvements
- Replace TF-IDF with domain embeddings + approximate nearest neighbor index.
- Add semantic chunking with section headers and policy hierarchy.
- Implement temporal filtering by policy effective date.

## Deployment
- Containerize with Docker; publish Helm chart for k8s.
- Use feature flags to enable new models/tools safely.
- Provide disaster-recovery plan and data retention controls.
