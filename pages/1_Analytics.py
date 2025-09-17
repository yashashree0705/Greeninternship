# pages/1_Analytics.py

import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------
# Load Data
# -------------------------
from utils import read_logs, append_log

# Optional debug
# print("LOG_FILE path:", LOG_FILE)
# print("Exists?", os.path.exists(LOG_FILE))
# print(df.head())




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

st.title("Energy Usage Analytics")
st.markdown("Explore trends, compare baseline vs post, and see who saved the most!")

if df.empty:
    st.warning("No data available. Please add logs first.")
    st.stop()

# -------------------------
# Baseline vs Post Comparison
# -------------------------
st.header("⚖ Baseline vs Post Comparison")

if "baseline" in df["period"].unique() and "post" in df["period"].unique():
    comp = df.groupby("period").agg(
        total_kwh=("kwh", "mean"),
        total_cost=("cost_rs", "mean"),
        total_co2=("co2_kg", "mean")
    ).reset_index()

    col1, col2, col3 = st.columns(3)
    col1.metric("Avg. kWh (Baseline)", f"{comp.loc[comp['period']=='baseline','total_kwh'].values[0]:.2f}")
    col2.metric("Avg. kWh (Post)", f"{comp.loc[comp['period']=='post','total_kwh'].values[0]:.2f}")
    col3.metric("Change (%)", f"{((comp.loc[comp['period']=='post','total_kwh'].values[0] - comp.loc[comp['period']=='baseline','total_kwh'].values[0]) / comp.loc[comp['period']=='baseline','total_kwh'].values[0])*100:.1f}%")

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
    st.info("Not enough data for baseline vs post comparison yet.")

# -------------------------
# Per User Savings
# -------------------------
st.header("Per-User Savings")

if "baseline" in df["period"].unique() and "post" in df["period"].unique():
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

    # Leaderboard chart
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
    st.info("Need both baseline and post entries for users to calculate savings.")

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
