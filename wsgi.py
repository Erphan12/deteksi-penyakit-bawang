#!/usr/bin/env python3
"""
WSGI entry point for production deployment
"""

import os
import sys
from pathlib import Path

# Add backend directory to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Import the Flask app
from backend.app import OnionDiseaseAPI

# Create application instance
api = OnionDiseaseAPI()
application = api.app

# For Railway and other WSGI servers
app = application

if __name__ == "__main__":
    # For local testing
    port = int(os.environ.get('PORT', 5050))
    app.run(host='0.0.0.0', port=port, debug=False)