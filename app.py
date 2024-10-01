from flask import Flask, render_template
import subprocess
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_script', methods=['POST'])
def run_script():
    try:
        script_path = os.path.join(os.path.dirname(__file__), 'remote_moniter.ps1')
        print(script_path)
        
        if not os.path.exists(script_path):
            return f"Script file does not exist: {script_path}"
        
        # Command to run your PowerShell script
        result = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path],
            capture_output=True, text=True, check=True
        )
        
        # Read the contents of RemoteSystemInfo.txt
        with open('RemoteSystemInfo.txt', 'r') as file:
            file_contents = file.read()
        
        # Return the contents of the file
        return file_contents

    except subprocess.CalledProcessError as e:
        # If the script fails, return the error message
        return f"Error executing script: {e.stderr}"

    except Exception as e:
        # Handle any other exceptions
        return f"An error occurred: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)