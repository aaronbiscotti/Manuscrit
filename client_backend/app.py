from flask import Flask, request, jsonify, session
from flask_cors import CORS
from datetime import datetime
import os
import cv2
import numpy as np
from queue import Queue
import threading
import time
import shutil
import subprocess
from dataclasses import dataclass
from typing import Dict

app = Flask(__name__)
app.config['SECRET_KEY'] = 'aadf68b78ebde4d4eab634b448a9df4a'
CORS(app)

UPLOAD_FOLDER = 'uploads'
GCODE_FOLDER = 'gcode'
PROCESSED_FOLDER = 'processed'
for folder in [UPLOAD_FOLDER, GCODE_FOLDER, PROCESSED_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

@dataclass
class Job:
    user_name: str
    timestamp: str
    png_path: str
    gcode_path: str
    status: str = 'pending'

# Globals
job_queue = Queue()
jobs: Dict[str, Job] = {}
jobs_lock = threading.Lock()

def process_drawing(png_path, gcode_path):
    try:
        img = cv2.imread(png_path)
        if img is None:
            raise ValueError("Failed to load image")

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        with open(gcode_path, 'w') as f:
            # Start job
            f.write("G0 X0 Y0\n")  # Home position
            for contour in contours:
                first_point = True
                for point in contour:
                    x, y = point[0]
                    x_scaled = int(x * 0.5) 
                    y_scaled = int(-y * 0.5)
                    
                    if first_point:
                        # Travel mode (pen up)
                        f.write(f"G0 X{x_scaled} Y{y_scaled}\n")
                        # Switch to write mode (pen down)
                        f.write(f"G1 X{x_scaled} Y{y_scaled}\n")
                        first_point = False
                    else:
                        # Continue drawing
                        f.write(f"G1 X{x_scaled} Y{y_scaled}\n")

                # Lift pen after each contour
                f.write(f"G0 X{x_scaled} Y{y_scaled}\n")

            # End job - return home
            f.write("G0 X0 Y0\n")

        return True
    except Exception:
        return False

def process_queue():
    while True:
        try:
            if not job_queue.empty():
                job_data = job_queue.get()
                timestamp = job_data['timestamp']
                
                with jobs_lock:
                    if timestamp in jobs:
                        jobs[timestamp].status = 'processing'

                success = process_drawing(job_data['png_path'], job_data['gcode_path'])

                with jobs_lock:
                    if timestamp in jobs:
                        jobs[timestamp].status = 'completed' if success else 'failed'
            
            # Clean up old jobs (older than 1 hour)
            with jobs_lock:
                current_time = datetime.now()
                old_jobs = [
                    ts for ts in jobs
                    if (current_time - datetime.strptime(ts, '%Y%m%d_%H%M%S')).total_seconds() > 3600
                ]
                for ts in old_jobs:
                    del jobs[ts]

            time.sleep(1)
        except Exception as e:
            print("Uh oh", e)

# Start the queue-processing thread immediately
processing_thread = threading.Thread(target=process_queue, daemon=True)
processing_thread.start()

@app.route('/', methods=['GET'])
def health():
    return "OK", 200

@app.route('/queue', methods=['GET'])
def get_queue():
    with jobs_lock:
        queue_items = []
        for job in jobs.values():
            queue_items.append({
                'user_name': job.user_name,
                'timestamp': job.timestamp,
                'status': job.status
            })
    return jsonify({'queue': queue_items})

@app.route('/upload', methods=['POST'])
def upload():
    # Limit to one upload per session
    if session.get('uploaded_once'):
        return jsonify({'error': 'You have already uploaded a drawing this session'}), 403

    # Require 'name'
    user_name = request.form.get('name')
    if not user_name:
        return jsonify({'error': 'You must provide a name'}), 400

    try:
        if 'drawing' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['drawing']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        png_filename = f'drawing_{timestamp}.png'
        gcode_filename = f'drawing_{timestamp}.nc'
        
        png_path = os.path.join(UPLOAD_FOLDER, png_filename)
        gcode_path = os.path.join(GCODE_FOLDER, gcode_filename)
        file.save(png_path)

        # Mark the session as having uploaded
        session['uploaded_once'] = True

        with jobs_lock:
            jobs[timestamp] = Job(
                user_name=user_name,
                timestamp=timestamp,
                png_path=png_path,
                gcode_path=gcode_path
            )
        
        job_queue.put({
            'png_path': png_path,
            'gcode_path': gcode_path,
            'timestamp': timestamp
        })
        
        return jsonify({
            'message': 'Drawing queued for processing',
            'timestamp': timestamp
        }), 200
    
    except Exception:
        return jsonify({'error': 'Server error'}), 500

@app.route('/pending-gcode', methods=['GET'])
def get_pending_gcode():
    gcode_files = []
    for filename in os.listdir(GCODE_FOLDER):
        if filename.endswith('.nc'):
            gcode_files.append(filename)
    return jsonify({'files': gcode_files})

@app.route('/execute-gcode/<filename>', methods=['POST'])
def execute_gcode(filename):
    try:
        gcode_path = os.path.join(GCODE_FOLDER, filename)
        if not os.path.exists(gcode_path):
            return jsonify({'error': 'File not found'}), 404

        serial_code_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'Python Serial Code',
            'serial_gcode_final.py'
        )

        try:
            subprocess.run(['python3', serial_code_path, gcode_path], check=True)
            processed_path = os.path.join(PROCESSED_FOLDER, filename)
            shutil.move(gcode_path, processed_path)
            
            timestamp = filename.replace('drawing_', '').replace('.nc', '')
            with jobs_lock:
                if timestamp in jobs:
                    jobs[timestamp].status = 'completed'
            
            return jsonify({'message': 'GCode executed successfully'})
        except subprocess.CalledProcessError as e:
            return jsonify({'error': f'Error executing GCode: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
