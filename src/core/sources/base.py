from dataclasses import dataclass, field
from typing import Any


@dataclass
class Source:
    title: str
    url: str
    snippet: str
    source_type: str  # 'europepmc' | 'medlineplus' | 'openfda'
    score: float = 1.0
    extra_meta: dict[str, Any] | None = field(default_factory=dict)
