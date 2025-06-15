# Image Processor untuk preprocessing gambar bawang merah
# Clean Code Implementation - Simplified version

import numpy as np
from PIL import Image, ImageEnhance
import logging

class ImageProcessor:
    """
    Class untuk memproses gambar sebelum dianalisis oleh model AI
    Versi sederhana tanpa OpenCV
    """
    
    def __init__(self, target_size=(224, 224)):
        self.target_size = target_size
        self.logger = logging.getLogger(__name__)
    
    def preprocess_image(self, image_path):
        """
        Preprocessing utama untuk gambar
        
        Args:
            image_path (str): Path ke file gambar
            
        Returns:
            np.array: Gambar yang sudah diproses
        """
        try:
            # Load gambar
            image = self.load_image(image_path)
            
            # Resize gambar
            image = self.resize_image(image)
            
            # Normalisasi
            image = self.normalize_image(image)
            
            # Enhancement (opsional)
            image = self.enhance_image(image)
            
            # Convert ke format yang sesuai untuk model
            image = self.prepare_for_model(image)
            
            return image
            
        except Exception as e:
            self.logger.error(f"Error preprocessing image: {str(e)}")
            raise
    
    def load_image(self, image_path):
        """Load gambar dari file"""
        try:
            image = Image.open(image_path)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert to numpy array
            image_array = np.array(image)
            return image_array
            
        except Exception as e:
            self.logger.error(f"Error loading image: {str(e)}")
            raise
    
    def resize_image(self, image):
        """Resize gambar ke ukuran target"""
        try:
            # Convert numpy array to PIL Image
            if isinstance(image, np.ndarray):
                pil_image = Image.fromarray(image.astype(np.uint8))
            else:
                pil_image = image
            
            # Resize using PIL
            resized_pil = pil_image.resize(self.target_size, Image.Resampling.LANCZOS)
            
            # Convert back to numpy array
            resized = np.array(resized_pil)
            return resized
            
        except Exception as e:
            self.logger.error(f"Error resizing image: {str(e)}")
            raise
    
    def normalize_image(self, image):
        """Normalisasi pixel values ke range 0-1"""
        try:
            normalized = image.astype(np.float32) / 255.0
            return normalized
            
        except Exception as e:
            self.logger.error(f"Error normalizing image: {str(e)}")
            raise
    
    def enhance_image(self, image):
        """
        Enhancement gambar untuk meningkatkan kualitas
        - Contrast enhancement
        - Brightness adjustment
        - Sharpening
        """
        try:
            # Convert ke PIL untuk enhancement
            pil_image = Image.fromarray((image * 255).astype(np.uint8))
            
            # Contrast enhancement
            enhancer = ImageEnhance.Contrast(pil_image)
            pil_image = enhancer.enhance(1.2)  # Increase contrast by 20%
            
            # Brightness adjustment
            enhancer = ImageEnhance.Brightness(pil_image)
            pil_image = enhancer.enhance(1.1)  # Increase brightness by 10%
            
            # Sharpness enhancement
            enhancer = ImageEnhance.Sharpness(pil_image)
            pil_image = enhancer.enhance(1.1)  # Increase sharpness by 10%
            
            # Convert back to numpy array
            enhanced = np.array(pil_image).astype(np.float32) / 255.0
            
            return enhanced
            
        except Exception as e:
            self.logger.error(f"Error enhancing image: {str(e)}")
            # Return original image if enhancement fails
            return image
    
    def prepare_for_model(self, image):
        """Prepare gambar untuk input ke model"""
        try:
            # Add batch dimension
            if len(image.shape) == 3:
                image = np.expand_dims(image, axis=0)
            
            return image
            
        except Exception as e:
            self.logger.error(f"Error preparing image for model: {str(e)}")
            raise
    
    def extract_color_features(self, image):
        """Extract basic color features yang berguna untuk deteksi penyakit"""
        try:
            # Calculate basic color statistics
            features = {
                'rgb_mean': np.mean(image, axis=(0, 1)),
                'rgb_std': np.std(image, axis=(0, 1)),
                'brightness': np.mean(image),
                'contrast': np.std(image)
            }
            
            return features
            
        except Exception as e:
            self.logger.error(f"Error extracting color features: {str(e)}")
            raise
    
    def validate_image_quality(self, image):
        """Validasi kualitas gambar sebelum processing"""
        try:
            # Check image dimensions
            if len(image.shape) != 3:
                return False, "Image must be RGB (3 channels)"
            
            # Check if image is too dark or too bright
            mean_brightness = np.mean(image) / 255.0 if image.dtype == np.uint8 else np.mean(image)
            if mean_brightness < 0.1:
                return False, "Image is too dark"
            elif mean_brightness > 0.9:
                return False, "Image is too bright"
            
            return True, "Image quality is acceptable"
            
        except Exception as e:
            self.logger.error(f"Error validating image quality: {str(e)}")
            return False, "Error validating image"