from flask import Flask, render_template, request
import subprocess


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/run_script', methods=['POST'])
def run_script():
    try:
        # Command to run your PowerShell script
        result = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-File", "remote_monitor.ps1"],
            capture_output=True, text=True, check=True
        )
       
        # Return the output of the PowerShell script
        return result.stdout


    except subprocess.CalledProcessError as e:
        # If the script fails, return the error message
        return f"Error executing script: {e.stderr}"


    except Exception as e:
        # Handle any other exceptions
        return f"An error occurred: {str(e)}"


if __name__ == '__main__':
    app.run(debug=True)