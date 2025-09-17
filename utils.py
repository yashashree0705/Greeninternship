# utils.py
import os
import pandas as pd
import tempfile

LOG_FILE = os.path.join(tempfile.gettempdir(), "logs.csv")

HEADERS = [
    "user_id","date","period",
    "fan_hours","light_hours","ac_hours","charger_hours","washing_cycles",
    "kwh","tariff_rs_per_kwh","cost_rs","emission_factor_kg_per_kwh","co2_kg"
]

def init_logs():
    if not os.path.exists(LOG_FILE) or os.path.getsize(LOG_FILE) == 0:
        df_init = pd.DataFrame(columns=HEADERS)
        df_init.to_csv(LOG_FILE, index=False)

def read_logs():
    init_logs()
    try:
        return pd.read_csv(LOG_FILE)
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=HEADERS)

def append_log(row: dict):
    df = read_logs()
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(LOG_FILE, index=False)
