"""Policy and process QA agent with RAG + tool calling."""
import argparse
from dataclasses import dataclass
from typing import List

import yaml

from src.logging.audit_logger import configure_logger, log_event
from src.prompts.base_prompt import SYSTEM_PROMPT
from src.retrieval.document_store import DocumentStore, DocumentChunk
from src.tools.case_metadata_tool import CaseMetadataTool
from src.tools.policy_tool import PolicyLookupTool


@dataclass
class AgentResponse:
    answer: str
    citations: List[str]
    status: str  # answered | refused | escalated


class PolicyAgent:
    """Lightweight agent that fuses RAG and structured tool calls."""

    def __init__(self, config_path: str = "configs/default.yaml") -> None:
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)
        self.store = DocumentStore(config_path)
        self.policy_tool = PolicyLookupTool()
        self.case_tool = CaseMetadataTool()
        self.logger = configure_logger(config_path)

    def _route(self, question: str) -> str:
        question_lower = question.lower()
        if "policy" in question_lower or "effective" in question_lower:
            return "policy"
        if "case" in question_lower or "req-" in question_lower:
            return "case"
        return "retrieval"

    def _answer_with_retrieval(self, question: str) -> AgentResponse:
        scored = self.store.search(question, k=self.config.get("agent", {}).get("max_context_docs", 3))
        log_event(
            self.logger,
            "retrieval",
            {
                "question": question,
                "results": [
                    {"doc_id": chunk.doc_id, "score": float(score), "text": chunk.text[:200]} for chunk, score in scored
                ],
            },
        )
        if not self.store.has_sufficient_evidence(scored):
            return AgentResponse(
                answer="Insufficient evidence found. Please escalate to Compliance.", citations=[], status="escalated"
            )
        answer_parts = []
        citations = []
        for idx, (chunk, _) in enumerate(scored, start=1):
            citations.append(f"[Doc-{idx}]")
            answer_parts.append(f"{chunk.text.strip()} [Doc-{idx}]")
        return AgentResponse(answer=" ".join(answer_parts), citations=citations, status="answered")

    def _answer_with_policy_tool(self, question: str) -> AgentResponse:
        key = "onboarding" if "onboard" in question.lower() else "data-retention"
        record = self.policy_tool.lookup(key)
        log_event(
            self.logger,
            "tool_call",
            {"tool": "policy_lookup", "key": key, "found": bool(record)},
        )
        if not record:
            return AgentResponse(
                answer="Insufficient evidence found. Please escalate to Compliance.", citations=[], status="escalated"
            )
        description = self.policy_tool.describe(record)
        return AgentResponse(answer=description, citations=["[PolicyTool]"], status="answered")

    def _answer_with_case_tool(self, question: str) -> AgentResponse:
        case_id = next((token for token in question.split() if token.upper().startswith("REQ-")), None)
        record = self.case_tool.lookup(case_id) if case_id else None
        log_event(
            self.logger,
            "tool_call",
            {"tool": "case_metadata", "case_id": case_id, "found": bool(record)},
        )
        if not record:
            return AgentResponse(
                answer="Insufficient evidence found. Please escalate to Compliance.", citations=[], status="escalated"
            )
        description = self.case_tool.describe(record)
        return AgentResponse(answer=description, citations=["[CaseTool]"] , status="answered")

    def answer(self, question: str) -> AgentResponse:
        log_event(self.logger, "user_query", {"question": question})
        route = self._route(question)
        if route == "policy" and self.config.get("agent", {}).get("enable_policy_tool", True):
            return self._answer_with_policy_tool(question)
        if route == "case" and self.config.get("agent", {}).get("enable_case_tool", True):
            return self._answer_with_case_tool(question)
        return self._answer_with_retrieval(question)


def main() -> None:
    parser = argparse.ArgumentParser(description="RAG + tool-calling policy agent")
    parser.add_argument("--question", required=True, help="User question about policy or process")
    parser.add_argument("--config", default="configs/default.yaml", help="Path to config YAML")
    args = parser.parse_args()

    agent = PolicyAgent(args.config)
    response = agent.answer(args.question)

    print("System Prompt:\n", SYSTEM_PROMPT)
    print("\nAnswer:\n", response.answer)
    print("Citations:", " ".join(response.citations))
    print("Status:", response.status)


if __name__ == "__main__":
    main()
