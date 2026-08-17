from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class TagResult:
    description: str       # rich natural language understanding of the video
    tags: list[str]        # short categorical labels for filtering


class BaseTagger(ABC):
    @abstractmethod
    def tag(self, video_path: str) -> TagResult:
        """Analyze a local video file and return description + tags."""
        raise NotImplementedError
