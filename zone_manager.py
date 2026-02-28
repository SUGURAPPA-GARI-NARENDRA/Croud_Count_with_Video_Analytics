import config

class ZoneManager:
    def __init__(self):
        self.zone_counts = {zone: 0 for zone in config.ZONES}
        self.zone_ids = {zone: set() for zone in config.ZONES}

    def update(self, objects):
        for zone_name, (x1, y1, x2, y2) in config.ZONES.items():
            for objectID, (cX, cY) in objects.items():
                if x1 < cX < x2 and y1 < cY < y2:
                    if objectID not in self.zone_ids[zone_name]:
                        self.zone_counts[zone_name] += 1
                        self.zone_ids[zone_name].add(objectID)

        return self.zone_counts