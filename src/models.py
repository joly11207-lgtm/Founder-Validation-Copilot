from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class Opportunity:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    title: str = ""
    input_type: str = ""
    original_input: str = ""
    keywords: list = field(default_factory=list)
    score: int = 0
    decision: str = ""
    status: str = "Inbox"
    report_markdown: str = ""

    def to_dict(self):
        return {
            "id": self.id,
            "created_at": self.created_at,
            "title": self.title,
            "input_type": self.input_type,
            "original_input": self.original_input,
            "keywords": self.keywords,
            "score": self.score,
            "decision": self.decision,
            "status": self.status,
            "report_markdown": self.report_markdown,
        }

    @classmethod
    def from_dict(cls, d: dict):
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


STATUS_OPTIONS = ["Inbox", "Researching", "Validated", "Building", "Launched", "Archived"]
