# pages/3_Tips_And_Recommendations.py
import streamlit as st
import pandas as pd
from utils import read_logs

st.set_page_config(page_title="Tips & Recommendations", layout="wide")

st.title("💡 Smart Energy Tips & Recommendations")

# -------------------------
# Load Logs
# -------------------------
df = read_logs()

if df is None or df.empty:
    st.warning("⚠ No data available. Please log entries first.")
    st.info("Meanwhile, here are some **general energy-saving tips**:")
    for tip in [
        "💡 Replace old bulbs with LED lights (up to 80% savings).",
        "🌬 Use natural ventilation instead of AC whenever possible.",
        "🔌 Turn off appliances completely instead of leaving them on standby.",
        "⏱ Use timers/smart plugs to automate turning off fans/lights.",
        "👕 Wash clothes in cold water to save heating energy."
    ]:
        st.write(tip)
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

# Ensure numeric
for col in ["fan_hours","light_hours","ac_hours","charger_hours","washing_cycles",
            "tariff_rs_per_kwh","emission_factor_kg_per_kwh"]:
    latest[col] = pd.to_numeric(latest.get(col, 0), errors="coerce") or 0

tariff = latest["tariff_rs_per_kwh"]
emission_factor = latest["emission_factor_kg_per_kwh"]

st.subheader(f"✨ Personalized Tips for **{selected_user}**")

# -------------------------
# Generate Personalized Tips
# -------------------------
tips = []

def add_tip(condition, title, description, saved, co2, color, icon):
    if condition:
        tips.append({
            "title": title,
            "description": description,
            "impact": f"💰 Save ~₹{saved:.1f}/month | 🌍 Cut {co2:.1f} kg CO₂",
            "color": color,
            "icon": icon
        })

# Fan
saved = (0.5 * 75 / 1000) * tariff * 30
co2 = (0.5 * 75 / 1000) * emission_factor * 30
add_tip(latest["fan_hours"] > 6, "Fan Overuse", "Try reducing fan usage by 30 min/day.", saved, co2, "#FFA726", "🌀")

# Light
saved = (1 * 40 / 1000) * tariff * 30
co2 = (1 * 40 / 1000) * emission_factor * 30
add_tip(latest["light_hours"] > 4, "Lights On Too Long", "Switch off lights 1h earlier or use LED bulbs.", saved, co2, "#29B6F6", "💡")

# AC
saved = (1 * 1500 / 1000) * tariff * 30
co2 = (1 * 1500 / 1000) * emission_factor * 30
add_tip(latest["ac_hours"] > 2, "AC Overuse", "Set AC to 26°C and reduce by 1h/day.", saved, co2, "#EF5350", "❄")

# Charger
saved = (1 * 5 / 1000) * tariff * 30
co2 = (1 * 5 / 1000) * emission_factor * 30
add_tip(latest["charger_hours"] > 2, "Chargers Plugged In", "Unplug chargers when not in use.", saved, co2, "#66BB6A", "🔌")

# Washing Machine
saved = (1 * 500 / 1000) * tariff * 4
co2 = (1 * 500 / 1000) * emission_factor * 4
add_tip(latest["washing_cycles"] > 1, "Frequent Washing", "Try reducing washing by 1 cycle/week.", saved, co2, "#AB47BC", "👕")

# -------------------------
# Display Tips in Boxes
# -------------------------
if tips:
    st.markdown("#### 🔎 Suggested Improvements")
    for tip in tips:
        st.markdown(
            f"""
            <div style="background-color:{tip['color']}20; padding:15px; border-radius:12px; margin-bottom:12px;">
                <h4>{tip['icon']} {tip['title']}</h4>
                <p>{tip['description']}</p>
                <b>{tip['impact']}</b>
            </div>
            """,
            unsafe_allow_html=True
        )
else:
    st.success("✅ Great job! Your usage is already efficient 🎉")

# -------------------------
# Gamification: Score
# -------------------------
st.subheader("🎯 Your Energy Efficiency Score")
score = max(0, 100 - int(latest["fan_hours"]*2 + latest["ac_hours"]*5 + latest["light_hours"]))
st.progress(score/100)
st.write(f"Your score: **{score}/100** (higher = better!)")

# -------------------------
# General Tips
# -------------------------
with st.expander("🌍 General Energy-Saving Tips"):
    general_tips = [
        "💡 Replace old bulbs with LED lights (up to 80% savings).",
        "🌬 Use natural ventilation instead of AC whenever possible.",
        "🔌 Turn off appliances completely instead of leaving them on standby.",
        "⏱ Use timers/smart plugs to automate turning off fans/lights.",
        "👕 Wash clothes in cold water to save heating energy."
    ]
    for tip in general_tips:
        st.write(tip)
