# pages/1_Analytics.py
# pages/1_Analytics.py
import streamlit as st
import pandas as pd
import os
import tempfile
import matplotlib.pyplot as plt
import plotly.express as px  # <-- you forgot this

# Use the SAME log file as app.py
LOG_FILE = os.path.join(tempfile.gettempdir(), "logs.csv")

def load_logs():
    try:
        return pd.read_csv(LOG_FILE)
    except Exception:
        return pd.DataFrame()

# -------------------------
# Streamlit Page Config
# -------------------------
st.set_page_config(page_title="Energy Usage Analytics", layout="wide")

st.title("Energy Usage Analytics")
st.markdown("Explore trends, compare baseline vs post, and see who saved the most!")

# -------------------------
# Load Data
# -------------------------
df = load_logs()

if df.empty:
    st.warning("⚠ No data available. Please add logs first in the main app.")
    st.stop()  # Exit early if no data

st.success(f"Loaded {len(df)} log entries")

# -------------------------
# Full Logs
# -------------------------
st.subheader("All Logs")
st.dataframe(df)

# -------------------------
# User Summary
# -------------------------
st.subheader("User Summary")
agg = df.groupby("user_id").agg({
    "kwh": ["sum", "mean", "count"],
    "cost_rs": "sum",
    "co2_kg": "sum"
})
agg.columns = ["_".join(col) for col in agg.columns]
st.table(agg.reset_index())

# -------------------------
# kWh Trend over Time
# -------------------------
st.subheader("Energy Trend")
df["date"] = pd.to_datetime(df["date"])

fig, ax = plt.subplots()
for uid, g in df.groupby("user_id"):
    g_sorted = g.sort_values("date")
    ax.step(g_sorted["date"], g_sorted["kwh"], where="mid", marker="o", label=uid)
ax.set_xlabel("Date")
ax.set_ylabel("kWh")
ax.legend()
ax.grid(True)
st.pyplot(fig)

# -------------------------
# Baseline vs Post Comparison
# -------------------------
st.header("⚖ Baseline vs Post Comparison")

if {"baseline", "post"}.issubset(df["period"].unique()):
    comp = df.groupby("period").agg(
        total_kwh=("kwh", "mean"),
        total_cost=("cost_rs", "mean"),
        total_co2=("co2_kg", "mean")
    ).reset_index()

    col1, col2, col3 = st.columns(3)
    baseline_kwh = comp.loc[comp["period"] == "baseline", "total_kwh"].values[0]
    post_kwh = comp.loc[comp["period"] == "post", "total_kwh"].values[0]
    col1.metric("Avg. kWh (Baseline)", f"{baseline_kwh:.2f}")
    col2.metric("Avg. kWh (Post)", f"{post_kwh:.2f}")
    col3.metric("Change (%)", f"{((post_kwh - baseline_kwh) / baseline_kwh) * 100:.1f}%")

    fig = px.bar(
        comp,
        x="period",
        y="total_kwh",
        color="period",
        text_auto=".2f",
        title="Average Energy Consumption (kWh)"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("ℹ Not enough data for baseline vs post comparison yet. Add both baseline and post entries.")

# -------------------------
# Per User Savings
# -------------------------
st.header("Per-User Savings")

if {"baseline", "post"}.issubset(df["period"].unique()):
    baseline = df[df["period"] == "baseline"].set_index("user_id")
    post = df[df["period"] == "post"].set_index("user_id")

    merged = baseline[["kwh", "cost_rs", "co2_kg"]].join(
        post[["kwh", "cost_rs", "co2_kg"]],
        lsuffix="_baseline",
        rsuffix="_post",
        how="inner"
    )

    merged["kwh_saving"] = merged["kwh_baseline"] - merged["kwh_post"]
    merged["cost_saving"] = merged["cost_rs_baseline"] - merged["cost_rs_post"]
    merged["co2_saving"] = merged["co2_kg_baseline"] - merged["co2_kg_post"]

    st.dataframe(merged[["kwh_baseline", "kwh_post", "kwh_saving", "cost_saving", "co2_saving"]])

    leaderboard = merged.reset_index().sort_values("kwh_saving", ascending=False)
    fig2 = px.bar(
        leaderboard,
        x="user_id",
        y="kwh_saving",
        text_auto=".2f",
        title="Leaderboard: kWh Savings per User",
        color="kwh_saving"
    )
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("ℹ Need both baseline and post entries for users to calculate savings.")

# -------------------------
# Appliance Usage Insights
# -------------------------
st.header("Appliance Usage Insights")

avg_hours = df.groupby("period")[["fan_hours", "light_hours", "ac_hours", "charger_hours", "washing_cycles"]].mean().reset_index()
fig3 = px.bar(
    avg_hours.melt(id_vars="period", var_name="appliance", value_name="hours"),
    x="appliance",
    y="hours",
    color="period",
    barmode="group",
    title="Average Appliance Usage Hours (Baseline vs Post)"
)
st.plotly_chart(fig3, use_container_width=True)
