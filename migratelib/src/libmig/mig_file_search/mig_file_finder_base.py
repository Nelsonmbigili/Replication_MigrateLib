from abc import ABC, abstractmethod


class MigFileFinderBase(ABC):
    @abstractmethod
    def find(self) -> dict[str, any]:
        pass
