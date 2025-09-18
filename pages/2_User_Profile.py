# pages/2_User_Profile.py
# pages/2_User_Profile.py
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

# ---------------------------
# Achievements
# ---------------------------
st.subheader("Achievements")
achievements = []
if user_df["kwh"].min() < 3:
    achievements.append("Ultra Saver (Lowest kWh < 3)")
if (user_df["cost_rs"].max() - user_df["cost_rs"].min()) >= 100:
    achievements.append("Big Saver (₹100+ Saved)")
if len(user_df["date"].dt.date.unique()) >= 7:
    achievements.append("Weekly Warrior (7+ active days)")

if achievements:
    for ach in achievements:
        st.success(ach)
else:
    st.info("No achievements yet – keep going!")

# ---------------------------
# Community Comparison
# ---------------------------
st.subheader("📈 Community Rank")
community_avg = df["kwh"].mean()
if avg_kwh < community_avg:
    st.success(f"👏 You use less energy ({avg_kwh:.2f}) than the community average ({community_avg:.2f})!")
else:
    st.error(f"⚡ You use more ({avg_kwh:.2f}) than the community average ({community_avg:.2f}). Try to reduce it!")
