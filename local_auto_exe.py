#!/usr/bin/env python3

import requests
import subprocess
import os
import sys
import json

BACKEND_URL = "https://manuscrit-production.up.railway.app"
LOCAL_GCODE_FOLDER = "client_backend/gcode"
SERIAL_SCRIPT = "Python Serial Code/serial_gcode_final.py"

def main():
    # 1) Get the list of pending G-code files
    pending_url = f"{BACKEND_URL}/pending-gcode"
    try:
        resp = requests.get(pending_url)
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError) as e:
        print(f"Error fetching pending G-code: {e}")
        sys.exit(1)

    files = data.get("files", [])
    if not files:
        print("No files in queue.")
        sys.exit(0)

    # Grab the first file in the list
    filename = files[0]
    print(f"Found G-code file in queue: {filename}")

    # 2) Download that file into client_backend/gcode
    download_url = f"{BACKEND_URL}/download-gcode/{filename}"
    local_path = os.path.join(LOCAL_GCODE_FOLDER, filename)
    print(f"Downloading from {download_url} to {local_path} ...")

    try:
        with requests.get(download_url, stream=True) as r:
            r.raise_for_status()
            os.makedirs(LOCAL_GCODE_FOLDER, exist_ok=True)
            with open(local_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
    except (requests.RequestException, OSError) as e:
        print(f"Error downloading G-code: {e}")
        sys.exit(1)

    print("Download successful.")

    # 3) Execute the G-code locally with serial_gcode_final.py
    print(f"Executing local script on {local_path} ...")

    try:
        subprocess.run(["python", SERIAL_SCRIPT, local_path], check=True)
        print("Local G-code execution succeeded.")
    except subprocess.CalledProcessError as e:
        print(f"Error running serial_gcode_final.py: {e}")
        sys.exit(1)

    # 4) Remove the local file after successful execution
    try:
        os.remove(local_path)
        print(f"Removed local file: {local_path}")
    except OSError as e:
        print(f"Warning: Could not remove local file {local_path}: {e}")

    # 5) Remove from the server queue as well
    #    Make sure you have a route: @app.route('/remove-from-queue/<filename>', methods=['DELETE'])
    remove_url = f"{BACKEND_URL}/remove-from-queue/{filename}"
    try:
        resp = requests.delete(remove_url)
        resp.raise_for_status()
        result_data = resp.json()
        print("Removed from server queue:", result_data.get("message", "No message"))
    except (requests.RequestException, ValueError) as e:
        print(f"Error removing file from server queue: {e}")

if __name__ == "__main__":
    main()
