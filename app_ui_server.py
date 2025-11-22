"""
Simple Flask API for MIMIQ - Uses existing app_integrated.py with WebSocket support
"""

from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
import sys
import os

# Import the existing app
sys.path.insert(0, os.path.dirname(__file__))
from app_integrated import app as base_app

# Create Flask app with CORS and SocketIO
app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://localhost:3000"])
socketio = SocketIO(app, cors_allowed_origins=["http://localhost:5173", "http://localhost:3000"])

# Import routes from existing app
from app_integrated import *

if __name__ == '__main__':
    print("=" * 60)
    print("🏥 MIMIQ Medical AI Platform - UI-Enhanced API Server")
    print("=" * 60)
    print(f"✅ CORS: Enabled for localhost:5173, localhost:3000")
    print(f"✅ WebSocket: Enabled")
    print(f"✅ Emergency Numbers: 911 (US), 108 (India)")
    print("=" * 60)
    print("🚀 Starting server on http://localhost:5000")
    print("=" * 60)
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
