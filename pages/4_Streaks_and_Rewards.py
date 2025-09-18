# pages/4_Streaks_and_Rewards.py

import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import random

from utils import read_logs  # Always use shared utils

@st.cache_data
def load_logs():
    try:
        df = read_logs()
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        return df
    except Exception as e:
        st.error(f"Error loading logs: {e}")
        return pd.DataFrame()

df = load_logs()

st.title("Streaks & Rewards Library")

if df.empty:
    st.warning(" No data available. Please log entries first.")
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
        col1.metric(" kWh (latest)", f"{kwh:.2f}")
        col2.metric(" Cost (Rs)", f"₹ {cost:.2f}")
        col3.metric(" CO₂ (kg)", f"{co2:.2f}")

        # Show user trend
        fig = px.line(
            user_df,
            x="date", y="kwh", markers=True,
            title=f"{user} — Energy Usage Trend"
        )
        st.plotly_chart(fig, use_container_width=True)

        # Gamified badges
        st.markdown(" **Badges Earned:**")
        badges = []
        if user_df["kwh"].max() - user_df["kwh"].min() >= 5:
            badges.append(" Power Saver (Saved 5+ kWh)")
        if (user_df["cost_rs"].max() - user_df["cost_rs"].min()) >= 50:
            badges.append(" Cost Cutter (Saved ₹50+)")
        if (user_df["co2_kg"].max() - user_df["co2_kg"].min()) >= 2:
            badges.append(" CO₂ Reducer (Cut 2+ kg CO₂)")
        if max_streak >= 3:
            badges.append(" Consistency Champ (3+ day streak)")

        if badges:
            for b in badges:
                st.success(b)
        else:
            st.info("No badges earned yet — keep saving energy!")

# -------------------------
# Dynamic Quiz
# -------------------------
st.header("Quick Energy Quiz")

# Pool of quiz questions
quiz_pool = [
    {
        "q": "Which of these saves the most energy?",
        "options": [" Turning off charger", " Switching to LED bulbs", " Unplugging fan for 30 minutes"],
        "answer": "Switching to LED bulbs"
    },
    {
        "q": "What is the most efficient AC temperature setting?",
        "options": ["18°C ", "22°C ", "24°C "],
        "answer": "24°C "
    },
    {
        "q": "Which appliance usually consumes the MOST electricity?",
        "options": ["Fan ", "Refrigerator ", "Laptop "],
        "answer": "Refrigerator "
    },
    {
        "q": "How can you reduce washing machine energy use?",
        "options": ["Half loads", "Full loads ", "Hot water wash"],
        "answer": "Full loads "
    },
    {
        "q": "What does using natural daylight instead of bulbs save?",
        "options": ["Money", "Energy", "Both"],
        "answer": "Both "
    },
]

# Pick one random question per refresh
quiz = random.choice(quiz_pool)

st.subheader(quiz["q"])
choice = st.radio("Choose one:", quiz["options"], key=quiz["q"])

if st.button("Submit Answer"):
    if choice == quiz["answer"]:
        st.success("Correct! You're an energy hero!")
    else:
        st.error(f" Not quite! The right answer is: **{quiz['answer']}**")

# -------------------------
# Reminders
# -------------------------
st.header(" Energy-Saving Reminders")

reminders = [
    "Turn off fans/lights when leaving a room.",
    " Set AC to 24°C for optimal efficiency.",
    " Unplug chargers and devices when not in use.",
    " Do laundry with full loads to save energy.",
    " Use natural daylight instead of lights during the day."
]

for r in reminders:
    st.info(r)
