class Counters:
    __COUNTERS = dict()

    def __init__(self):
        raise NotImplementedError("Counters object is static. Object creation isn't allowed.")

    @staticmethod
    def get_all_counters():
        return Counters.__COUNTERS

    @staticmethod
    def get_counter_by_name(name):
        return Counters.__COUNTERS.get(name, None)

    @staticmethod
    def increment(name):
        Counters.increment_by_number(name, 1)

    @staticmethod
    def increment_by_number(name, num):
        Counters.__COUNTERS[name] = Counters.__COUNTERS.get(name, 0) + num



