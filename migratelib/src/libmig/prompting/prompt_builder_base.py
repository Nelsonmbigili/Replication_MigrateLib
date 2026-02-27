from abc import abstractmethod, ABC


class PromptBuilderBase(ABC):
    @abstractmethod
    def build(self, file: str):
        pass
