"""Smoke tests for policy agent behaviors."""
from src.agent.policy_agent import PolicyAgent


def test_policy_tool_route():
    agent = PolicyAgent()
    response = agent.answer("What is the effective date of the onboarding policy?")
    assert "PolicyTool" in " ".join(response.citations)
    assert response.status == "answered"


def test_refusal_when_unknown_case():
    agent = PolicyAgent()
    response = agent.answer("What is the status of case REQ-9999?")
    assert response.status == "escalated"
    assert "Insufficient evidence" in response.answer
