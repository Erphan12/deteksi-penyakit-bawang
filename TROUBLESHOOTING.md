# 🔧 Troubleshooting Guide - ERR_BLOCKED_BY_CLIENT

## Masalah Umum: ERR_BLOCKED_BY_CLIENT

Error `ERR_BLOCKED_BY_CLIENT` terjadi ketika browser atau sistem memblokir request API. Berikut solusi lengkapnya:

## 🚀 Solusi Cepat

### 1. Jalankan Script Otomatis
```bash
# Jalankan script perbaikan otomatis
python fix_connection.py

# Atau gunakan server enhanced
python start_server.py
```

### 2. Manual Troubleshooting

#### A. Disable Ad Blocker
- **uBlock Origin**: Klik icon → Disable untuk localhost
- **AdBlock Plus**: Settings → Whitelist → Tambahkan `localhost`
- **Browser Built-in**: Settings → Privacy → Ad blocking → Disable

#### B. Browser Settings
```
1. Buka mode Incognito/Private
2. Clear cache dan cookies (Ctrl+Shift+Del)
3. Disable semua extensions
4. Restart browser
```

#### C. Coba URL Alternatif
- `http://127.0.0.1:5050/` (IP instead of localhost)
- `http://localhost:5050/` (standard)
- Buka `debug_connection.html` untuk testing

## 🔍 Diagnosis Tools

### 1. Debug Connection Tool
Buka file `debug_connection.html` di browser untuk:
- Test koneksi backend
- Deteksi ad blocker
- Check semua API endpoints
- Lihat browser information

### 2. Manual Check
```bash
# Check apakah server berjalan
curl http://localhost:5050/api

# Check port usage
netstat -ano | findstr :5050

# Test dengan wget/curl
wget http://localhost:5050/api -O -
```

## 🛠️ Solusi Berdasarkan Browser

### Chrome
1. Settings → Privacy and security → Site Settings
2. Additional content settings → Ads → Allow
3. JavaScript → Allow
4. Cookies → Allow

### Firefox
1. about:config → dom.security.https_only_mode → false
2. Enhanced Tracking Protection → Turn off for localhost
3. Extensions → Disable ad blockers

### Edge
1. Settings → Cookies and site permissions
2. Ads → Allow
3. JavaScript → Allow

## 🔥 Firewall & Antivirus

### Windows Firewall
```cmd
# Buat rule untuk Python
netsh advfirewall firewall add rule name="Python Flask" dir=in action=allow protocol=TCP localport=5050

# Atau disable firewall sementara
netsh advfirewall set allprofiles state off
```

### Antivirus
- Tambahkan Python.exe ke whitelist
- Disable real-time protection sementara
- Allow network access untuk Python

## �� Alternative Solutions

### 1. Ganti Port
Edit `run.py`:
```python
port = 8080  # Ganti dari 5050
```

### 2. Gunakan HTTPS
Install certificate dan jalankan dengan HTTPS:
```python
app.run(ssl_context='adhoc', port=5050)
```

### 3. Proxy Setup
Gunakan nginx atau Apache sebagai reverse proxy.

## 📱 Mobile/Network Issues

### Local Network
```bash
# Find your IP
ipconfig  # Windows
ifconfig  # Linux/Mac

# Access from other devices
http://YOUR_IP:5050/
```

### VPN/Proxy
- Disable VPN sementara
- Check proxy settings
- Use direct connection

## 🐛 Advanced Debugging

### 1. Browser Console
1. Tekan F12
2. Lihat tab Console untuk error
3. Check Network tab untuk failed requests

### 2. Python Logging
Tambahkan logging di `backend/app.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 3. Network Analysis
```bash
# Windows
netsh trace start capture=yes
# Reproduce error
netsh trace stop

# Linux
tcpdump -i lo port 5050
```

## 📋 Checklist Troubleshooting

- [ ] Ad blocker disabled
- [ ] Browser extensions disabled
- [ ] Firewall allows port 5050
- [ ] Antivirus not blocking
- [ ] Server actually running
- [ ] Correct URL (localhost vs 127.0.0.1)
- [ ] Browser cache cleared
- [ ] Tried different browser
- [ ] Tried incognito mode
- [ ] Python dependencies installed

## 🆘 Last Resort Solutions

### 1. Complete Reset
```bash
# Kill all Python processes
taskkill /f /im python.exe

# Clear all browser data
# Restart computer
# Run as administrator
```

### 2. Alternative Deployment
```bash
# Use different framework
python -m http.server 8000  # Simple HTTP server

# Or use Flask development server
export FLASK_APP=backend/app.py
flask run --host=0.0.0.0 --port=5050
```

### 3. Docker Solution
```dockerfile
FROM python:3.9
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 5050
CMD ["python", "run.py"]
```

## 📞 Getting Help

Jika semua solusi di atas tidak berhasil:

1. **Check System Logs**: Event Viewer (Windows) atau /var/log (Linux)
2. **Network Diagnostics**: `ping localhost`, `telnet localhost 5050`
3. **Python Environment**: Virtual environment conflicts
4. **System Updates**: Windows/browser updates yang memblokir

## 🎯 Prevention

Untuk mencegah masalah di masa depan:

1. **Whitelist Development URLs** di ad blocker
2. **Use Development Browser Profile** terpisah
3. **Document Working Configuration** untuk tim
4. **Regular Updates** dependencies dan browser

---

💡 **Tip**: Simpan konfigurasi yang berhasil dan buat script otomatis untuk setup development environment.