import os
import sys

# Add the current directory to sys.path to allow blueprints to import modules from backend/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from flask import Flask, send_from_directory
from flask_cors import CORS

# Import configurations
from config import DATA_DIR, ANNOTATIONS_DIR

# Import blueprints
from routes.auth_routes import auth_bp
from routes.data_routes import data_bp
from routes.annotation_routes import annotation_bp
from routes.label_routes import label_bp

app = Flask(__name__, static_folder='../frontend/dist', static_url_path='')
CORS(app)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(data_bp)
app.register_blueprint(annotation_bp)
app.register_blueprint(label_bp)

# ==================== Static Files ====================
@app.route('/')
def index():
    """Serve the frontend"""
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    print("=" * 60)
    print("Time Series Annotator v2 - Modular Backend Starting...")
    print("API Server: http://localhost:5000")
    print(f"Data Directory: {DATA_DIR}")
    print(f"Annotations Directory: {ANNOTATIONS_DIR}")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)