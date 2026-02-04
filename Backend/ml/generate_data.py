import csv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "prescription_time.csv")

PER_MED_TIME = 60
FINAL_CHECK_TIME = 90

with open(CSV_PATH, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["medicine_count", "total_time_sec"])

    for meds in range(1, 31):
        total_time = meds * PER_MED_TIME + FINAL_CHECK_TIME
        writer.writerow([meds, total_time])

print("✅ prescription_time.csv generated")
