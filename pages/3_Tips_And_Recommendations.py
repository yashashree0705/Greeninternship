# pages/3_Tips_And_Recommendations.py

import streamlit as st
import pandas as pd

LOG_FILE = os.path.join(tempfile.gettempdir(), "logs.csv")

@st.cache_data
def load_logs():
    try:
        df = pd.read_csv(LOG_FILE)
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        return df
    except Exception:
        return pd.DataFrame()

df = load_logs()

@st.cache_data
def load_logs():
    try:
        df = pd.read_csv(LOG_FILE)
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        return df
    except Exception as e:
        st.error(f"Error loading logs: {e}")
        return pd.DataFrame()

df = load_logs()

st.title("Tips & Recommendations")

if df.empty:
    st.warning("No data available. Please log entries first.")
    st.stop()

# -------------------------
# User Selection
# -------------------------
users = df["user_id"].unique().tolist()
selected_user = st.selectbox("Select User", users)

user_df = df[df["user_id"] == selected_user].sort_values("date")
latest = user_df.iloc[-1]

st.subheader(f"Personalized Tips for {selected_user}")

# -------------------------
# Appliance-Based Suggestions
# -------------------------
st.markdown("### Appliance Usage Review")

tariff = latest["tariff_rs_per_kwh"]
emission_factor = latest["emission_factor_kg_per_kwh"]

tips = []

# Fan
if latest["fan_hours"] > 6:
    saved = (0.5 * 75 / 1000) * tariff * 30  # 0.5h/day for 30 days
    co2 = (0.5 * 75 / 1000) * emission_factor * 30
    tips.append(f"Reduce **fan usage by 30 min/day** → Save ~₹{saved:.1f}/month & cut {co2:.1f} kg CO₂.")

# Light
if latest["light_hours"] > 4:
    saved = (1 * 40 / 1000) * tariff * 30
    co2 = (1 * 40 / 1000) * emission_factor * 30
    tips.append(f"Switch off lights 1h earlier → Save ~₹{saved:.1f}/month & cut {co2:.1f} kg CO₂.")

# AC
if latest["ac_hours"] > 2:
    saved = (1 * 1500 / 1000) * tariff * 30
    co2 = (1 * 1500 / 1000) * emission_factor * 30
    tips.append(f"❄Reduce AC by 1h/day → Save ~₹{saved:.1f}/month & cut {co2:.1f} kg CO₂.")

# Charger
if latest["charger_hours"] > 2:
    saved = (1 * 5 / 1000) * tariff * 30
    co2 = (1 * 5 / 1000) * emission_factor * 30
    tips.append(f"Unplug charger when not in use → Save ~₹{saved:.1f}/month & cut {co2:.1f} kg CO₂.")

# Washing Machine
if latest["washing_cycles"] > 1:
    saved = (1 * 500 / 1000) * tariff * 4  # one cycle/week less
    co2 = (1 * 500 / 1000) * emission_factor * 4
    tips.append(f"Reduce washing by 1 cycle/week → Save ~₹{saved:.1f}/month & cut {co2:.1f} kg CO₂.")

# -------------------------
# Display Tips
# -------------------------
if tips:
    for tip in tips:
        st.success(tip)
else:
    st.info("Your usage looks efficient! Keep it up.")

# -------------------------
# General Recommendations
# -------------------------
st.markdown("### General Energy-Saving Tips")
general_tips = [
    "Replace old bulbs with LED lights (up to 80% savings).",
    "🌬Use natural ventilation instead of AC whenever possible.",
    "Turn off appliances completely instead of leaving them on standby.",
    "Use timers/smart plugs to automate turning off fans/lights.",
    "Wash clothes in cold water to save heating energy."
]

for tip in general_tips:
    st.write(tip)
