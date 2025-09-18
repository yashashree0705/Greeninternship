# pages/2_User_Profile.py
import streamlit as st
import pandas as pd
import plotly.express as px
import os
import datetime
import random

from utils import LOG_FILE, read_logs

st.title("User Profile Dashboard")

# Load logs
df = read_logs()

if df.empty:
    st.warning("⚠ No user data found. Please add some logs first.")
    st.stop()

# ---------------------------
# User Selector
# ---------------------------
users = df["user_id"].unique().tolist()
selected_user = st.selectbox("Select a user", users)

user_df = df[df["user_id"] == selected_user].sort_values("date")

# ---------------------------
# Profile Card
# ---------------------------
st.subheader("Profile Overview")
col1, col2 = st.columns([1, 2])

with col1:
    st.image("https://cdn-icons-png.flaticon.com/512/847/847969.png", width=120)  # placeholder avatar
    st.markdown(f"### {selected_user}")
    st.markdown("Location: Not set")
    st.markdown("Role: Energy Enthusiast")

with col2:
    avg_kwh = user_df["kwh"].mean()
    avg_cost = user_df["cost_rs"].mean()
    avg_co2 = user_df["co2_kg"].mean()

    st.metric("Avg. kWh/day", f"{avg_kwh:.2f}")
    st.metric("Avg. Cost/day", f"₹ {avg_cost:.2f}")
    st.metric("Avg. CO₂/day", f"{avg_co2:.2f} kg")

# ---------------------------
# Trend Snapshot
# ---------------------------
st.subheader("Usage Snapshot")
fig = px.line(user_df, x="date", y="kwh", markers=True, title="Daily Energy Usage")
st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# Goals & Progress
# ---------------------------
st.subheader("Personal Goals")
goal = st.slider("Set your daily kWh reduction goal", 1, 20, 5)
latest_usage = user_df.iloc[-1]["kwh"]

if latest_usage <= goal:
    st.success(f"Great! You stayed under your goal of {goal} kWh.")
else:
    st.warning(f"You used {latest_usage:.2f} kWh, above your goal of {goal} kWh.")

# -------------------------
# Achievements
# -------------------------
st.subheader("Achievements")

achievements = []

if "date" in user_df.columns:
    # Ensure date is datetime
    user_df["date"] = pd.to_datetime(user_df["date"], errors="coerce")
    user_df["date"].fillna(pd.Timestamp.today().normalize(), inplace=True)

    # Active days
    active_days = user_df["date"].dt.normalize().nunique()
    if active_days >= 7:
        achievements.append("Weekly Warrior – Logged 7+ active days")
    if active_days >= 30:
        achievements.append("Monthly Master – Logged 30+ active days")

# Energy milestones
if "kwh" in user_df.columns:
    total_kwh = user_df["kwh"].sum()
    if total_kwh <= 50:
        achievements.append("Low Power User – Kept usage under 50 kWh")
    if total_kwh >= 200:
        achievements.append("Power Tracker – Logged over 200 kWh usage")

# CO₂ milestones
if "co2_kg" in user_df.columns:
    total_co2 = user_df["co2_kg"].sum()
    if total_co2 < 20:
        achievements.append("Green Guardian – CO₂ footprint < 20 kg")
    if total_co2 >= 100:
        achievements.append("Climate Contributor – Tracked 100+ kg CO₂")

# Consistency
if "date" in user_df.columns:
    dates_sorted = sorted(user_df["date"].dt.normalize().unique())
    streak, max_streak = 1, 1
    for i in range(1, len(dates_sorted)):
        if (dates_sorted[i] - dates_sorted[i-1]) == pd.Timedelta(days=1):
            streak += 1
            max_streak = max(max_streak, streak)
        else:
            streak = 1
    if max_streak >= 5:
        achievements.append(f"Consistency Champ – {max_streak}-day streak")

# Display achievements
if achievements:
    for ach in achievements:
        st.success(ach)
else:
    st.info("No achievements yet – keep logging to unlock badges!")


# ---------------------------
# Community Comparison
# ---------------------------
st.subheader("Community Rank")
community_avg = df["kwh"].mean()
if avg_kwh < community_avg:
    st.success(f"You use less energy ({avg_kwh:.2f}) than the community average ({community_avg:.2f})!")
else:
    st.error(f"You use more ({avg_kwh:.2f}) than the community average ({community_avg:.2f}). Try to reduce it!")
