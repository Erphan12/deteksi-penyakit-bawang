# 🚂 Railway Deployment Guide

## ✅ Deployment Checklist

### 1. File Konfigurasi
- [x] `Procfile` - Entry point untuk Railway
- [x] `requirements.txt` - Python dependencies
- [x] `railway.toml` - Railway configuration
- [x] `runtime.txt` - Python version (opsional)

### 2. Environment Variables
Set di Railway dashboard:
```
FLASK_ENV=production
PYTHONPATH=/app
PORT=(auto-assigned by Railway)
```

### 3. Domain & URL
Setelah deploy, Railway akan memberikan:
- **Domain**: `https://your-app-name.up.railway.app`
- **Custom Domain**: Bisa ditambahkan di settings

## 🔧 Troubleshooting Railway

### Common Issues:

#### 1. Build Failures
```bash
# Check logs di Railway dashboard
# Pastikan requirements.txt lengkap
# Pastikan Python version compatible
```

#### 2. Runtime Errors
```bash
# Check application logs
# Pastikan PORT environment variable digunakan
# Pastikan host='0.0.0.0'
```

#### 3. Static Files
```python
# Pastikan Flask serve static files dengan benar
# Check routing untuk frontend files
```

## 📊 Monitoring

### Health Check
Railway akan check endpoint: `/api/health`

### Logs
```bash
# Via Railway CLI
railway logs

# Via Dashboard
# Go to your project → Deployments → View logs
```

## 🔄 Updates

### Auto Deploy
- Push ke GitHub repository
- Railway auto-deploy dari main branch

### Manual Deploy
```bash
# Via Railway CLI
railway up
```

## 🌐 Testing Deployment

### 1. Basic Connectivity
```bash
curl https://your-app.up.railway.app/api
```

### 2. API Endpoints
- `GET /api` - API info
- `GET /api/health` - Health check
- `GET /api/diseases` - Disease information
- `POST /api/detect` - Image detection

### 3. Frontend
- `GET /` - Main application
- Static files (CSS, JS, images)

## 🚨 Common Railway Issues

### 1. Cold Starts
- Railway apps sleep after inactivity
- First request might be slow
- Solution: Use Railway Pro atau implement keep-alive

### 2. File Uploads
- Railway has ephemeral filesystem
- Uploaded files disappear on restart
- Solution: Use cloud storage (AWS S3, Cloudinary)

### 3. Database
- SQLite files are ephemeral
- Use Railway PostgreSQL addon
- Or external database service

## 💡 Optimization Tips

### 1. Reduce Build Time
```dockerfile
# Use .dockerignore
node_modules/
*.pyc
__pycache__/
.git/
```

### 2. Environment-specific Config
```python
import os

DEBUG = os.environ.get('FLASK_ENV') == 'development'
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///local.db')
```

### 3. Static File Caching
```python
# Add cache headers
@app.after_request
def add_cache_headers(response):
    if request.endpoint == 'static':
        response.cache_control.max_age = 31536000  # 1 year
    return response
```

## 🔐 Security

### 1. Environment Variables
- Never commit secrets to git
- Use Railway environment variables
- Rotate keys regularly

### 2. HTTPS
- Railway provides HTTPS by default
- Force HTTPS in production:
```python
if not app.debug:
    @app.before_request
    def force_https():
        if not request.is_secure:
            return redirect(request.url.replace('http://', 'https://'))
```

## 📈 Scaling

### 1. Railway Pro Features
- Custom domains
- More resources
- Priority support
- No sleep mode

### 2. Performance Monitoring
```python
import time
import logging

@app.before_request
def log_request_info():
    app.logger.info('Request: %s %s', request.method, request.url)

@app.after_request
def log_response_info(response):
    app.logger.info('Response: %s', response.status_code)
    return response
```

## 🎯 Next Steps

1. **Custom Domain**: Add your own domain
2. **Database**: Upgrade to PostgreSQL
3. **File Storage**: Implement cloud storage
4. **Monitoring**: Add error tracking (Sentry)
5. **Analytics**: Add usage analytics
6. **CDN**: Use CloudFlare for static assets

## 📞 Support

- **Railway Docs**: https://docs.railway.app
- **Community**: Railway Discord
- **Status**: https://status.railway.app

---

🎉 **Selamat! Aplikasi Anda sudah live di Railway!**