import random


class InGameLocation:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def get_random_point(self):
        x = random.randint(self.x1, self.x2)
        y = random.randint(self.y1, self.y2)
        return (x, y)

    def get_center(self):
        return ((self.x1 + self.x2)/2, (self.y1 + self.y2)/2)
        
    def equals(self, other):
        return ((other.x1 == self.x1) and (other.y1 == self.y1) and (other.x2 == self.x2) and (other.y2 == self.y2))

    def get_width(self):
        return self.x2 - self.x1
    
    def get_height(self):
        return self.y2 - self.y1
        
    def __str__(self):
        return "({}, {}, {}, {})".format(self.x1, self.y1, self.x2, self.y2)