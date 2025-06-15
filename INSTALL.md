# 📦 Panduan Instalasi

## 🚀 Quick Start (Prototype)

Untuk menjalankan aplikasi prototype dengan cepat:

```bash
# Install dependencies minimal
pip install -r requirements-minimal.txt

# Jalankan aplikasi
python run_fixed.py
```

**Atau gunakan batch file:**
```bash
start_simple.bat
```

## 📋 Pilihan Requirements

### 1. **requirements-minimal.txt** (Direkomendasikan untuk mulai)
- Hanya Flask, Flask-CORS, dan Pillow
- Ukuran download kecil (~10MB)
- Cocok untuk prototype dan demo

### 2. **requirements.txt** (Dokumentasi lengkap)
- Berisi semua opsi dependencies
- Dengan komentar dan penjelasan
- Pilih sesuai kebutuhan

### 3. **requirements-full.txt** (Untuk AI/ML development)
- Semua dependencies termasuk TensorFlow
- Ukuran download besar (~2GB)
- Untuk training model sesungguhnya

## 🔧 Instalasi Bertahap

### Tahap 1: Prototype (Sekarang)
```bash
pip install -r requirements-minimal.txt
```

### Tahap 2: Development (Nanti)
```bash
pip install -r requirements-full.txt
```

## ⚠️ Troubleshooting

### Error TensorFlow/Keras
Jika ada error TensorFlow, gunakan requirements-minimal.txt dulu.

### Error Pillow
```bash
pip install --upgrade Pillow
```

### Error Flask
```bash
pip install --upgrade Flask Flask-CORS
```

## 🎯 Rekomendasi

**Untuk petani/end user:** Gunakan `requirements-minimal.txt`
**Untuk developer:** Gunakan `requirements-full.txt` ketika dataset siap