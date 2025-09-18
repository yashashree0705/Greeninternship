# pages/1_Analytics.py
# pages/1_Analytics.py
import streamlit as st
import pandas as pd
import plotly.express as px
from utils import read_logs

st.title("Energy Usage Analytics")

df = read_logs()
if df.empty:
    st.warning("No data available. Please add logs first.")
    st.stop()

# Aggregate View
st.header("Overall Energy Trends")
fig = px.line(df, x="date", y="kwh", color="user_id", markers=True,
              title="Energy Consumption Over Time")
st.plotly_chart(fig, use_container_width=True)

# Baseline vs Post
st.header("⚖ Baseline vs Post Comparison")
if "baseline" in df["period"].values and "post" in df["period"].values:
    compare = df.groupby("period")[["kwh", "cost_rs", "co2_kg"]].mean().reset_index()
    fig2 = px.bar(compare.melt(id_vars="period", var_name="Metric", value_name="Value"),
                  x="Metric", y="Value", color="period", barmode="group", text_auto=".2f")
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("Need both baseline and post data to show comparison.")

# Appliance Breakdown
st.header("🔌 Appliance Usage Breakdown")
appliance_cols = ["fan_hours", "light_hours", "ac_hours", "charger_hours", "washing_cycles"]
avg_usage = df.groupby("period")[appliance_cols].mean().reset_index()
fig3 = px.bar(avg_usage.melt(id_vars="period", var_name="Appliance", value_name="Hours"),
              x="Appliance", y="Hours", color="period", barmode="group", text_auto=".2f")
st.plotly_chart(fig3, use_container_width=True)

# Top Energy Savers
st.header("Top Energy Savers")
savings = df.groupby("user_id")["kwh"].sum().sort_values()
st.bar_chart(savings)
