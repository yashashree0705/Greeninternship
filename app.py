# app.py
import streamlit as st
import pandas as pd
import os
from datetime import datetime
import matplotlib.pyplot as plt

# -------------------------
# Configuration / defaults
# -------------------------
#DATA_PATH = "data"
#LOG_FILE = os.path.join(DATA_PATH, "logs.csv")
import tempfile
LOG_FILE = os.path.join(tempfile.gettempdir(), "logs.csv")

DEFAULT_WATTAGES = {
    "fan": 75,        # watts
    "light": 40,      # watts (tube/led)
    "ac": 1500,       # watts (1.5 ton typical)
    "charger": 5,     # watts
    "washing_machine": 500  # watts per cycle (approx average energy per cycle handled specially)
}

DEFAULT_TARIFF = 7.0            # Rs per kWh
DEFAULT_EMISSION = 0.82         # kg CO2 per kWh

# Ensure data folder exists
#os.makedirs(DATA_PATH, exist_ok=True)

# Initialize log file if doesn't exist
if not os.path.exists(LOG_FILE):
    df_init = pd.DataFrame(columns=[
        "user_id", "date", "period",
        "fan_hours", "light_hours", "ac_hours", "charger_hours", "washing_cycles",
        "kwh", "tariff_rs_per_kwh", "cost_rs", "emission_factor_kg_per_kwh", "co2_kg"
    ])
    df_init.to_csv(LOG_FILE, index=False)

# -------------------------
# Helper functions
# -------------------------
def hours_to_kwh(watt, hours):
    """Convert watt * hours to kWh"""
    return (watt * hours) / 1000.0

def washing_cycles_to_kwh(per_cycle_watt, cycles):
    """If washing machine watt is specified as 'per cycle energy in Wh', convert accordingly.
       Here we assume `per_cycle_watt` is a watt-equivalent assumed running for 1 hour.
       For simplicity, treat washing machine as per-cycle fixed kWh: (per_cycle_watt*1h)/1000 * cycles."""
    return (per_cycle_watt * 1.0 / 1000.0) * cycles

def append_log(row: dict):
    df = pd.read_csv(LOG_FILE)
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(LOG_FILE, index=False)

def load_logs():
    return pd.read_csv(LOG_FILE)

# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(page_title="Energy Savings Habit Tracker", layout="wide")

st.title("Energy Savings Habit Tracker")
st.markdown("Log daily appliance usage, see estimated energy (kWh), cost (₹), and CO₂ (kg). Save and analyze entries.")

# Sidebar settings
st.sidebar.header("App Settings")
tariff = st.sidebar.number_input("Tariff (Rs per kWh)", value=DEFAULT_TARIFF, min_value=0.0, step=0.5, format="%.2f")
emission_factor = st.sidebar.number_input("Emission factor (kg CO₂ per kWh)", value=DEFAULT_EMISSION, min_value=0.0, step=0.01, format="%.3f")
st.sidebar.markdown("**Default appliance wattages (W)** — edit if you want:")
w_fan = st.sidebar.number_input("Fan (W)", value=DEFAULT_WATTAGES["fan"], step=1)
w_light = st.sidebar.number_input("Light (W)", value=DEFAULT_WATTAGES["light"], step=1)
w_ac = st.sidebar.number_input("AC (W)", value=DEFAULT_WATTAGES["ac"], step=10)
w_charger = st.sidebar.number_input("Charger (W)", value=DEFAULT_WATTAGES["charger"], step=1)
w_washing = st.sidebar.number_input("Washing machine (W per cycle-equivalent)", value=DEFAULT_WATTAGES["washing_machine"], step=10)

# Input form
st.header("Log a new entry")
with st.form("log_form", clear_on_submit=False):
    col1, col2, col3 = st.columns(3)
    with col1:
        user_id = st.text_input("User ID (e.g., User01)", value="User01")
        date_input = st.date_input("Date", value=datetime.today().date())
    with col2:
        period = st.selectbox("Period (label)", options=["baseline", "post", "daily", "weekly"], index=2)
        st.write("")  # spacing
    with col3:
        st.write("")

    st.subheader("Appliance usage (hours)")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        fan_hours = st.number_input("Fan hours", min_value=0.0, value=4.0, step=0.5)
    with c2:
        light_hours = st.number_input("Light hours", min_value=0.0, value=4.0, step=0.5)
    with c3:
        ac_hours = st.number_input("AC hours", min_value=0.0, value=2.0, step=0.5)
    with c4:
        charger_hours = st.number_input("Charger hours", min_value=0.0, value=2.0, step=0.5)
    with c5:
        washing_cycles = st.number_input("Washing cycles (per day)", min_value=0, value=0, step=1, format="%d")

    submitted = st.form_submit_button("Calculate & Save")

