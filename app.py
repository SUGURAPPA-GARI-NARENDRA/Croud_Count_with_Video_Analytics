from flask import Flask, jsonify, render_template, send_file
from flask_cors import CORS
import pandas as pd
import cv2
import base64
from io import BytesIO
import json
from datetime import datetime
import threading
import time

app = Flask(__name__)
CORS(app)

# Configuration
COUNT_DATA_FILE = 'count_data.csv'
CURRENT_FRAME = None
FRAME_LOCK = threading.Lock()

# Global variables to store latest counts
latest_data = {
    'total_people': 0,
    'entry_count': 0,
    'exit_count': 0,
    'zone_counts': {},
    'timestamp': None
}

def read_csv_data():
    """Read the latest data from CSV file"""
    try:
        df = pd.read_csv(COUNT_DATA_FILE)
        if len(df) > 0:
            latest_row = df.iloc[-1]
            latest_data['timestamp'] = str(latest_row.iloc[0])
            latest_data['entry_count'] = int(latest_row.iloc[2]) if len(latest_row) > 2 else 0
            latest_data['exit_count'] = int(latest_row.iloc[3]) if len(latest_row) > 3 else 0
            
            # Parse zone counts from the second column (it's stored as a string)
            try:
                zone_dict = eval(latest_row.iloc[1])
                latest_data['zone_counts'] = zone_dict
                latest_data['total_people'] = sum(zone_dict.values())
            except:
                latest_data['zone_counts'] = {}
                latest_data['total_people'] = 0
        return True
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return False

# API Routes

@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get current statistics"""
    read_csv_data()
    return jsonify({
        'total_people': latest_data['total_people'],
        'entry_count': latest_data['entry_count'],
        'exit_count': latest_data['exit_count'],
        'net_flow': latest_data['entry_count'] - latest_data['exit_count'],
        'timestamp': latest_data['timestamp']
    })

@app.route('/api/zones', methods=['GET'])
def get_zones():
    """Get zone-wise distribution"""
    read_csv_data()
    return jsonify({
        'zones': latest_data['zone_counts'],
        'timestamp': latest_data['timestamp']
    })

@app.route('/api/all-data', methods=['GET'])
def get_all_data():
    """Get all data including stats and zones"""
    read_csv_data()
    return jsonify({
        'total_people': latest_data['total_people'],
        'entry_count': latest_data['entry_count'],
        'exit_count': latest_data['exit_count'],
        'net_flow': latest_data['entry_count'] - latest_data['exit_count'],
        'zones': latest_data['zone_counts'],
        'timestamp': latest_data['timestamp']
    })

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get historical data from CSV"""
    try:
        limit = request.args.get('limit', default=100, type=int)
        df = pd.read_csv(COUNT_DATA_FILE)
        
        # Get last 'limit' rows
        df = df.tail(limit)
        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/video-frame', methods=['GET'])
def get_video_frame():
    """Get current video frame (base64 encoded)"""
    global CURRENT_FRAME
    
    try:
        with FRAME_LOCK:
            if CURRENT_FRAME is None:
                return jsonify({'frame': None, 'status': 'no_frame'}), 200
            
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', CURRENT_FRAME)
            frame_base64 = base64.b64encode(buffer).decode()
            
        return jsonify({
            'frame': frame_base64,
            'status': 'success',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'running',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("Starting Flask server...")
    print("Access the dashboard at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)