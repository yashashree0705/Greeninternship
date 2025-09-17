# pages/3_Tips_And_Recommendations.py
import streamlit as st
import pandas as pd
from utils import read_logs   # ✅ centralized log reading

st.title("Tips & Recommendations")

# -------------------------
# Load Logs Safely
# -------------------------
df = read_logs()

if df is None or df.empty:
    st.warning("No data available. Please log entries first.")
    st.markdown("### General Energy-Saving Tips")
    general_tips = [
        "Replace old bulbs with LED lights (up to 80% savings).",
        "🌬 Use natural ventilation instead of AC whenever possible.",
        "Turn off appliances completely instead of leaving them on standby.",
        "Use timers/smart plugs to automate turning off fans/lights.",
        "Wash clothes in cold water to save heating energy."
    ]
    for tip in general_tips:
        st.write(tip)
    st.stop()

# -------------------------
# User Selection
# -------------------------
if "user_id" not in df.columns:
    st.error("Logs file is missing the `user_id` column.")
    st.stop()

users = df["user_id"].dropna().unique().tolist()

if not users:
    st.warning("No users found in logs. Please add entries first.")
    st.stop()

selected_user = st.selectbox("Select User", users)

user_df = df[df["user_id"] == selected_user].sort_values("date")
if user_df.empty:
    st.warning(f"No records found for {selected_user}.")
    st.stop()

latest = user_df.iloc[-1]

st.subheader(f"Personalized Tips for {selected_user}")

# -------------------------
# Appliance-Based Suggestions
# -------------------------
st.markdown("### Appliance Usage Review")

tariff = latest.get("tariff_rs_per_kwh", 0)
emission_factor = latest.get("emission_factor_kg_per_kwh", 0)

tips = []

# Fan
if latest.get("fan_hours", 0) > 6:
    saved = (0.5 * 75 / 1000) * tariff * 30
    co2 = (0.5 * 75 / 1000) * emission_factor * 30
    tips.append(f"Reduce **fan usage by 30 min/day** → Save ~₹{saved:.1f}/month & cut {co2:.1f} kg CO₂.")

# Light
if latest.get("light_hours", 0) > 4:
    saved = (1 * 40 / 1000) * tariff * 30
    co2 = (1 * 40 / 1000) * emission_factor * 30
    tips.append(f"Switch off lights 1h earlier → Save ~₹{saved:.1f}/month & cut {co2:.1f} kg CO₂.")

# AC
if latest.get("ac_hours", 0) > 2:
    saved = (1 * 1500 / 1000) * tariff * 30
    co2 = (1 * 1500 / 1000) * emission_factor * 30
    tips.append(f"❄ Reduce AC by 1h/day → Save ~₹{saved:.1f}/month & cut {co2:.1f} kg CO₂.")

# Charger
if latest.get("charger_hours", 0) > 2:
    saved = (1 * 5 / 1000) * tariff * 30
    co2 = (1 * 5 / 1000) * emission_factor * 30
    tips.append(f"Unplug charger when not in use → Save ~₹{saved:.1f}/month & cut {co2:.1f} kg CO₂.")

# Washing Machine
if latest.get("washing_cycles", 0) > 1:
    saved = (1 * 500 / 1000) * tariff * 4
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
    "🌬 Use natural ventilation instead of AC whenever possible.",
    "Turn off appliances completely instead of leaving them on standby.",
    "Use timers/smart plugs to automate turning off fans/lights.",
    "Wash clothes in cold water to save heating energy."
]

for tip in general_tips:
    st.write(tip)
