"""Mock case metadata tool for demonstrating structured retrieval."""
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional


@dataclass
class CaseMetadata:
    case_id: str
    status: str
    risk_flag: str
    last_updated: datetime


class CaseMetadataTool:
    """Provides case status and risk indicators."""

    def __init__(self) -> None:
        now = datetime.utcnow()
        self._cases: Dict[str, CaseMetadata] = {
            "REQ-1001": CaseMetadata(
                case_id="REQ-1001", status="pending-review", risk_flag="high-risk jurisdiction", last_updated=now
            ),
            "REQ-2002": CaseMetadata(case_id="REQ-2002", status="approved", risk_flag="none", last_updated=now),
        }

    def lookup(self, case_id: str) -> Optional[CaseMetadata]:
        return self._cases.get(case_id)

    def describe(self, record: CaseMetadata) -> str:
        return (
            f"Case {record.case_id}: status={record.status}, risk_flag={record.risk_flag}, "
            f"updated={record.last_updated.isoformat()} [CaseTool]"
        )
