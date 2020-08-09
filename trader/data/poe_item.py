from enum import Enum

class ItemRarities(Enum):
    UNKNOWN = 0
    NORMAL = 1
    MAGIC = 2
    RARE = 3
    UNIQUE = 4

class ItemType(Enum):
    UNKNOWN = 0
    CURRENCY = 1
    ITEM = 2

class Item:
    def __init__(self, name, type=ItemType.UNKNOWN, rarity=ItemRarities.UNKNOWN):
        self.type = type
        self.rarity = rarity
        self.name = name
    
    def __str__(self):
        return "Rarity: {}, Name: {}".format(self.rarity, self.name)