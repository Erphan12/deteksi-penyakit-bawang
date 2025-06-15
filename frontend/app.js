// Onion Disease Detection App JavaScript
class OnionDiseaseApp {
    constructor() {
        // Detect if running on Railway or localhost
        const isLocalhost = window.location.hostname === 'localhost' || 
                           window.location.hostname === '127.0.0.1' ||
                           window.location.hostname === '';
        
        if (isLocalhost) {
            // Local development
            this.API_BASE_URL = window.location.origin + '/api';
            this.FALLBACK_URLS = [
                '/api',
                'http://127.0.0.1:5050/api',
                'http://localhost:5050/api'
            ];
        } else {
            // Production (Railway)
            this.API_BASE_URL = window.location.origin + '/api';
            this.FALLBACK_URLS = ['/api'];
        }
        
        this.currentSection = 'upload';
        this.isOnline = navigator.onLine;
        this.analysisHistory = JSON.parse(localStorage.getItem('analysisHistory') || '[]');
        
        this.init();
    }

    init() {
        // Wait for DOM to be fully loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.setupEventListeners();
                this.setupDragAndDrop();
                this.loadDiseaseInfo();
                this.hideLoadingScreen();
            });
        } else {
            this.setupEventListeners();
            this.setupDragAndDrop();
            this.loadDiseaseInfo();
            this.hideLoadingScreen();
        }
    }

    setupEventListeners() {
        // Image upload
        const imageInput = document.getElementById('image-input');
        const uploadArea = document.getElementById('upload-area');
        const uploadBtn = document.getElementById('upload-btn');
        const analyzeBtn = document.getElementById('analyze-btn');
        const clearBtn = document.getElementById('clear-btn');
        
        
        // Pastikan elemen ada sebelum menambahkan event listener
        if (imageInput) {
            imageInput.addEventListener('change', (e) => this.handleImageSelect(e));
        }
        
        if (uploadArea) {
            uploadArea.addEventListener('click', (e) => {
                // Prevent event bubbling dan pastikan hanya area upload yang diklik
                e.preventDefault();
                e.stopPropagation();
                if (imageInput) {
                    imageInput.click();
                }
            });
        }
        
        if (uploadBtn) {
            uploadBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                if (imageInput) {
                    imageInput.click();
                }
            });
        }
        
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', () => this.analyzeImage());
        }
        
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearImage());
        }

        // Navigation
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                const section = e.currentTarget.dataset.section;
                this.switchSection(section);
            });
        });

        // Header buttons
        document.getElementById('info-btn').addEventListener('click', () => this.showModal('info-modal'));
        document.getElementById('history-btn').addEventListener('click', () => this.showHistoryModal());
        document.getElementById('settings-btn').addEventListener('click', () => this.showModal('settings-modal'));

        // Modal close buttons
        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const modal = e.target.closest('.modal');
                this.hideModal(modal.id);
            });
        });

        // Modal background click
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.hideModal(modal.id);
                }
            });
        });

        // Result actions
        document.getElementById('save-result-btn').addEventListener('click', () => this.saveResult());
        document.getElementById('share-result-btn').addEventListener('click', () => this.shareResult());
        document.getElementById('new-analysis-btn').addEventListener('click', () => this.newAnalysis());

            }

        
    setupDragAndDrop() {
        const uploadArea = document.getElementById('upload-area');
        
        if (!uploadArea) {
            console.warn('Upload area not found');
            return;
        }

        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            });
        });

        // Highlight drop area when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => {
                uploadArea.classList.add('dragover');
            });
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => {
                uploadArea.classList.remove('dragover');
            });
        });

        // Handle dropped files
        uploadArea.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            
            if (files.length === 0) {
                this.showToast('Tidak ada file yang dipilih', 'warning');
                return;
            }
            
            if (files.length > 1) {
                this.showToast('Pilih hanya satu gambar', 'warning');
                return;
            }
            
            const file = files[0];
            this.processSelectedFile(file);
        });
    }

    handleImageSelect(event) {
        if (!event.target.files || event.target.files.length === 0) {
            return;
        }
        
        const file = event.target.files[0];
        this.processSelectedFile(file);
    }

    processSelectedFile(file) {
        if (!file) {
            this.showToast('File tidak valid', 'error');
            return;
        }

        // Validasi tipe file
        if (!this.isValidImageFile(file)) {
            this.showToast('Format file tidak didukung. Gunakan JPG, JPEG, atau PNG', 'error');
            return;
        }

        // Validasi ukuran file (maksimal 10MB)
        const maxSize = 10 * 1024 * 1024; // 10MB
        if (file.size > maxSize) {
            this.showToast('Ukuran file terlalu besar. Maksimal 10MB', 'error');
            return;
        }

        // Proses file jika valid
        this.displayImagePreview(file);
    }

    isValidImageFile(file) {
        const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
        const validExtensions = ['.jpg', '.jpeg', '.png', '.webp'];
        
        // Check MIME type
        if (!validTypes.includes(file.type.toLowerCase())) {
            return false;
        }
        
        // Check file extension as backup
        const fileName = file.name.toLowerCase();
        const hasValidExtension = validExtensions.some(ext => fileName.endsWith(ext));
        
        return hasValidExtension;
    }

    displayImagePreview(file) {
        const previewImg = document.getElementById('preview-img');
        const imagePreview = document.getElementById('image-preview');
        
        if (!previewImg || !imagePreview) {
            this.showToast('Error: Elemen preview tidak ditemukan', 'error');
            return;
        }

        const reader = new FileReader();
        
        reader.onload = (e) => {
            try {
                previewImg.src = e.target.result;
                imagePreview.classList.remove('hidden');
                
                // Store file for analysis
                this.selectedFile = file;
                
                // Show success message
                this.showToast(`Gambar "${file.name}" berhasil dipilih`, 'success');
                
                // Scroll to preview
                imagePreview.scrollIntoView({ behavior: 'smooth', block: 'center' });
                
            } catch (error) {
                console.error('Error displaying image preview:', error);
                this.showToast('Gagal menampilkan preview gambar', 'error');
            }
        };
        
        reader.onerror = () => {
            this.showToast('Gagal membaca file gambar', 'error');
        };
        
        reader.onabort = () => {
            this.showToast('Pembacaan file dibatalkan', 'warning');
        };
        
        try {
            reader.readAsDataURL(file);
        } catch (error) {
            console.error('Error reading file:', error);
            this.showToast('Gagal memproses file gambar', 'error');
        }
    }

    clearImage() {
        const imagePreview = document.getElementById('image-preview');
        const imageInput = document.getElementById('image-input');
        const previewImg = document.getElementById('preview-img');
        const analysisSection = document.getElementById('analysis-section');
        
        try {
            // Clear preview
            if (imagePreview) {
                imagePreview.classList.add('hidden');
            }
            
            // Clear input
            if (imageInput) {
                imageInput.value = '';
            }
            
            // Clear preview image src
            if (previewImg) {
                previewImg.src = '';
                previewImg.alt = 'Preview';
            }
            
            // Clear stored file
            this.selectedFile = null;
            
            // Hide analysis section if visible
            if (analysisSection) {
                analysisSection.classList.add('hidden');
            }
            
            // Clear current result
            this.currentResult = null;
            
            this.showToast('Gambar berhasil dihapus', 'info');
            
        } catch (error) {
            console.error('Error clearing image:', error);
            this.showToast('Gagal menghapus gambar', 'error');
        }
    }

    async analyzeImage() {
        if (!this.selectedFile) {
            this.showToast('Pilih gambar terlebih dahulu', 'error');
            return;
        }

        // Show analysis section and loading
        const analysisSection = document.getElementById('analysis-section');
        const analysisLoading = document.getElementById('analysis-loading');
        const analysisResults = document.getElementById('analysis-results');
        
        analysisSection.classList.remove('hidden');
        analysisLoading.style.display = 'block';
        analysisResults.classList.add('hidden');

        // Scroll to analysis section
        analysisSection.scrollIntoView({ behavior: 'smooth' });

        try {
            const result = await this.sendImageToAPI(this.selectedFile);
            this.displayAnalysisResults(result);
            
            // Save to history
            this.saveToHistory(result);
            
        } catch (error) {
            console.error('Analysis error:', error);
            this.showToast('Gagal menganalisis gambar. Silakan coba lagi.', 'error');
            analysisSection.classList.add('hidden');
        }
    }

    async sendImageToAPI(file) {
        const formData = new FormData();
        formData.append('image', file);

        // Try main URL first, then fallbacks
        const urlsToTry = [this.API_BASE_URL, ...this.FALLBACK_URLS];
        
        for (let i = 0; i < urlsToTry.length; i++) {
            const baseUrl = urlsToTry[i];
            try {
                console.log(`Trying API URL: ${baseUrl}/detect`);
                
                const response = await fetch(`${baseUrl}/detect`, {
                    method: 'POST',
                    body: formData,
                    // Add headers to avoid blocking
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });

                if (response.ok) {
                    // Update API_BASE_URL to working URL for future requests
                    this.API_BASE_URL = baseUrl;
                    return await response.json();
                } else {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
            } catch (error) {
                console.warn(`Failed with URL ${baseUrl}: ${error.message}`);
                
                // If this is the last URL, throw the error
                if (i === urlsToTry.length - 1) {
                    throw new Error(`All API endpoints failed. Last error: ${error.message}`);
                }
                
                // Continue to next URL
                continue;
            }
        }
    }

    displayAnalysisResults(result) {
        const analysisLoading = document.getElementById('analysis-loading');
        const analysisResults = document.getElementById('analysis-results');
        
        // Hide loading, show results
        analysisLoading.style.display = 'none';
        analysisResults.classList.remove('hidden');

        // Update result content
        document.getElementById('disease-name').textContent = result.disease || 'Tidak terdeteksi';
        document.getElementById('disease-description').textContent = result.description || 'Tidak ada deskripsi';
        
        // Update confidence
        const confidenceValue = document.getElementById('confidence-value');
        const confidenceBadge = document.getElementById('confidence-badge');
        const confidence = result.confidence || 0;
        
        confidenceValue.textContent = `${confidence}%`;
        
        // Set confidence badge color
        confidenceBadge.className = 'confidence-badge';
        if (confidence < 70) {
            confidenceBadge.classList.add('low');
        } else if (confidence < 85) {
            confidenceBadge.classList.add('medium');
        }

        // Update severity
        const severityValue = document.getElementById('severity-value');
        const severity = result.severity || 'Normal';
        severityValue.textContent = severity;
        severityValue.className = `severity-badge ${severity.toLowerCase()}`;

        // Update treatments
        const treatmentList = document.getElementById('treatment-list');
        treatmentList.innerHTML = '';
        if (result.treatments && result.treatments.length > 0) {
            result.treatments.forEach(treatment => {
                const li = document.createElement('li');
                li.textContent = treatment;
                treatmentList.appendChild(li);
            });
        }

        // Update prevention
        const preventionList = document.getElementById('prevention-list');
        preventionList.innerHTML = '';
        if (result.prevention && result.prevention.length > 0) {
            result.prevention.forEach(prevention => {
                const li = document.createElement('li');
                li.textContent = prevention;
                preventionList.appendChild(li);
            });
        }

        // Store current result
        this.currentResult = result;
    }

    
    saveToHistory(result) {
        const historyItem = {
            id: Date.now(),
            timestamp: new Date().toISOString(),
            disease: result.disease,
            confidence: result.confidence,
            severity: result.severity,
            image: document.getElementById('preview-img').src
        };

        this.analysisHistory.unshift(historyItem);
        
        // Keep only last 50 items
        if (this.analysisHistory.length > 50) {
            this.analysisHistory = this.analysisHistory.slice(0, 50);
        }

        localStorage.setItem('analysisHistory', JSON.stringify(this.analysisHistory));
    }

    async loadDiseaseInfo() {
        const urlsToTry = [this.API_BASE_URL, ...this.FALLBACK_URLS];
        
        for (let i = 0; i < urlsToTry.length; i++) {
            const baseUrl = urlsToTry[i];
            try {
                console.log(`Trying to load disease info from: ${baseUrl}/diseases`);
                
                const response = await fetch(`${baseUrl}/diseases`, {
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });
                
                if (response.ok) {
                    const data = await response.json();
                    this.displayDiseaseCards(data.diseases);
                    // Update API_BASE_URL to working URL
                    this.API_BASE_URL = baseUrl;
                    return;
                } else {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
            } catch (error) {
                console.warn(`Failed to load disease info from ${baseUrl}: ${error.message}`);
                
                // If this is the last URL, use default info
                if (i === urlsToTry.length - 1) {
                    console.error('All disease info endpoints failed, using default data');
                    this.displayDefaultDiseaseInfo();
                    return;
                }
                
                // Continue to next URL
                continue;
            }
        }
    }

    displayDiseaseCards(diseases) {
        const diseaseCards = document.getElementById('disease-cards');
        diseaseCards.innerHTML = '';

        diseases.forEach(disease => {
            const card = document.createElement('div');
            card.className = 'disease-card';
            card.innerHTML = `
                <h4>${disease.name}</h4>
                <p class="pathogen"><strong>Patogen:</strong> ${disease.pathogen}</p>
                <p class="symptoms"><strong>Gejala:</strong> ${disease.symptoms}</p>
                <p class="conditions"><strong>Kondisi:</strong> ${disease.conditions}</p>
            `;
            diseaseCards.appendChild(card);
        });
    }

    displayDefaultDiseaseInfo() {
        const diseases = [
            {
                name: 'Bercak Ungu (Purple Blotch)',
                pathogen: 'Alternaria porri',
                symptoms: 'Bercak ungu pada daun, dapat menyebar ke seluruh tanaman',
                conditions: 'Kelembaban tinggi, suhu 20-30°C'
            },
            {
                name: 'Embun Bulu (Downy Mildew)',
                pathogen: 'Peronospora destructor',
                symptoms: 'Lapisan putih keabu-abuan pada permukaan daun',
                conditions: 'Kelembaban sangat tinggi, suhu dingin'
            },
            {
                name: 'Busuk Daun (Leaf Blight)',
                pathogen: 'Botrytis squamosa',
                symptoms: 'Bercak putih kecil yang membesar dan mengering',
                conditions: 'Kelembaban tinggi, angin kencang'
            },
            {
                name: 'Antraknosa',
                pathogen: 'Colletotrichum gloeosporioides',
                symptoms: 'Bercak coklat dengan tepi gelap pada daun',
                conditions: 'Curah hujan tinggi, suhu hangat'
            }
        ];

        this.displayDiseaseCards(diseases);
    }

    switchSection(section) {
        // Update navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-section="${section}"]`).classList.add('active');

        // Handle section switching
        this.currentSection = section;
        
        switch (section) {
            case 'upload':
                // Already visible by default
                break;
            case 'info':
                this.showModal('info-modal');
                break;
            case 'history':
                this.showHistoryModal();
                break;
            case 'settings':
                this.showModal('settings-modal');
                break;
        }
    }

    showModal(modalId) {
        const modal = document.getElementById(modalId);
        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
        
        // Update settings modal with current values
        if (modalId === 'settings-modal') {
            this.updateSettingsModal();
        }
    }
    
    updateSettingsModal() {
        // Settings modal updated - music controls removed
    }

    hideModal(modalId) {
        const modal = document.getElementById(modalId);
        modal.classList.remove('show');
        document.body.style.overflow = '';
    }

    showHistoryModal() {
        const historyContent = document.getElementById('history-content');
        
        if (this.analysisHistory.length === 0) {
            historyContent.innerHTML = '<p>Belum ada riwayat analisis.</p>';
        } else {
            historyContent.innerHTML = this.analysisHistory.map(item => `
                <div class="history-item" style="border-bottom: 1px solid var(--border-color); padding: var(--spacing-md) 0;">
                    <div style="display: flex; align-items: center; gap: var(--spacing-md); margin-bottom: var(--spacing-sm);">
                        <img src="${item.image}" alt="Analyzed image" style="width: 60px; height: 60px; object-fit: cover; border-radius: var(--border-radius);">
                        <div>
                            <h5 style="margin: 0; color: var(--primary-color);">${item.disease}</h5>
                            <p style="margin: 0; font-size: var(--font-size-small); color: var(--text-secondary);">
                                ${new Date(item.timestamp).toLocaleDateString('id-ID')} - 
                                Confidence: ${item.confidence}%
                            </p>
                        </div>
                    </div>
                </div>
            `).join('');
        }
        
        this.showModal('history-modal');
    }

    saveResult() {
        if (!this.currentResult) {
            this.showToast('Tidak ada hasil untuk disimpan', 'error');
            return;
        }

        // Create downloadable report
        const report = {
            timestamp: new Date().toISOString(),
            disease: this.currentResult.disease,
            confidence: this.currentResult.confidence,
            severity: this.currentResult.severity,
            description: this.currentResult.description,
            treatments: this.currentResult.treatments,
            prevention: this.currentResult.prevention
        };

        const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `analisis-penyakit-bawang-${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);

        this.showToast('Hasil analisis berhasil disimpan', 'success');
    }

    async shareResult() {
        if (!this.currentResult) {
            this.showToast('Tidak ada hasil untuk dibagikan', 'error');
            return;
        }

        const shareData = {
            title: 'Hasil Analisis Penyakit Bawang Merah',
            text: `Penyakit: ${this.currentResult.disease}\nTingkat Kepercayaan: ${this.currentResult.confidence}%\nKeparahan: ${this.currentResult.severity}`,
            url: window.location.href
        };

        try {
            if (navigator.share) {
                await navigator.share(shareData);
                this.showToast('Hasil berhasil dibagikan', 'success');
            } else {
                // Fallback: copy to clipboard
                await navigator.clipboard.writeText(shareData.text);
                this.showToast('Hasil disalin ke clipboard', 'success');
            }
        } catch (error) {
            console.error('Error sharing:', error);
            this.showToast('Gagal membagikan hasil', 'error');
        }
    }

    newAnalysis() {
        this.clearImage();
        document.getElementById('analysis-section').classList.add('hidden');
        document.getElementById('upload-area').scrollIntoView({ behavior: 'smooth' });
    }

    
    showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icon = this.getToastIcon(type);
        toast.innerHTML = `
            <i class="${icon}"></i>
            <span>${message}</span>
        `;
        
        toastContainer.appendChild(toast);
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }

    getToastIcon(type) {
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        return icons[type] || icons.info;
    }

    hideLoadingScreen() {
        setTimeout(() => {
            const loadingScreen = document.getElementById('loading-screen');
            loadingScreen.classList.add('hidden');
        }, 1500);
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.onionApp = new OnionDiseaseApp();
});

// Prevent zoom on double tap (iOS)
let lastTouchEnd = 0;
document.addEventListener('touchend', (event) => {
    const now = (new Date()).getTime();
    if (now - lastTouchEnd <= 300) {
        event.preventDefault();
    }
    lastTouchEnd = now;
}, false);