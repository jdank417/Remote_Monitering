from flask import Flask, render_template, redirect, url_for
import json
import os
import subprocess
import time

app = Flask(__name__)

JSON_FILE_PATH = "C:\\Users\\Jason Dank\\Remote_Monitering\\RemoteSystemInfo.json"
PS_SCRIPT_PATH = "C:\\Users\\Jason Dank\\Remote_Monitering\\remote_json.ps1"

def read_json_file():
    if os.path.exists(JSON_FILE_PATH):
        with open(JSON_FILE_PATH, 'rb') as f:
            content = f.read()
            if content.startswith(b'\xff\xfe'):
                content = content[2:]
            content = content.decode('utf-16')
            return json.loads(content)
    return None

def run_powershell_script():
    try:
        subprocess.run(["powershell", "-File", PS_SCRIPT_PATH], capture_output=True, text=True, check=True)
        # Wait for a short time to ensure the file is written
        time.sleep(2)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running PowerShell script: {e}")
        return False

@app.route('/')
def index():
    data = read_json_file()
    if data:
        return render_template('index.html', data=data)
    return "No data available", 404

@app.route('/refresh')
def refresh():
    if run_powershell_script():
        return redirect(url_for('index'))
    return "Error refreshing data", 500

if __name__ == '__main__':
    app.run(debug=True)