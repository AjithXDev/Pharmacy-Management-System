import pickle
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")

_model = None

def get_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise Exception("❌ ML model not found. Train model first.")
        with open(MODEL_PATH, "rb") as f:
            _model = pickle.load(f)
    return _model


def predict_prescription_time(medicine_count):
    model = get_model()
    X = pd.DataFrame([[medicine_count]], columns=["medicine_count"])
    return int(model.predict(X)[0])
