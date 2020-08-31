from siosa.data.zones import Zones


class ZoneChangeEvent:
    MAP = {
        'The Menagerie': Zones.MENAERIE,
        'Azurite Mine': Zones.DELVE,
        'The Sacred Grove': Zones.HARVEST,
        'Tane\'s Laboratory': Zones.METAMORPH,
        'Aspirants\' Plaza': Zones.ASPIRANTS_PLAZA
    }

    def __init__(self, zone_str):
        self.zone_str = zone_str
        self.zone = self._get_zone_type()

    @staticmethod
    def create(log_line):
        if log_line.find("You have entered") == -1:
            return None
        zone = log_line.strip().split("You have entered ")[1][:-1].strip()
        if zone:
            return ZoneChangeEvent(zone)
        return None

    def _get_zone_type(self):
        if self.zone_str.find("Hideout") > -1:
            return Zones.HIDEOUT
        elif self.zone_str in ZoneChangeEvent.MAP.keys():
            return ZoneChangeEvent.MAP[self.zone_str]
        else:
            return Zones.UNKNOWN
