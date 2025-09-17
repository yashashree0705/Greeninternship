# pages/3_Tips_And_Recommendations.py
import streamlit as st
import pandas as pd
from utils import read_logs

st.title("💡 Tips & Recommendations")

# -------------------------
# Load Logs Safely
# -------------------------
df = read_logs()

if df is None or df.empty:
    st.warning("⚠ No data available. Please log entries first.")
    st.markdown("### General Energy-Saving Tips")
    general_tips = [
        "💡 Replace old bulbs with LED lights (up to 80% savings).",
        "🌬 Use natural ventilation instead of AC whenever possible.",
        "🔌 Turn off appliances completely instead of leaving them on standby.",
        "⏱ Use timers/smart plugs to automate turning off fans/lights.",
        "👕 Wash clothes in cold water to save heating energy."
    ]
    for tip in general_tips:
        st.info(tip)
    st.stop()

# -------------------------
# User Selection
# -------------------------
users = df["user_id"].dropna().unique().tolist()
selected_user = st.selectbox("👤 Select User", users)

user_df = df[df["user_id"] == selected_user].sort_values("date")
if user_df.empty:
    st.warning(f"No records found for {selected_user}.")
    st.stop()

latest = user_df.iloc[-1].copy()

# Ensure numeric types
for col in ["fan_hours","light_hours","ac_hours","charger_hours","washing_cycles",
            "tariff_rs_per_kwh","emission_factor_kg_per_kwh"]:
    latest[col] = pd.to_numeric(latest.get(col, 0), errors="coerce") or 0

st.subheader(f"✨ Personalized Tips for **{selected_user}**")

# -------------------------
# Interactive Suggestions
# -------------------------
with st.expander("📊 Appliance Usage Analysis", expanded=True):
    tariff = latest["tariff_rs_per_kwh"]
    emission_factor = latest["emission_factor_kg_per_kwh"]
    tips = []

    # Fan
    if latest["fan_hours"] > 6:
        saved = (0.5 * 75 / 1000) * tariff * 30
        co2 = (0.5 * 75 / 1000) * emission_factor * 30
        tips.append(f"🌀 Reduce **fan usage by 30 min/day** → Save ~₹{saved:.1f}/month & cut {co2:.1f} kg CO₂.")

    # Light
    if latest["light_hours"] > 4:
        saved = (1 * 40 / 1000) * tariff * 30
        co2 = (1 * 40 / 1000) * emission_factor * 30
        tips.append(f"💡 Switch off lights 1h earlier → Save ~₹{saved:.1f}/month & cut {co2:.1f} kg CO₂.")

    # AC
    if latest["ac_hours"] > 2:
        saved = (1 * 1500 / 1000) * tariff * 30
        co2 = (1 * 1500 / 1000) * emission_factor * 30
        tips.append(f"❄ Reduce AC by 1h/day → Save ~₹{saved:.1f}/month & cut {co2:.1f} kg CO₂.")

    # Charger
    if latest["charger_hours"] > 2:
        saved = (1 * 5 / 1000) * tariff * 30
        co2 = (1 * 5 / 1000) * emission_factor * 30
        tips.append(f"🔌 Unplug charger → Save ~₹{saved:.1f}/month & cut {co2:.1f} kg CO₂.")

    # Washing Machine
    if latest["washing_cycles"] > 1:
        saved = (1 * 500 / 1000) * tariff * 4
        co2 = (1 * 500 / 1000) * emission_factor * 4
        tips.append(f"👕 Reduce washing by 1 cycle/week → Save ~₹{saved:.1f}/month & cut {co2:.1f} kg CO₂.")

    if tips:
        for tip in tips:
            st.success(tip)
    else:
        st.info("✅ Your usage looks efficient! Keep it up.")

# -------------------------
# Progress Feedback
# -------------------------
st.markdown("### 📈 Your Usage Compared to Suggested Limits")

limits = {"fan_hours": 6, "light_hours": 4, "ac_hours": 2, "charger_hours": 2, "washing_cycles": 1}
for appliance, limit in limits.items():
    value = latest.get(appliance, 0)
    pct = min(int((value / (limit + 0.1)) * 100), 200)
    st.progress(min(pct, 100), text=f"{appliance.replace('_',' ').title()}: {value} (Limit: {limit})")

# -------------------------
# General Recommendations
# -------------------------
st.markdown("### 🌍 General Energy-Saving Tips")
general_tips = [
    "💡 Replace old bulbs with LED lights (up to 80% savings).",
    "🌬 Use natural ventilation instead of AC whenever possible.",
    "🔌 Turn off appliances completely instead of leaving them on standby.",
    "⏱ Use timers/smart plugs to automate turning off fans/lights.",
    "👕 Wash clothes in cold water to save heating energy."
]
for tip in general_tips:
    st.write(tip)
