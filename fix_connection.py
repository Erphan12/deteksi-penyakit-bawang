#!/usr/bin/env python3
"""
Script untuk memperbaiki masalah koneksi ERR_BLOCKED_BY_CLIENT
"""

import os
import sys
import subprocess
import platform
import socket
import requests
import time
from pathlib import Path

def check_port_availability(port):
    """Check apakah port tersedia"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(('localhost', port))
            return result != 0  # True jika port tersedia (tidak digunakan)
    except Exception:
        return True

def find_available_port(start_port=5050, max_attempts=10):
    """Cari port yang tersedia"""
    for port in range(start_port, start_port + max_attempts):
        if check_port_availability(port):
            return port
    return None

def kill_process_on_port(port):
    """Kill process yang menggunakan port tertentu"""
    try:
        system = platform.system().lower()
        if system == "windows":
            # Windows
            result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            
            for line in lines:
                if f':{port}' in line and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        print(f"🔄 Killing process {pid} on port {port}")
                        subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True)
                        return True
        else:
            # Linux/Mac
            result = subprocess.run(['lsof', '-ti', f':{port}'], capture_output=True, text=True)
            if result.stdout.strip():
                pid = result.stdout.strip()
                print(f"🔄 Killing process {pid} on port {port}")
                subprocess.run(['kill', '-9', pid], capture_output=True)
                return True
    except Exception as e:
        print(f"⚠️ Error killing process: {e}")
    return False

def test_backend_connection(port=5050):
    """Test koneksi ke backend"""
    try:
        response = requests.get(f'http://localhost:{port}/api', timeout=5)
        if response.status_code == 200:
            print(f"✅ Backend berjalan di port {port}")
            return True
        else:
            print(f"❌ Backend error: HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Tidak dapat terhubung ke backend di port {port}")
        return False
    except Exception as e:
        print(f"❌ Error testing backend: {e}")
        return False

def create_alternative_config():
    """Buat konfigurasi alternatif untuk mengatasi masalah blocking"""
    
    # Update app.js dengan konfigurasi alternatif
    app_js_path = Path(__file__).parent / "frontend" / "app.js"
    
    if app_js_path.exists():
        with open(app_js_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Ganti API_BASE_URL dengan alternatif
        original_url = "this.API_BASE_URL = 'http://localhost:5050/api';"
        alternative_configs = [
            "this.API_BASE_URL = window.location.origin + '/api';",  # Relative URL
            "this.API_BASE_URL = 'http://127.0.0.1:5050/api';",     # IP instead of localhost
            "this.API_BASE_URL = '/api';"                            # Root relative
        ]
        
        for i, alt_config in enumerate(alternative_configs):
            backup_path = app_js_path.with_suffix(f'.backup{i+1}.js')
            
            # Buat backup
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Update content
            updated_content = content.replace(original_url, alt_config)
            
            # Simpan versi alternatif
            alt_path = app_js_path.with_name(f'app_alt{i+1}.js')
            with open(alt_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print(f"📝 Created alternative config: {alt_path.name}")
    
    # Buat index.html alternatif yang menggunakan IP
    index_path = Path(__file__).parent / "frontend" / "index.html"
    if index_path.exists():
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Ganti localhost dengan 127.0.0.1
        updated_content = content.replace('localhost:5050', '127.0.0.1:5050')
        
        alt_index_path = index_path.with_name('index_alt.html')
        with open(alt_index_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"📝 Created alternative index: {alt_index_path.name}")

def check_firewall_windows():
    """Check Windows Firewall untuk port 5050"""
    try:
        result = subprocess.run([
            'netsh', 'advfirewall', 'firewall', 'show', 'rule', 
            'name=all', 'dir=in', 'protocol=tcp', 'localport=5050'
        ], capture_output=True, text=True)
        
        if 'No rules match' in result.stdout:
            print("⚠️ Tidak ada firewall rule untuk port 5050")
            
            # Tawarkan untuk membuat rule
            response = input("Buat firewall rule untuk port 5050? (y/n): ")
            if response.lower() == 'y':
                subprocess.run([
                    'netsh', 'advfirewall', 'firewall', 'add', 'rule',
                    'name=Python Flask App', 'dir=in', 'action=allow',
                    'protocol=TCP', 'localport=5050'
                ], check=True)
                print("✅ Firewall rule dibuat")
        else:
            print("✅ Firewall rule sudah ada untuk port 5050")
    except subprocess.CalledProcessError:
        print("⚠️ Tidak dapat mengecek firewall (mungkin perlu admin privileges)")
    except Exception as e:
        print(f"⚠️ Error checking firewall: {e}")

def main():
    print("🔧 Fix Connection Script - Onion Disease Detection")
    print("=" * 60)
    
    # 1. Check port availability
    print("\n1️⃣ Checking port availability...")
    if not check_port_availability(5050):
        print("⚠️ Port 5050 sedang digunakan")
        kill_response = input("Kill process di port 5050? (y/n): ")
        if kill_response.lower() == 'y':
            kill_process_on_port(5050)
            time.sleep(2)
    
    # 2. Find alternative port if needed
    available_port = find_available_port()
    if available_port and available_port != 5050:
        print(f"💡 Port alternatif tersedia: {available_port}")
    
    # 3. Test backend connection
    print("\n2️⃣ Testing backend connection...")
    backend_running = test_backend_connection()
    
    if not backend_running:
        print("❌ Backend tidak berjalan atau tidak dapat diakses")
        print("💡 Solusi:")
        print("   - Jalankan: python run.py")
        print("   - Atau: python backend/app.py")
    
    # 4. Create alternative configurations
    print("\n3️⃣ Creating alternative configurations...")
    create_alternative_config()
    
    # 5. Check firewall (Windows only)
    if platform.system().lower() == "windows":
        print("\n4️⃣ Checking Windows Firewall...")
        check_firewall_windows()
    
    # 6. Browser recommendations
    print("\n5️⃣ Browser Troubleshooting:")
    print("   ✅ Disable ad blocker untuk localhost")
    print("   ✅ Coba mode incognito/private")
    print("   ✅ Clear browser cache dan cookies")
    print("   ✅ Disable browser extensions")
    print("   ✅ Coba browser lain (Chrome, Firefox, Edge)")
    
    # 7. Alternative access methods
    print("\n6️⃣ Alternative Access Methods:")
    print("   🌐 http://127.0.0.1:5050/")
    print("   🌐 http://localhost:5050/")
    if available_port and available_port != 5050:
        print(f"   🌐 http://localhost:{available_port}/")
    
    # 8. Debug tool
    debug_path = Path(__file__).parent / "debug_connection.html"
    if debug_path.exists():
        print(f"\n7️⃣ Debug Tool Available:")
        print(f"   📋 Open: {debug_path}")
        print("   🔧 Atau akses: http://localhost:5050/debug_connection.html")
    
    print("\n" + "=" * 60)
    print("✅ Fix script completed!")
    print("💡 Jika masalah masih ada, coba restart komputer dan jalankan sebagai administrator")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Script dihentikan")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)