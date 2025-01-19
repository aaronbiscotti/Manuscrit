from flask import Flask, request, jsonify
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
CORS(app)

UPLOAD_FOLDER = 'uploads'
GCODE_FOLDER = 'gcode'
PROCESSED_FOLDER = 'processed'
for folder in [UPLOAD_FOLDER, GCODE_FOLDER, PROCESSED_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Track jobs
@dataclass
class Job:
    timestamp: str
    png_path: str
    gcode_path: str
    status: str = 'pending'

# Globals
job_queue = Queue()
jobs: Dict[str, Job] = {}
jobs_lock = threading.Lock()
processing_thread = None


# THIS FUNCTION IS GPTED CODE, NEED TO ADJUST LATER
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
                # Start with travel mode (pen up)
                first_point = True
                for point in contour:
                    x, y = point[0]
                    x_scaled = int(x * 0.5) 
                    y_scaled = int(-y * 0.5)
                    
                    if first_point:
                        # Travel to start point
                        f.write(f"G0 X{x_scaled} Y{y_scaled}\n")
                        # Switch to write mode
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
    except Exception as e:
        return False

def process_queue():
    while True:
        try:
            if not job_queue.empty():
                job_data = job_queue.get()
                timestamp = job_data['timestamp']
                
                # Update status to processing then process drawing and update the status
                with jobs_lock:
                    if timestamp in jobs:
                        jobs[timestamp].status = 'processing'
                success = process_drawing(job_data['png_path'], job_data['gcode_path'])

                with jobs_lock:
                    if timestamp in jobs:
                        jobs[timestamp].status = 'completed' if success else 'failed'
                
            
            # Clean up old jobs (if older than 1 hour)
            with jobs_lock:
                current_time = datetime.now()
                old_jobs = [
                    timestamp for timestamp in jobs
                    if (current_time - datetime.strptime(timestamp, '%Y%m%d_%H%M%S')).total_seconds() > 3600
                ]
                for timestamp in old_jobs:
                    del jobs[timestamp]
            
            time.sleep(1)
        except Exception as e:
            print("Uh oh")

processing_thread = threading.Thread(target=process_queue, daemon=True)
processing_thread.start()

@app.route('/', methods=['GET'])
def health():
    return "OK", 200

@app.route('/queue', methods=['GET'])
def get_queue():
    with jobs_lock:
        queue_items = [
            {'timestamp': job.timestamp, 'status': job.status}
            for job in jobs.values()
        ]
    return jsonify({'queue': queue_items})

@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'drawing' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['drawing']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Generate filename using timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        png_filename = f'drawing_{timestamp}.png'
        gcode_filename = f'drawing_{timestamp}.nc'
        
        png_path = os.path.join(UPLOAD_FOLDER, png_filename)
        gcode_path = os.path.join(GCODE_FOLDER, gcode_filename)

        file.save(png_path)
        

        with jobs_lock:
            jobs[timestamp] = Job(
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
    
    except Exception as e:
        return jsonify({'error': 'Server error'}), 500

@app.route('/pending-gcode', methods=['GET'])
def get_pending_gcode():
    """Get list of pending GCode files."""
    gcode_files = []
    for filename in os.listdir(GCODE_FOLDER):
        if filename.endswith('.nc'):
            gcode_files.append(filename)
    return jsonify({'files': gcode_files})

#### FOR EXECUTING G-CODE ####
@app.route('/execute-gcode/<filename>', methods=['POST'])
def execute_gcode(filename):
    try:
        gcode_path = os.path.join(GCODE_FOLDER, filename)
        
        if not os.path.exists(gcode_path):
            return jsonify({'error': 'File not found'}), 404

        # Get absolute path to serial code
        serial_code_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'Python Serial Code',
            'serial_gcode_final.py'
        )

        try:
            subprocess.run([
                'python', 
                serial_code_path, 
                gcode_path
            ], check=True)
            
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
    # For local dev/testing only
    app.run(host="0.0.0.0", port=5000, debug=False)