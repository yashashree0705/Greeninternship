# utils.py
import os
import pandas as pd

# Central location for logs.csv
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "logs.csv")

def init_logs():
    """Create logs.csv if it doesn't exist"""
    if not os.path.exists(LOG_FILE):
        df_init = pd.DataFrame(columns=[
            "user_id", "date", "period",
            "fan_hours", "light_hours", "ac_hours", "charger_hours", "washing_cycles",
            "kwh", "tariff_rs_per_kwh", "cost_rs", "emission_factor_kg_per_kwh", "co2_kg"
        ])
        df_init.to_csv(LOG_FILE, index=False)
