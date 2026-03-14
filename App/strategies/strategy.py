from abc import ABC, abstractmethod

class SchedulingStrategy(ABC):
    @abstractmethod
    def generate_schedule(self, exams, venues):
        pass