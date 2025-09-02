import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.cluster import KMeans
import joblib
import structlog
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import os

from app.core.config import settings
from app.models.hospital import HospitalProcedure
from app.core.database import SessionLocal

logger = structlog.get_logger()

class HealthcarePriceAnalyzer:
    """AI-powered healthcare price analysis and optimization"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.anomaly_detector = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )
        self.price_predictor = RandomForestRegressor(
            n_estimators=100,
            random_state=42,
            max_depth=10
        )
        self.procedure_encoder = LabelEncoder()
        self.hospital_encoder = LabelEncoder()
        
        # Model paths
        self.models_dir = "app/ml/models"
        self._ensure_models_directory()
        
    def _ensure_models_directory(self):
        """Ensure models directory exists"""
        os.makedirs(self.models_dir, exist_ok=True)
    
    def prepare_data(self, procedures: List[HospitalProcedure]) -> pd.DataFrame:
        """Prepare data for ML models"""
        data = []
        
        for procedure in procedures:
            data.append({
                'cpt_code': procedure.cpt_code,
                'procedure_name': procedure.procedure_name,
                'hospital_name': procedure.hospital.name,
                'cash_price': procedure.cash_price or 0,
                'negotiated_rate_min': procedure.negotiated_rate_min or 0,
                'negotiated_rate_max': procedure.negotiated_rate_max or 0,
                'medicare_rate': procedure.medicare_rate or 0,
                'medicaid_rate': procedure.medicaid_rate or 0,
                'facility_fee': procedure.facility_fee or 0,
                'professional_fee': procedure.professional_fee or 0,
                'anesthesia_fee': procedure.anesthesia_fee or 0
            })
        
        df = pd.DataFrame(data)
        
        # Clean and encode categorical variables
        df['cpt_code_encoded'] = self.procedure_encoder.fit_transform(df['cpt_code'].fillna('UNKNOWN'))
        df['hospital_encoded'] = self.hospital_encoder.fit_transform(df['hospital_name'].fillna('UNKNOWN'))
        
        # Calculate derived features
        df['total_price'] = df['cash_price']
        df['price_range'] = df['negotiated_rate_max'] - df['negotiated_rate_min']
        df['insurance_discount'] = df['cash_price'] - df['negotiated_rate_min']
        
        # Handle missing values
        numeric_columns = ['cash_price', 'negotiated_rate_min', 'negotiated_rate_max', 
                          'medicare_rate', 'medicaid_rate', 'facility_fee', 
                          'professional_fee', 'anesthesia_fee']
        
        for col in numeric_columns:
            df[col] = df[col].fillna(df[col].median())
        
        return df
    
    def train_anomaly_detector(self, procedures: List[HospitalProcedure]) -> Dict:
        """Train anomaly detection model for price outliers"""
        try:
            logger.info("Training anomaly detection model...")
            
            df = self.prepare_data(procedures)
            
            # Features for anomaly detection
            anomaly_features = [
                'cash_price', 'negotiated_rate_min', 'negotiated_rate_max',
                'medicare_rate', 'medicaid_rate', 'price_range', 'insurance_discount'
            ]
            
            X_anomaly = df[anomaly_features].values
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X_anomaly)
            
            # Train anomaly detector
            self.anomaly_detector.fit(X_scaled)
            
            # Detect anomalies
            anomaly_scores = self.anomaly_detector.decision_function(X_scaled)
            anomaly_predictions = self.anomaly_detector.predict(X_scaled)
            
            # Convert predictions to boolean (1 = normal, -1 = anomaly)
            anomalies = anomaly_predictions == -1
            
            # Calculate anomaly statistics
            anomaly_stats = {
                'total_procedures': len(df),
                'anomalies_detected': anomalies.sum(),
                'anomaly_percentage': (anomalies.sum() / len(df)) * 100,
                'mean_anomaly_score': np.mean(anomaly_scores),
                'threshold': settings.PRICE_ANOMALY_THRESHOLD
            }
            
            logger.info(f"Anomaly detection model trained. Found {anomalies.sum()} anomalies out of {len(df)} procedures.")
            
            # Save model
            self._save_model('anomaly_detector.pkl', self.anomaly_detector)
            self._save_model('scaler.pkl', self.scaler)
            
            return {
                'model_trained': True,
                'anomaly_stats': anomaly_stats,
                'anomaly_indices': np.where(anomalies)[0].tolist()
            }
            
        except Exception as e:
            logger.error(f"Error training anomaly detection model: {e}")
            return {'model_trained': False, 'error': str(e)}
    
    def train_price_predictor(self, procedures: List[HospitalProcedure]) -> Dict:
        """Train price prediction model"""
        try:
            logger.info("Training price prediction model...")
            
            df = self.prepare_data(procedures)
            
            # Features for price prediction
            feature_columns = [
                'cpt_code_encoded', 'hospital_encoded', 'negotiated_rate_min',
                'medicare_rate', 'medicaid_rate', 'facility_fee', 'professional_fee'
            ]
            
            X = df[feature_columns].values
            y = df['cash_price'].values
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Train model
            self.price_predictor.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = self.price_predictor.predict(X_test)
            
            metrics = {
                'mae': mean_absolute_error(y_test, y_pred),
                'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
                'r2': r2_score(y_test, y_pred),
                'mean_price': np.mean(y_test),
                'prediction_accuracy': (1 - np.mean(np.abs(y_test - y_pred) / y_test)) * 100
            }
            
            logger.info(f"Price prediction model trained. R²: {metrics['r2']:.3f}, Accuracy: {metrics['prediction_accuracy']:.1f}%")
            
            # Save model
            self._save_model('price_predictor.pkl', self.price_predictor)
            
            return {
                'model_trained': True,
                'metrics': metrics,
                'feature_importance': self._get_feature_importance(feature_columns)
            }
            
        except Exception as e:
            logger.error(f"Error training price prediction model: {e}")
            return {'model_trained': False, 'error': str(e)}
    
    def detect_price_anomalies(self, procedures: List[HospitalProcedure]) -> List[Dict]:
        """Detect price anomalies in procedures"""
        try:
            # Load models if not already trained
            if not hasattr(self, 'anomaly_detector') or not hasattr(self, 'scaler'):
                self._load_models()
            
            df = self.prepare_data(procedures)
            
            # Features for anomaly detection
            anomaly_features = [
                'cash_price', 'negotiated_rate_min', 'negotiated_rate_max',
                'medicare_rate', 'medicaid_rate', 'price_range', 'insurance_discount'
            ]
            
            X_anomaly = df[anomaly_features].values
            X_scaled = self.scaler.transform(X_anomaly)
            
            # Detect anomalies
            anomaly_scores = self.anomaly_detector.decision_function(X_scaled)
            anomaly_predictions = self.anomaly_detector.predict(X_scaled)
            
            anomalies = []
            
            for i, (score, prediction) in enumerate(zip(anomaly_scores, anomaly_predictions)):
                if prediction == -1:  # Anomaly detected
                    procedure = procedures[i]
                    
                    anomaly_info = {
                        'procedure_id': procedure.id,
                        'hospital_name': procedure.hospital.name,
                        'procedure_name': procedure.procedure_name,
                        'cpt_code': procedure.cpt_code,
                        'cash_price': procedure.cash_price,
                        'anomaly_score': float(score),
                        'anomaly_type': self._classify_anomaly(procedure, df.iloc[i]),
                        'recommendations': self._generate_anomaly_recommendations(procedure, df.iloc[i]),
                        'detected_at': datetime.now()
                    }
                    
                    anomalies.append(anomaly_info)
            
            logger.info(f"Detected {len(anomalies)} price anomalies")
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting price anomalies: {e}")
            return []
    
    def predict_procedure_price(self, procedure_data: Dict) -> Dict:
        """Predict price for a procedure"""
        try:
            # Load model if not already trained
            if not hasattr(self, 'price_predictor'):
                self._load_models()
            
            # Prepare input data
            input_features = self._prepare_prediction_input(procedure_data)
            
            # Make prediction
            predicted_price = self.price_predictor.predict([input_features])[0]
            
            # Calculate confidence interval (simplified)
            confidence_interval = predicted_price * 0.15  # ±15% confidence
            
            return {
                'predicted_price': float(predicted_price),
                'confidence_lower': float(predicted_price - confidence_interval),
                'confidence_upper': float(predicted_price + confidence_interval),
                'confidence_level': 0.85,
                'prediction_timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error predicting procedure price: {e}")
            return {'error': str(e)}
    
    def optimize_medication_costs(self, medication_name: str, location: str) -> List[Dict]:
        """Find cost-optimized medication alternatives"""
        try:
            # This would integrate with medication pricing APIs
            # For now, return mock optimization suggestions
            
            optimization_suggestions = [
                {
                    'medication_name': medication_name,
                    'current_price': 150.00,
                    'alternatives': [
                        {
                            'name': f"{medication_name} Generic",
                            'price': 45.00,
                            'savings': 70.0,
                            'pharmacy': 'CVS Pharmacy',
                            'location': location,
                            'availability': 'In Stock'
                        },
                        {
                            'name': f"{medication_name} Alternative",
                            'price': 75.00,
                            'savings': 50.0,
                            'pharmacy': 'Walgreens',
                            'location': location,
                            'availability': 'In Stock'
                        }
                    ],
                    'discount_programs': [
                        {
                            'program': 'GoodRx',
                            'discount': 25.0,
                            'final_price': 112.50
                        },
                        {
                            'program': 'SingleCare',
                            'discount': 30.0,
                            'final_price': 105.00
                        }
                    ]
                }
            ]
            
            return optimization_suggestions
            
        except Exception as e:
            logger.error(f"Error optimizing medication costs: {e}")
            return []
    
    def _classify_anomaly(self, procedure: HospitalProcedure, row: pd.Series) -> str:
        """Classify the type of price anomaly"""
        cash_price = procedure.cash_price or 0
        medicare_rate = procedure.medicare_rate or 0
        medicaid_rate = procedure.medicaid_rate or 0
        
        if cash_price > 0 and medicare_rate > 0:
            markup_ratio = cash_price / medicare_rate
            if markup_ratio > 5:
                return "Excessive Cash Markup"
            elif markup_ratio > 3:
                return "High Cash Markup"
        
        if cash_price > 0 and medicaid_rate > 0:
            markup_ratio = cash_price / medicaid_rate
            if markup_ratio > 8:
                return "Excessive Medicaid Markup"
        
        return "Price Outlier"
    
    def _generate_anomaly_recommendations(self, procedure: HospitalProcedure, row: pd.Series) -> List[str]:
        """Generate recommendations for price anomalies"""
        recommendations = []
        
        cash_price = procedure.cash_price or 0
        medicare_rate = procedure.medicare_rate or 0
        
        if medicare_rate > 0 and cash_price > medicare_rate * 3:
            recommendations.append("Consider negotiating cash price closer to Medicare rates")
            recommendations.append("Check if patient qualifies for financial assistance programs")
        
        if procedure.negotiated_rate_min and cash_price > procedure.negotiated_rate_min * 2:
            recommendations.append("Cash price significantly higher than negotiated rates")
            recommendations.append("Recommend patient contact hospital billing for discounts")
        
        if not recommendations:
            recommendations.append("Monitor pricing trends for this procedure")
            recommendations.append("Compare with regional pricing benchmarks")
        
        return recommendations
    
    def _prepare_prediction_input(self, procedure_data: Dict) -> List:
        """Prepare input features for price prediction"""
        # Encode categorical variables
        cpt_encoded = self.procedure_encoder.transform([procedure_data.get('cpt_code', 'UNKNOWN')])[0]
        hospital_encoded = self.hospital_encoder.transform([procedure_data.get('hospital_name', 'UNKNOWN')])[0]
        
        return [
            cpt_encoded,
            hospital_encoded,
            procedure_data.get('negotiated_rate_min', 0),
            procedure_data.get('medicare_rate', 0),
            procedure_data.get('medicaid_rate', 0),
            procedure_data.get('facility_fee', 0),
            procedure_data.get('professional_fee', 0)
        ]
    
    def _get_feature_importance(self, feature_names: List[str]) -> Dict[str, float]:
        """Get feature importance from the price predictor model"""
        if hasattr(self.price_predictor, 'feature_importances_'):
            importance_dict = {}
            for name, importance in zip(feature_names, self.price_predictor.feature_importances_):
                importance_dict[name] = float(importance)
            return importance_dict
        return {}
    
    def _save_model(self, filename: str, model):
        """Save a trained model"""
        filepath = os.path.join(self.models_dir, filename)
        joblib.dump(model, filepath)
        logger.info(f"Model saved to {filepath}")
    
    def _load_models(self):
        """Load trained models"""
        try:
            anomaly_path = os.path.join(self.models_dir, 'anomaly_detector.pkl')
            scaler_path = os.path.join(self.models_dir, 'scaler.pkl')
            predictor_path = os.path.join(self.models_dir, 'price_predictor.pkl')
            
            if os.path.exists(anomaly_path):
                self.anomaly_detector = joblib.load(anomaly_path)
            if os.path.exists(scaler_path):
                self.scaler = joblib.load(scaler_path)
            if os.path.exists(predictor_path):
                self.price_predictor = joblib.load(predictor_path)
                
            logger.info("Models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise

def train_models():
    """Train all ML models with current data"""
    try:
        # Get data from database
        db = SessionLocal()
        procedures = db.query(HospitalProcedure).all()
        db.close()
        
        if not procedures:
            logger.warning("No procedures found in database")
            return
        
        # Initialize analyzer
        analyzer = HealthcarePriceAnalyzer()
        
        # Train models
        anomaly_results = analyzer.train_anomaly_detector(procedures)
        prediction_results = analyzer.train_price_predictor(procedures)
        
        logger.info("Model training completed")
        logger.info(f"Anomaly detection: {anomaly_results}")
        logger.info(f"Price prediction: {prediction_results}")
        
    except Exception as e:
        logger.error(f"Error training models: {e}")

if __name__ == "__main__":
    train_models()
