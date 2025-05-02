from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from API.aadhar_route import aadhar_route
from API.pan_route import pan_route
from API.marksheet_10_route import marksheet_10_route
from API.marksheet_12_route import marksheet_12_route
from API.college_marksheet_route import college_route
from API.certificate_route import certificate_route

# Initialize Flask app with static folder
app = Flask(__name__, static_folder='static')

# Enable CORS for all routes with specific options
CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["POST", "OPTIONS"]}})

# Register blueprints
app.register_blueprint(aadhar_route)
app.register_blueprint(pan_route)
app.register_blueprint(marksheet_10_route)
app.register_blueprint(marksheet_12_route)
app.register_blueprint(college_route)
app.register_blueprint(certificate_route)

# Serve the frontend HTML from static folder
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

# Catch-all route to handle other static files
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

if __name__ == "__main__":
    app.run(debug=False)  # Turn off debug mode