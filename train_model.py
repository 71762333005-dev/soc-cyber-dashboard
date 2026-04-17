"""
Model Training Script for Cyber Attack Detection
Trains a Random Forest classifier on NSL-KDD dataset
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)
from sklearn.preprocessing import LabelEncoder
import json
import os
from datetime import datetime
import joblib


# ---------------- LOAD DATA ---------------- #
def load_and_preprocess_data():
    print("📊 Loading dataset...")

    if not os.path.exists("dataset/nsl_kdd.csv"):
        print("❌ Dataset not found!")
        return None

    column_names = [
        "duration", "protocol_type", "service", "flag",
        "src_bytes", "dst_bytes", "land", "wrong_fragment", "urgent",
        "hot", "num_failed_logins", "logged_in", "num_compromised",
        "root_shell", "su_attempted", "num_root", "num_file_creations",
        "num_shells", "num_access_files", "num_outbound_cmds",
        "is_host_login", "is_guest_login", "count", "srv_count",
        "serror_rate", "srv_serror_rate", "rerror_rate", "srv_rerror_rate",
        "same_srv_rate", "diff_srv_rate", "srv_diff_host_rate",
        "dst_host_count", "dst_host_srv_count",
        "dst_host_same_srv_rate", "dst_host_diff_srv_rate",
        "dst_host_same_src_port_rate", "dst_host_srv_diff_host_rate",
        "dst_host_serror_rate", "dst_host_srv_serror_rate",
        "dst_host_rerror_rate", "dst_host_srv_rerror_rate",
        "attack_type", "difficulty",
    ]

    df = pd.read_csv("dataset/nsl_kdd.csv", names=column_names)
    print(f"✅ Dataset loaded: {df.shape}")
    return df


# ---------------- FEATURE ENGINEERING ---------------- #
def engineer_features(df):
    print("🔧 Engineering features...")

    selected_features = [
        "duration", "protocol_type", "service", "flag",
        "src_bytes", "dst_bytes", "count", "srv_count",
        "serror_rate", "srv_serror_rate", "same_srv_rate",
        "diff_srv_rate", "dst_host_count", "dst_host_srv_count",
    ]

    categorical_features = ["protocol_type", "service", "flag"]

    x = pd.get_dummies(df[selected_features], columns=categorical_features)
    y = df["attack_type"]

    def simplify_attack(a):
        a = str(a).lower()

        if a == "normal":
            return "normal"
        elif a in ["neptune", "smurf", "pod", "teardrop", "back", "land"]:
            return "dos"
        elif a in ["satan", "ipsweep", "nmap", "portsweep"]:
            return "probe"
        elif a in ["guess_passwd", "ftp_write", "imap", "phf", "warezmaster"]:
            return "r2l"
        elif a in ["buffer_overflow", "rootkit", "perl"]:
            return "u2r"
        else:
            return "unknown"

    y = y.apply(simplify_attack)

    mask = y != "unknown"
    x = x[mask]
    y = y[mask]

    print(f"✅ Features: {x.shape[1]}")
    print(f"✅ Classes:\n{y.value_counts()}")

    return x, y


# ---------------- TRAIN MODEL ---------------- #
def train_model(x, y):
    print("🤖 Training model...")

    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)

    feature_names = x.columns.tolist()

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y_encoded,
        test_size=0.2,
        random_state=42,
        stratify=y_encoded,
    )

    model = RandomForestClassifier(
        n_estimators=50,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )

    model.fit(x_train, y_train)

    y_pred = model.predict(x_test)

    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, average="weighted", zero_division=0),
        "recall": recall_score(y_test, y_pred, average="weighted", zero_division=0),
        "f1_score": f1_score(y_test, y_pred, average="weighted", zero_division=0),
        "timestamp": datetime.now().isoformat(),
    }

    print("✅ Training complete")
    print(metrics)

    return model, label_encoder, metrics, feature_names


# ---------------- SAVE ARTIFACTS ---------------- #
def save_model_artifacts(model, label_encoder, metrics, feature_names):
    print("💾 Saving artifacts...")

    os.makedirs("model", exist_ok=True)

    joblib.dump(model, "model/random_forest_model.joblib")

    attack_mapping = pd.DataFrame({
        "attack_id": range(len(label_encoder.classes_)),
        "attack_name": label_encoder.classes_,
    })
    attack_mapping.to_csv("model/attack_mapping.csv", index=False)

    with open("model/feature_names.json", "w") as f:
        json.dump(feature_names, f, indent=2)

    config = {
        "model_type": "RandomForestClassifier",
        "accuracy": metrics["accuracy"],
        "f1_score": metrics["f1_score"],
        "features": len(feature_names),
    }

    with open("model/model_config.json", "w") as f:
        json.dump(config, f, indent=2)

    pd.DataFrame([metrics]).to_csv("model/training_history.csv", index=False)

    print("✅ Saved successfully")


# ---------------- MAIN ---------------- #
def main():
    print("=" * 50)
    print("🚀 TRAINING STARTED")
    print("=" * 50)

    df = load_and_preprocess_data()
    if df is None:
        return

    x, y = engineer_features(df)

    model, label_encoder, metrics, feature_names = train_model(x, y)

    save_model_artifacts(model, label_encoder, metrics, feature_names)

    print("=" * 50)
    print("✅ TRAINING COMPLETE")
    print("=" * 50)


if __name__ == "__main__":
    main()
