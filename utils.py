import os
import pandas as pd

# Streamlit CWD is usually the folder you run the app from
PROJECT_ROOT = os.getcwd()  # safest way in multi-page Streamlit apps

DATA_DIR = os.path.join(PROJECT_ROOT, "data")
os.makedirs(DATA_DIR, exist_ok=True)

LOG_FILE = os.path.join(DATA_DIR, "logs.csv")

def init_logs():
    """Create logs.csv with headers if missing or empty"""
    if not os.path.exists(LOG_FILE) or os.path.getsize(LOG_FILE) == 0:
        df_init = pd.DataFrame(columns=[
            "user_id", "date", "period",
            "fan_hours", "light_hours", "ac_hours", "charger_hours", "washing_cycles",
            "kwh", "tariff_rs_per_kwh", "cost_rs", "emission_factor_kg_per_kwh", "co2_kg"
        ])
        df_init.to_csv(LOG_FILE, index=False)
