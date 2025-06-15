#!/usr/bin/env python3
"""
Enhanced server startup script dengan error handling dan troubleshooting
"""

import os
import sys
import time
import webbrowser
import threading
import subprocess
import platform
from pathlib import Path

def check_dependencies():
    """Check dan install dependencies jika perlu"""
    print("🔍 Checking dependencies...")
    
    required_packages = ['flask', 'flask-cors', 'pillow', 'requests']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'pillow':
                import PIL
            elif package == 'flask-cors':
                import flask_cors
            else:
                __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - MISSING")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    return True

def kill_existing_processes():
    """Kill existing processes on port 5050"""
    try:
        system = platform.system().lower()
        if system == "windows":
            # Windows
            result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            
            for line in lines:
                if ':5050' in line and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        print(f"🔄 Killing existing process {pid} on port 5050")
                        subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True)
        else:
            # Linux/Mac
            result = subprocess.run(['lsof', '-ti', ':5050'], capture_output=True, text=True)
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    print(f"🔄 Killing existing process {pid} on port 5050")
                    subprocess.run(['kill', '-9', pid], capture_output=True)
    except Exception as e:
        print(f"⚠️ Could not kill existing processes: {e}")

def setup_environment():
    """Setup environment variables dan directories"""
    print("🔧 Setting up environment...")
    
    # Create necessary directories
    directories = ['backend/uploads', 'logs']
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"📁 Created directory: {directory}")
    
    # Set environment variables
    os.environ['FLASK_ENV'] = 'development'
    os.environ['PYTHONPATH'] = str(Path(__file__).parent)
    
    print("✅ Environment setup complete")

def start_backend_server():
    """Start Flask backend server dengan error handling"""
    try:
        # Add backend to Python path
        backend_path = Path(__file__).parent / "backend"
        sys.path.insert(0, str(backend_path))
        
        # Import app
        from backend.app import OnionDiseaseAPI
        
        print("🚀 Starting Flask backend server...")
        api = OnionDiseaseAPI()
        
        # Start server
        api.run(debug=True, host='0.0.0.0', port=5050, threaded=True)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure backend/app.py exists and is properly configured")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

def open_browser():
    """Open browser setelah server ready"""
    print("⏳ Waiting for server to start...")
    time.sleep(3)
    
    urls_to_try = [
        "http://localhost:5050/",
        "http://127.0.0.1:5050/",
        f"file://{Path(__file__).parent / 'debug_connection.html'}"
    ]
    
    for url in urls_to_try:
        try:
            print(f"🌐 Opening: {url}")
            webbrowser.open(url)
            break
        except Exception as e:
            print(f"⚠️ Could not open {url}: {e}")
            continue

def show_troubleshooting_info():
    """Show troubleshooting information"""
    print("\n" + "="*60)
    print("🔧 TROUBLESHOOTING GUIDE")
    print("="*60)
    print("Jika mengalami error ERR_BLOCKED_BY_CLIENT:")
    print()
    print("1️⃣ DISABLE AD BLOCKER:")
    print("   - Matikan ad blocker untuk localhost")
    print("   - Tambahkan localhost ke whitelist")
    print()
    print("2️⃣ BROWSER SETTINGS:")
    print("   - Coba mode incognito/private")
    print("   - Clear cache dan cookies")
    print("   - Disable browser extensions")
    print()
    print("3️⃣ ALTERNATIVE URLs:")
    print("   - http://127.0.0.1:5050/")
    print("   - http://localhost:5050/")
    print()
    print("4️⃣ FIREWALL:")
    print("   - Allow Python/Flask through Windows Firewall")
    print("   - Check antivirus settings")
    print()
    print("5️⃣ DEBUG TOOLS:")
    debug_path = Path(__file__).parent / "debug_connection.html"
    if debug_path.exists():
        print(f"   - Open: {debug_path}")
    print("   - Check browser console (F12)")
    print("   - Run: python fix_connection.py")
    print()
    print("6️⃣ ALTERNATIVE BROWSERS:")
    print("   - Try Chrome, Firefox, Edge")
    print("   - Use different browser profiles")
    print("="*60)

def main():
    """Main function"""
    print("🧅 Onion Disease Detection - Enhanced Server")
    print("="*60)
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Dependency check failed")
        return
    
    # Kill existing processes
    kill_existing_processes()
    time.sleep(1)
    
    # Setup environment
    setup_environment()
    
    # Show troubleshooting info
    show_troubleshooting_info()
    
    # Start browser in separate thread
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    print("\n🚀 Starting server...")
    print("💡 Press Ctrl+C to stop")
    print("="*60)
    
    # Start backend server (blocking)
    try:
        start_backend_server()
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        print("\n💡 Try running: python fix_connection.py")

if __name__ == "__main__":
    main()