# 🧅 Website Deteksi Penyakit Bawang Merah

Aplikasi web berbasis AI untuk mendeteksi penyakit pada tanaman bawang merah menggunakan analisis gambar.

## ✨ Fitur

- 🔍 **Deteksi Penyakit Otomatis** - Upload gambar dan dapatkan diagnosis AI
- 📊 **Analisis Tingkat Kepercayaan** - Skor confidence untuk setiap diagnosis
- 💊 **Rekomendasi Pengobatan** - Saran treatment berdasarkan penyakit yang terdeteksi
- 🛡️ **Tips Pencegahan** - Panduan mencegah penyakit di masa depan
- 📱 **Responsive Design** - Bekerja optimal di desktop dan mobile
- 📈 **Riwayat Analisis** - Simpan dan lihat hasil analisis sebelumnya

## 🚀 Demo

Aplikasi ini dapat mendeteksi berbagai penyakit bawang merah:
- Bercak Ungu (Purple Blotch)
- Embun Bulu (Downy Mildew)
- Busuk Daun (Leaf Blight)
- Antraknosa

## 🛠️ Teknologi

**Backend:**
- Python 3.9+
- Flask (Web Framework)
- Pillow (Image Processing)
- SQLite (Database)

**Frontend:**
- HTML5, CSS3, JavaScript
- Responsive Design
- Modern UI/UX

## 📦 Instalasi

### Prerequisites
- Python 3.9 atau lebih baru
- pip (Python package manager)

### Local Development

1. **Clone repository**
   ```bash
   git clone <repository-url>
   cd mybini
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Jalankan aplikasi**
   ```bash
   python run.py
   ```

4. **Buka browser**
   ```
   http://localhost:5050
   ```

## 🌐 Deployment ke Render

### Persiapan
1. Push kode ke GitHub repository
2. Pastikan semua file deployment sudah ada:
   - `requirements.txt`
   - `Procfile`
   - `render.yaml`

### Deploy Steps
1. **Buat akun di [Render.com](https://render.com)**

2. **Connect GitHub repository**
   - Pilih "New Web Service"
   - Connect repository GitHub Anda

3. **Konfigurasi deployment**
   - **Name:** `onion-disease-detector`
   - **Environment:** `Python`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python run.py`
   - **Plan:** Free

4. **Environment Variables**
   ```
   PYTHON_VERSION=3.9.16
   PORT=10000
   ```

5. **Deploy**
   - Klik "Create Web Service"
   - Tunggu proses deployment selesai

### Auto-Deploy
Setiap push ke branch main akan otomatis trigger deployment baru.

## 📁 Struktur Project

```
mybini/
├── backend/                 # Backend Flask application
│   ├── app.py              # Main Flask app
��   ├── models/             # AI models (placeholder)
│   └── utils/              # Utility functions
├── frontend/               # Frontend files
│   ├── index.html          # Main HTML file
│   ├── styles.css          # CSS styles
│   ├── app.js              # JavaScript logic
│   └── icons/              # App icons
├── requirements.txt        # Python dependencies
├── Procfile               # Render deployment config
├── render.yaml            # Render service config
├── run.py                 # Application entry point
└── README.md              # Documentation
```

## 🔧 Konfigurasi

### Environment Variables
- `PORT` - Port untuk production (default: 5050)
- `FLASK_ENV` - Environment mode (development/production)

### File Upload
- **Max file size:** 10MB
- **Supported formats:** JPG, JPEG, PNG, WebP
- **Auto cleanup:** Temporary files dihapus otomatis

## 🧪 Testing

### Manual Testing
1. Upload gambar bawang merah
2. Klik "Analisis Gambar"
3. Periksa hasil deteksi
4. Test fitur riwayat dan informasi penyakit

### API Testing
```bash
# Health check
curl https://your-app.onrender.com/api/health

# API info
curl https://your-app.onrender.com/api

# Disease info
curl https://your-app.onrender.com/api/diseases
```

## 📝 API Documentation

### Endpoints

#### `GET /api`
Informasi API dan endpoints yang tersedia.

#### `POST /api/detect`
Upload gambar untuk deteksi penyakit.
- **Content-Type:** `multipart/form-data`
- **Parameter:** `image` (file)

#### `GET /api/health`
Health check endpoint.

#### `GET /api/diseases`
Informasi semua penyakit bawang merah.

## 🐛 Troubleshooting

### Common Issues

1. **File upload gagal**
   - Periksa ukuran file (max 10MB)
   - Pastikan format file didukung

2. **Aplikasi tidak bisa diakses**
   - Periksa logs di Render dashboard
   - Pastikan environment variables sudah benar

3. **Error 500**
   - Periksa logs untuk detail error
   - Pastikan semua dependencies terinstall

### Logs
```bash
# Local development
tail -f app.log

# Production (Render)
# Check logs di Render dashboard
```

## 🤝 Contributing

1. Fork repository
2. Buat feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buat Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

## 👥 Authors

- **Developer** - Initial work

## 🙏 Acknowledgments

- Dataset penyakit bawang merah
- Flask community
- Render platform
- Open source libraries yang digunakan

---

**Note:** Aplikasi ini menggunakan data simulasi untuk testing. Untuk production, diperlukan model AI yang dilatih dengan dataset real penyakit bawang merah.