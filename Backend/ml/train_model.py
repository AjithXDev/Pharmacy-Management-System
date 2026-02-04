import pandas as pd
from sklearn.linear_model import LinearRegression
import pickle
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "prescription_time.csv")
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")

df = pd.read_csv(CSV_PATH)

X = df[["medicine_count"]]
y = df["total_time_sec"]

model = LinearRegression()
model.fit(X, y)

with open(MODEL_PATH, "wb") as f:
    pickle.dump(model, f)

print("✅ ML model trained and saved as model.pkl")
