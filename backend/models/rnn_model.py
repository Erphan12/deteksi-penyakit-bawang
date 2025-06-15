# RNN Model untuk Analisis Temporal Penyakit Bawang Merah
# Template untuk implementasi model RNN

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
import logging
from datetime import datetime, timedelta

class RNNModel:
    """
    Recurrent Neural Network untuk analisis temporal penyakit bawang merah
    Digunakan untuk memprediksi perkembangan penyakit berdasarkan riwayat
    """
    
    def __init__(self, sequence_length=7, num_features=10, num_classes=5):
        self.sequence_length = sequence_length  # 7 hari riwayat
        self.num_features = num_features        # Features per hari
        self.num_classes = num_classes          # Jumlah kelas penyakit
        self.model = None
        self.logger = logging.getLogger(__name__)
        
        # Feature names untuk temporal analysis
        self.feature_names = [
            'temperature',      # Suhu harian
            'humidity',         # Kelembaban
            'rainfall',         # Curah hujan
            'wind_speed',       # Kecepatan angin
            'disease_severity', # Tingkat keparahan penyakit
            'leaf_health',      # Kesehatan daun (0-1)
            'growth_rate',      # Tingkat pertumbuhan
            'treatment_applied', # Apakah ada treatment (0/1)
            'fertilizer_applied', # Apakah ada pemupukan (0/1)
            'irrigation_amount'  # Jumlah penyiraman
        ]
        
        self.class_names = [
            'healthy',
            'purple_blotch', 
            'downy_mildew',
            'leaf_blight',
            'anthracnose'
        ]
    
    def build_model(self):
        """
        Build RNN architecture untuk analisis temporal
        Menggunakan LSTM untuk menangkap long-term dependencies
        """
        try:
            model = keras.Sequential([
                # Input layer
                keras.Input(shape=(self.sequence_length, self.num_features)),
                
                # LSTM layers
                layers.LSTM(128, return_sequences=True, dropout=0.2),
                layers.LSTM(64, return_sequences=True, dropout=0.2),
                layers.LSTM(32, dropout=0.2),
                
                # Dense layers
                layers.Dense(64, activation='relu'),
                layers.BatchNormalization(),
                layers.Dropout(0.3),
                layers.Dense(32, activation='relu'),
                layers.Dropout(0.2),
                
                # Output layer
                layers.Dense(self.num_classes, activation='softmax')
            ])
            
            self.model = model
            self.logger.info("RNN model built successfully")
            return model
            
        except Exception as e:
            self.logger.error(f"Error building RNN model: {str(e)}")
            raise
    
    def build_advanced_model(self):
        """
        Build advanced RNN dengan attention mechanism
        """
        try:
            # Input
            inputs = keras.Input(shape=(self.sequence_length, self.num_features))
            
            # Bidirectional LSTM
            lstm_out = layers.Bidirectional(
                layers.LSTM(64, return_sequences=True, dropout=0.2)
            )(inputs)
            
            # Attention mechanism
            attention = layers.MultiHeadAttention(
                num_heads=4, key_dim=64
            )(lstm_out, lstm_out)
            
            # Add & Norm
            attention = layers.Add()([lstm_out, attention])
            attention = layers.LayerNormalization()(attention)
            
            # Global pooling
            pooled = layers.GlobalAveragePooling1D()(attention)
            
            # Dense layers
            dense = layers.Dense(128, activation='relu')(pooled)
            dense = layers.BatchNormalization()(dense)
            dense = layers.Dropout(0.3)(dense)
            dense = layers.Dense(64, activation='relu')(dense)
            dense = layers.Dropout(0.2)(dense)
            
            # Output
            outputs = layers.Dense(self.num_classes, activation='softmax')(dense)
            
            model = keras.Model(inputs=inputs, outputs=outputs)
            
            self.model = model
            self.logger.info("Advanced RNN model built successfully")
            return model
            
        except Exception as e:
            self.logger.error(f"Error building advanced RNN model: {str(e)}")
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
            
            self.logger.info("RNN model compiled successfully")
            
        except Exception as e:
            self.logger.error(f"Error compiling RNN model: {str(e)}")
            raise
    
    def prepare_sequence_data(self, data, target_column='disease_class'):
        """
        Prepare data untuk sequence learning
        
        Args:
            data: DataFrame dengan kolom temporal
            target_column: Nama kolom target
            
        Returns:
            X, y: Sequence data dan labels
        """
        try:
            sequences = []
            labels = []
            
            # Group by plant/field ID
            for plant_id in data['plant_id'].unique():
                plant_data = data[data['plant_id'] == plant_id].sort_values('date')
                
                # Create sequences
                for i in range(len(plant_data) - self.sequence_length + 1):
                    # Feature sequence
                    sequence = plant_data[self.feature_names].iloc[i:i+self.sequence_length].values
                    sequences.append(sequence)
                    
                    # Label (last day of sequence)
                    label = plant_data[target_column].iloc[i+self.sequence_length-1]
                    labels.append(label)
            
            X = np.array(sequences)
            y = keras.utils.to_categorical(labels, num_classes=self.num_classes)
            
            return X, y
            
        except Exception as e:
            self.logger.error(f"Error preparing sequence data: {str(e)}")
            raise
    
    def train(self, X_train, y_train, X_val, y_val, epochs=100):
        """
        Train RNN model
        
        Args:
            X_train, y_train: Training data
            X_val, y_val: Validation data
            epochs: Number of training epochs
        """
        try:
            if self.model is None:
                self.compile_model()
            
            # Callbacks
            callbacks = [
                keras.callbacks.EarlyStopping(
                    monitor='val_loss',
                    patience=15,
                    restore_best_weights=True
                ),
                keras.callbacks.ReduceLROnPlateau(
                    monitor='val_loss',
                    factor=0.5,
                    patience=8,
                    min_lr=1e-7
                ),
                keras.callbacks.ModelCheckpoint(
                    'best_rnn_model.h5',
                    monitor='val_accuracy',
                    save_best_only=True
                )
            ]
            
            # Training
            history = self.model.fit(
                X_train, y_train,
                validation_data=(X_val, y_val),
                epochs=epochs,
                batch_size=32,
                callbacks=callbacks,
                verbose=1
            )
            
            self.logger.info("RNN model training completed")
            return history
            
        except Exception as e:
            self.logger.error(f"Error training RNN model: {str(e)}")
            raise
    
    def predict_sequence(self, sequence_data):
        """
        Predict berdasarkan sequence data
        
        Args:
            sequence_data: Array dengan shape (sequence_length, num_features)
            
        Returns:
            dict: Prediction results
        """
        try:
            if self.model is None:
                raise ValueError("Model not loaded")
            
            # Ensure correct shape
            if len(sequence_data.shape) == 2:
                sequence_data = np.expand_dims(sequence_data, axis=0)
            
            # Prediction
            predictions = self.model.predict(sequence_data, verbose=0)
            
            # Get results
            class_probabilities = predictions[0]
            predicted_class_idx = np.argmax(class_probabilities)
            confidence = float(class_probabilities[predicted_class_idx]) * 100
            
            result = {
                'predicted_class': self.class_names[predicted_class_idx],
                'confidence': confidence,
                'all_probabilities': {
                    class_name: float(prob) * 100 
                    for class_name, prob in zip(self.class_names, class_probabilities)
                },
                'trend_analysis': self._analyze_trend(sequence_data[0])
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error making sequence prediction: {str(e)}")
            raise
    
    def _analyze_trend(self, sequence_data):
        """Analyze trend dari sequence data"""
        try:
            trends = {}
            
            for i, feature_name in enumerate(self.feature_names):
                feature_values = sequence_data[:, i]
                
                # Calculate trend
                if len(feature_values) > 1:
                    trend = np.polyfit(range(len(feature_values)), feature_values, 1)[0]
                    trends[feature_name] = {
                        'slope': float(trend),
                        'direction': 'increasing' if trend > 0 else 'decreasing' if trend < 0 else 'stable',
                        'current_value': float(feature_values[-1]),
                        'change_rate': float(trend * len(feature_values))
                    }
            
            return trends
            
        except Exception as e:
            self.logger.error(f"Error analyzing trend: {str(e)}")
            return {}
    
    def predict_future(self, sequence_data, days_ahead=3):
        """
        Predict kondisi penyakit beberapa hari ke depan
        
        Args:
            sequence_data: Historical sequence data
            days_ahead: Jumlah hari yang ingin diprediksi
            
        Returns:
            list: Predictions untuk setiap hari
        """
        try:
            if self.model is None:
                raise ValueError("Model not loaded")
            
            predictions = []
            current_sequence = sequence_data.copy()
            
            for day in range(days_ahead):
                # Predict next day
                pred = self.predict_sequence(current_sequence)
                predictions.append({
                    'day': day + 1,
                    'date': (datetime.now() + timedelta(days=day+1)).strftime('%Y-%m-%d'),
                    'prediction': pred
                })
                
                # Update sequence for next prediction
                # (Simplified - in real implementation, you'd need weather forecast data)
                # For now, we'll use the last values with some variation
                last_values = current_sequence[-1].copy()
                
                # Add some realistic variation
                for i in range(len(last_values)):
                    if i < 4:  # Weather features - add some random variation
                        last_values[i] += np.random.normal(0, 0.1)
                    elif i == 4:  # Disease severity - might increase if no treatment
                        if last_values[7] == 0:  # No treatment applied
                            last_values[i] = min(1.0, last_values[i] + 0.1)
                
                # Shift sequence and add new prediction
                current_sequence = np.roll(current_sequence, -1, axis=0)
                current_sequence[-1] = last_values
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"Error predicting future: {str(e)}")
            raise
    
    def generate_recommendations(self, sequence_data, prediction_result):
        """
        Generate rekomendasi berdasarkan analisis temporal
        """
        try:
            recommendations = []
            trends = prediction_result.get('trend_analysis', {})
            predicted_class = prediction_result.get('predicted_class', 'unknown')
            
            # Weather-based recommendations
            if 'humidity' in trends:
                humidity_trend = trends['humidity']
                if humidity_trend['direction'] == 'increasing' and humidity_trend['current_value'] > 0.8:
                    recommendations.append("Kelembaban tinggi dan meningkat - tingkatkan ventilasi")
            
            if 'rainfall' in trends:
                rainfall_trend = trends['rainfall']
                if rainfall_trend['direction'] == 'increasing':
                    recommendations.append("Curah hujan meningkat - perbaiki drainase lahan")
            
            # Disease-specific recommendations
            if predicted_class != 'healthy':
                if 'disease_severity' in trends:
                    severity_trend = trends['disease_severity']
                    if severity_trend['direction'] == 'increasing':
                        recommendations.append("Tingkat keparahan penyakit meningkat - segera aplikasi fungisida")
                
                if 'treatment_applied' in trends:
                    treatment_trend = trends['treatment_applied']
                    if treatment_trend['current_value'] == 0:
                        recommendations.append("Belum ada treatment - segera lakukan penanganan")
            
            # Growth-based recommendations
            if 'growth_rate' in trends:
                growth_trend = trends['growth_rate']
                if growth_trend['direction'] == 'decreasing':
                    recommendations.append("Pertumbuhan menurun - periksa nutrisi dan kondisi tanah")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {str(e)}")
            return ["Error generating recommendations"]
    
    def save_model(self, filepath):
        """Save trained RNN model"""
        try:
            if self.model is None:
                raise ValueError("No model to save")
            
            self.model.save(filepath)
            self.logger.info(f"RNN model saved to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Error saving RNN model: {str(e)}")
            raise
    
    def load_model(self, filepath):
        """Load trained RNN model"""
        try:
            self.model = keras.models.load_model(filepath)
            self.logger.info(f"RNN model loaded from {filepath}")
            
        except Exception as e:
            self.logger.error(f"Error loading RNN model: {str(e)}")
            raise

