# CNN Model untuk Deteksi Penyakit Bawang Merah
# Template untuk implementasi model CNN

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
import logging
from pathlib import Path

class CNNModel:
    """
    Convolutional Neural Network untuk klasifikasi penyakit bawang merah
    """
    
    def __init__(self, input_shape=(224, 224, 3), num_classes=5):
        self.input_shape = input_shape
        self.num_classes = num_classes
        self.model = None
        self.logger = logging.getLogger(__name__)
        self.class_names = [
            'healthy',
            'purple_blotch', 
            'downy_mildew',
            'leaf_blight',
            'anthracnose'
        ]
    
    def build_model(self):
        """
        Build CNN architecture untuk deteksi penyakit
        Menggunakan transfer learning dengan MobileNetV2 sebagai base
        """
        try:
            # Base model menggunakan MobileNetV2 (pre-trained)
            base_model = keras.applications.MobileNetV2(
                input_shape=self.input_shape,
                include_top=False,
                weights='imagenet'
            )
            
            # Freeze base model layers
            base_model.trainable = False
            
            # Build custom classifier
            model = keras.Sequential([
                # Input layer
                keras.Input(shape=self.input_shape),
                
                # Data augmentation layers
                layers.RandomFlip("horizontal"),
                layers.RandomRotation(0.1),
                layers.RandomZoom(0.1),
                
                # Preprocessing
                keras.applications.mobilenet_v2.preprocess_input,
                
                # Base model
                base_model,
                
                # Custom classifier
                layers.GlobalAveragePooling2D(),
                layers.Dropout(0.2),
                layers.Dense(128, activation='relu'),
                layers.BatchNormalization(),
                layers.Dropout(0.3),
                layers.Dense(64, activation='relu'),
                layers.Dropout(0.2),
                layers.Dense(self.num_classes, activation='softmax')
            ])
            
            self.model = model
            self.logger.info("CNN model built successfully")
            return model
            
        except Exception as e:
            self.logger.error(f"Error building CNN model: {str(e)}")
            raise
    
    def compile_model(self, learning_rate=0.001):
        """Compile model dengan optimizer dan loss function"""
        try:
            if self.model is None:
                self.build_model()
            
            self.model.compile(
                optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
                loss='categorical_crossentropy',
                metrics=['accuracy', 'precision', 'recall']
            )
            
            self.logger.info("Model compiled successfully")
            
        except Exception as e:
            self.logger.error(f"Error compiling model: {str(e)}")
            raise
    
    def train(self, train_dataset, validation_dataset, epochs=50):
        """
        Train model dengan dataset
        
        Args:
            train_dataset: Training dataset
            validation_dataset: Validation dataset
            epochs: Number of training epochs
        """
        try:
            if self.model is None:
                self.compile_model()
            
            # Callbacks
            callbacks = [
                keras.callbacks.EarlyStopping(
                    monitor='val_loss',
                    patience=10,
                    restore_best_weights=True
                ),
                keras.callbacks.ReduceLROnPlateau(
                    monitor='val_loss',
                    factor=0.2,
                    patience=5,
                    min_lr=1e-7
                ),
                keras.callbacks.ModelCheckpoint(
                    'best_model.h5',
                    monitor='val_accuracy',
                    save_best_only=True,
                    save_weights_only=False
                )
            ]
            
            # Training
            history = self.model.fit(
                train_dataset,
                epochs=epochs,
                validation_data=validation_dataset,
                callbacks=callbacks,
                verbose=1
            )
            
            self.logger.info("Model training completed")
            return history
            
        except Exception as e:
            self.logger.error(f"Error training model: {str(e)}")
            raise
    
    def fine_tune(self, train_dataset, validation_dataset, epochs=10):
        """
        Fine-tuning dengan unfreeze beberapa layer terakhir
        """
        try:
            if self.model is None:
                raise ValueError("Model must be trained first")
            
            # Unfreeze top layers of base model
            base_model = self.model.layers[4]  # MobileNetV2 layer
            base_model.trainable = True
            
            # Fine-tune from this layer onwards
            fine_tune_at = 100
            
            # Freeze all layers before fine_tune_at
            for layer in base_model.layers[:fine_tune_at]:
                layer.trainable = False
            
            # Recompile with lower learning rate
            self.model.compile(
                optimizer=keras.optimizers.Adam(learning_rate=0.0001/10),
                loss='categorical_crossentropy',
                metrics=['accuracy', 'precision', 'recall']
            )
            
            # Fine-tuning
            history = self.model.fit(
                train_dataset,
                epochs=epochs,
                validation_data=validation_dataset,
                verbose=1
            )
            
            self.logger.info("Fine-tuning completed")
            return history
            
        except Exception as e:
            self.logger.error(f"Error fine-tuning model: {str(e)}")
            raise
    
    def predict(self, image):
        """
        Predict penyakit dari gambar
        
        Args:
            image: Preprocessed image array
            
        Returns:
            dict: Prediction results
        """
        try:
            if self.model is None:
                raise ValueError("Model not loaded")
            
            # Ensure image has batch dimension
            if len(image.shape) == 3:
                image = np.expand_dims(image, axis=0)
            
            # Prediction
            predictions = self.model.predict(image, verbose=0)
            
            # Get class probabilities
            class_probabilities = predictions[0]
            predicted_class_idx = np.argmax(class_probabilities)
            confidence = float(class_probabilities[predicted_class_idx]) * 100
            
            result = {
                'predicted_class': self.class_names[predicted_class_idx],
                'confidence': confidence,
                'all_probabilities': {
                    class_name: float(prob) * 100 
                    for class_name, prob in zip(self.class_names, class_probabilities)
                }
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error making prediction: {str(e)}")
            raise
    
    def save_model(self, filepath):
        """Save trained model"""
        try:
            if self.model is None:
                raise ValueError("No model to save")
            
            self.model.save(filepath)
            self.logger.info(f"Model saved to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Error saving model: {str(e)}")
            raise
    
    def load_model(self, filepath):
        """Load trained model"""
        try:
            if not Path(filepath).exists():
                raise FileNotFoundError(f"Model file not found: {filepath}")
            
            self.model = keras.models.load_model(filepath)
            self.logger.info(f"Model loaded from {filepath}")
            
        except Exception as e:
            self.logger.error(f"Error loading model: {str(e)}")
            raise
    
    def get_model_summary(self):
        """Get model architecture summary"""
        if self.model is None:
            return "Model not built yet"
        
        return self.model.summary()
    
    def evaluate(self, test_dataset):
        """Evaluate model performance"""
        try:
            if self.model is None:
                raise ValueError("Model not loaded")
            
            results = self.model.evaluate(test_dataset, verbose=0)
            
            metrics = {
                'loss': results[0],
                'accuracy': results[1],
                'precision': results[2] if len(results) > 2 else None,
                'recall': results[3] if len(results) > 3 else None
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error evaluating model: {str(e)}")
            raise

# Utility functions untuk data preparation
def create_dataset_from_directory(data_dir, image_size=(224, 224), batch_size=32):
    """
    Create dataset from directory structure
    
    Expected structure:
    data_dir/
    ├── healthy/
    ├── purple_blotch/
    ├── downy_mildew/
    ├── leaf_blight/
    └── anthracnose/
    """
    try:
        dataset = keras.utils.image_dataset_from_directory(
            data_dir,
            image_size=image_size,
            batch_size=batch_size,
            label_mode='categorical'
        )
        
        # Optimize dataset performance
        AUTOTUNE = tf.data.AUTOTUNE
        dataset = dataset.cache().prefetch(buffer_size=AUTOTUNE)
        
        return dataset
        
    except Exception as e:
        logging.error(f"Error creating dataset: {str(e)}")
        raise

def split_dataset(dataset, train_split=0.8, val_split=0.1, test_split=0.1):
    """Split dataset into train, validation, and test sets"""
    try:
        dataset_size = len(dataset)
        train_size = int(train_split * dataset_size)
        val_size = int(val_split * dataset_size)
        
        train_dataset = dataset.take(train_size)
        remaining = dataset.skip(train_size)
        val_dataset = remaining.take(val_size)
        test_dataset = remaining.skip(val_size)
        
        return train_dataset, val_dataset, test_dataset
        
    except Exception as e:
        logging.error(f"Error splitting dataset: {str(e)}")
        raise