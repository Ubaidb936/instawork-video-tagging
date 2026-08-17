from abc import ABC, abstractmethod
from sqlalchemy.orm import Session


class BaseAgent(ABC):
    @abstractmethod
    def run(self, query: str, db: Session) -> list:
        """Process a user query and return results."""
        raise NotImplementedError
