import config

class ZoneManager:
    def __init__(self):
        self.zone_counts = {zone: 0 for zone in config.ZONES}
        self.zone_ids = {zone: set() for zone in config.ZONES}

    def update(self, objects):
        # Reset counts (or implement persistent occupancy)
        # Here we count current objects in each zone
        for zone_name, (x1, y1, x2, y2) in config.ZONES.items():
            self.zone_counts[zone_name] = 0
            self.zone_ids[zone_name].clear()

        for objectID, (cX, cY) in objects.items():
            for zone_name, (x1, y1, x2, y2) in config.ZONES.items():
                if x1 < cX < x2 and y1 < cY < y2:
                    self.zone_counts[zone_name] += 1
                    self.zone_ids[zone_name].add(objectID)

        return self.zone_counts