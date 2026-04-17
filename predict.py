"""
Prediction Module for Cyber Attack Detection
Handles loading model and making predictions
"""

import joblib
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ FIX: constant for Sonar duplication issue
PREDICTIONS_LOG_FILE = "data/predictions_log.csv"


class AttackPredictor:

    def __init__(self):
        self.model = None
        self.feature_names = []
        self.attack_mapping = {}
        self.reverse_mapping = {}
        self.model_loaded = False
        self.load_model()

    # ---------------- MODEL ----------------
    def load_model(self):
        try:
            model_path = "model/random_forest_model.joblib"

            if not os.path.exists(model_path):
                logger.warning("Model not found")
                return False

            self.model = joblib.load(model_path)

            if os.path.exists("model/feature_names.json"):
                with open("model/feature_names.json") as f:
                    self.feature_names = json.load(f)

            if os.path.exists("model/attack_mapping.csv"):
                df = pd.read_csv("model/attack_mapping.csv")
                self.attack_mapping = dict(zip(df["attack_id"], df["attack_name"]))
                self.reverse_mapping = dict(zip(df["attack_name"], df["attack_id"]))

            self.model_loaded = True
            return True

        except Exception as e:
            logger.error(f"Model load error: {e}")
            return False

    # ---------------- MAIN PREPROCESS ----------------
    def preprocess_input(self, raw_data):
        df = pd.DataFrame(columns=self.feature_names)
        df.loc[0] = 0

        df = self._numeric_features(raw_data, df)
        df = self._categorical_features(raw_data, df)

        return df

    # ---------------- NUMERIC ----------------
    def _numeric_features(self, raw, df):
        mapping = {
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

        for k, v in mapping.items():
            if k in raw and v in self.feature_names:
                df[v] = float(raw[k])

        return df

    # ---------------- CATEGORICAL ----------------
    def _categorical_features(self, raw, df):
        if "protocol_type" in raw:
            self._encode(df, "protocol_type", raw["protocol_type"].lower())

        if "service" in raw:
            self._encode(df, "service", raw["service"].lower())

        if "flag" in raw:
            self._encode(df, "flag", raw["flag"].upper())

        return df

    def _encode(self, df, prefix, value):
        for col in self.feature_names:
            if col.startswith(prefix + "_"):
                df[col] = 1 if col == f"{prefix}_{value}" else 0

    # ---------------- PREDICTION ----------------
    def predict(self, input_data):
        if not self.model_loaded:
            return "Model not loaded", 0.0, "UNKNOWN"

        try:
            X = self.preprocess_input(input_data)[self.feature_names]

            pred = self.model.predict(X)[0]
            probs = self.model.predict_proba(X)[0]
            conf = float(max(probs))

            attack = self.attack_mapping.get(pred, "unknown")

            risk = self._risk_level(attack, conf)

            self.log_prediction(input_data, attack, conf, risk)

            return attack, conf, risk

        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return "error", 0.0, "UNKNOWN"

    # ---------------- RISK LOGIC ----------------
    def _risk_level(self, attack_type, confidence):
        if attack_type == "normal":
            return "LOW"
        if confidence > 0.85:
            return "CRITICAL" if attack_type in ["dos", "u2r"] else "HIGH"
        if confidence > 0.60:
            return "MEDIUM"
        return "LOW"

    # ---------------- LOGGING ----------------
    def log_prediction(self, input_data, attack, confidence, risk):
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
                "attack_type": attack,
                "confidence": round(confidence, 3),
                "risk_level": risk,
            }

            df = pd.DataFrame([log_entry])

            if os.path.exists(PREDICTIONS_LOG_FILE):
                old = pd.read_csv(PREDICTIONS_LOG_FILE)
                df = pd.concat([old, df], ignore_index=True)

                if len(df) > 1000:
                    df = df.tail(1000)

            df.to_csv(PREDICTIONS_LOG_FILE, index=False)

        except Exception as e:
            logger.error(f"Logging error: {e}")

    # ---------------- STATS ----------------
    def get_stats(self):
        try:
            if not os.path.exists(PREDICTIONS_LOG_FILE):
                return {
                    "total_predictions": 0,
                    "total_attacks": 0,
                    "critical_alerts": 0,
                    "high_risk_alerts": 0,
                    "attack_rate": 0,
                }

            df = pd.read_csv(PREDICTIONS_LOG_FILE)

            total = len(df)
            attacks = len(df[df["attack_type"] != "normal"])

            return {
                "total_predictions": total,
                "total_attacks": attacks,
                "critical_alerts": len(df[df["risk_level"] == "CRITICAL"]),
                "high_risk_alerts": len(df[df["risk_level"] == "HIGH"]),
                "attack_rate": round(attacks / total * 100, 1) if total else 0,
            }

        except Exception as e:
            logger.error(f"Stats error: {e}")
            return {}
        

# Global instance
predictor = AttackPredictor()
