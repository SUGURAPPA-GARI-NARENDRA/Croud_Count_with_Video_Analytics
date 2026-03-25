# config.py
MODEL_PATH = "yolov8n.pt"
CONFIDENCE = 0.4
LINE_POSITION = 300

# Task 3: Define Max Limits
ZONE_LIMITS = {
    "Zone 1": 5,
    "Zone 2": 3
}

ZONES = {
    "Zone 1": (50, 100, 350, 450),
    "Zone 2": (400, 100, 700, 450)
}

# Task 5: Screenshot Path
ALERT_SCREENSHOT_PATH = "alerts/"