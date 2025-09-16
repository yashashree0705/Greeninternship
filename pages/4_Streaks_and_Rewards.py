# pages/4_Streaks_and_Rewards.py

import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

import os

LOG_FILE = "logs.csv"

# If logs.csv doesn't exist, create it with correct headers
if not os.path.exists(LOG_FILE):
    import pandas as pd
    df_init = pd.DataFrame(columns=[
        "user_id", "date", "period",
        "fan_hours", "light_hours", "ac_hours", "charger_hours", "washing_cycles",
        "kwh", "tariff_rs_per_kwh", "cost_rs", "emission_factor_kg_per_kwh", "co2_kg"
    ])
    df_init.to_csv(LOG_FILE, index=False)


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

st.title("Streaks & Rewards Library")

if df.empty:
    st.warning("No data available. Please log entries first.")
    st.stop()

# -------------------------
# User Cards (Library View)
# -------------------------
st.header(" User Energy Heroes")

users = df["user_id"].unique().tolist()

for user in users:
    user_df = df[df["user_id"] == user].sort_values("date")

    # Streak calculation = consecutive days logged
    dates = user_df["date"].dt.date.unique()
    dates_sorted = sorted(dates)
    streak = 1
    max_streak = 1
    for i in range(1, len(dates_sorted)):
        if (dates_sorted[i] - dates_sorted[i-1]) == datetime.timedelta(days=1):
            streak += 1
            max_streak = max(max_streak, streak)
        else:
            streak = 1

    latest = user_df.iloc[-1]
    kwh = latest["kwh"]
    cost = latest["cost_rs"]
    co2 = latest["co2_kg"]

    with st.expander(f" {user} — Current Streak: {max_streak} days"):
        col1, col2, col3 = st.columns(3)
        col1.metric("kWh (latest)", f"{kwh:.2f}")
        col2.metric("Cost Rs", f"₹ {cost:.2f}")
        col3.metric("CO₂ (kg)", f"{co2:.2f}")

        # Show user trend
        fig = px.line(
            user_df,
            x="date", y="kwh", markers=True,
            title=f"{user} Energy Usage Trend"
        )
        st.plotly_chart(fig, use_container_width=True)

        # Gamified badges
        st.markdown(" **Badges Earned:**")
        badges = []
        if user_df["kwh"].max() - user_df["kwh"].min() >= 5:
            badges.append(" Power Saver (Saved 5+ kWh)")
        if (user_df["cost_rs"].max() - user_df["cost_rs"].min()) >= 50:
            badges.append("Cost Cutter (Saved ₹50+)")
        if (user_df["co2_kg"].max() - user_df["co2_kg"].min()) >= 2:
            badges.append("CO₂ Reducer (Cut 2+ kg CO₂)")
        if max_streak >= 3:
            badges.append(" Consistency Champ (3+ day streak)")

        if badges:
            for b in badges:
                st.success(b)
        else:
            st.info("No badges earned yet — keep saving energy! ")

# -------------------------
# Quizzes / Engagement
# -------------------------
st.header("Quick Energy Quiz")

q = st.radio(
    "Which of these saves the most energy?",
    ["Turning off charger when not in use", "Switching to LED bulbs", "Unplugging fan for 30 minutes"]
)

if st.button("Submit Answer"):
    if q == "Switching to LED bulbs":
        st.success("Correct! LEDs save up to 80% compared to old bulbs.")
    else:
        st.error(" Not quite! The biggest saving comes from switching to LEDs.")

# -------------------------
# Reminders
# -------------------------
st.header("Energy-Saving Reminders")

reminders = [
    " Turn off fans/lights when leaving a room.",
    "❄ Set AC to 24°C for optimal efficiency.",
    " Unplug chargers and devices when not in use.",
    " Do laundry with full loads to save energy.",
    " Use natural daylight instead of lights during the day."
]

for r in reminders:
    st.write(r)
