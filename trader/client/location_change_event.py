class LocationChangeEvent:
    def __init__(self, location):
        self.location = location

    @staticmethod
    def create(log_line):
        if log_line.find("You have entered") == -1:
            return None
        location = log_line.strip().split("You have entered")[1][:-1]
        if location:
            return LocationChangeEvent(location)
        return None
