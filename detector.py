from ultralytics import YOLO
import config

class PersonDetector:
    def __init__(self):
        self.model = YOLO(config.MODEL_PATH)

    def detect(self, frame):
        results = self.model(frame, conf=config.CONFIDENCE)
        detections = []

        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                if cls == 0:  # 0 = person
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    detections.append((x1, y1, x2, y2))

        return detections