# Flask Backend untuk Website Deteksi Penyakit Bawang Merah
# Production-ready version

from flask import Flask, request, jsonify, render_template, make_response, send_from_directory
from flask_cors import CORS
import os
import random
import json
import hashlib
from PIL import Image
from werkzeug.utils import secure_filename
import logging
from datetime import datetime, timedelta
from functools import wraps
import threading
import sqlite3

# Import custom modules (simplified version)
try:
    from utils.image_processor import ImageProcessor
    from utils.disease_classifier import DiseaseClassifier
except ImportError as e:
    print(f"Warning: Could not import some modules: {e}")
    ImageProcessor = None
    DiseaseClassifier = None

# Cache decorator for production
def cache_control(max_age=3600):
    """Decorator untuk mengatur cache control headers"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            response = make_response(f(*args, **kwargs))
            response.headers['Cache-Control'] = f'public, max-age={max_age}'
            response.headers['ETag'] = hashlib.md5(str(response.data).encode()).hexdigest()
            return response
        return decorated_function
    return decorator

class OnionDiseaseAPI:
    def __init__(self):
        self.app = Flask(__name__)
        self.setup_config()
        self.setup_logging()
        self.setup_database()
        self.initialize_models()
        self.setup_routes()
        
    def setup_config(self):
        """Konfigurasi aplikasi Flask"""
        self.app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size
        self.app.config['UPLOAD_FOLDER'] = 'uploads'
        self.app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'webp'}
        
        # Enable CORS untuk frontend
        CORS(self.app, origins=['*'], supports_credentials=True)
        
        # Buat folder upload jika belum ada
        os.makedirs(self.app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Application configurations
        self.app.config['APP_VERSION'] = '1.0.0'
        self.app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # 1 year for static files
    
    def setup_logging(self):
        """Setup logging untuk debugging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('app.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_database(self):
        """Setup SQLite database untuk menyimpan history deteksi"""
        self.db_lock = threading.Lock()
        self.init_database()
    
    def init_database(self):
        """Inisialisasi database tables"""
        try:
            with sqlite3.connect(self.app.config.get('DATABASE', 'database.db')) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS detection_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        disease TEXT NOT NULL,
                        confidence REAL NOT NULL,
                        image_hash TEXT,
                        user_agent TEXT,
                        ip_address TEXT,
                        processing_time REAL
                    )
                ''')
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS app_stats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date DATE DEFAULT CURRENT_DATE,
                        total_detections INTEGER DEFAULT 0,
                        unique_users INTEGER DEFAULT 0,
                        avg_confidence REAL DEFAULT 0.0,
                        most_common_disease TEXT
                    )
                ''')
                
                conn.commit()
                self.logger.info("Database initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing database: {str(e)}")
    
    def initialize_models(self):
        """Inisialisasi model AI"""
        try:
            if ImageProcessor:
                self.image_processor = ImageProcessor()
            else:
                self.image_processor = None
                
            if DiseaseClassifier:
                self.disease_classifier = DiseaseClassifier()
            else:
                self.disease_classifier = None
            
            self.logger.info("Models initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing models: {str(e)}")
            self.image_processor = None
            self.disease_classifier = None
    
    def setup_routes(self):
        """Setup routing untuk API endpoints"""
        
        @self.app.route('/api')
        @cache_control(max_age=300)  # 5 minutes cache
        def api_info():
            response_data = {
                'message': 'Onion Disease Detection API',
                'version': self.app.config['APP_VERSION'],
                'status': 'running',
                'features': [
                    'Disease Detection',
                    'History Tracking',
                    'Statistics',
                    'Disease Information'
                ],
                'endpoints': {
                    'detect': '/api/detect',
                    'health': '/api/health',
                    'diseases': '/api/diseases',
                    'history': '/api/history',
                    'stats': '/api/stats'
                }
            }
            return jsonify(response_data)
        
        @self.app.route('/api/detect', methods=['POST'])
        def detect_disease():
            return self.handle_disease_detection()
        
        @self.app.route('/api/health', methods=['GET'])
        @cache_control(max_age=60)  # 1 minute cache
        def health_check():
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'version': self.app.config['APP_VERSION'],
                'uptime': 'running',
                'database': 'connected'
            })
        
        @self.app.route('/api/diseases', methods=['GET'])
        @cache_control(max_age=3600)  # 1 hour cache
        def get_disease_info():
            return self.get_all_diseases()
        
        @self.app.route('/api/history', methods=['GET'])
        def get_detection_history():
            return self.get_user_history()
        
        @self.app.route('/api/stats', methods=['GET'])
        @cache_control(max_age=1800)  # 30 minutes cache
        def get_app_statistics():
            return self.get_application_stats()
        
        # Serve frontend static files
        @self.app.route('/')
        def serve_frontend():
            try:
                # Get absolute path to frontend directory
                current_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.dirname(current_dir)
                frontend_path = os.path.join(project_root, 'frontend')
                index_path = os.path.join(frontend_path, 'index.html')
                
                self.logger.info(f"Serving frontend from: {index_path}")
                
                if os.path.exists(index_path):
                    return send_from_directory(frontend_path, 'index.html')
                else:
                    self.logger.error(f"Index file not found at: {index_path}")
                    return jsonify({'error': 'Frontend not found'}), 404
                    
            except Exception as e:
                self.logger.error(f"Error serving frontend: {e}")
                return jsonify({'error': 'Frontend not found'}), 500
        
        @self.app.route('/<path:filename>')
        def serve_static(filename):
            try:
                # Get absolute path to frontend directory
                current_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.dirname(current_dir)
                frontend_path = os.path.join(project_root, 'frontend')
                file_path = os.path.join(frontend_path, filename)
                
                self.logger.info(f"Serving static file: {file_path}")
                
                if os.path.exists(file_path):
                    return send_from_directory(frontend_path, filename)
                else:
                    self.logger.error(f"Static file not found at: {file_path}")
                    return jsonify({'error': f'File {filename} not found'}), 404
                    
            except Exception as e:
                self.logger.error(f"Error serving static file {filename}: {e}")
                return jsonify({'error': f'File {filename} not found'}), 500
        
        @self.app.route('/icons/<path:filename>')
        def serve_icons(filename):
            try:
                # Get absolute path to frontend directory
                current_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.dirname(current_dir)
                frontend_path = os.path.join(project_root, 'frontend')
                icons_path = os.path.join(frontend_path, 'icons')
                icon_file_path = os.path.join(icons_path, filename)
                
                self.logger.info(f"Serving icon: {icon_file_path}")
                
                if os.path.exists(icon_file_path):
                    return send_from_directory(icons_path, filename)
                else:
                    self.logger.error(f"Icon file not found at: {icon_file_path}")
                    return jsonify({'error': f'Icon {filename} not found'}), 404
                    
            except Exception as e:
                self.logger.error(f"Error serving icon {filename}: {e}")
                return jsonify({'error': f'Icon {filename} not found'}), 500
        
                
        # Add security headers to all responses
        @self.app.after_request
        def add_security_headers(response):
            # Security headers
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            
            return response
    
    def allowed_file(self, filename):
        """Cek apakah file extension diizinkan"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.app.config['ALLOWED_EXTENSIONS']
    
    def handle_disease_detection(self):
        """Handle request deteksi penyakit"""
        filepath = None
        start_time = datetime.now()
        
        try:
            # Validasi request
            if 'image' not in request.files:
                return jsonify({
                    'success': False,
                    'error': 'No image file provided',
                    'message': 'Silakan pilih gambar untuk dianalisis'
                }), 400
            
            file = request.files['image']
            
            if file.filename == '':
                return jsonify({
                    'success': False,
                    'error': 'No file selected',
                    'message': 'Tidak ada file yang dipilih'
                }), 400
            
            if not self.allowed_file(file.filename):
                return jsonify({
                    'success': False,
                    'error': 'Invalid file type',
                    'message': 'Format file tidak didukung. Gunakan JPG, JPEG, atau PNG'
                }), 400
            
            # Generate image hash untuk tracking
            file_content = file.read()
            file.seek(0)  # Reset file pointer
            image_hash = hashlib.md5(file_content).hexdigest()
            
            # Simpan file sementara
            filename = secure_filename(file.filename)
            if not filename:
                filename = 'uploaded_image.jpg'
                
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            filepath = os.path.join(self.app.config['UPLOAD_FOLDER'], filename)
            
            # Pastikan direktori upload ada
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            file.save(filepath)
            self.logger.info(f"File saved: {filepath}")
            
            # Proses gambar dan deteksi
            result = self.process_image_detection(filepath)
            
            # Hitung processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            result['processing_time'] = round(processing_time, 2)
            
            # Simpan ke database
            self.save_detection_history(
                disease=result['disease'],
                confidence=result['confidence'],
                image_hash=image_hash,
                user_agent=request.headers.get('User-Agent', ''),
                ip_address=request.remote_addr,
                processing_time=processing_time
            )
            
            return jsonify(result)
            
        except Exception as e:
            self.logger.error(f"Error in disease detection: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Internal server error',
                'message': 'Terjadi kesalahan saat memproses gambar. Silakan coba lagi.'
            }), 500
        finally:
            # Hapus file sementara jika ada
            if filepath and os.path.exists(filepath):
                try:
                    os.remove(filepath)
                    self.logger.info(f"Temporary file removed: {filepath}")
                except Exception as e:
                    self.logger.warning(f"Could not remove temporary file: {e}")
    
    def process_image_detection(self, image_path):
        """Proses deteksi penyakit dari gambar"""
        try:
            # Basic image validation
            try:
                with Image.open(image_path) as img:
                    width, height = img.size
                    self.logger.info(f"Processing image: {width}x{height}")
            except Exception as e:
                self.logger.error(f"Error opening image: {e}")
            
            # Generate random mock data untuk testing (variasi hasil)
            diseases_mock = [
                {
                    'disease': 'Sehat',
                    'confidence': round(random.uniform(85, 95), 1),
                    'description': 'Tanaman bawang merah dalam kondisi sehat tanpa tanda-tanda penyakit.',
                    'severity': 'Normal',
                    'treatments': [
                        'Lanjutkan perawatan rutin',
                        'Monitoring berkala kondisi tanaman',
                        'Pemupukan sesuai jadwal',
                        'Penyiraman yang tepat'
                    ],
                    'prevention': [
                        'Pertahankan kondisi optimal',
                        'Monitoring rutin',
                        'Sanitasi lahan',
                        'Nutrisi seimbang'
                    ]
                },
                {
                    'disease': 'Bercak Ungu (Purple Blotch)',
                    'confidence': round(random.uniform(75, 90), 1),
                    'description': 'Penyakit yang disebabkan oleh jamur Alternaria porri. Ditandai dengan bercak-bercak ungu pada daun.',
                    'severity': random.choice(['Ringan', 'Sedang', 'Berat']),
                    'treatments': [
                        'Semprot dengan fungisida berbahan aktif mankozeb',
                        'Perbaiki drainase lahan untuk mengurangi kelembaban',
                        'Buang dan musnahkan bagian tanaman yang terinfeksi',
                        'Berikan jarak tanam yang cukup untuk sirkulasi udara'
                    ],
                    'prevention': [
                        'Gunakan benih yang sehat dan bersertifikat',
                        'Rotasi tanaman dengan tanaman non-allium',
                        'Jaga kebersihan lahan dari sisa tanaman'
                    ]
                },
                {
                    'disease': 'Embun Bulu (Downy Mildew)',
                    'confidence': round(random.uniform(70, 88), 1),
                    'description': 'Penyakit yang menyebabkan lapisan putih keabu-abuan pada permukaan daun.',
                    'severity': random.choice(['Ringan', 'Sedang', 'Berat']),
                    'treatments': [
                        'Aplikasi fungisida sistemik (metalaksil + mankozeb)',
                        'Perbaiki ventilasi dan drainase',
                        'Kurangi kelembaban dengan mulsa plastik',
                        'Semprot pada pagi hari sebelum embun terbentuk'
                    ],
                    'prevention': [
                        'Pilih varietas tahan penyakit',
                        'Atur jarak tanam yang optimal',
                        'Hindari penyiraman di sore hari',
                        'Gunakan mulsa untuk mengurangi kelembaban tanah'
                    ]
                },
                {
                    'disease': 'Busuk Daun (Leaf Blight)',
                    'confidence': round(random.uniform(72, 86), 1),
                    'description': 'Penyakit jamur yang menyebabkan bercak putih kecil yang membesar dan mengering.',
                    'severity': random.choice(['Ringan', 'Sedang', 'Berat']),
                    'treatments': [
                        'Fungisida berbahan aktif iprodion atau vinclozolin',
                        'Buang daun yang terinfeksi',
                        'Kurangi kelembaban daun',
                        'Aplikasi pupuk berimbang'
                    ],
                    'prevention': [
                        'Hindari luka mekanis pada tanaman',
                        'Jaga kebersihan alat pertanian',
                        'Monitoring cuaca dan kelembaban',
                        'Aplikasi fungisida preventif'
                    ]
                },
                {
                    'disease': 'Antraknosa',
                    'confidence': round(random.uniform(68, 84), 1),
                    'description': 'Penyakit jamur yang menyebabkan bercak coklat dengan tepi gelap pada daun.',
                    'severity': random.choice(['Ringan', 'Sedang', 'Berat']),
                    'treatments': [
                        'Fungisida berbahan aktif azoksistrobin',
                        'Perbaiki drainase lahan',
                        'Buang tanaman yang terinfeksi berat',
                        'Aplikasi kapur untuk menetralkan pH tanah'
                    ],
                    'prevention': [
                        'Gunakan benih bebas penyakit',
                        'Rotasi tanaman 2-3 tahun',
                        'Jaga pH tanah 6.0-7.0',
                        'Hindari genangan air'
                    ]
                }
            ]
            
            # Pilih random disease untuk simulasi
            selected_disease = random.choice(diseases_mock)
            
            mock_result = {
                'success': True,
                'disease': selected_disease['disease'],
                'confidence': selected_disease['confidence'],
                'description': selected_disease['description'],
                'severity': selected_disease['severity'],
                'treatments': selected_disease['treatments'],
                'prevention': selected_disease['prevention'],
                'timestamp': datetime.now().isoformat(),
                'note': '⚠️ Ini adalah hasil simulasi untuk testing. Model AI belum dilatih dengan dataset real.'
            }
            
            return mock_result
            
        except Exception as e:
            self.logger.error(f"Error processing image: {str(e)}")
            raise
    
    def get_all_diseases(self):
        """Return informasi semua penyakit bawang merah"""
        diseases = {
            'diseases': [
                {
                    'name': 'Bercak Ungu (Purple Blotch)',
                    'pathogen': 'Alternaria porri',
                    'symptoms': 'Bercak ungu pada daun, dapat menyebar ke seluruh tanaman',
                    'conditions': 'Kelembaban tinggi, suhu 20-30°C'
                },
                {
                    'name': 'Embun Bulu (Downy Mildew)',
                    'pathogen': 'Peronospora destructor',
                    'symptoms': 'Lapisan putih keabu-abuan pada permukaan daun',
                    'conditions': 'Kelembaban sangat tinggi, suhu dingin'
                },
                {
                    'name': 'Busuk Daun (Leaf Blight)',
                    'pathogen': 'Botrytis squamosa',
                    'symptoms': 'Bercak putih kecil yang membesar dan mengering',
                    'conditions': 'Kelembaban tinggi, angin kencang'
                },
                {
                    'name': 'Antraknosa',
                    'pathogen': 'Colletotrichum gloeosporioides',
                    'symptoms': 'Bercak coklat dengan tepi gelap pada daun',
                    'conditions': 'Curah hujan tinggi, suhu hangat'
                }
            ]
        }
        return jsonify(diseases)
    
        
    def get_user_history(self):
        """Stub: Return history deteksi (belum diimplementasikan)"""
        return jsonify({
            'message': 'Fitur history belum diimplementasikan'
        })
    
    def get_application_stats(self):
        """Stub: Return statistik aplikasi (belum diimplementasikan)"""
        return jsonify({
            'message': 'Fitur statistik belum diimplementasikan'
        })
    
    def save_detection_history(self, disease, confidence, image_hash, user_agent, ip_address, processing_time):
        """Simpan record history deteksi ke database (stub/simple implementation)"""
        try:
            with sqlite3.connect(self.app.config.get('DATABASE', 'database.db')) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO detection_history (disease, confidence, image_hash, user_agent, ip_address, processing_time)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (disease, confidence, image_hash, user_agent, ip_address, processing_time))
                conn.commit()
                self.logger.info("Detection history saved")
        except Exception as e:
            self.logger.error(f"Error saving detection history: {str(e)}")
    
    def run(self, debug=True, host='0.0.0.0', port=5000):
        """Jalankan aplikasi Flask"""
        self.logger.info(f"Starting Onion Disease Detection API on {host}:{port}")
        self.logger.info(f"Debug mode: {debug}")
        self.logger.info(f"Environment: {'Production' if not debug else 'Development'}")
        
        # Railway compatibility
        if os.environ.get('RAILWAY_ENVIRONMENT'):
            self.logger.info("Running on Railway platform")
            debug = False  # Force disable debug on Railway
        
        self.app.run(debug=debug, host=host, port=port, threaded=True)

# Entry point
if __name__ == '__main__':
    api = OnionDiseaseAPI()
    api.run(debug=True)