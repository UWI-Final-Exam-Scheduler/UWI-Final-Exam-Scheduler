from App.strategies.loadfromlast import LoadFromLastStrategy


def generate_timetable():
    strategy = LoadFromLastStrategy()
    result = strategy.execute()
    return result