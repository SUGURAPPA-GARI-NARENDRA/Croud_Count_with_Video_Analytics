import config

class Counter:
    def __init__(self):
        self.entry_count = 0
        self.exit_count = 0
        self.counted_ids = set()
        self.previous_positions = {}

    def update(self, objects):
        for objectID, centroid in objects.items():
            cX, cY = centroid

            prevY = self.previous_positions.get(objectID, None)

            if prevY is not None:
                # Entry
                if prevY < config.LINE_POSITION and cY >= config.LINE_POSITION:
                    if objectID not in self.counted_ids:
                        self.entry_count += 1
                        self.counted_ids.add(objectID)

                # Exit
                elif prevY > config.LINE_POSITION and cY <= config.LINE_POSITION:
                    if objectID not in self.counted_ids:
                        self.exit_count += 1
                        self.counted_ids.add(objectID)

            self.previous_positions[objectID] = cY

        return self.entry_count, self.exit_count