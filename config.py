# config.py

MODEL_PATH = "yolov8n.pt"   # lightweight & fast
CONFIDENCE = 0.4

# Entry/Exit line position (Y coordinate)
LINE_POSITION = 300

# Zone definitions (x1, y1, x2, y2)
ZONES = {
    "Zone 1": (50, 100, 350, 450),
    "Zone 2": (400, 100, 700, 450)
}