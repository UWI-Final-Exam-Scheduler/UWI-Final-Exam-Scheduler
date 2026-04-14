from App.strategies.loadfromlast import LoadFromLastStrategy
from App.strategies.strategy import SchedulingStrategy

class ExamSchedulerService:
    def __init__(self):
        # Currently using LoadFromLastStrategy as the default and only strategy 
        self.strategy: SchedulingStrategy = LoadFromLastStrategy()

    def generate_timetable(self, **kwargs):
        
        # In the future, if more strategies are added,
        # logic can be implemented here to select the appropriate strategy based on kwargs or other criteria.

        return self.strategy.execute(**kwargs)
