import os
import pandas as pd

# Safe for multi-page Streamlit apps: CSV will always be in the project root
PROJECT_ROOT = os.getcwd()  # folder where Streamlit was launched
LOG_FILE = os.path.join(PROJECT_ROOT, "logs.csv")

def init_logs():
    """
    Ensure logs.csv exists and has headers.
    If missing or empty, create with predefined columns.
    """
    headers = [
        "user_id", "date", "period",
        "fan_hours", "light_hours", "ac_hours", "charger_hours", "washing_cycles",
        "kwh", "tariff_rs_per_kwh", "cost_rs", "emission_factor_kg_per_kwh", "co2_kg"
    ]
    
    # Create file if it doesn't exist or is empty
    if not os.path.exists(LOG_FILE) or os.path.getsize(LOG_FILE) == 0:
        df_init = pd.DataFrame(columns=headers)
        df_init.to_csv(LOG_FILE, index=False)

def read_logs():
    """
    Safely read logs.csv into a DataFrame.
    Handles empty files.
    """
    init_logs()  # ensure file exists with headers
    
    try:
        df = pd.read_csv(LOG_FILE)
    except pd.errors.EmptyDataError:
        # fallback if file exists but is empty
        df = pd.DataFrame(columns=[
            "user_id", "date", "period",
            "fan_hours", "light_hours", "ac_hours", "charger_hours", "washing_cycles",
            "kwh", "tariff_rs_per_kwh", "cost_rs", "emission_factor_kg_per_kwh", "co2_kg"
        ])
    return df
