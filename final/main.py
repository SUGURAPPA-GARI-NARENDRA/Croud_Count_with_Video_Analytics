import cv2
import config
from detector import PersonDetector
from tracker import CentroidTracker
from counter import Counter
from zone_manager import ZoneManager
from data_logger import log_data

detector = PersonDetector()
tracker = CentroidTracker()
counter = Counter()
zone_manager = ZoneManager()

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    detections = detector.detect(frame)
    objects = tracker.update(detections)

    entry, exit = counter.update(objects)
    zone_counts = zone_manager.update(objects)

    # Draw zones
    for zone_name, (x1, y1, x2, y2) in config.ZONES.items():
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
        cv2.putText(frame, f"{zone_name}: {zone_counts[zone_name]}",
                    (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (0,255,0), 2)

    # Draw line
    cv2.line(frame, (0, config.LINE_POSITION),
             (frame.shape[1], config.LINE_POSITION),
             (0,0,255), 2)

    # Draw tracked objects
    for objectID, (cX, cY) in objects.items():
        cv2.circle(frame, (cX, cY), 5, (255,0,0), -1)
        cv2.putText(frame, f"ID {objectID}",
                    (cX - 10, cY - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (255,0,0), 2)

    # Dashboard Panel
    total_people = len(objects)

    cv2.rectangle(frame, (10,10), (350,180), (50,50,50), -1)

    cv2.putText(frame, f"Total People: {total_people}", (20,40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
    cv2.putText(frame, f"Entry Count: {entry}", (20,70),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
    cv2.putText(frame, f"Exit Count: {exit}", (20,100),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)

    y_offset = 130
    for zone_name, count in zone_counts.items():
        cv2.putText(frame, f"{zone_name}: {count}",
                    (20, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (255,255,0), 2)
        y_offset += 25

    log_data(zone_counts, entry, exit)

    cv2.imshow("Smart People Counter", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()