if submitted:
    # Calculate kWh per appliance
    kwh_fan = hours_to_kwh(w_fan, fan_hours)
    kwh_light = hours_to_kwh(w_light, light_hours)
    kwh_ac = hours_to_kwh(w_ac, ac_hours)
    kwh_charger = hours_to_kwh(w_charger, charger_hours)
    kwh_washing = washing_cycles_to_kwh(w_washing, washing_cycles)

    total_kwh = round(kwh_fan + kwh_light + kwh_ac + kwh_charger + kwh_washing, 3)
    cost_rs = round(total_kwh * tariff, 2)
    co2_kg = round(total_kwh * emission_factor, 3)

    st.success("Entry calculated!")
    st.metric("Total kWh", f"{total_kwh} kWh")
    st.metric("Estimated cost (Rs)", f"₹ {cost_rs}")
    st.metric("Estimated CO₂ (kg)", f"{co2_kg} kg")

    # Show breakdown
    st.subheader("Breakdown (kWh)")
    breakdown = pd.DataFrame({
        "appliance": ["fan", "light", "ac", "charger", "washing_machine"],
        "kwh": [round(kwh_fan,3), round(kwh_light,3), round(kwh_ac,3), round(kwh_charger,3), round(kwh_washing,3)]
    })
    st.table(breakdown.set_index("appliance"))

    # Save to CSV
    row = {
        "user_id": user_id,
        "date": pd.to_datetime(date_input).strftime("%Y-%m-%d"),
        "period": period,
        "fan_hours": fan_hours,
        "light_hours": light_hours,
        "ac_hours": ac_hours,
        "charger_hours": charger_hours,
        "washing_cycles": int(washing_cycles),
        "kwh": total_kwh,
        "tariff_rs_per_kwh": tariff,
        "cost_rs": cost_rs,
        "emission_factor_kg_per_kwh": emission_factor,
        "co2_kg": co2_kg
    }
    append_log(row)
    st.info(f"Saved to {LOG_FILE}")

# -------------------------
# Data display & analysis
# -------------------------
st.header("Logged entries & Analysis")
df_logs = load_logs()
if df_logs.empty:
    st.warning("No logs yet. Add an entry above.")
else:
    st.markdown("**Recent entries**")
    st.dataframe(df_logs.sort_values("date", ascending=False).reset_index(drop=True))

    st.subheader("Aggregate summary")
    agg = df_logs.groupby("user_id").agg({
        "kwh": ["mean", "sum", "count"],
        "cost_rs": "sum",
        "co2_kg": "sum"
    })
    agg.columns = ["_".join(col).strip() for col in agg.columns.values]
    st.table(agg.reset_index())

    st.subheader("Charts")
    # kWh over time per user (line)
    st.markdown("**Energy (kWh) over time**")
    users = df_logs["user_id"].unique().tolist()
    sel_user = st.selectbox("Select user for time series chart (or All)", options=["All"] + users, index=0)

    plot_df = df_logs.copy()
    plot_df["date"] = pd.to_datetime(plot_df["date"])

    if sel_user != "All":
        plot_df = plot_df[plot_df["user_id"] == sel_user]

    fig, ax = plt.subplots()
    for uid, g in plot_df.groupby("user_id"):
        g_sorted = g.sort_values("date")
        ax.plot(g_sorted["date"], g_sorted["kwh"], marker='o', label=uid)
    ax.set_xlabel("Date")
    ax.set_ylabel("kWh")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    st.markdown("**Average appliance-wise kWh across all logs**")
    # compute appliance-wise kWh using reverse calculation from hours and wattages.
    # We'll compute a simple avg by re-calculating per-row with the current wattages.
    rew = df_logs.copy()
    rew["kwh_fan_calc"] = (w_fan * rew["fan_hours"]) / 1000.0
    rew["kwh_light_calc"] = (w_light * rew["light_hours"]) / 1000.0
    rew["kwh_ac_calc"] = (w_ac * rew["ac_hours"]) / 1000.0
    rew["kwh_charger_calc"] = (w_charger * rew["charger_hours"]) / 1000.0
    rew["kwh_washing_calc"] = (w_washing * 1.0 / 1000.0) * rew["washing_cycles"]

    app_avg = pd.DataFrame({
        "appliance": ["fan", "light", "ac", "charger", "washing_machine"],
        "avg_kwh": [
            round(rew["kwh_fan_calc"].mean(), 3),
            round(rew["kwh_light_calc"].mean(), 3),
            round(rew["kwh_ac_calc"].mean(), 3),
            round(rew["kwh_charger_calc"].mean(), 3),
            round(rew["kwh_washing_calc"].mean(), 3)
        ]
    })
    st.bar_chart(app_avg.set_index("appliance"))

    st.markdown("**Download full logs**")
    csv = df_logs.to_csv(index=False).encode('utf-8')
    st.download_button("Download logs as CSV", data=csv, file_name="energy_logs.csv", mime="text/csv")