# Utility functions untuk temporal data
def create_mock_temporal_data(num_plants=100, days_per_plant=30):
    """
    Create mock temporal data untuk testing
    """
    import pandas as pd
    
    data = []
    
    for plant_id in range(num_plants):
        for day in range(days_per_plant):
            date = datetime.now() - timedelta(days=days_per_plant-day)
            
            # Mock weather data
            temperature = 25 + np.random.normal(0, 3)
            humidity = 0.7 + np.random.normal(0, 0.1)
            rainfall = max(0, np.random.exponential(2))
            wind_speed = max(0, np.random.normal(5, 2))
            
            # Mock plant data
            disease_severity = max(0, min(1, np.random.beta(2, 5)))
            leaf_health = 1 - disease_severity + np.random.normal(0, 0.1)
            growth_rate = max(0, np.random.normal(0.1, 0.02))
            
            # Mock management data
            treatment_applied = 1 if np.random.random() < 0.2 else 0
            fertilizer_applied = 1 if np.random.random() < 0.1 else 0
            irrigation_amount = max(0, np.random.normal(10, 3))
            
            # Mock disease class (simplified logic)
            if disease_severity < 0.2:
                disease_class = 0  # healthy
            elif disease_severity < 0.4:
                disease_class = np.random.choice([1, 2, 3, 4])
            else:
                disease_class = np.random.choice([1, 2, 3, 4])
            
            data.append({
                'plant_id': plant_id,
                'date': date,
                'temperature': temperature,
                'humidity': humidity,
                'rainfall': rainfall,
                'wind_speed': wind_speed,
                'disease_severity': disease_severity,
                'leaf_health': leaf_health,
                'growth_rate': growth_rate,
                'treatment_applied': treatment_applied,
                'fertilizer_applied': fertilizer_applied,
                'irrigation_amount': irrigation_amount,
                'disease_class': disease_class
            })
    
    return pd.DataFrame(data)