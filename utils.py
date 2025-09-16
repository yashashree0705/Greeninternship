import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "logs.csv")

def init_logs():
    """Create logs.csv with headers if it doesn't exist or is empty"""
    if not os.path.exists(LOG_FILE) or os.path.getsize(LOG_FILE) == 0:
        df_init = pd.DataFrame(columns=[
            "user_id", "date", "period",
            "fan_hours", "light_hours", "ac_hours", "charger_hours", "washing_cycles",
            "kwh", "tariff_rs_per_kwh", "cost_rs", "emission_factor_kg_per_kwh", "co2_kg"
        ])
        df_init.to_csv(LOG_FILE, index=False)
