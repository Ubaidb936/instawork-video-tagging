from abc import ABC, abstractmethod


class BaseTool(ABC):
    name: str
    description: str

    @abstractmethod
    def run(self, **kwargs):
        """Execute the tool and return results."""
        raise NotImplementedError
