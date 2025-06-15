#!/usr/bin/env python3
"""
Website Deteksi Penyakit Bawang Merah
Production-ready version for deployment
"""

import os
import sys
import webbrowser
import threading
import time
from pathlib import Path

def check_dependencies():
    """Check apakah dependencies sudah terinstall"""
    try:
        import flask
        print("✅ Flask tersedia")
        try:
            import PIL
            print("✅ Pillow tersedia")
        except ImportError:
            print("⚠️ Pillow tidak tersedia, tapi aplikasi tetap bisa jalan")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Jalankan: pip install -r requirements.txt")
        return False

def start_backend():
    """Start Flask backend server"""
    try:
        # Add backend directory to Python path
        backend_path = Path(__file__).parent / "backend"
        sys.path.insert(0, str(backend_path))
        
        # Import dan jalankan app
        import importlib.util
        app_path = backend_path / "app.py"
        spec = importlib.util.spec_from_file_location("app", str(app_path))
        app_module = importlib.util.module_from_spec(spec)
        sys.modules["app"] = app_module
        spec.loader.exec_module(app_module)
        OnionDiseaseAPI = app_module.OnionDiseaseAPI
        
        print("🚀 Starting server...")
        api = OnionDiseaseAPI()
        
        # Get port from environment (for deployment) or use default
        port = int(os.environ.get('PORT', 5050))
        host = '0.0.0.0' if os.environ.get('PORT') else 'localhost'
        
        # Production settings
        debug_mode = os.environ.get('FLASK_ENV') == 'development'
        
        print(f"🌐 Server running on {host}:{port}")
        api.run(debug=debug_mode, host=host, port=port)
        
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        sys.exit(1)

def open_frontend():
    """Open frontend di browser (hanya untuk development)"""
    if os.environ.get('PORT'):  # Skip browser opening in production
        return
        
    time.sleep(3)  # Wait for backend to start
    print("🌐 Opening frontend in browser...")
    webbrowser.open("http://localhost:5050/")

def main():
    """Main function"""
    print("=" * 60)
    print("🧅 Website Deteksi Penyakit Bawang Merah")
    print("   AI-Powered Onion Disease Detection")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Create necessary directories
    uploads_dir = Path(__file__).parent / "backend" / "uploads"
    uploads_dir.mkdir(exist_ok=True)
    
    # Environment info
    is_production = bool(os.environ.get('PORT'))
    port = int(os.environ.get('PORT', 5050))
    
    print(f"\n📋 Environment: {'Production' if is_production else 'Development'}")
    print(f"🌐 Port: {port}")
    print(f"🔧 Debug: {'Off' if is_production else 'On'}")
    
    if not is_production:
        print("💡 Tekan Ctrl+C untuk menghentikan server")
        # Start frontend in separate thread for development
        frontend_thread = threading.Thread(target=open_frontend)
        frontend_thread.daemon = True
        frontend_thread.start()
    
    print("=" * 60)
    
    # Start backend (blocking)
    start_backend()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Server dihentikan. Terima kasih!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)