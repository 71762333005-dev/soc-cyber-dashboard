"""
Prediction Module for Cyber Attack Detection
Handles loading model and making predictions
"""

import joblib
import pandas as pd
import json
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PREDICTIONS_LOG_FILE = "data/predictions_log.csv"


class AttackPredictor:
    """Main predictor class for cyber attack detection"""

    def __init__(self):
        self.model = None
        self.feature_names = []
        self.attack_mapping = {}
        self.reverse_mapping = {}
        self.model_loaded = False
        self.load_model()

    # ---------------- LOAD MODEL ---------------- #
    def load_model(self):
        try:
            model_path = "model/random_forest_model.joblib"

            if not os.path.exists(model_path):
                logger.warning("No trained model found. Run training first.")
                return False

            self.model = joblib.load(model_path)
            logger.info("Model loaded successfully")

            self._load_features()
            self._load_attack_mapping()

            self.model_loaded = True
            return True

        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False

    def _load_features(self):
        feature_path = "model/feature_names.json"

        if os.path.exists(feature_path):
            with open(feature_path, "r") as f:
                self.feature_names = json.load(f)

    def _load_attack_mapping(self):
        mapping_path = "model/attack_mapping.csv"

        if os.path.exists(mapping_path):
            df = pd.read_csv(mapping_path)

            self.attack_mapping = dict(zip(df["attack_id"], df["attack_name"]))
            self.reverse_mapping = dict(zip(df["attack_name"], df["attack_id"]))

    # ---------------- FEATURE ENGINEERING ---------------- #
    def preprocess_input(self, raw_data):
        df = pd.DataFrame(columns=self.feature_names)
        df.loc[0] = 0

        numeric_map = {
            "duration": "duration",
            "src_bytes": "src_bytes",
            "dst_bytes": "dst_bytes",
            "count": "count",
            "srv_count": "srv_count",
            "serror_rate": "serror_rate",
            "srv_serror_rate": "srv_serror_rate",
            "same_srv_rate": "same_srv_rate",
            "diff_srv_rate": "diff_srv_rate",
            "dst_host_count": "dst_host_count",
            "dst_host_srv_count": "dst_host_srv_count",
        }

        for raw_key, feature in numeric_map.items():
            if raw_key in raw_data and feature in self.feature_names:
                df[feature] = float(raw_data[raw_key])

        self._encode_categorical(df, raw_data)

        return df

    def _encode_categorical(self, df, raw_data):
        if "protocol_type" in raw_data:
            self._encode_one_hot(df, raw_data["protocol_type"], "protocol_type_")

        if "service" in raw_data:
            self._encode_one_hot(df, raw_data["service"], "service_")

        if "flag" in raw_data:
            self._encode_one_hot(df, raw_data["flag"], "flag_", upper=True)

    def _encode_one_hot(self, df, value, prefix, upper=False):
        val = value.upper() if upper else value.lower()

        for col in self.feature_names:
            if col.startswith(prefix):
                df[col] = 1 if col == f"{prefix}{val}" else 0

    # ---------------- PREDICTION ---------------- #
    def predict(self, input_data):
        if not self.model_loaded:
            return "Model not loaded", 0.0, "UNKNOWN"

        try:
            X = self.preprocess_input(input_data)
            X = X[self.feature_names]

            prediction_id, confidence = self._get_prediction(X)

            attack_type = self.attack_mapping.get(prediction_id, "unknown")
            risk_level = self._calculate_risk(attack_type, confidence)

            self.log_prediction(input_data, attack_type, confidence, risk_level)

            return attack_type, confidence, risk_level

        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return "error", 0.0, "UNKNOWN"

    def _get_prediction(self, x):
        """
        FIXED:
        - removed wrong variable X
        - fixed consistency
        """
        prediction = self.model.predict(x)[0]
        probabilities = self.model.predict_proba(x)[0]
        confidence = float(max(probabilities))

        return prediction, confidence

    def _calculate_risk(self, attack_type, confidence):
        if attack_type == "normal":
            return "LOW"

        if confidence > 0.85:
            return "CRITICAL" if attack_type in ["dos", "u2r"] else "HIGH"

        if confidence > 0.60:
            return "MEDIUM"

        return "LOW"

    # ---------------- LOGGING ---------------- #
    def log_prediction(self, input_data, attack_type, confidence, risk_level):
        try:
            os.makedirs("data", exist_ok=True)

            log_entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "src_ip": input_data.get("src_ip", "unknown"),
                "duration": input_data.get("duration", 0),
                "protocol": input_data.get("protocol_type", "unknown"),
                "service": input_data.get("service", "unknown"),
                "src_bytes": input_data.get("src_bytes", 0),
                "dst_bytes": input_data.get("dst_bytes", 0),
                "flag": input_data.get("flag", "unknown"),
                "attack_type": attack_type,
                "confidence": round(confidence, 3),
                "risk_level": risk_level,
            }

            log_df = pd.DataFrame([log_entry])

            if os.path.exists(PREDICTIONS_LOG_FILE):
                existing = pd.read_csv(PREDICTIONS_LOG_FILE)
                updated = pd.concat([existing, log_df], ignore_index=True)
                updated = updated.tail(1000)
                updated.to_csv(PREDICTIONS_LOG_FILE, index=False)
            else:
                log_df.to_csv(PREDICTIONS_LOG_FILE, index=False)

        except Exception as e:
            logger.error(f"Logging error: {e}")

    # ---------------- STATS ---------------- #
    def get_stats(self):
        try:
            if not os.path.exists(PREDICTIONS_LOG_FILE):
                return self._empty_stats()

            df = pd.read_csv(PREDICTIONS_LOG_FILE)

            total = len(df)
            attacks = len(df[df["attack_type"] != "normal"])
            critical = len(df[df["risk_level"] == "CRITICAL"])
            high = len(df[df["risk_level"] == "HIGH"])

            return {
                "total_predictions": total,
                "total_attacks": attacks,
                "critical_alerts": critical,
                "high_risk_alerts": high,
                "attack_rate": round(attacks / total * 100, 1) if total else 0,
            }

        except Exception as e:
            logger.error(f"Stats error: {e}")
            return self._empty_stats()

    def _empty_stats(self):
        return {
            "total_predictions": 0,
            "total_attacks": 0,
            "critical_alerts": 0,
            "high_risk_alerts": 0,
            "attack_rate": 0,
        }


# Global instance
predictor = AttackPredictor()
