# Disease Classifier untuk klasifikasi penyakit bawang merah
# Clean Code Implementation

import numpy as np
import logging
from datetime import datetime
from typing import Dict, List, Tuple

class DiseaseClassifier:
    """
    Class untuk mengklasifikasi penyakit bawang merah berdasarkan hasil prediksi model
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.disease_database = self._initialize_disease_database()
        self.confidence_threshold = 0.7  # Minimum confidence untuk diagnosis
    
    def _initialize_disease_database(self) -> Dict:
        """Inisialisasi database penyakit bawang merah"""
        return {
            'purple_blotch': {
                'name': 'Bercak Ungu (Purple Blotch)',
                'scientific_name': 'Alternaria porri',
                'type': 'Fungal',
                'description': 'Penyakit jamur yang menyebabkan bercak ungu pada daun bawang merah. Dapat menyebar dengan cepat dalam kondisi lembab.',
                'symptoms': [
                    'Bercak kecil berwarna putih dengan tepi ungu',
                    'Bercak membesar dan bergabung',
                    'Daun menguning dan mengering',
                    'Pertumbuhan tanaman terhambat'
                ],
                'conditions': {
                    'temperature': '20-30°C',
                    'humidity': 'Tinggi (>80%)',
                    'weather': 'Cuaca lembab, hujan berkepanjangan'
                },
                'severity_levels': {
                    'ringan': 'Bercak sedikit, belum menyebar',
                    'sedang': 'Bercak mulai menyebar, beberapa daun terinfeksi',
                    'berat': 'Sebagian besar daun terinfeksi, pertumbuhan terhambat'
                },
                'treatments': [
                    'Semprot fungisida berbahan aktif mankozeb atau klorotalonil',
                    'Perbaiki drainase untuk mengurangi kelembaban',
                    'Buang dan musnahkan bagian tanaman yang terinfeksi',
                    'Berikan jarak tanam yang cukup untuk sirkulasi udara',
                    'Aplikasi pupuk kalium untuk meningkatkan daya tahan'
                ],
                'prevention': [
                    'Gunakan benih sehat dan bersertifikat',
                    'Rotasi tanaman dengan tanaman non-allium',
                    'Jaga kebersihan lahan dari sisa tanaman',
                    'Hindari penyiraman berlebihan',
                    'Monitoring rutin kondisi tanaman'
                ]
            },
            'downy_mildew': {
                'name': 'Embun Bulu (Downy Mildew)',
                'scientific_name': 'Peronospora destructor',
                'type': 'Oomycete',
                'description': 'Penyakit yang menyebabkan lapisan putih keabu-abuan pada permukaan daun, terutama pada kondisi lembab.',
                'symptoms': [
                    'Lapisan putih keabu-abuan pada permukaan daun',
                    'Daun menguning dari ujung',
                    'Pertumbuhan kerdil',
                    'Daun melengkung dan mengering'
                ],
                'conditions': {
                    'temperature': '15-20°C',
                    'humidity': 'Sangat tinggi (>90%)',
                    'weather': 'Embun pagi, kelembaban tinggi'
                },
                'severity_levels': {
                    'ringan': 'Lapisan putih tipis pada beberapa daun',
                    'sedang': 'Lapisan putih menyebar, daun mulai menguning',
                    'berat': 'Seluruh tanaman terinfeksi, pertumbuhan sangat terhambat'
                },
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
            'leaf_blight': {
                'name': 'Busuk Daun (Leaf Blight)',
                'scientific_name': 'Botrytis squamosa',
                'type': 'Fungal',
                'description': 'Penyakit jamur yang menyebabkan bercak putih kecil yang membesar dan mengering pada daun.',
                'symptoms': [
                    'Bercak putih kecil dengan halo kuning',
                    'Bercak membesar dan mengering',
                    'Daun patah pada bagian yang terinfeksi',
                    'Ujung daun mengering dan mati'
                ],
                'conditions': {
                    'temperature': '18-24°C',
                    'humidity': 'Tinggi dengan angin kencang',
                    'weather': 'Cuaca berubah-ubah, angin kencang'
                },
                'severity_levels': {
                    'ringan': 'Beberapa bercak kecil pada daun tua',
                    'sedang': 'Bercak menyebar ke daun muda',
                    'berat': 'Sebagian besar daun rusak dan patah'
                },
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
            'anthracnose': {
                'name': 'Antraknosa',
                'scientific_name': 'Colletotrichum gloeosporioides',
                'type': 'Fungal',
                'description': 'Penyakit jamur yang menyebabkan bercak coklat dengan tepi gelap pada daun dan dapat menyerang umbi.',
                'symptoms': [
                    'Bercak coklat dengan tepi gelap',
                    'Bercak cekung pada umbi',
                    'Daun layu dan mengering',
                    'Pertumbuhan terhambat'
                ],
                'conditions': {
                    'temperature': '25-30°C',
                    'humidity': 'Tinggi dengan hujan',
                    'weather': 'Curah hujan tinggi, suhu hangat'
                },
                'severity_levels': {
                    'ringan': 'Bercak sedikit pada daun',
                    'sedang': 'Bercak menyebar, mulai menyerang umbi',
                    'berat': 'Umbi busuk, tanaman mati'
                },
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
            },
            'healthy': {
                'name': 'Sehat',
                'scientific_name': None,
                'type': 'Normal',
                'description': 'Tanaman bawang merah dalam kondisi sehat tanpa tanda-tanda penyakit.',
                'symptoms': [
                    'Daun hijau segar',
                    'Pertumbuhan normal',
                    'Tidak ada bercak atau kelainan',
                    'Umbi berkembang baik'
                ],
                'conditions': {
                    'temperature': 'Optimal untuk pertumbuhan',
                    'humidity': 'Seimbang',
                    'weather': 'Kondisi cuaca mendukung'
                },
                'treatments': [
                    'Lanjutkan perawatan rutin',
                    'Monitoring berkala',
                    'Pemupukan sesuai jadwal',
                    'Penyiraman yang tepat'
                ],
                'prevention': [
                    'Pertahankan kondisi optimal',
                    'Monitoring rutin',
                    'Sanitasi lahan',
                    'Nutrisi seimbang'
                ]
            }
        }
    
    def classify(self, prediction_result: np.ndarray, image_features: Dict = None) -> Dict:
        """
        Klasifikasi penyakit berdasarkan hasil prediksi model
        
        Args:
            prediction_result: Output dari model CNN/RNN
            image_features: Features tambahan dari gambar (opsional)
            
        Returns:
            Dict: Hasil klasifikasi lengkap
        """
        try:
            # TODO: Implementasi real classification ketika model sudah ready
            # Sementara return mock classification
            return self._mock_classification()
            
        except Exception as e:
            self.logger.error(f"Error in classification: {str(e)}")
            raise
    
    def _mock_classification(self) -> Dict:
        """Mock classification untuk testing"""
        # Simulasi hasil klasifikasi
        disease_key = 'purple_blotch'
        confidence = 87.5
        severity = 'sedang'
        
        disease_info = self.disease_database[disease_key]
        
        result = {
            'success': True,
            'disease_key': disease_key,
            'disease': disease_info['name'],
            'scientific_name': disease_info['scientific_name'],
            'type': disease_info['type'],
            'confidence': confidence,
            'severity': severity,
            'description': disease_info['description'],
            'symptoms': disease_info['symptoms'],
            'conditions': disease_info['conditions'],
            'treatments': disease_info['treatments'],
            'prevention': disease_info['prevention'],
            'severity_info': disease_info['severity_levels'][severity],
            'timestamp': datetime.now().isoformat(),
            'recommendations': self._generate_recommendations(disease_key, severity, confidence)
        }
        
        return result
    
    def _generate_recommendations(self, disease_key: str, severity: str, confidence: float) -> List[str]:
        """Generate rekomendasi berdasarkan hasil diagnosis"""
        recommendations = []
        
        if confidence < self.confidence_threshold:
            recommendations.append("Confidence rendah - disarankan konsultasi dengan ahli")
            recommendations.append("Ambil foto yang lebih jelas untuk analisis ulang")
        
        if disease_key == 'healthy':
            recommendations.extend([
                "Tanaman dalam kondisi sehat",
                "Lanjutkan perawatan rutin",
                "Monitor secara berkala"
            ])
        else:
            if severity == 'ringan':
                recommendations.extend([
                    "Segera lakukan tindakan pencegahan",
                    "Monitor perkembangan penyakit",
                    "Aplikasi fungisida preventif"
                ])
            elif severity == 'sedang':
                recommendations.extend([
                    "Segera aplikasi fungisida kuratif",
                    "Isolasi tanaman yang terinfeksi",
                    "Perbaiki kondisi lingkungan"
                ])
            else:  # berat
                recommendations.extend([
                    "Tindakan darurat diperlukan",
                    "Buang tanaman yang terinfeksi berat",
                    "Desinfeksi area sekitar",
                    "Konsultasi dengan penyuluh pertanian"
                ])
        
        return recommendations
    
    def get_disease_info(self, disease_key: str) -> Dict:
        """Get informasi lengkap tentang penyakit tertentu"""
        if disease_key in self.disease_database:
            return self.disease_database[disease_key]
        else:
            raise ValueError(f"Disease key '{disease_key}' not found in database")
    
    def get_all_diseases(self) -> Dict:
        """Get informasi semua penyakit"""
        return self.disease_database
    
    def calculate_risk_score(self, disease_key: str, severity: str, confidence: float) -> float:
        """Hitung risk score berdasarkan penyakit, severity, dan confidence"""
        base_scores = {
            'healthy': 0.0,
            'purple_blotch': 0.6,
            'downy_mildew': 0.7,
            'leaf_blight': 0.5,
            'anthracnose': 0.8
        }
        
        severity_multipliers = {
            'ringan': 1.0,
            'sedang': 1.5,
            'berat': 2.0
        }
        
        base_score = base_scores.get(disease_key, 0.5)
        severity_mult = severity_multipliers.get(severity, 1.0)
        confidence_factor = confidence / 100.0
        
        risk_score = base_score * severity_mult * confidence_factor
        return min(risk_score, 1.0)  # Cap at 1.0