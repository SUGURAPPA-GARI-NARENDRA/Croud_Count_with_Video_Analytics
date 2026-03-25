from flask import Flask, render_template, Response, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import cv2
import time
import threading
import pandas as pd
import os
from datetime import datetime

# Import your existing detection modules
from camera import Camera
from detector import PersonDetector
from tracker import CentroidTracker
from counter import Counter
from zone_manager import ZoneManager
import data_logger
import config

app = Flask(__name__)
app.config['SECRET_KEY'] = 'smart-people-counter-secret'
CORS(app)

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')


frame_lock = threading.Lock()
current_frame = None

data_lock = threading.Lock()
latest_data = {
    'total_people': 0,
    'entry_count': 0,
    'exit_count': 0,
    'net_flow': 0,
    'zones': {},
    'timestamp': ''
}

# Detection loop function (runs in a background thread)


# Start detection thread when the first client connects
@socketio.on('connect')
def handle_connect():
    emit('connected', {'message': 'Connected to server'})
    # Start background thread only once
    if not hasattr(app, 'detection_started'):
        app.detection_started = True
        thread = threading.Thread(target=detection_loop, daemon=True)
        thread.start()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    def generate():
        global current_frame
        while True:
            with frame_lock:
                if current_frame is not None:
                    ret, buffer = cv2.imencode('.jpg', current_frame)
                    frame_bytes = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(0.05)
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/all-data')
def get_all_data():
    with data_lock:
        return jsonify(latest_data)
# --- NEW CONFIGS ---
CROWD_THRESHOLD = 15  # Max people allowed
ALERT_DIR = "static/alerts"
if not os.path.exists(ALERT_DIR): os.makedirs(ALERT_DIR)

last_screenshot_time = 0

def detection_loop():
    global current_frame, latest_data, last_screenshot_time
    cam = Camera()
    detector = PersonDetector()
    tracker = CentroidTracker()
    counter = Counter()
    zone_manager = ZoneManager()

    while True:
        frame = cam.get_frame()
        if frame is None:
            time.sleep(0.01)
            continue

        detections = detector.detect(frame)
        objects = tracker.update(detections)
        entry, exit_ = counter.update(objects)
        zone_counts = zone_manager.update(objects)
        
        total_people = len(objects)

        # --- DRAWING LOGIC ---
        for zone_name, (x1, y1, x2, y2) in config.ZONES.items():
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"{zone_name}: {zone_counts.get(zone_name, 0)}",
                        (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        cv2.line(frame, (0, config.LINE_POSITION),
                 (frame.shape[1], config.LINE_POSITION), (0, 0, 255), 3)

        for (objectID, centroid) in objects.items():
            cv2.circle(frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)
            cv2.putText(frame, f"ID {objectID}", (centroid[0] - 10, centroid[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        # --- CROWD ALERT SCREENSHOT LOGIC ---
        if total_people > CROWD_THRESHOLD:
            current_time = time.time()
            # Only save if 10 seconds have passed since the last screenshot
            if current_time - last_screenshot_time > 10:
                timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
                screenshot_name = f"crowd_alert_{timestamp_str}.jpg"
                filepath = os.path.join(ALERT_DIR, screenshot_name)
                
                # Save the current frame
                cv2.imwrite(filepath, frame)
                
                last_screenshot_time = current_time
                print(f"📸 ALERT: Crowd limit reached! Screenshot saved to {filepath}")

        # --- UPDATE DATA & EMIT ---
        with data_lock:
            latest_data.update({
                'total_people': total_people,
                'entry_count': entry,
                'exit_count': exit_,
                'net_flow': entry - exit_,
                'zones': zone_counts,
                'timestamp': datetime.now().strftime('%H:%M:%S')
            })

        socketio.emit('data_update', latest_data)
        data_logger.log_data(zone_counts, entry, exit_)
        
        with frame_lock:
            current_frame = frame.copy()
            
        time.sleep(0.05)
# FEATURE 4: Generate Crowd Report
@app.route('/api/download-report')
def download_report():
    # In a real app, you'd process the CSV here. For now, we serve the raw log.
    return Response(open("count_data.csv"), mimetype="text/csv", 
                    headers={"Content-disposition": "attachment; filename=crowd_report.csv"})
@app.route('/api/alerts-list')
def get_alerts():
    # List all files in the alert directory, sorted by newest first
    if not os.path.exists(ALERT_DIR):
        return jsonify([])
    
    files = [f for f in os.listdir(ALERT_DIR) if f.endswith('.jpg')]
    files.sort(reverse=True) # Newest alerts first
    return jsonify(files)

if __name__ == '__main__':
    print("🚀 Smart People Counter Dashboard starting...")
    print("📍 Access at http://localhost:5000")
    # Use socketio.run instead of app.run
    socketio.run(app, debug=False, host='0.0.0.0', port=5000)