from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class QueryAnalysis:
    rewritten_query: str          # semantically richer version of the user query
    tags: list[str] = field(default_factory=list)  # extracted intent tags for soft boosting


class BaseLLMClient(ABC):
    @abstractmethod
    def analyze_query(self, query: str) -> QueryAnalysis:
        """Rewrite query for semantic search and extract intent tags."""
        raise NotImplementedError
