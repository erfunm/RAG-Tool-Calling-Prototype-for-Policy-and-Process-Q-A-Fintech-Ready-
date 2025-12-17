"""Mock policy lookup tool returning structured metadata."""
from dataclasses import dataclass
from datetime import date
from typing import Dict, Optional


@dataclass
class PolicyRecord:
    policy_id: str
    name: str
    version: str
    effective_date: date
    summary: str


class PolicyLookupTool:
    """Returns authoritative policy metadata for auditability."""

    def __init__(self) -> None:
        self._policies: Dict[str, PolicyRecord] = {
            "onboarding": PolicyRecord(
                policy_id="POL-ONB-021",
                name="Customer Onboarding Policy",
                version="2.1",
                effective_date=date(2024, 3, 1),
                summary="Identity verification, address proof thresholds, and enhanced due diligence triggers.",
            ),
            "data-retention": PolicyRecord(
                policy_id="STD-DATA-014",
                name="Data Retention Standard",
                version="1.4",
                effective_date=date(2023, 11, 15),
                summary="Retention requirements for KYC, audit logs, and marketing preferences.",
            ),
        }

    def lookup(self, key: str) -> Optional[PolicyRecord]:
        return self._policies.get(key)

    def describe(self, record: PolicyRecord) -> str:
        return (
            f"{record.name} (ID {record.policy_id}, v{record.version}, effective {record.effective_date.isoformat()}). "
            f"Summary: {record.summary} [PolicyTool]"
        )
