from abc import ABC, abstractmethod

class SchedulingStrategy(ABC):
    @abstractmethod
    def execute(self, **kwargs):
        pass