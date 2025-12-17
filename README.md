# RAG + Tool Calling Prototype for Policy and Process Q&A (Fintech-Ready)

## Problem Statement
Compliance and operations teams in regulated fintechs need a trustworthy assistant that can answer internal policy and process questions with grounded evidence and audit-ready logging. This repository contains a Python-based Retrieval-Augmented Generation (RAG) plus tool-calling prototype built for policy lookup and case metadata retrieval. It emphasizes safety, refusal behavior when evidence is insufficient, and structured logging suitable for later audits.

## Architecture Overview
```
+-----------------------------+
| User Query                  |
+--------------+--------------+
               |
               v
       +-------+-------+        +----------------+
       | Retrieval     |<-------+ Document Store |
       | (TF-IDF)      |        +----------------+
       +-------+-------+
               |
               v
       +-------+-------+        +---------------------------+
       | Safety &      |<-------+ Tools (Policy, Case Meta) |
       | Decision Layer|        +---------------------------+
       +-------+-------+
               |
               v
       +---------------+
       | Response +    |
       | Citations     |
       +---------------+
```

### Interaction of RAG and Tools
- The agent first retrieves policy/process passages via TF-IDF vector search.
- A lightweight router determines whether to call tools (e.g., for authoritative policy metadata or case status) based on intent cues in the query.
- Retrieved passages and tool outputs are combined into a final answer with citation tags like `[Doc-2]` or `[PolicyTool]`.

### Safety, Refusal, and Escalation
- If the top retrieved similarity score falls below a configured threshold, the agent refuses to answer and suggests escalation: _"Insufficient evidence found. Please escalate to Compliance."_
- Conflicting evidence or missing required tool fields also trigger refusal.
- Prompts include explicit instructions to avoid speculation and to surface uncertainty.

## Running the Prototype Locally
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.agent.policy_agent --question "What is the onboarding policy threshold?"
```

### Configuration
- Default values live in `configs/default.yaml`.
- Logging is JSONL via `src/logging/audit_logger.py` and writes to `logs/audit.log` by default.

## Repository Structure
```
.
├── README.md
├── ROADMAP.md
├── configs/
│   └── default.yaml
├── data/
│   └── documents/
├── requirements.txt
├── src/
│   ├── agent/
│   ├── retrieval/
│   ├── tools/
│   ├── prompts/
│   └── logging/
└── tests/
    └── evaluation/
```

## Limitations and Next Steps
- Prototype retrieval uses TF-IDF; swap in domain embeddings for better recall.
- Tool routing is rule-based; integrate LLM-based function calling for richer orchestration.
- Evaluation set is small; expand golden questions and add safety regression suites.
- Latency is single-machine and unoptimized; see `ROADMAP.md` for production targets.

## License
This project is licensed under the MIT License. See `LICENSE` for details.
